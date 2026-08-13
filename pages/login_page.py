"""
pages/login_page.py
====================
Login NewDLA pakai tombol "Login with Google". Selenium TIDAK mengisi
email/password Google (akan diblokir Google) -- Chrome yang dipakai
Selenium memakai profile yang session Google-nya SUDAH aktif (login
manual dilakukan SEKALI di komputer kamu, lihat README.md).
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class LoginPage(BasePage):

    # Dikonfirmasi lewat tools/scan_locators.py (data-qtip='Logout').
    MENU_LOGOUT = (By.CSS_SELECTOR, "[data-qtip='Logout']")

    # TODO: Update locator -- biasanya harus buka menu profil dulu
    # sebelum tombol Logout muncul/bisa diklik.
    MENU_PROFIL_USER = (By.CSS_SELECTOR, "[data-qtip='Profil']")

    # Cek login lewat tab Dashboard aktif (tampil langsung setelah login
    # tanpa interaksi tambahan), bukan MENU_LOGOUT yang baru muncul
    # setelah menu profil dibuka.
    TAB_DASHBOARD_AKTIF = (By.CSS_SELECTOR, "[data-qtip='Dashboard']")

    # TODO: Update locator -- dipakai untuk memastikan sudah kembali ke
    # halaman login setelah logout.
    BTN_LOGIN_GOOGLE = (By.XPATH, "//*[contains(text(),'Login with Google')]")

    def open(self, url):
        self.driver.get(url)
        self.pace()

    def is_login_success(self, timeout=20):
        """Login sukses = Dashboard tampil (fallback: menu Logout)."""
        if self.is_visible(self.TAB_DASHBOARD_AKTIF, timeout=timeout):
            return True
        return self.is_visible(self.MENU_LOGOUT, timeout=3)

    # ------------------------------- MODUL 9 - LOGOUT -------------------------------
    def logout(self):
        """Buka menu profil dulu (kalau perlu), klik Logout, lalu konfirmasi Ya."""
        if not self.is_visible(self.MENU_LOGOUT, timeout=3):
            self.click(self.MENU_PROFIL_USER)
        self.click(self.MENU_LOGOUT)
        self.wait_loading_mask_gone(timeout=10)
        btn_ya = (By.XPATH, "//span[normalize-space(text())='Ya']")
        try:
            if self.is_visible(btn_ya, timeout=3):
                self.click_visible_among(btn_ya, timeout=5)
                self.wait_loading_mask_gone(timeout=10)
        except TimeoutException:
            pass

    def is_kembali_ke_halaman_login(self, timeout=15):
        """Verifikasi logout berhasil (salah satu sinyal cukup):
        1. teks "Login with Google" tampil; 2. field login tampil;
        3. menu Logout sudah tidak tampil."""
        if self.is_visible(self.BTN_LOGIN_GOOGLE, timeout=5):
            return True
        input_login = (
            By.CSS_SELECTOR,
            "input[type='email'], input[type='password'], "
            "input[name='email'], input[name='password'], "
            "input[name='username']",
        )
        if self.is_visible(input_login, timeout=3):
            return True
        return not self.is_visible(self.MENU_LOGOUT, timeout=timeout)
