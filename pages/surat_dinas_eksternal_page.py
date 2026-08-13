"""
pages/surat_dinas_eksternal_page.py
=====================================
Modul 6 - Surat Keluar Eksternal (20 Test Steps, lihat
Flow_Automation_Testing_DLA.md). Step 1-11 (navigasi, filter posisi,
pencarian, advanced filter) memakai FilterableListPage. Step 12-20
(Tambah surat -> upload berkas Link -> isi form -> penyetuju -> penerima
-> tembusan -> Ajukan Penyetujuan) memakai SuratFormBasePage -- lihat
pages/surat_form_base_page.py untuk detail locator (diambil dari HTML
asli, bukan tebakan id ExtJS).
"""

from selenium.webdriver.common.by import By
from pages.surat_form_base_page import SuratFormBasePage


class SuratDinasEksternalPage(SuratFormBasePage):

    # Locator dikonfirmasi lewat tools/scan_locators.py -- qtip aslinya
    # "Agenda Surat Keluar Eksternal".
    MENU_LOCATOR = (By.CSS_SELECTOR, "[data-qtip='Agenda Surat Keluar Eksternal']")

    HEADER_LOCATOR = (By.XPATH, "//*[normalize-space(text())='Surat Keluar Eksternal']")

    # Alias supaya nama lama tetap jalan.
    MENU_SURAT_DINAS_EKSTERNAL = MENU_LOCATOR
    HEADER_SURAT_DINAS_EKSTERNAL = HEADER_LOCATOR

    def open_menu_surat_dinas_eksternal(self):
        self.open_menu()

    def is_surat_dinas_eksternal_loaded(self):
        return self.is_halaman_loaded()

    # ==========================================================
    # ISI FORM -- KHUSUS Surat Keluar Eksternal (step 15).
    # Field: Kepada, Alamat, Perihal, Lampiran, Jenis/Klasifikasi/
    # Sifat/Prioritas/Media Surat, Lokasi Arsip Fisik.
    # ==========================================================
    def isi_form(self, data_surat):
        if data_surat.get("kepada"):
            self.isi_kepada(data_surat["kepada"])
        if data_surat.get("alamat"):
            self.isi_alamat(data_surat["alamat"])
        if data_surat.get("perihal"):
            self.isi_perihal(data_surat["perihal"])
        if data_surat.get("lampiran_jumlah"):
            self.isi_lampiran(data_surat["lampiran_jumlah"], data_surat.get("lampiran_satuan"))
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
        if data_surat.get("media_surat"):
            self.pilih_media_surat(data_surat["media_surat"])
        if data_surat.get("lokasi_arsip_fisik"):
            self.pilih_lokasi_arsip_fisik(data_surat["lokasi_arsip_fisik"])
