"""
pages/base_page.py
===================
BasePage berisi fungsi umum yang dipakai di SEMUA page object (klik,
ketik teks, tunggu elemen, tunggu loading ExtJS selesai, dll), supaya
tidak ditulis ulang di setiap page object.

CATATAN PENTING soal ExtJS (framework yang dipakai NewDLA):
- ExtJS sering menampilkan "loading mask" (overlay abu-abu + spinner) saat
  mengambil data dari server. Klik SAAT mask masih ada bisa gagal/nyasar,
  makanya ada wait_loading_mask_gone().
- id elemen yang di-generate ExtJS (misal id="button-1042") TIDAK STABIL --
  berubah setiap kali komponen di-render ulang. Prioritas locator yang
  dipakai di seluruh project ini (dari paling stabil ke paling rapuh):
    1. data-qtip (tooltip yang sengaja ditulis developer)
    2. itemId / name / id custom
    3. teks yang tampil ke user (label tombol, header, dsb.)
    4. class css yang stabil (bukan class auto-generate ExtJS)
- Framework ini menghindari time.sleep() tetap (fixed) -- semua "menunggu"
  memakai WebDriverWait + expected_conditions supaya tidak flaky dan tidak
  boros waktu menunggu tanpa alasan.
"""

import os
import time
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from config import config


