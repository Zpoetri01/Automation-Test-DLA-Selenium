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

# ------------------- URL aplikasi yang akan diuji -------------------
BASE_URL = os.getenv("DLA_BASE_URL", "https://qa-dla.antm.tech/")

# ------------------- Login Google SSO -------------------
# NewDLA login pakai "Login with Google". Selenium TIDAK mengisi
# email/password (diblokir Google) -- Chrome memakai folder profile yang
# session Google-nya SUDAH aktif (login manual dilakukan SEKALI di luar
# automation). Override lewat env DLA_CHROME_PROFILE.
CHROME_PROFILE_PATH = os.getenv("DLA_CHROME_PROFILE", r"D:\selenium-chrome-profile")

# ------------------- Mode browser -------------------
# HEADLESS=true -> Chrome tanpa jendela (cocok untuk CI/CD).
HEADLESS = os.getenv("DLA_HEADLESS", "false").strip().lower() in ("1", "true", "yes")

# ------------------- Timeout default (detik) untuk WebDriverWait -------------------
DEFAULT_TIMEOUT = int(os.getenv("DLA_TIMEOUT", "15"))

# Timeout lebih panjang untuk proses yang butuh loading data lama
# (grid setelah CARI, upload dokumen, dll).
LONG_TIMEOUT = int(os.getenv("DLA_LONG_TIMEOUT", "30"))

# ------------------- Jeda antar-aksi (detik) -------------------
# HANYA untuk kebutuhan visual (alur bisa diikuti mata saat browser
# dibuka), BUKAN untuk menunggu elemen (itu tugas WebDriverWait).
# Rentang jeda antar-aksi: 2-5 detik (pace eksplisit lain di kode
# juga sudah berada dalam rentang ini, tidak ada yang > 5).
ACTION_PACE_SECONDS = float(os.getenv("DLA_ACTION_PACE", "2"))

# ------------------- Lokasi folder laporan & screenshot -------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
SCREENSHOT_DIR = os.path.join(REPORTS_DIR, "screenshots")
