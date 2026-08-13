"""
Scan topbar: klik tombol topbar (Kelola Surat/Notifikasi) untuk membuka
dropdown-nya, lalu scan semua elemen yang muncul (mencari Arsip Surat).
Jalankan: python tools/scan_topbar_dropdown.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.webdriver.common.by import By
from scan_locators_v2 import sambungkan_ke_chrome, ambil_elemen, format_output

driver = sambungkan_ke_chrome()
print(f"Terhubung: {driver.title}")

# Coba klik tiap tombol topbar yang mungkin, lalu scan
kandidat_tombol = [
    (By.CSS_SELECTOR, "[data-qtip='Notifikasi Agenda Surat']"),
    (By.XPATH, "//*[normalize-space(text())='Kelola Surat']"),
    (By.XPATH, "//*[normalize-space(text())='Pengaturan']"),
    (By.XPATH, "//*[normalize-space(text())='Arsip Surat']"),
]

for i, (by, loc) in enumerate(kandidat_tombol):
    try:
        els = driver.find_elements(by, loc)
        visibles = [e for e in els if e.is_displayed()]
        if visibles:
            print(f"[{i}] Klik: {loc}")
            driver.execute_script("arguments[0].click();", visibles[0])
            time.sleep(2)
            break
    except Exception as exc:
        print(f"[{i}] Gagal klik {loc}: {exc}")

time.sleep(2)

# Scan elemen yang sekarang tampil
data = ambil_elemen(driver)
print(f"Elemen ditemukan: {len(data)}")

hasil = format_output(data)
print(hasil)

Path("reports").mkdir(exist_ok=True)
with open("reports/locator_scan_topbar_dropdown.txt", "w", encoding="utf-8") as f:
    f.write(hasil)
print("Hasil disimpan ke: reports/locator_scan_topbar_dropdown.txt")
