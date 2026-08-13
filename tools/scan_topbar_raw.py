"""
Dump HTML area topbar (header atas halaman) untuk mencari tombol
"Arsip Surat". Jalankan: python tools/scan_topbar_raw.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.webdriver.common.by import By
from scan_locators_v2 import sambungkan_ke_chrome

driver = sambungkan_ke_chrome()
print(f"Terhubung: {driver.title}")

# Cari container header/topbar
html = driver.execute_script(r"""
    // Tutup menu yang masih terbuka dulu dengan klik body
    document.body.click();

    // Cari elemen header/topbar: semua div di atas grid utama
    var out = [];
    var candidates = document.querySelectorAll(
        'div[class*="header"], div[class*="topbar"], div[class*="north"], '
        + 'div[class*="toolbar"], div[class*="top "]'
    );
    candidates.forEach(function(el) {
        var r = el.getBoundingClientRect();
        if (r.width > 0 && r.height > 0 && r.top < 200) {
            var txt = (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 300);
            if (txt) {
                out.push('--- CONTAINER class="' + (el.getAttribute('class') || '').slice(0, 80) + '" ---\n' + txt);
            }
        }
    });
    return out.join('\n\n');
""")
print("=== AREA ATAS HALAMAN (top < 200px) ===")
print(html[:4000])
