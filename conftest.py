"""
conftest.py
===========
PENTING - kenapa driver di sini scope="session":
Sesuai aturan alur E2E, Chrome HANYA dibuka 1 KALI dari test pertama
(Dashboard) sampai test terakhir (Logout). Kalau scope-nya "function"
(default), Selenium akan buka & tutup browser di SETIAP fungsi test --
itu yang bikin flow-nya "putus-putus" dan harus login ulang setiap kali.

Dengan scope="session":
- Browser dibuka SEKALI oleh test pertama yang memakai fixture `driver`.
- Instance browser yang SAMA dipakai ulang oleh semua test lain sampai
  seluruh sesi pytest selesai.
- Browser ditutup OTOMATIS di akhir (tidak ada jeda "tekan ENTER").
"""

import json
import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config


# ------------------ Ringkasan hasil per modul (kotak "AUTOMATION TESTING RESULT") ------------------
# Pemetaan: nama method test -> label modul. Method test_dashboard_*
# (7 method) digabung jadi 1 baris "Dashboard".
STEP_LABELS = [
    ("test_login", "Login"),
    ("test_dashboard_buka", "Dashboard"),  # kepala grup dashboard
    ("test_tugas", "Tugas"),
    ("test_masuk", "Masuk"),
    ("test_disposisi_keluar", "Disposisi Keluar"),
    ("test_progress_surat", "Progress Surat"),
    ("test_surat_keluar_eksternal", "Surat Keluar Eksternal"),
    ("test_simpan_draft_pertama", "Tambah Surat"),
    ("test_hapus_draft", "Hapus Draft"),
    ("test_ubah_dan_ajukan", "Perubahan Surat"),
    ("test_nota_dinas_keluar", "Nota Dinas Keluar"),
    ("test_detail_surat", "Detail Surat"),
    ("test_topbar", "Topbar"),
    ("test_logout", "Logout"),
]

# Hasil kumulatif: label -> bool (semua step modul lulus); urutan dict = urutan eksekusi.
_step_results = {}


def _label_for_step(item_name):
    """Label modul untuk method test, atau None kalau bagian grup (mis. dashboard)."""
    if item_name.startswith("test_dashboard_"):
        return "Dashboard"
    for prefix, label in STEP_LABELS:
        if item_name == prefix:
            return label
    return None


def _is_head_step(item_name):
    """True kalau method ini 'kepala' grup -- hasilnya dicetak sebagai
    baris status (anggota grup lain hanya diakumulasi)."""
    for prefix, _label in STEP_LABELS:
        if item_name == prefix:
            return True
    return False


# -------------------- Fixture: driver (session-scoped -> 1 browser) --------------------
@pytest.fixture(scope="session")
def driver():

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")

    # Flag stabilitas standar untuk ExtJS/app berat di Chrome versi baru.
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )

    if config.HEADLESS:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.implicitly_wait(0)

    yield chrome_driver

    # Tutup browser otomatis di akhir sesi (idempoten walau logout
    # sudah menutup session di sisi aplikasi).
    try:
        chrome_driver.quit()
    except Exception:
        pass


# -------------------- Fixture: test_data (dari data/test_data.json) --------------------
@pytest.fixture(scope="session")
def test_data():
    data_path = os.path.join(
        os.path.dirname(__file__), "data", "test_data.json"
    )
    with open(data_path, "r", encoding="utf-8") as data_file:
        return json.load(data_file)


# ------------------ Ambil driver aktif dari test (untuk hook screenshot) ------------------
def _get_active_driver(test_item):
    active_driver = test_item.funcargs.get("driver")
    if active_driver is not None:
        return active_driver

    test_instance = getattr(test_item, "instance", None)
    if test_instance is not None:
        return getattr(test_instance, "driver", None)

    return None


# ------------------ Screenshot otomatis saat test gagal / di-skip ------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report_extras = getattr(report, "extra", [])

    # --- Catat hasil per modul + cetak baris status rapi di terminal ---
    if report.when == "call":
        label = _label_for_step(item.name)
        if label:
            ok = bool(report.passed)
            # Akumulasi: modul gagal kalau salah satu method-nya gagal
            _step_results[label] = _step_results.get(label, True) and ok
            if _is_head_step(item.name):
                mark = "V" if ok else "X"
                ket = "berhasil" if ok else "GAGAL"
                print(f"\n{mark} [{label}] {ket}")

    if report.when == "call" and (report.failed or report.skipped):
        active_driver = _get_active_driver(item)

        if active_driver:
            os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join(config.SCREENSHOT_DIR, screenshot_name)

            try:
                active_driver.save_screenshot(screenshot_path)
                print(f"\n[SCREENSHOT SAAT GAGAL] {screenshot_path}")
                print(f"[URL SAAT GAGAL] {active_driver.current_url}")

                try:
                    from pytest_html import extras

                    relative_path = os.path.join("screenshots", screenshot_name)
                    report_extras.append(extras.image(relative_path))
                    report_extras.append(extras.url(active_driver.current_url))
                except Exception:
                    pass

            except Exception as screenshot_error:
                print(f"\n[GAGAL AMBIL SCREENSHOT] {screenshot_error}")

    report.extra = report_extras


# ------------------ Akhir sesi: cetak kotak "AUTOMATION TESTING RESULT" ------------------
def pytest_sessionfinish(session, exitstatus):
    if not _step_results:
        return  # tidak ada test yang dieksekusi (mis. cuma collect)

    total = len(_step_results)
    passed = sum(1 for ok in _step_results.values() if ok)
    failed = total - passed
    status = "PASSED" if failed == 0 else "FAILED"

    sep = "=" * 40
    lines = [sep]
    lines.append("       AUTOMATION TESTING RESULT")
    lines.append(sep)
    lines.append("")
    for label, ok in _step_results.items():
        mark = "V" if ok else "X"
        ket = "berhasil" if ok else "GAGAL"
        lines.append(f"{mark} [{label}] {ket}")
    lines.append("")
    lines.append(sep)
    lines.append(f"TOTAL TEST : {total}")
    lines.append(f"PASSED     : {passed}")
    lines.append(f"FAILED     : {failed}")
    lines.append(f"STATUS     : {status}")
    lines.append(sep)
    print("\n" + "\n".join(lines))
