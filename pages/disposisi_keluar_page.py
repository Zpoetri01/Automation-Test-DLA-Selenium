"""
pages/disposisi_keluar_page.py
================================
Modul 4 - Disposisi Keluar (12 Test Steps, lihat
Flow_Automation_Testing_DLA.md). Semua logic generic (filter posisi,
pencarian, advanced filter) ada di FilterableListPage -- lihat
pages/filterable_list_page.py.
"""

from selenium.webdriver.common.by import By
from pages.filterable_list_page import FilterableListPage


class DisposisiKeluarPage(FilterableListPage):

    # Locator dikonfirmasi lewat tools/scan_locators.py
    # (data-qtip='Disposisi Keluar').
    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Disposisi Keluar']")

    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Disposisi Keluar']")

    MENU_DISPOSISI_KELUAR = MENU_LOCATOR
    HEADER_DISPOSISI_KELUAR = HEADER_LOCATOR
