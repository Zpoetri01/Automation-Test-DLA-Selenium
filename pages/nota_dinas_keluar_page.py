"""
pages/nota_dinas_keluar_page.py
=================================
Modul 7 - Nota Dinas Keluar (lihat Flow_Automation_Testing_DLA.md):
  A. Filter + Advanced Filter (search, "Surat Disetujui", checkbox "Disetujui")
  B. Cek Detail Surat (pilih surat -> verifikasi popup detail ->
     Log Aktifitas Surat -> close log -> close detail)
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pages.surat_form_base_page import SuratFormBasePage


class NotaDinasKeluarPage(SuratFormBasePage):

    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Agenda Surat Keluar Internal']")
    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Nota Dinas Keluar']")

    MENU_NOTA_DINAS_KELUAR = MENU_LOCATOR
    HEADER_NOTA_DINAS_KELUAR = HEADER_LOCATOR

    def open_menu_nota_dinas_keluar(self):
        self.open_menu()

    def is_nota_dinas_keluar_loaded(self):
        return self.is_halaman_loaded()

    # ==========================================================
    # ISI FORM -- KHUSUS Nota Dinas Keluar
    # ==========================================================
    def isi_form(self, data_surat):
        if data_surat.get("perihal"):
            self.isi_perihal(data_surat["perihal"])
        if data_surat.get("jenis_surat"):
            self.pilih_jenis_surat(
                data_surat["jenis_surat"], data_surat.get("jenis_surat_keyword")
            )
        if data_surat.get("klasifikasi_surat"):
            self.pilih_klasifikasi_surat(
                data_surat["klasifikasi_surat"], data_surat.get("klasifikasi_surat_keyword")
            )
        if data_surat.get("sifat_surat"):
            self.pilih_sifat_surat(data_surat["sifat_surat"])
        if data_surat.get("prioritas_surat"):
            self.pilih_prioritas_surat(data_surat["prioritas_surat"])
        if data_surat.get("lokasi_arsip_fisik"):
            self.pilih_lokasi_arsip_fisik(data_surat["lokasi_arsip_fisik"])
        if data_surat.get("uraian"):
            self.isi_uraian(data_surat["uraian"])

    # ==========================================================
    # B. CEK DETAIL SURAT
    # ==========================================================
    POPUP_DETAIL_SURAT = (
        By.XPATH,
        "//span[contains(@class,'x-window-header-text')]"
        "[normalize-space(text())='Identitas Agenda Surat Nota Dinas Keluar']",
    )
    BTN_LOG_AKTIFITAS = (
        By.XPATH,
        "//span[normalize-space(text())='Log Aktifitas Surat']",
    )
    POPUP_LOG_AKTIFITAS = (
        By.XPATH,
        "//span[contains(@class,'x-window-header-text')]"
        "[normalize-space(text())='Log Aktifitas Surat']",
    )
    # PENTING (fix popup tidak pernah tertutup): di HTML asli, class
    # `x-tool-close` ada di elemen <img> (img.x-tool-img.x-tool-close),
    # BUKAN di <div>. Selector lama div.x-tool-close tidak pernah match
    # sehingga klik close selalu gagal diam-diam.
    BTN_CLOSE_LOG = (
        By.CSS_SELECTOR,
        "img.x-tool-close",
    )

    def is_detail_surat_terbuka(self, timeout=15):
        """Step B.2: Verifikasi popup 'Identitas Agenda Surat Nota Dinas
        Keluar' muncul setelah klik baris surat."""
        return self.is_visible(self.POPUP_DETAIL_SURAT, timeout=timeout)

    def klik_log_aktifitas_surat(self):
        """Step B.3: Klik tombol 'Log Aktifitas Surat' di footer popup detail."""
        self.click_visible_among(self.BTN_LOG_AKTIFITAS, timeout=10)
        self.wait_loading_mask_gone(timeout=10)

    def is_log_aktifitas_terbuka(self, timeout=10):
        """Step B.4: Verifikasi popup 'Log Aktifitas Surat' muncul."""
        return self.is_visible(self.POPUP_LOG_AKTIFITAS, timeout=timeout)

    def _tutup_popup_dengan_header(self, judul_popup, timeout=5):
        """Klik tombol Close DI DALAM window popup yang judulnya persis
        `judul_popup` — BUKAN cari semua x-tool-close di seluruh halaman
        (popup detail & popup log sama-sama punya tombol close, jadi
        klik `[-1]` global bisa salah sasaran / nyasar ke popup lain)."""
        windows = self.driver.find_elements(By.CSS_SELECTOR, "div.x-window")
        for win in windows:
            try:
                rect = self.driver.execute_script(
                    "var r=arguments[0].getBoundingClientRect();"
                    "return [r.width,r.height];", win
                )
                if rect[0] <= 0 or rect[1] <= 0:
                    continue  # window tersembunyi, skip

                # Cek judul window ini
                header = win.find_elements(
                    By.XPATH,
                    ".//span[contains(@class,'x-window-header-text')]"
                    f"[normalize-space(text())='{judul_popup}']",
                )
                if not header:
                    continue  # bukan popup yang dicari

                # Klik semua tombol close DI DALAM window ini.
                # Class x-tool-close ada di <img>, handler klik ExtJS
                # ada di div.x-tool induknya -- klik img lalu parent div
                # supaya event benar-benar terekam.
                close_imgs = win.find_elements(By.CSS_SELECTOR, "img.x-tool-close")
                for img in close_imgs:
                    try:
                        parent_tool = self.driver.execute_script(
                            "return arguments[0].closest('div.x-tool');", img
                        )
                        if parent_tool:
                            self.driver.execute_script(
                                "arguments[0].click();", parent_tool
                            )
                        else:
                            self.driver.execute_script("arguments[0].click();", img)
                    except Exception:
                        continue
                return len(close_imgs) > 0
            except Exception:
                continue
        return False

    def tutup_log_aktifitas(self):
        """Step B.5: Klik tombol Close pada popup Log Aktifitas Surat."""
        if not self._tutup_popup_dengan_header("Log Aktifitas Surat"):
            # Fallback lama: klik close button terakhir yang tampil
            close_buttons = self.find_all_visible(self.BTN_CLOSE_LOG, timeout=5)
            if close_buttons:
                self.click_via_js(close_buttons[-1])
        self.wait_loading_mask_gone(timeout=10)

    def is_log_aktifitas_tertutup(self, timeout=10):
        """Step B.6: Verifikasi popup Log Aktifitas sudah tidak tampil."""
        return not self.is_visible(self.POPUP_LOG_AKTIFITAS, timeout=timeout)

    def tutup_detail_surat(self):
        """Step B.7: Klik tombol Close pada popup detail surat."""
        if not self._tutup_popup_dengan_header("Identitas Agenda Surat Nota Dinas Keluar"):
            # Fallback lama: klik close button terakhir yang tampil
            close_buttons = self.find_all_visible(self.BTN_CLOSE_LOG, timeout=5)
            if close_buttons:
                self.click_via_js(close_buttons[-1])
        self.wait_loading_mask_gone(timeout=10)

    def is_detail_surat_tertutup(self, timeout=10):
        """Step B.8: Verifikasi popup detail surat sudah tidak tampil."""
        return not self.is_visible(self.POPUP_DETAIL_SURAT, timeout=timeout)
