"""
pages/progress_surat_page.py
=============================
Modul 5 - Progress Surat (12 Test Steps, lihat
Flow_Automation_Testing_DLA.md -- catatan dari kamu: "ga harus revisi
yaa gausah gapapaa, log aktivitas" -> jadi modul ini TIDAK perlu skenario
negative-test revisi, cukup ikuti 12 langkah generic yang sama seperti
Tugas/Masuk/Disposisi Keluar. Tombol LOG AKTIFITAS tetap disediakan
sebagai method opsional kalau suatu saat dibutuhkan.
"""

from selenium.webdriver.common.by import By
from pages.filterable_list_page import FilterableListPage


class ProgressSuratPage(FilterableListPage):

    # Dikonfirmasi lewat tools/scan_locators.py (data-qtip='Progress Surat').
    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Progress Surat']")

    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Progress Surat']")

    MENU_PROGRESS_SURAT = MENU_LOCATOR
    HEADER_PROGRESS_SURAT = HEADER_LOCATOR

    # ==========================================================
    # LOG AKTIFITAS (opsional, tidak wajib per catatan kamu)
    # ==========================================================
    BTN_LOG_AKTIFITAS = (By.XPATH, "//*[normalize-space(text())='LOG AKTIFITAS']")
    ROW_LOG_AKTIFITAS = (By.CSS_SELECTOR, "tr.x-grid-row.x-grid-data-row")

    def buka_detail_surat_pertama(self):
        row = (By.CSS_SELECTOR, "tr.x-grid-data-row")
        self.click(row)
        self.wait_loading_mask_gone(timeout=10)

    def buka_log_aktifitas(self):
        self.click(self.BTN_LOG_AKTIFITAS)
        self.wait_loading_mask_gone(timeout=10)

    def is_log_aktifitas_terisi(self, timeout=10):
        return self.is_visible(self.ROW_LOG_AKTIFITAS, timeout=timeout)
