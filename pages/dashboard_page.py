"""
pages/dashboard_page.py
========================
Modul 1 - Dashboard (10 Test Steps)
- Verifikasi widget: Surat Masuk, Disposisi Masuk, Disposisi Keluar,
  Surat Keluar Eksternal, Surat Keluar Internal.
- Fitur rentang tanggal: klik ikon -> isi tanggal awal & akhir -> klik CARI.
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class DashboardPage(BasePage):

    # ------------------------------- Header dashboard -------------------------------
    # TODO: Update locator
    HEADER_DASHBOARD = (
        By.XPATH,
        "//*[normalize-space(text())='Dashboard']")

    # Dikonfirmasi lewat tools/scan_locators.py (data-qtip='Dashboard').
    TAB_DASHBOARD_AKTIF = (By.CSS_SELECTOR, "[data-qtip='Dashboard']")

    # ------------------------------- Widget dashboard -------------------------------
    # "Surat Keluar" dipecah jadi 2 widget (Eksternal & Internal).
    # TODO: Update locator
    WIDGET_SURAT_MASUK = (By.XPATH, "//*[normalize-space(text())='Surat Masuk']")

    # TODO: Update locator
    WIDGET_DISPOSISI_MASUK = (By.XPATH, "//*[normalize-space(text())='Disposisi Masuk']")

    # TODO: Update locator
    WIDGET_DISPOSISI_KELUAR = (By.XPATH, "//*[normalize-space(text())='Disposisi Keluar']")

    # TODO: Update locator -- exact text match supaya tidak ikut match "Surat Keluar Internal".
    WIDGET_SURAT_KELUAR_EKSTERNAL = (
        By.XPATH,
        "//*[normalize-space(text())='Eksternal' or normalize-space(text())='Surat Keluar Eksternal']",
    )

    # TODO: Update locator
    WIDGET_SURAT_KELUAR_INTERNAL = (
        By.XPATH,
        "//*[normalize-space(text())='Internal' or normalize-space(text())='Surat Keluar Internal']",
    )

    # ----------------------------- Filter rentang tanggal -----------------------------
    # TODO: Update locator -- beberapa kandidat, dicoba satu per satu.
    ICON_RENTANG_TANGGAL_KANDIDAT = [
        (By.CSS_SELECTOR, "[data-qtip*='Rentang Tanggal']"),
        (By.CSS_SELECTOR, "[data-qtip*='Filter Tanggal']"),
        (By.XPATH, "//span[contains(@class, 'x-btn-inner') and contains(text(), '-')]"),
        (By.XPATH, "//span[contains(@class, 'ion-md-filing') or contains(@class, 'ion-md-calendar')]"),
        (By.XPATH, "//a[contains(@class,'x-btn')][.//*[contains(@class,'ion-md-filing') or contains(@class,'calendar')]]"),
    ]

    # TODO: Update locator
    INPUT_TANGGAL_AWAL = (By.XPATH, "//label[contains(text(),'Awal')]/ancestor::table//input")

    # TODO: Update locator
    INPUT_TANGGAL_AKHIR = (By.XPATH, "//label[contains(text(),'Akhir')]/ancestor::table//input")

    # Cocokkan kedua penulisan (Cari/CARI) supaya tidak gagal karena kapitalisasi.
    BTN_CARI = (By.XPATH, "//span[normalize-space()='Cari' or normalize-space()='CARI']")

    # ---------------------------------- Verifikasi ----------------------------------
    def is_dashboard_loaded(self, timeout=10):
        """Cek dashboard tampil (find_visible_among biar tidak terkunci ke match hidden)."""
        self.wait_loading_mask_gone(timeout=timeout)
        for locator in (self.TAB_DASHBOARD_AKTIF, self.HEADER_DASHBOARD, self.WIDGET_SURAT_MASUK):
            try:
                self.find_visible_among(locator, timeout=3)
                return True
            except TimeoutException:
                continue
        return False

    def is_widget_visible(self, locator, timeout=5):
        """Cek widget tampil (mask sudah ditunggu sekali di pemanggil)."""
        try:
            self.find_visible_among(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    # ----------------------------- Filter rentang tanggal -----------------------------
    def open_rentang_tanggal(self, timeout=8):
        """Klik ikon Rentang Tanggal (tiap kandidat dicari maks 3 detik)."""
        self.wait_loading_mask_gone(timeout=5)
        for locator in self.ICON_RENTANG_TANGGAL_KANDIDAT:
            try:
                element = self.find_visible_among(locator, timeout=3)
                self.click_via_js(element)
                self.wait_loading_mask_gone(timeout=5)
                return
            except TimeoutException:
                continue
        raise AssertionError("Ikon Rentang Tanggal tidak ditemukan.")

    def pilih_rentang_tanggal(self, tanggal_awal, tanggal_akhir):
        self.type_text(self.INPUT_TANGGAL_AWAL, tanggal_awal)
        self.type_text(self.INPUT_TANGGAL_AKHIR, tanggal_akhir)

    def klik_cari(self):
        self.click(self.BTN_CARI)
        self.wait_loading_mask_gone(timeout=30)
