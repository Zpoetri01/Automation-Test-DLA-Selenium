"""
Scan locator TOPBAR halaman aktif. Jalankan: python tools/scan_topbar_sekarang.py
Requirement: Chrome berjalan dengan --remote-debugging-port=9222.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scan_locators_v2 import sambungkan_ke_chrome, ambil_elemen, format_output

driver = sambungkan_ke_chrome()
print(f"Terhubung: {driver.title}")

# Buka aplikasi kalau belum login (session profile sudah aktif)
driver.get("https://qa-dla.antm.tech/")
time.sleep(10)

print(f"URL sekarang : {driver.current_url}")
print(f"Title       : {driver.title}")

data = ambil_elemen(driver)
print(f"Elemen ditemukan: {len(data)}")

hasil = format_output(data)
print(hasil)

Path("reports").mkdir(exist_ok=True)
with open("reports/locator_scan_topbar.txt", "w", encoding="utf-8") as f:
    f.write(hasil)
print("Hasil disimpan ke: reports/locator_scan_topbar.txt")
