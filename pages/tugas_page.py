"""
pages/tugas_page.py
====================
Modul 2 - Tugas (12 Test Steps, lihat Flow_Automation_Testing_DLA.md).
Semua logic generic (filter posisi, pencarian, advanced filter) ada di
FilterableListPage -- lihat pages/filterable_list_page.py.
"""

from selenium.webdriver.common.by import By
from pages.filterable_list_page import FilterableListPage


class TugasPage(FilterableListPage):

    # Locator dikonfirmasi lewat tools/scan_locators.py (data-qtip='Tugas').
    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Tugas']")

    # Header halaman -- teks yang tampil ke user (lihat tugas_locator.md).
    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Tugas']")

    # Alias supaya nama lama (dipakai project lain) tetap jalan.
    MENU_TUGAS = MENU_LOCATOR
    HEADER_TUGAS = HEADER_LOCATOR
