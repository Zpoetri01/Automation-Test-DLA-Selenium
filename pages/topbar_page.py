"""
pages/topbar_page.py
=====================
Modul Topbar -- 4 tombol di bar ATAS halaman:
  1. Lonceng Notifikasi      -> combo trigger-only (table.x-field-triggeronly-notif)
  2. Notifikasi Agenda Surat -> tombol icon bookmarks (data-qtip='Notifikasi Agenda Surat')
  3. Kelola Surat            -> teks 'Kelola Surat'
  4. Pengaturan              -> teks 'Pengaturan'

Test hanya MEMBUKA tiap dropdown & memastikan isinya muncul -- TANPA
test mendalam di tiap item (menunya sangat banyak). Locator dikonfirmasi
via tools/scan_locators_v2.py + probe langsung ke aplikasi.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class TopbarPage(BasePage):

    # ---- Tombol topbar ----
    # Lonceng notifikasi: trigger div combo trigger-only (HTML asli user).
    BTN_LONCENG = (
        By.CSS_SELECTOR,
        "div.x-form-arrow-trigger.x-trigger-index-0",
    )
    BTN_NOTIFIKASI_AGENDA = (By.CSS_SELECTOR, "[data-qtip='Notifikasi Agenda Surat']")
    BTN_KELOLA_SURAT = (By.XPATH, "//*[normalize-space(text())='Kelola Surat']")
    BTN_PENGATURAN = (By.XPATH, "//*[normalize-space(text())='Pengaturan']")

    # ---- Item verifikasi (muncul kalau dropdown benar terbuka) ----
    ITEM_NOTIFIKASI_AGENDA = (By.CSS_SELECTOR, "[data-qtip='Agd Masuk Blm Diarah']")
    ITEM_KELOLA_SURAT = (By.XPATH, "//*[normalize-space(text())='Registrasi Surat Masuk']")
    ITEM_PENGATURAN = (By.XPATH, "//*[normalize-space(text())='Hak Akses']")

    def _lonceng_terbuka(self):
        """Lonceng terbuka kalau combo picker dalam keadaan
        'x-pickerfield-open' (kelas pada body combo-nya)."""
        return bool(self.driver.execute_script("""
            var c = document.querySelector('table.x-field-triggeronly-notif');
            if (!c) return false;
            var body = c.querySelector('.x-form-item-body');
            return body && body.className.indexOf('x-pickerfield-open') >= 0;
        """))

    def _klik_lonceng(self):
        """Klik trigger lonceng dengan NATIVE click (mousedown+mouseup) --
        trigger ExtJS merespons event mouse asli, bukan JS .click()."""
        trigger = self.find_visible_among(self.BTN_LONCENG, timeout=10)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", trigger
        )
        try:
            trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)
        self.pace(2)

    def _klik_tombol(self, locator):
        """Klik tombol topbar SEKALI (native click dulu, fallback JS)."""
        btn = self.find_visible_among(locator, timeout=10)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        self.pace(2)

    def buka_semua_menu(self):
        """Klik SETIAP tombol topbar SEKALI untuk membuka dropdown-nya,
        pastikan isinya muncul, lalu klik SEKALI lagi untuk menutup.
        Return list (nama, ok)."""
        hasil = []

        # 1. Lonceng Notifikasi -- sekali klik buka, sekali klik tutup
        self._klik_lonceng()
        ok = self._lonceng_terbuka()
        hasil.append(("Lonceng Notifikasi", ok))
        if self._lonceng_terbuka():
            self._klik_lonceng()  # tutup lagi (toggle)

        # 2. Notifikasi Agenda Surat
        self._klik_tombol(self.BTN_NOTIFIKASI_AGENDA)
        ok = self.is_visible(self.ITEM_NOTIFIKASI_AGENDA, timeout=8)
        hasil.append(("Notifikasi Agenda Surat", ok))
        self._klik_tombol(self.BTN_NOTIFIKASI_AGENDA)  # tutup (toggle)

        # 3. Kelola Surat
        self._klik_tombol(self.BTN_KELOLA_SURAT)
        ok = self.is_visible(self.ITEM_KELOLA_SURAT, timeout=8)
        hasil.append(("Kelola Surat", ok))
        self._klik_tombol(self.BTN_KELOLA_SURAT)  # tutup (toggle)

        # 4. Pengaturan
        self._klik_tombol(self.BTN_PENGATURAN)
        ok = self.is_visible(self.ITEM_PENGATURAN, timeout=8)
        hasil.append(("Pengaturan", ok))
        self._klik_tombol(self.BTN_PENGATURAN)  # tutup (toggle)

        return hasil