class BasePage:
    # Loading mask ExtJS (lebih dari satu kandidat class tergantung versi).
    LOADING_MASK_LOCATORS = (
        (By.CSS_SELECTOR, "div.x-mask"),
        (By.CSS_SELECTOR, "div.x-mask-msg"),
    )

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or config.DEFAULT_TIMEOUT

    # ------------------------------ Helper dasar ------------------------------
    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def pace(self, seconds=None):
        """Jeda visual antar-aksi (bukan untuk menunggu elemen)."""
        time.sleep(seconds if seconds is not None else config.ACTION_PACE_SECONDS)

    def find(self, locator, timeout=None):
        """Tunggu elemen ADA di DOM, kembalikan elemennya."""
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def find_all(self, locator, timeout=None):
        """Tunggu minimal 1 elemen ADA di DOM, kembalikan semuanya."""
        return self._wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def find_visible_among(self, locator, timeout=None):
        """Ambil elemen PERTAMA yang benar2 TAMPIL dari locator yang
        match banyak elemen (yang lain hidden di DOM)."""
        elements = self._wait(timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
        for element in elements:
            try:
                if element.is_displayed():
                    return element
            except StaleElementReferenceException:
                continue
        raise TimeoutException(
            f"Tidak ada elemen yang benar-benar tampil untuk locator: {locator}"
        )

    def find_all_visible(self, locator, timeout=None):
        """Sama seperti find_visible_among() tapi kembalikan SEMUA yang
        tampil (dipakai saat urutan elemen tampil penting)."""
        try:
            elements = self._wait(timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            return []
        visible = []
        for element in elements:
            try:
                if element.is_displayed():
                    visible.append(element)
            except StaleElementReferenceException:
                continue
        return visible

    # ------------------ Dialog/window ExtJS yang SEDANG AKTIF ------------------
    # is_displayed() TIDAK peduli elemen tertutup mask/dialog lain, jadi
    # elemen harus dicari DI DALAM window aktif (z-index tertinggi) supaya
    # tidak salah sasaran ke elemen senama di dialog/layer di belakangnya.
    WINDOW_LOCATOR = (By.CSS_SELECTOR, "div.x-window")

    def find_active_window(self, timeout=None):
        """Window ExtJS yang tampil dengan z-index PALING TINGGI (paling atas)."""
        windows = self.find_all_visible(self.WINDOW_LOCATOR, timeout=timeout or self.timeout)
        if not windows:
            raise TimeoutException("Tidak ada dialog/window ExtJS yang tampil saat ini.")

        def _z_index(el):
            try:
                value = self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).zIndex;", el
                )
                return int(value) if value and value != "auto" else 0
            except Exception:
                return 0

        return max(windows, key=_z_index)

    def find_all_visible_in_active_window(self, locator, timeout=None):
        """Semua elemen tampil untuk locator, HANYA di dalam window aktif."""
        window = self.find_active_window(timeout=timeout)
        by, value = locator
        relative_value = value
        if by == By.XPATH and not value.startswith("."):
            relative_value = "." + value if value.startswith("//") else value
        try:
            elements = window.find_elements(by, relative_value)
        except Exception:
            elements = []
        visible = []
        for element in elements:
            try:
                if element.is_displayed():
                    visible.append(element)
            except StaleElementReferenceException:
                continue
        return visible

    def find_visible_in_active_window(self, locator, timeout=None):
        """Elemen PERTAMA yang tampil di dalam window aktif."""
        deadline = time.time() + (timeout or self.timeout)
        last_error = None
        while time.time() < deadline:
            try:
                elements = self.find_all_visible_in_active_window(locator, timeout=2)
                if elements:
                    return elements[0]
            except TimeoutException as exc:
                last_error = exc
            time.sleep(0.25)
        raise TimeoutException(
            f"Tidak ada elemen yang benar-benar tampil di dalam window aktif untuk locator: {locator}"
        ) from last_error

    def click_visible_in_active_window(self, locator, timeout=None):
        """Native click + JS fallback pada elemen tampil di window aktif."""
        element = self.find_visible_in_active_window(locator, timeout=timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        clicked = False
        for _ in range(2):
            try:
                element.click()
                clicked = True
                break
            except Exception:
                self.pace(1)
        if not clicked:
            self.driver.execute_script("arguments[0].click();", element)
        self.pace()
        return element

    def click_visible_among(self, locator, timeout=None):
        """Klik elemen yang benar2 tampil (bukan match pertama yang bisa hidden)."""
        element = self.find_visible_among(locator, timeout=timeout)
        self.click_via_js(element)
        return element

    def click(self, locator, timeout=None):
        """Klik elemen. Fallback JS kalau kena StaleElement/terhalang
        (loading mask / ikon tombol menutupi titik klik)."""
        try:
            element = self._wait(timeout).until(EC.element_to_be_clickable(locator))
            element.click()
        except StaleElementReferenceException:
            element = self._wait(timeout).until(EC.element_to_be_clickable(locator))
            element.click()
        except ElementClickInterceptedException:
            self.wait_loading_mask_gone(timeout=10)
            element = self.find(locator, timeout=timeout)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            self.driver.execute_script("arguments[0].click();", element)
        self.pace()

    def click_via_js(self, locator_or_element, timeout=None):
        """Klik pakai JavaScript."""
        element = locator_or_element
        if isinstance(locator_or_element, tuple):
            element = self.find(locator_or_element, timeout=timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)
        self.pace()

    def type_text(self, locator, text, clear_first=True, timeout=None):
        """Tunggu elemen tampil, kosongkan (opsional), lalu ketik teks."""
        element = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.pace()

    def type_text_visible(self, locator, text, clear_first=True, timeout=None):
        """Ketik ke elemen yang benar2 TAMPIL (untuk locator yang match
        elemen ganda di DOM) + scroll ke viewport sebelum ketik."""
        element = self.find_visible_among(locator, timeout=timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.pace()

    def get_text(self, locator, timeout=None):
        return self.find(locator, timeout=timeout).text

    def is_visible(self, locator, timeout=None):
        """True/False apakah elemen tampil. HATI-HATI: mengunci ke match
        PERTAMA di DOM -- pakai find_visible_among untuk locator ganda."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_present(self, locator, timeout=None):
        """Cek apakah elemen ADA di DOM (tidak wajib terlihat)."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_url_contains(self, text, timeout=None):
        return self._wait(timeout).until(EC.url_contains(text))

    def find_first_visible(self, locator_candidates, timeout=None):
        """Coba kandidat locator satu per satu, kembalikan yang pertama
        ketemu & terlihat (untuk locator yang belum 100% dikonfirmasi)."""
        for locator in locator_candidates:
            if self.is_visible(locator, timeout=timeout or 3):
                return locator
        return None

    # ----------------------------- Loading mask ExtJS -----------------------------
    def wait_loading_mask_gone(self, timeout=None):
        """Tunggu loading mask hilang. Tidak error kalau mask tidak muncul."""
        wait_timeout = timeout or self.timeout
        for mask_locator in self.LOADING_MASK_LOCATORS:
            try:
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.invisibility_of_element_located(mask_locator)
                )
            except TimeoutException:
                continue

    # --------------------- Screenshot manual (di luar hook conftest) ---------------------
    def take_screenshot(self, name):
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(config.SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filepath)
        return filepath

    def scroll_into_view(self, locator, timeout=None):
        element = self.find(locator, timeout=timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        return element
