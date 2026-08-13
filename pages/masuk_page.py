"""
pages/masuk_page.py
====================
Modul 3 - Masuk (12 Test Steps, lihat Flow_Automation_Testing_DLA.md).
Semua logic generic (filter posisi, pencarian, advanced filter) ada di
FilterableListPage -- lihat pages/filterable_list_page.py.
"""

from selenium.webdriver.common.by import By
from pages.filterable_list_page import FilterableListPage


class MasukPage(FilterableListPage):

    # Locator dikonfirmasi lewat tools/scan_locators.py (data-qtip='Masuk').
    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Masuk']")

    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Masuk']")

    MENU_MASUK = MENU_LOCATOR
    HEADER_MASUK = HEADER_LOCATOR
