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
    # Loading mask ExtJS yang umum dipakai (bisa lebih dari satu kandidat
    # class tergantung versi ExtJS yang dipakai NewDLA).
    LOADING_MASK_LOCATORS = (
        (By.CSS_SELECTOR, "div.x-mask"),
        (By.CSS_SELECTOR, "div.x-mask-msg"),
    )

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or config.DEFAULT_TIMEOUT

    # ------------------------------------------------------------------
    # Helper dasar
    # ------------------------------------------------------------------
    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def pace(self, seconds=None):
        """Jeda singkat HANYA untuk kebutuhan visual (supaya urutan aksi
        kelihatan jelas satu-satu saat browser diamati/didemokan) --
        BUKAN untuk menunggu elemen (itu tugas WebDriverWait, tetap dipakai
        di semua method lain). Dipanggil otomatis setelah click(),
        click_via_js(), dan type_text() supaya aksi tidak terasa
        instan/sekelebat, tapi juga tidak berlarut-larut (default 5 detik,
        bisa diubah lewat config.ACTION_PACE_SECONDS / env DLA_ACTION_PACE)."""
        time.sleep(seconds if seconds is not None else config.ACTION_PACE_SECONDS)

    def find(self, locator, timeout=None):
        """Tunggu sampai elemen ADA di DOM, kembalikan elemennya."""
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def find_all(self, locator, timeout=None):
        """Tunggu sampai minimal 1 elemen ADA di DOM, kembalikan semuanya."""
        return self._wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def find_visible_among(self, locator, timeout=None):
        """Untuk locator yang TIDAK unik (banyak elemen cocok di DOM,
        tapi cuma satu yang benar-benar tampil di layar -- elemen lain
        ada di DOM namun disembunyikan/display:none, misalnya dropdown
        Posisi lain di popup Advanced Filter yang belum dibuka).

        Dipakai supaya kita tidak salah klik elemen yang tersembunyi
        (yang kalau diklik pakai JS tetap "berhasil" secara teknis,
        tapi dropdown/boundlist yang muncul jadi salah posisi / muncul
        sendirian di sudut layar, karena elemen sumbernya tidak
        punya posisi render yang valid)."""
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
        """Sama seperti find_visible_among(), TAPI kembalikan SEMUA elemen
        yang benar-benar tampil (bukan cuma yang pertama ketemu). Dipakai
        di tempat yang butuh tahu URUTAN elemen yang tampil di layar --
        misal tombol 'Tambah' Penyetuju vs Tambah Penerima/Tembusan di
        form Surat Keluar Eksternal & Nota Dinas Keluar, yang teksnya
        identik ('Tambah') dan cuma bisa dibedakan lewat urutan
        tampilnya di form yang SEDANG terbuka -- bukan urutan di DOM
        (yang bisa kebawa elemen lain yang sudah basi/tersembunyi kalau
        popup sebelumnya belum benar2 tertutup, penyebab popup
        tertumpuk/tertindih)."""
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

    # ------------------------------------------------------------------
    # Dialog/window ExtJS yang SEDANG AKTIF (fix bug #3/#4/#5/#6: popup
    # "nyasar"/menumpuk/tertindih)
    # ------------------------------------------------------------------
    # AKAR MASALAH: is_displayed() Selenium cuma cek CSS
    # visibility/opacity/ukuran elemen -- TIDAK PEDULI elemen itu
    # sedang TERTUTUP MASK/dialog lain yang tumpang tindih di atasnya.
    # Saat dialog "Tambah Agenda Surat" terbuka, tombol 'Tambah' di
    # halaman LIST di belakangnya masih is_displayed()==True (cuma
    # ketutup mask overlay secara visual, bukan display:none) --
    # akibatnya find_all_visible(BTN_TAMBAH_ANY) bisa ikut menghitung
    # tombol 'Tambah' milik halaman list itu sebagai salah satu tombol
    # "Tambah" yang tampil, sehingga index Tambah Penyetuju/Tambah
    # Penerima jadi bergeser (salah sasaran) -- persis gejala "tombol
    # tambah penyetuju/penerima tidak muncul" & "form Tambah menumpuk
    # / berkali-kali" yang dilaporkan. Fix: batasi pencarian elemen HANYA
    # di dalam dialog/window ExtJS yang sedang AKTIF (z-index paling
    # tinggi di antara semua div.x-window yang tampil).
    WINDOW_LOCATOR = (By.CSS_SELECTOR, "div.x-window")

    def find_active_window(self, timeout=None):
        """Kembalikan elemen dialog/window ExtJS yang sedang AKTIF (paling
        atas) saat ini -- dipilih dari semua div.x-window yang BENAR-BENAR
        tampil, diambil yang z-index-nya PALING TINGGI (dialog yang paling
        terakhir dibuka / paling atas)."""
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
        """Sama seperti find_all_visible(), TAPI dibatasi HANYA di dalam
        dialog/window ExtJS yang sedang aktif (lihat find_active_window) --
        mencegah ikut menghitung elemen yang senama tapi milik halaman/
        dialog LAIN di belakangnya yang cuma tertutup mask (bukan
        benar-benar display:none)."""
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
        """Elemen PERTAMA yang benar-benar tampil di dalam dialog/window
        ExtJS yang sedang aktif. Sama alasannya dengan
        find_all_visible_in_active_window()."""
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
        """Native click + JS fallback. ExtJS checkboxes perlu JS click."""
        element = self.find_visible_in_active_window(locator, timeout=timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        # Coba native click
        clicked = False
        for _ in range(2):
            try:
                element.click()
                clicked = True
                break
            except Exception:
                self.pace(1)
        # Fallback: JS click
        if not clicked:
            self.driver.execute_script("arguments[0].click();", element)
        self.pace()
        return element

    def click_visible_among(self, locator, timeout=None):
        """Gabungan find_visible_among() + klik via JS -- dipakai di
        SEMUA tempat yang memilih 1 opsi dari daftar/boundlist yang
        teksnya bisa DUPLIKAT di DOM (opsi yang sama muncul di lebih
        dari satu boundlist/combo, tapi cuma satu yang benar-benar
        tampil). Ini akar penyebab banyak TimeoutException di flow
        filter & form: element_to_be_clickable() pada elemen PERTAMA
        yang match (yang ternyata tersembunyi) akan menunggu sampai
        timeout tanpa pernah mencoba elemen lain yang benar-benar
        tampil."""
        element = self.find_visible_among(locator, timeout=timeout)
        self.click_via_js(element)
        return element

    def click(self, locator, timeout=None):
        """Tunggu elemen bisa DIKLIK, baru klik. Kalau kena
        StaleElementReferenceException (elemen sempat di-render ulang
        ExtJS di antara pencarian & klik), coba sekali lagi.

        Kalau kena ElementClickInterceptedException -- ada 2 penyebab
        umum yang ditemukan di NewDLA:
          1. Loading mask (div.x-mask) belum hilang saat diklik (klik
             menu/tombol saat halaman sebelumnya masih transisi).
          2. Tombol ExtJS yang punya ikon + teks di satu elemen <a>,
             titik tengah yang dihitung Selenium untuk native click()
             kadang jatuh di elemen ikon (sibling), bukan di teks
             (contoh: tombol SIMPAN pada popup upload berkas Link).
        Kedua kasus ini diatasi dengan fallback klik via JavaScript
        (tidak bergantung ke titik koordinat / elemen di atasnya)."""
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
        """Tunggu elemen muncul, kosongkan (opsional), lalu ketik teks."""
        element = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.pace()

    def type_text_visible(self, locator, text, clear_first=True, timeout=None):
        """Sama seperti type_text(), TAPI untuk locator yang TIDAK unik --
        banyak elemen cocok di DOM tapi cuma satu yang benar-benar tampil
        (misal input[type='search'] yang di ExtJS sering dirender ganda:
        satu tersembunyi lebih dulu di DOM, satu lagi yang aktif/tampil).

        type_text() versi biasa pakai visibility_of_element_located() yang
        MENGUNCI ke elemen PERTAMA yang match locator lalu menunggu elemen
        ITU tampil -- kalau yang pertama di DOM justru yang tersembunyi,
        dia menunggu sampai timeout tanpa pernah mencoba elemen lain yang
        benar-benar tampil (akar penyebab TimeoutException di cari_otomatis
        modul 2-5). Fix: pilih elemen yang benar-benar tampil lewat
        find_visible_among (mirror find_visible_among/click_visible_among),
        baru clear()+send_keys()."""
        element = self.find_visible_among(locator, timeout=timeout)
        # PENTING (fix bug field form yang "terputus"/tidak keisi mulai
        # dari field yang letaknya di bawah/harus discroll dulu -- mis.
        # Jenis Surat s.d. Lokasi Arsip Fisik pada form Tambah Agenda
        # Surat): send_keys() tidak selalu memicu auto-scroll pada
        # container yang overflow-nya diatur manual oleh ExtJS (bukan
        # scroll bawaan browser/document), jadi elemen yang belum masuk
        # area pandang bisa gagal diketik walau is_displayed()==True.
        # Fix: scroll elemen ke tengah viewport dulu via JS (sama seperti
        # click_via_js) sebelum clear()/send_keys().
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
        """True/False apakah elemen tampil dalam waktu tertentu -- TIDAK
        melempar error kalau tidak ketemu. Berguna untuk verifikasi
        elemen yang sifatnya opsional."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_present(self, locator, timeout=None):
        """Cek apakah elemen ADA di DOM (tidak wajib terlihat di layar)."""
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
        """Coba beberapa kandidat locator, kembalikan locator PERTAMA
        yang berhasil ditemukan & terlihat, atau None kalau semua gagal.

        Berguna selama locator asli belum 100% dikonfirmasi (dummy /
        candidate locator bertanda TODO) -- daripada langsung gagal
        karena 1 tebakan salah, coba beberapa alternatif sekaligus."""
        for locator in locator_candidates:
            if self.is_visible(locator, timeout=timeout or 3):
                return locator
        return None

    # ------------------------------------------------------------------
    # Khusus ExtJS: loading mask
    # ------------------------------------------------------------------
    def wait_loading_mask_gone(self, timeout=None):
        """Tunggu sampai loading mask ExtJS (overlay abu-abu + spinner)
        hilang. Dipanggil setelah aksi yang memicu request ke server
        (klik CARI, buka dokumen, dll) supaya kita tidak membaca data
        SAAT masih loading. Kalau mask memang tidak pernah muncul
        (request cepat), fungsi ini tidak error -- lanjut saja."""
        wait_timeout = timeout or self.timeout
        for mask_locator in self.LOADING_MASK_LOCATORS:
            try:
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.invisibility_of_element_located(mask_locator)
                )
            except TimeoutException:
                continue

    # ------------------------------------------------------------------
    # Screenshot manual (di luar hook kegagalan otomatis di conftest.py)
    # ------------------------------------------------------------------
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
