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

    # ==========================================================
    # HEADER DASHBOARD
    # ==========================================================
    # TODO: Update locator
    HEADER_DASHBOARD = (
        By.XPATH,
        "//*[normalize-space(text())='Dashboard']")

    # Locator dikonfirmasi lewat tools/scan_locators.py (data-qtip='Dashboard').
    # NB: sebelumnya value CSS selector ini salah dipasangkan dengan By.XPATH
    # (bug) sehingga tidak pernah match -- sudah diperbaiki ke By.CSS_SELECTOR.
    TAB_DASHBOARD_AKTIF = (By.CSS_SELECTOR, "[data-qtip='Dashboard']")

    # ==========================================================
    # WIDGET DASHBOARD
    # Catatan: "Surat Keluar" dipecah jadi 2 widget terpisah sesuai
    # kebutuhan (Eksternal & Internal), sebelumnya sempat digabung jadi 1.
    # ==========================================================
    # TODO: Update locator
    WIDGET_SURAT_MASUK = (By.XPATH, "//*[normalize-space(text())='Surat Masuk']")

    # TODO: Update locator
    WIDGET_DISPOSISI_MASUK = (By.XPATH, "//*[normalize-space(text())='Disposisi Masuk']")

    # TODO: Update locator
    WIDGET_DISPOSISI_KELUAR = (By.XPATH, "//*[normalize-space(text())='Disposisi Keluar']")

    # TODO: Update locator -- pastikan xpath ini TIDAK ikut ke-match oleh
    # "Surat Keluar Internal" (pakai exact text match, bukan contains()).
    WIDGET_SURAT_KELUAR_EKSTERNAL = (
        By.XPATH,
        "//*[normalize-space(text())='Eksternal' or normalize-space(text())='Surat Keluar Eksternal']",
    )

    # TODO: Update locator
    WIDGET_SURAT_KELUAR_INTERNAL = (
        By.XPATH,
        "//*[normalize-space(text())='Internal' or normalize-space(text())='Surat Keluar Internal']",
    )

    # ==========================================================
    # FILTER RENTANG TANGGAL
    # ==========================================================
    # TODO: Update locator -- beberapa kandidat, find_first_visible()
    # akan coba satu per satu.
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

    # Teks tombol di aplikasi ini konsisten UPPERCASE (lihat hasil
    # scan_locators.py: FILTER, CARI, RESET, MUAT ULANG) -- cocokkan kedua
    # kemungkinan penulisan supaya tidak gagal karena beda kapitalisasi.
    BTN_CARI = (By.XPATH, "//span[normalize-space()='Cari' or normalize-space()='CARI']")

    # ==========================================================
    # VERIFIKASI
    # ==========================================================
    def is_dashboard_loaded(self, timeout=10):
        """Cek dashboard tampil. PENTING (percepat awal dashboard):
        pakai find_visible_among (cari elemen yang benar-benar TAMPIL di
        antara semua match) -- is_visible lama mengunci ke match PERTAMA
        di DOM yang sering hidden, sehingga tiap kandidat menunggu penuh
        sampai timeout dan totalnya lama sekali."""
        self.wait_loading_mask_gone(timeout=timeout)
        for locator in (self.TAB_DASHBOARD_AKTIF, self.HEADER_DASHBOARD, self.WIDGET_SURAT_MASUK):
            try:
                self.find_visible_among(locator, timeout=3)
                return True
            except TimeoutException:
                continue
        return False

    def is_widget_visible(self, locator, timeout=5):
        """Cek widget tampil -- find_visible_among (cari yang benar2
        tampil), tanpa wait mask per widget (mask sudah ditunggu sekali
        di pemanggil) supaya awal dashboard cepat."""
        try:
            self.find_visible_among(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    # ==========================================================
    # FILTER RENTANG TANGGAL
    # ==========================================================
    def open_rentang_tanggal(self, timeout=8):
        """Klik ikon Rentang Tanggal. PENTING (percepat -- dulu 47 detik
        karena tiap kandidat locator menunggu timeout PENUH): sekarang
        tiap kandidat dicari dengan find_visible_among (elemen yang
        benar-benar tampil) maks 3 detik, langsung klik begitu ketemu."""
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
