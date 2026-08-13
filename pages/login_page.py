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

    # Locator dikonfirmasi lewat tools/scan_locators.py (data-qtip='Logout').
    MENU_LOGOUT = (By.CSS_SELECTOR, "[data-qtip='Logout']")

    # TODO: Update locator -- Modul 9 (Logout): biasanya harus buka menu
    # profil/avatar dulu sebelum tombol Logout muncul/bisa diklik.
    MENU_PROFIL_USER = (By.CSS_SELECTOR, "[data-qtip='Profil']")

    # FIX (root cause "login selalu tertulis failed padahal Dashboard
    # benar-benar tampil"): is_login_success() sebelumnya CUMA cek
    # MENU_LOGOUT -- tapi MENU_LOGOUT ada di dalam menu profil yang HARUS
    # dibuka dulu (lihat catatan MENU_PROFIL_USER di atas), jadi begitu
    # login sukses & Dashboard tampil, MENU_LOGOUT tetap TIDAK visible
    # sampai menu profil diklik -- is_visible()-nya timeout & return
    # False walau login-nya sendiri sebenarnya berhasil.
    # Fix: cek elemen yang SUDAH CONFIRMED tampil langsung setelah login
    # tanpa interaksi tambahan apapun -- tab Dashboard aktif
    # (data-qtip='Dashboard', locator yang sama dipakai & sudah
    # dikonfirmasi di DashboardPage.TAB_DASHBOARD_AKTIF).
    TAB_DASHBOARD_AKTIF = (By.CSS_SELECTOR, "[data-qtip='Dashboard']")

    # TODO: Update locator -- tombol/link "Login with Google" di halaman login,
    # dipakai untuk memastikan sudah kembali ke halaman login setelah logout.
    BTN_LOGIN_GOOGLE = (By.XPATH, "//*[contains(text(),'Login with Google')]")

    def open(self, url):
        self.driver.get(url)
        # Jeda singkat (default 5 detik) supaya tidak langsung "meloncat"
        # cek elemen login sepersekian detik setelah URL dibuka -- lihat
        # config.ACTION_PACE_SECONDS. Bukan pengganti WebDriverWait di
        # is_login_success(), cuma jeda visual sebelum aksi berikutnya.
        self.pace()

    def is_login_success(self, timeout=20):
        """Login dianggap berhasil kalau sudah sampai di Dashboard, bukan
        masih di halaman login Google.

        PENTING: dicek lewat TAB_DASHBOARD_AKTIF (tampil LANGSUNG setelah
        login, tanpa interaksi tambahan) -- BUKAN MENU_LOGOUT, karena
        MENU_LOGOUT baru muncul setelah menu profil dibuka (lihat catatan
        MENU_PROFIL_USER), jadi mengecek MENU_LOGOUT di sini akan selalu
        timeout & return False walau Dashboard-nya sendiri sudah benar-
        benar tampil. MENU_LOGOUT tetap dicek sebagai fallback kedua kalau
        kebetulan sudah visible (misal profile menu sisa kebuka dari
        sesi sebelumnya)."""
        if self.is_visible(self.TAB_DASHBOARD_AKTIF, timeout=timeout):
            return True
        return self.is_visible(self.MENU_LOGOUT, timeout=3)

    # ==========================================================
    # MODUL 9 - LOGOUT (1 Test Step)
    # ==========================================================
    def logout(self):
        """Klik menu profil dulu (kalau tombol Logout belum tampil),
        baru klik Logout -- selaras dengan fix di is_login_success():
        MENU_LOGOUT ada di dalam menu profil, jadi kalau belum kebuka,
        klik langsung ke MENU_LOGOUT akan timeout/gagal.

        Setelah klik Logout, bisa muncul popup konfirmasi ("Apakah anda
        yakin ?") -- klik Ya kalau muncul, supaya logout benar-benar
        diproses sampai kembali ke halaman login."""
        if not self.is_visible(self.MENU_LOGOUT, timeout=3):
            self.click(self.MENU_PROFIL_USER)
        self.click(self.MENU_LOGOUT)
        self.wait_loading_mask_gone(timeout=10)
        # Handle popup konfirmasi logout kalau ada
        btn_ya = (By.XPATH, "//span[normalize-space(text())='Ya']")
        try:
            if self.is_visible(btn_ya, timeout=3):
                self.click_visible_among(btn_ya, timeout=5)
                self.wait_loading_mask_gone(timeout=10)
        except TimeoutException:
            pass

    def is_kembali_ke_halaman_login(self, timeout=15):
        """Verifikasi logout berhasil.

        PENTING: BTN_LOGIN_GOOGLE masih locator TEBAKAN (belum
        dikonfirmasi scan_locators.py di halaman Login NewDLA), jadi
        test_m08_01_logout sebelumnya SELALU gagal (assert False) kalau
        teks tombol login sebenarnya beda dari "Login with Google" --
        bukan berarti logout-nya gagal.

        Verifikasi dilakukan dengan beberapa sinyal sekaligus (salah
        satu cukup dianggap berhasil):
          1. BTN_LOGIN_GOOGLE terlihat (kalau locatornya kebetulan
             benar).
          2. Field khas halaman login (input email/password) terlihat.
          3. Menu Logout (elemen yang HANYA ada saat sudah login) sudah
             TIDAK terlihat lagi -- indikator paling pasti tanpa perlu
             tahu teks tombol login yang benar.

        Tolong kirim hasil scan_locators.py halaman Login (khususnya
        tombol/link untuk masuk lagi) supaya BTN_LOGIN_GOOGLE bisa
        diganti locator yang pasti."""
        # Sinyal 1: tombol/tulisan "Login with Google"
        if self.is_visible(self.BTN_LOGIN_GOOGLE, timeout=5):
            return True
        # Sinyal 2: field email/password khas halaman login
        input_login = (
            By.CSS_SELECTOR,
            "input[type='email'], input[type='password'], "
            "input[name='email'], input[name='password'], "
            "input[name='username']",
        )
        if self.is_visible(input_login, timeout=3):
            return True
        # Sinyal 3: elemen yang hanya ada saat login sudah hilang
        return not self.is_visible(self.MENU_LOGOUT, timeout=timeout)
