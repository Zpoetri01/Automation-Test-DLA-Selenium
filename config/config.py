"""
config.py
=========
Semua pengaturan project (URL, timeout, path profil Chrome, mode headless)
dipusatkan di sini. Kalau ada yang berubah (URL staging, timeout, dst),
cukup ubah di 1 tempat -- tidak perlu cari-cari di banyak file test.

Semua nilai bisa di-override lewat environment variable, supaya:
- Tiap anggota tim bisa punya path Chrome profile sendiri-sendiri.
- Bisa dijalankan headless di CI/CD tanpa ubah kode.
"""

import os

# ---------------------------------------------------------------------------
# URL aplikasi yang akan diuji
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("DLA_BASE_URL", "https://qa-dla.antm.tech/")

# ---------------------------------------------------------------------------
# Login Google SSO
# ---------------------------------------------------------------------------
# NewDLA login pakai tombol "Login with Google". Selenium TIDAK mengisi
# email/password Google secara otomatis (akan diblokir Google). Solusinya:
# Chrome yang dipakai Selenium memakai folder profile yang session
# Google-nya SUDAH aktif (login manual dilakukan SEKALI di luar automation,
# bukan setiap kali test dijalankan).
#
# Override via environment variable supaya tiap tester bisa pakai path
# profile masing-masing, contoh (Windows PowerShell):
#   $env:DLA_CHROME_PROFILE = "D:\selenium-chrome-profile"
CHROME_PROFILE_PATH = os.getenv("DLA_CHROME_PROFILE", r"D:\selenium-chrome-profile")

# ---------------------------------------------------------------------------
# Mode browser
# ---------------------------------------------------------------------------
# HEADLESS=true -> Chrome jalan tanpa membuka jendela (cocok untuk CI/CD).
# Karena login pakai profile yang session-nya sudah aktif, headless tetap
# bisa dipakai (tidak butuh interaksi manual).
HEADLESS = os.getenv("DLA_HEADLESS", "false").strip().lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# Timeout default (detik) untuk WebDriverWait
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT = int(os.getenv("DLA_TIMEOUT", "15"))

# Timeout lebih panjang khusus untuk proses yang butuh loading data
# (misalnya menunggu grid/tabel selesai memuat data setelah klik CARI,
# atau upload dokumen di modul Surat Dinas Eksternal / Nota Dinas Keluar).
LONG_TIMEOUT = int(os.getenv("DLA_LONG_TIMEOUT", "30"))

# ---------------------------------------------------------------------------
# Jeda antar-aksi (detik) -- HANYA untuk kebutuhan visual (supaya alur bisa
# diikuti mata saat browser dibuka/didemokan), BUKAN untuk menunggu elemen
# (itu tetap tugas WebDriverWait di base_page.py).
# Dipakai di 2 tempat:
#   1. Sesaat setelah browser membuka URL pertama kali (login_page.open()).
#   2. Setelah setiap aksi klik/isi teks (BasePage.click / type_text) supaya
#      langkah-langkah tidak terlihat "sekelebat" satu sama lain.
# ---------------------------------------------------------------------------
ACTION_PACE_SECONDS = float(os.getenv("DLA_ACTION_PACE", "1"))

# ---------------------------------------------------------------------------
# Lokasi folder laporan & screenshot
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
SCREENSHOT_DIR = os.path.join(REPORTS_DIR, "screenshots")
