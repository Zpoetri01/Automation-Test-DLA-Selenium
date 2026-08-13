"""
tests/test_e2e_dla.py
======================
Alur E2E NewDLA - CONTINUOUS FLOW, 1 browser session, mengikuti PERSIS
struktur Flow_Automation_Testing_DLA.md.
"""

import pytest

from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.tugas_page import TugasPage
from pages.masuk_page import MasukPage
from pages.disposisi_keluar_page import DisposisiKeluarPage
from pages.progress_surat_page import ProgressSuratPage
from pages.surat_dinas_eksternal_page import SuratDinasEksternalPage
from pages.nota_dinas_keluar_page import NotaDinasKeluarPage
from pages.topbar_page import TopbarPage


@pytest.mark.e2e
class TestE2EDlaFlow:

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup_page_objects(cls, request, driver, test_data):
        # Classmethod (bukan instance method) sesuai deprecation pytest:
        # fixture class-scoped berjalan sekali per class, tapi tiap test
        # dapat instance baru -- set attribute di `cls` (bukan self/
        # request.cls) supaya tetap terlihat di semua test method.
        cls.driver = driver
        cls.data = test_data

        cls.login_page = LoginPage(driver)
        cls.dashboard_page = DashboardPage(driver)
        cls.tugas_page = TugasPage(driver)
        cls.masuk_page = MasukPage(driver)
        cls.disposisi_keluar_page = DisposisiKeluarPage(driver)
        cls.progress_surat_page = ProgressSuratPage(driver)
        cls.surat_dinas_eksternal_page = SuratDinasEksternalPage(driver)
        cls.nota_dinas_keluar_page = NotaDinasKeluarPage(driver)
        cls.topbar_page = TopbarPage(driver)

    def test_login(self):
        print("\n[LOGIN]")
        self.login_page.open(self.data["base_url"])
        # Timeout 30 detik -- load pertama (SSO redirect) kadang > 20 detik.
        assert self.login_page.is_login_success(timeout=30), "Login gagal / Dashboard tidak muncul"
        print("v Login berhasil, Dashboard tampil")

    def test_dashboard_buka(self):
        print("\n[MODUL 1 - DASHBOARD]")
        assert self.dashboard_page.is_dashboard_loaded(timeout=10), "Dashboard tidak tampil"
        print("v Halaman Dashboard tampil")

    def test_dashboard_widget(self):
        # Verifikasi widget CEPAT (3 detik/widget) biar awal dashboard cepat.
        self.dashboard_page.wait_loading_mask_gone(timeout=5)
        self.dashboard_page.pace(2)
        assert self.dashboard_page.is_widget_visible(self.dashboard_page.WIDGET_SURAT_MASUK, timeout=3), \
            "Widget Surat Masuk tidak tampil"
        assert self.dashboard_page.is_widget_visible(self.dashboard_page.WIDGET_DISPOSISI_MASUK, timeout=3), \
            "Widget Disposisi Masuk tidak tampil"
        assert self.dashboard_page.is_widget_visible(self.dashboard_page.WIDGET_DISPOSISI_KELUAR, timeout=3), \
            "Widget Disposisi Keluar tidak tampil"
        assert self.dashboard_page.is_widget_visible(self.dashboard_page.WIDGET_SURAT_KELUAR_EKSTERNAL, timeout=3), \
            "Widget Surat Keluar tidak tampil"
        print("v Widget Surat Masuk, Disposisi Masuk, Disposisi Keluar, Surat Keluar tampil")

    def test_dashboard_rentang_tanggal(self):
        self.dashboard_page.open_rentang_tanggal()
        print("v Tombol Rentang Tanggal berhasil diklik")

    def test_dashboard_popup_tanggal(self):
        assert self.dashboard_page.is_visible(self.dashboard_page.INPUT_TANGGAL_AWAL, timeout=10), \
            "Pop-up Rentang Tanggal tidak muncul"
        print("v Pop-up Rentang Tanggal muncul")

    def test_dashboard_pilih_tanggal(self):
        filter_dashboard = self.data["dashboard"]
        self.dashboard_page.pilih_rentang_tanggal(
            filter_dashboard["tanggal_awal"], filter_dashboard["tanggal_akhir"]
        )
        print("v Tanggal awal & tanggal akhir berhasil dipilih")

    def test_dashboard_cari(self):
        self.dashboard_page.klik_cari()
        print("v Tombol Cari pada pop-up Rentang Tanggal berhasil diklik")

    def test_dashboard_verifikasi(self):
        assert self.dashboard_page.is_dashboard_loaded(), "Dashboard tidak reload setelah filter tanggal"
        print("v Data dashboard berhasil diperbarui sesuai rentang tanggal yang dipilih")

    def _jalankan_flow_filter_generic(self, page, data_key, nama_modul, skip_posisi=False):
        data_modul = self.data[data_key]

        page.open_menu()
        assert page.is_halaman_loaded(), f"Halaman {nama_modul} tidak tampil"
        print(f"v Halaman {nama_modul} tampil")

        # Modul 6 & 7 (Surat Keluar Eksternal & Nota Dinas Keluar)
        # TIDAK punya dropdown Posisi -- hanya search & Advanced Filter.
        # Skip posisi cycling (step 2-5) untuk 2 modul ini.
        if not skip_posisi:
            for opsi_posisi in page.POSISI_FILTER_OPTIONS:
                page.pilih_posisi(opsi_posisi)
                assert page.is_halaman_loaded(), f"Grid {nama_modul} tidak reload untuk posisi '{opsi_posisi}'"
                print(f"v Opsi Posisi '{opsi_posisi}' berhasil dipilih")

        # Step 6: Pencarian dengan kata kunci otomatis
        page.cari_otomatis(data_modul["kata_kunci_pencarian"])
        print(f"v Pencarian otomatis dengan kata kunci '{data_modul['kata_kunci_pencarian']}' berhasil")
        assert page.is_halaman_loaded(), f"Pencarian {nama_modul} gagal -- grid tidak reload"

        # Step 7: Pastikan pencarian berhasil, lalu hapus keyword (kembali ke semula)
        page.clear_pencarian()
        print(f"v Pencarian {nama_modul} berhasil ditemukan, keyword dihapus, grid kembali ke semula")

        # Step 9: Klik tombol Filter
        page.klik_filter()
        # Step 10: Pastikan pop-up Advanced Filter muncul
        assert page.is_popup_advanced_filter_terbuka(), "Pop-up Advanced Filter tidak muncul"
        print("v Pop-up Advanced Filter muncul")

        # Step 11: Pilih jenis filter dengan dropdown
        page.pilih_jenis_filter(data_modul["jenis_filter"])
        print(f"v Jenis filter '{data_modul['jenis_filter']}' berhasil dipilih")

        # Step 12: Mengisi data filter dengan checkbox
        checkbox_labels = data_modul.get("checkbox_labels_filter")
        page.isi_data_filter(data_modul["kata_kunci_filter"], checkbox_labels=checkbox_labels)
        print(f"v Data filter '{data_modul['kata_kunci_filter']}' berhasil diisi"
              f"{' (checkbox: ' + ', '.join(checkbox_labels) + ')' if checkbox_labels else ''}")

        # Step 13: Klik tombol Cari pada pop-up Advanced Filter
        page.klik_cari_popup()
        # Step 14: Pastikan data berhasil difilter sesuai kriteria
        assert page.is_halaman_loaded(), f"Data {nama_modul} tidak berhasil difilter"
        print(f"v Data {nama_modul} berhasil difilter sesuai kriteria")

    def test_tugas(self):
        print("\n[MODUL 2 - TUGAS]")
        self._jalankan_flow_filter_generic(self.tugas_page, "tugas", "Tugas")

    def test_masuk(self):
        print("\n[MODUL 3 - MASUK]")
        self._jalankan_flow_filter_generic(self.masuk_page, "masuk", "Masuk")

    def test_disposisi_keluar(self):
        print("\n[MODUL 4 - DISPOSISI KELUAR]")
        self._jalankan_flow_filter_generic(
            self.disposisi_keluar_page, "disposisi_keluar", "Disposisi Keluar"
        )

    def test_progress_surat(self):
        print("\n[MODUL 5 - PROGRESS SURAT]")
        self._jalankan_flow_filter_generic(
            self.progress_surat_page, "progress_surat", "Progress Surat"
        )

    def _buat_surat_baru_generic(self, page, data_surat, nama_modul):
        # Step 15: Klik tombol Tambah
        page.klik_tambah()
        print("v Tombol Tambah berhasil diklik")

        # Step 16: Unggah berkas menggunakan opsi Link
        page.upload_berkas_via_link(data_surat["url_dokumen"], data_surat.get("nama_dokumen"))
        print(f"v Berkas berhasil diunggah lewat opsi Link ({data_surat['url_dokumen']})")

        # Step 17: Mengisi link dokumen
        # Step 18: Mengisi form Surat Keluar Eksternal
        # Tunggu form benar-benar siap setelah upload popup menutup
        page.wait_loading_mask_gone(timeout=15)
        page.isi_form(data_surat)
        print(f"v Form {nama_modul} berhasil diisi")

        # Step 19: Menambahkan penyetuju dengan keyword & pilih checkbox
        # sesuai baris (default: baris ke-3 = IT & Digitalization)
        checkbox_row_penyetuju = data_surat.get("checkbox_row_penyetuju", 3)
        page.tambah_penyetuju(
            data_surat["kata_kunci_penyetuju"],
            checkbox_row=checkbox_row_penyetuju,
        )
        print(f"v Penyetuju dengan kata kunci '{data_surat['kata_kunci_penyetuju']}'"
              f" berhasil ditambahkan (checkbox baris ke-{checkbox_row_penyetuju})")

        # Step 21: Menambahkan penerima dengan keyword & pilih checkbox
        # sesuai baris (default: baris ke-1 = ICT Solusi desain)
        checkbox_row_penerima = data_surat.get("checkbox_row_penerima", 1)
        page.tambah_penerima(
            data_surat["kata_kunci_penerima"],
            checkbox_row=checkbox_row_penerima,
        )
        print(f"v Penerima dengan kata kunci '{data_surat['kata_kunci_penerima']}'"
              f" berhasil ditambahkan (checkbox baris ke-{checkbox_row_penerima})")

        # Step 23: Klik tombol Ajukan Penyetujuan
        # (flow TIDAK menyebutkan pilih_tembusan_checkbox setelah penerima --
        # langsung ke Ajukan Penyetujuan)
        berhasil = page.ajukan_penyetujuan()
        # Step 24: Pastikan surat berhasil diajukan
        assert berhasil, f"{nama_modul} gagal diajukan untuk proses persetujuan"
        print(f"v {nama_modul} berhasil diajukan untuk proses persetujuan")

    # ==========================================================
    # MODUL 6 - SURAT KELUAR EKSTERNAL
    # ==========================================================
    def test_surat_keluar_eksternal(self):
        """Steps 1-9: search otomatis + Advanced Filter, lalu RESET
        supaya filter dibersihkan & grid siap untuk Tambah."""
        print("\n[MODUL 6 - SURAT KELUAR EKSTERNAL]")
        self._jalankan_flow_filter_generic(
            self.surat_dinas_eksternal_page, "surat_dinas_eksternal",
            "Surat Keluar Eksternal", skip_posisi=True,
        )

        # Buka Advanced Filter lagi lalu RESET (langsung RESET kalau popup masih terbuka).
        if not self.surat_dinas_eksternal_page.is_popup_advanced_filter_terbuka():
            self.surat_dinas_eksternal_page.klik_filter()
        assert self.surat_dinas_eksternal_page.is_popup_advanced_filter_terbuka(), (
            "Pop-up Advanced Filter (kedua) tidak muncul"
        )
        print("v Pop-up Advanced Filter dibuka lagi")

        self.surat_dinas_eksternal_page.klik_reset_filter()
        print("v Tombol RESET diklik, filter dibersihkan, grid kembali semula")

    def test_simpan_draft_pertama(self):
        print("\n[MODUL 6A - SIMPAN DRAFT PERTAMA]")
        data = self.data["surat_dinas_eksternal"]
        self._isi_form_dan_simpan_draft(self.surat_dinas_eksternal_page, data, "pertama")

    def test_hapus_draft(self):
        print("\n[MODUL 6B - HAPUS DRAFT]")
        self.surat_dinas_eksternal_page.wait_loading_mask_gone(timeout=10)
        self.surat_dinas_eksternal_page.pilih_draft_pertama()
        print("v Draft berhasil dipilih")
        self.surat_dinas_eksternal_page.klik_hapus()
        print("v Tombol Hapus diklik")
        self.surat_dinas_eksternal_page.klik_ya_konfirmasi()
        print("v Ya diklik")
        self.surat_dinas_eksternal_page.klik_ok_notifikasi()
        print("v OK diklik")
        assert self.surat_dinas_eksternal_page.is_draft_terhapus()
        print("v Draft berhasil dihapus")

    def test_ubah_dan_ajukan(self):
        print("\n[MODUL 6C - SIMPAN DRAFT KEDUA + PERUBAHAN + AJUKAN]")
        data = self.data["surat_dinas_eksternal"]
        f2 = data.get("_form2", {})

        # Step C.6-15: Tambah → isi form beda → Simpan Draft
        self._isi_form_dan_simpan_draft(
            self.surat_dinas_eksternal_page,
            {**data, **f2},  # merge form2 overrides
            "kedua"
        )

        # Step C.16: Pilih surat yang baru disimpan
        self.surat_dinas_eksternal_page.pilih_draft_pertama()
        print("v Draft kedua berhasil dipilih")

        # Step C.17: Klik Perubahan
        self.surat_dinas_eksternal_page.klik_perubahan()
        print("v Tombol Perubahan diklik")

        # Step C.18: Hapus penerima lama (ikon bin)
        self.surat_dinas_eksternal_page.hapus_penerima()
        print("v Penerima lama dihapus")
        # Yang terhapus harus PENERIMA (Ryco) -- penyetuju (Yulia) masih ada.
        assert self.surat_dinas_eksternal_page.verifikasi_penyetuju_masih_ada(
            data["kata_kunci_penyetuju"]
        ), ("Penyetuju ikut terhapus! Yang harusnya terhapus adalah "
            "PENERIMA (Ryco), bukan penyetuju (Yulia).")

        # Step C.19-21: Tambah penerima baru "Arru"
        self.surat_dinas_eksternal_page.tambah_penerima_baru(
            data["kata_kunci_penerima_baru"]
        )
        print(f"v Penerima '{data['kata_kunci_penerima_baru']}' ditambahkan")
        # Verifikasi staf baru masuk ke bagian PENERIMA (bukan Penyetuju)
        assert self.surat_dinas_eksternal_page.verifikasi_penerima_ditambahkan(
            data["kata_kunci_penerima_baru"]
        ), ("Staf baru TIDAK masuk ke bagian Penerima -- "
            "kemungkinan masuk ke bagian Penyetuju (salah section)")

        # Step C.22-23: Ajukan Penyetujuan
        berhasil = self.surat_dinas_eksternal_page.ajukan_perubahan()
        assert berhasil, "Gagal diajukan"
        print("v Surat berhasil diajukan")

    def _isi_form_dan_simpan_draft(self, page, data_surat, label):
        """Helper: Tambah → upload → isi form → tambah staff → Simpan Draft."""
        page.klik_tambah()
        print(f"v [{label}] Tombol Tambah diklik")
        page.upload_berkas_via_link(data_surat["url_dokumen"], data_surat.get("nama_dokumen"))
        print(f"v [{label}] Berkas diunggah")
        page.wait_loading_mask_gone(timeout=15)
        page.isi_form(data_surat)
        print(f"v [{label}] Form diisi")
        # Tutup popup Nota Dinas yang mungkin muncul saat isi form
        page._tutup_popup_detail_surat()
        page.tambah_penyetuju(
            data_surat["kata_kunci_penyetuju"],
            checkbox_row=data_surat.get("checkbox_row_penyetuju", 3),
        )
        print(f"v [{label}] Penyetuju ditambahkan")
        page.tambah_penerima(
            data_surat["kata_kunci_penerima"],
            checkbox_row=data_surat.get("checkbox_row_penerima", 1),
        )
        print(f"v [{label}] Penerima ditambahkan")
        berhasil = page.simpan_draft()
        assert berhasil, f"[{label}] Gagal simpan draft"
        print(f"v [{label}] Draft berhasil disimpan")
        # TANPA REFRESH: form sudah tertutup, reload grid via ExtJS store
        page._klik_muat_ulang()
        page.wait_loading_mask_gone(timeout=20)

    # ==========================================================
    # MODUL 7 - NOTA DINAS KELUAR
    # ==========================================================
    def test_nota_dinas_keluar(self):
        """Steps 1-9: Buka halaman → search → Advanced Filter → pastikan
        data berhasil difilter sebelum masuk ke Cek Detail Surat."""
        print("\n[MODUL 7 - NOTA DINAS KELUAR]")
        self._jalankan_flow_filter_generic(
            self.nota_dinas_keluar_page, "nota_dinas_keluar",
            "Nota Dinas Keluar", skip_posisi=True,
        )

    def test_detail_surat(self):
        print("\n[MODUL 7B - CEK DETAIL SURAT]")

        self.nota_dinas_keluar_page.pilih_draft_pertama()
        print("v Salah satu surat berhasil dipilih")

        assert self.nota_dinas_keluar_page.is_detail_surat_terbuka(), (
            "Pop-up Identitas Agenda Surat Nota Dinas Keluar tidak muncul"
        )
        print("v Pop-up Identitas Agenda Surat Nota Dinas Keluar muncul")

        self.nota_dinas_keluar_page.klik_log_aktifitas_surat()
        print("v Tombol Log Aktifitas Surat berhasil diklik")

        assert self.nota_dinas_keluar_page.is_log_aktifitas_terbuka(), (
            "Pop-up Log Aktifitas Surat tidak muncul"
        )
        print("v Pop-up Log Aktifitas Surat muncul")

        self.nota_dinas_keluar_page.tutup_log_aktifitas()
        print("v Tombol Close pada popup Log Aktifitas berhasil diklik")
        assert self.nota_dinas_keluar_page.is_log_aktifitas_tertutup(), (
            "Pop-up Log Aktifitas Surat tidak berhasil ditutup"
        )
        print("v Pop-up Log Aktifitas Surat berhasil ditutup")

        self.nota_dinas_keluar_page.tutup_detail_surat()
        print("v Tombol Close pada popup detail surat berhasil diklik")
        assert self.nota_dinas_keluar_page.is_detail_surat_tertutup(), (
            "Pop-up detail surat tidak berhasil ditutup"
        )
        print("v Pop-up detail surat berhasil ditutup")
        print("v Cek Detail Surat selesai")

    def test_topbar(self):
        """4 tombol topbar: buka tiap dropdown & pastikan isinya muncul."""
        print("\n[MODUL TOPBAR]")
        # Kembali ke Dashboard dulu (lonceng notifikasi hanya ada di Dashboard).
        self.dashboard_page.wait_loading_mask_gone(timeout=10)
        menu = self.dashboard_page.find_visible_among(
            (By.CSS_SELECTOR, "[data-qtip='Dashboard']"), timeout=10
        )
        self.dashboard_page.click_via_js(menu)
        self.dashboard_page.wait_loading_mask_gone(timeout=10)
        self.dashboard_page.pace(1)
        print("v Kembali ke Dashboard")

        hasil = self.topbar_page.buka_semua_menu()
        for nama, ok in hasil:
            assert ok, f"Dropdown {nama} tidak terbuka"
            print(f"v Dropdown {nama} terbuka")

    def test_logout(self):
        print("\n[MODUL 8 - LOGOUT]")
        self.login_page.logout()
        print("v Menu Logout pada sidebar berhasil diklik")

        assert self.login_page.is_kembali_ke_halaman_login(), "Pengguna tidak berhasil keluar dari aplikasi"
        print("v Pengguna berhasil keluar dari aplikasi")
        print("v Halaman Login kembali ditampilkan")
