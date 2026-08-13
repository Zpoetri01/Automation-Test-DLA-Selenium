"""
Diagnostic: dump state halaman Surat Keluar Eksternal SETELAH filter + CARI.
Jalankan: python tests/diagnose_filter_state.py
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


def dump_state(driver, judul):
    print(f"\n{'='*70}\n{judul}\n{'='*70}")

    print("\n--- ELEMEN BERISI 'FILTER' (semua) ---")
    els = driver.find_elements(By.XPATH, "//*[contains(normalize-space(text()),'FILTER') or contains(normalize-space(text()),'Filter')]")
    for el in els:
        try:
            print(f"  tag={el.tag_name} visible={el.is_displayed()} "
                  f"text='{el.text.strip()[:60]}' class='{(el.get_attribute('class') or '')[:60]}'")
        except Exception:
            pass

    print("\n--- TOMBOL a.x-btn YANG TAMPIL ---")
    btns = driver.find_elements(By.CSS_SELECTOR, "a.x-btn")
    for el in btns:
        try:
            if el.is_displayed():
                print(f"  text='{el.text.strip()[:60]}' id='{(el.get_attribute('id') or '')[:40]}'")
        except Exception:
            pass

    print("\n--- WINDOW/POPUP YANG TAMPIL ---")
    wins = driver.find_elements(By.CSS_SELECTOR, "div.x-window")
    for w in wins:
        try:
            if w.is_displayed():
                header = w.find_elements(By.CSS_SELECTOR, "span.x-window-header-text")
                htext = header[0].text.strip() if header else "-"
                print(f"  id='{w.get_attribute('id')}' header='{htext}'")
        except Exception:
            pass

    print("\n--- LOADING MASK ---")
    masks = driver.find_elements(By.CSS_SELECTOR, "div.x-mask")
    for m in masks:
        try:
            print(f"  visible={m.is_displayed()} class='{(m.get_attribute('class') or '')[:50]}'")
        except Exception:
            pass

    print("\n--- GRID & JUMLAH ROW ---")
    grids = driver.find_elements(By.CSS_SELECTOR, "div.x-grid")
    for g in grids:
        try:
            if g.is_displayed():
                rows = g.find_elements(By.CSS_SELECTOR, "tr.x-grid-data-row")
                print(f"  grid id='{g.get_attribute('id')}' rows={len(rows)}")
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

        # Jalankan flow filter persis seperti test
        page.open_menu()
        page.cari_otomatis("1")
        page.clear_pencarian()
        page.klik_filter()
        page.pilih_jenis_filter("Surat Disetujui")
        page.isi_data_filter("1")
        page.klik_cari_popup()
        print("v Filter + CARI selesai")

        dump_state(driver, "STATE SETELAH CARI (filter aktif)")

        # Coba klik FILTER kedua (persis yang gagal di test)
        print("\n>>> Mencoba klik FILTER kedua...")
        try:
            page.klik_filter()
            print(">>> klik_filter BERHASIL")
        except Exception as exc:
            print(f">>> klik_filter GAGAL: {type(exc).__name__}: {exc}")

        dump_state(driver, "STATE SETELAH COBA KLIK FILTER KEDUA")

    finally:
        print("\n=== DONE ===")
        driver.quit()


if __name__ == "__main__":
    main()
