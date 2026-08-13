"""
Diagnostic: dump ATRIBUT lengkap tombol toolbar halaman Surat Keluar
Eksternal SETELAH filter + CARI (tombol jadi icon-only, teks hilang).
Jalankan: python tests/diagnose_toolbar_buttons.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config import config

from pages.login_page import LoginPage
from pages.surat_dinas_eksternal_page import SuratDinasEksternalPage


def dump_buttons(driver, judul):
    print(f"\n{'='*70}\n{judul}\n{'='*70}")
    btns = driver.find_elements(By.CSS_SELECTOR, "a.x-btn")
    for el in btns:
        try:
            if not el.is_displayed():
                continue
            print(f"\n--- tombol id='{el.get_attribute('id')}' ---")
            print(f"  class : {(el.get_attribute('class') or '')[:120]}")
            print(f"  qtip  : '{el.get_attribute('data-qtip')}'")
            print(f"  text  : '{el.text.strip()[:50]}'")
            # Icon class di dalam tombol
            icons = el.find_elements(By.CSS_SELECTOR, "span[class*='ion-'], i[class*='ion-']")
            for ic in icons:
                print(f"  icon  : class='{(ic.get_attribute('class') or '')[:80]}'")
            # Inner html singkat
            inner = el.get_attribute("innerHTML")
            print(f"  html  : {inner[:200]}")
        except Exception:
            pass


def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(0)

    try:
        login = LoginPage(driver)
        page = SuratDinasEksternalPage(driver)

        login.open(config.BASE_URL)
        assert login.is_login_success(timeout=20), "Login gagal"
        print("v Login OK")

        page.open_menu()
        dump_buttons(driver, "TOOLBAR SEBELUM FILTER (fresh)")

        page.cari_otomatis("1")
        page.clear_pencarian()
        dump_buttons(driver, "TOOLBAR SETELAH SEARCH+CLEAR")

        page.klik_filter()
        page.pilih_jenis_filter("Surat Disetujui")
        page.isi_data_filter("1")
        page.klik_cari_popup()
        dump_buttons(driver, "TOOLBAR SETELAH FILTER+CARI")

        # Cek apakah popup Advanced Filter masih terbuka?
        print("\n>>> Cek popup Advanced Filter masih terbuka?")
        try:
            terbuka = page.is_popup_advanced_filter_terbuka()
            print(f">>> hasil: {terbuka}")
        except Exception as exc:
            print(f">>> error: {exc}")

        # Coba buka ulang dengan klik icon-only FILTER? coba klik
        # tombol yang mengandung icon funnel/filter
        print("\n>>> Cari tombol icon filter (ion-md-funnel / filter)...")
        funnel = driver.find_elements(By.CSS_SELECTOR,
            "[class*='ion-md-funnel'], [class*='ion-ios-funnel'], [class*='ion-md-filter'], [class*='filter']")
        for f in funnel:
            try:
                print(f"  visible={f.is_displayed()} class='{(f.get_attribute('class') or '')[:80]}' "
                      f"qtip='{f.get_attribute('data-qtip')}'")
            except Exception:
                pass

    finally:
        print("\n=== DONE ===")
        driver.quit()


if __name__ == "__main__":
    main()
