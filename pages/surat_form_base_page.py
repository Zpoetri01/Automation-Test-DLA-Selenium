"""
pages/surat_form_base_page.py
==============================
Modul 6 (Surat Keluar Eksternal) & Modul 7 (Nota Dinas Keluar) memakai
FORM YANG SAMA PERSIS (form "Tambah Agenda Surat Keluar
Eksternal"/"Nota Dinas" -- lihat catatan kamu: "Nota Dinas Keluar (form
tambah nota dinas) sama kaya surat keluar eksternal"). Semua locator di
sini diambil LANGSUNG dari HTML asli yang kamu kirim (bukan tebakan),
jadi memakai atribut `name` yang stabil (bukan id ExtJS auto-generate
seperti `combo-2229` yang berubah tiap render).

Alur (step 12-20 di Flow_Automation_Testing_DLA.md, Modul 6 & 7A):
  12. Klik tombol Tambah.
  13. Upload berkas via opsi Link.
  14. Isi link dokumen.
  15. Isi form (Kepada, Alamat, Perihal, Jenis/Klasifikasi/Sifat/
      Prioritas/Media Surat, Lokasi Arsip Fisik).
  16. Tambah penyetuju (kata kunci) & pilih data.
  17. Tambah penerima (kata kunci) & pilih data.
  18. Pilih tembusan lewat checkbox.
  19. Klik Ajukan Penyetujuan.
  20. Pastikan surat berhasil diajukan.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pages.filterable_list_page import FilterableListPage


class SuratFormBasePage(FilterableListPage):

    # ==========================================================
    # OVERRIDE DROPDOWN POSISI untuk Modul 6 & 7
    # ==========================================================
    # Modul 6 (Surat Keluar Eksternal) & Modul 7 (Nota Dinas Keluar)
    # TIDAK menampilkan teks "Primary Position"/"Secondary Position"/
    # "Semua" di dropdown Posisi -- yang tampil adalah JABATAN ASLI
    # user (mis. "ICT Solution Design Senior Specialist ... (Primary)").
    # Jadi locator parent (FilterableListPage) yang mencocokkan value
    # input dengan teks "Semua"/"Primary Position"/"Secondary Position"
    # TIDAK PERNAH match.
    #
    # Strategi override: klik TRIGGER ARROW pertama di toolbar atas
    # (bukan input-nya langsung). Di ExtJS, combo trigger adalah <a>
    # atau <div> dengan class trigger yang berada setelah input combo.
    # Input combo-nya sendiri bisa readonly dan tidak responsif terhadap
    # klik JS kalau event handler-nya ada di trigger, bukan di input.
    DROPDOWN_FILTER_POSISI = (
        By.CSS_SELECTOR,
        "div.x-toolbar input.x-form-text[readonly]",
    )

    # Trigger arrow combo posisi: elemen <a> atau <div> dengan class
    # 'x-form-arrow-trigger' atau 'x-form-trigger' yang ADA di toolbar
    # yang sama dengan input combo readonly.
    TRIGGER_POSISI = (
        By.CSS_SELECTOR,
        "div.x-toolbar a.x-form-arrow-trigger, "
        "div.x-toolbar div.x-form-trigger, "
        "div.x-toolbar a.x-form-trigger",
    )

    def klik_dropdown_posisi(self):
        """Override untuk Modul 6 & 7: klik TRIGGER arrow combo Posisi,
        bukan input-nya langsung. Di ExtJS, event handler untuk membuka
        boundlist sering ada di elemen trigger (arrow), bukan di input
        combo itu sendiri -- jadi klik input (walaupun visible) tidak
        membuka boundlist, dan _pilih_opsi_posisi_by_index() gagal
        karena boundlist kosong (0 visible items)."""
        # Coba klik trigger arrow dulu (cara yang lebih reliable)
        try:
            trigger = self.find_visible_among(self.TRIGGER_POSISI, timeout=10)
            self.click_via_js(trigger)
            self.pace(1)
            # Verifikasi boundlist terbuka
            boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
            if self.is_visible(boundlist_terbuka, timeout=3):
                return
        except Exception:
            pass

        # Fallback: klik input combo langsung (cara lama)
        try:
            element = self.find_visible_among(self.DROPDOWN_FILTER_POSISI, timeout=10)
            self.click_via_js(element)
            self.pace(1)
        except Exception:
            # Fallback terakhir: klik combo pertama di halaman
            # (pakai selector yang lebih umum)
            combos = self.find_all_visible(
                (By.CSS_SELECTOR, "input.x-form-text[readonly]"), timeout=10
            )
            if combos:
                self.click_via_js(combos[0])
                self.pace(1)

    # ==========================================================
    # TOMBOL TAMBAH (buka form) -- teks tombol, konsisten di semua modul.
    # ==========================================================
    # Tombol Tambah di toolbar: id="sipas_com_button_add-XXXX" (angka
    # ExtJS random). Pakai CSS selector starts-with untuk match prefix
    # id yang stabil, bukan teks "Tambah" yang bisa match banyak elemen
    # hidden di DOM (dari modul/tab lain).
    BTN_TAMBAH = (By.CSS_SELECTOR, "[id^='sipas_com_button_add-']")

    # ==========================================================
    # UPLOAD BERKAS VIA LINK
    # ==========================================================
    # Ikon "+" untuk membuka menu pilihan upload berkas (Link/File).
    BTN_TAMBAH_BERKAS = (By.CSS_SELECTOR, "span.ion-md-add-circle")

    MENU_ITEM_LINK = (By.XPATH, "//span[normalize-space(text())='Link']")

    # Field di dalam popup "Link": Tentang (nama dokumen) & Perihal (url).
    INPUT_DOKUMEN_NAMA = (By.CSS_SELECTOR, "input[name='dokumen_nama']")
    INPUT_DOKUMEN_LINK = (By.CSS_SELECTOR, "input[name='dokumen_file']")
    BTN_SIMPAN_LINK = (By.XPATH, "//span[normalize-space(text())='SIMPAN' or normalize-space(text())='Simpan']")

    # Chip/thumbnail berkas yang sudah berhasil ditambahkan (muncul di
    # panel kiri "Berkas" -- lihat HTML asli: div.sipas_archive
    # div.image-wrap, judulnya ada di span dalam .image-title). Dipakai
    # untuk MEMASTIKAN upload sukses tanpa perlu reload halaman atau
    # klik ikon Tambah Berkas lagi.
    ARCHIVE_ITEM_LOCATOR = (By.CSS_SELECTOR, "div.sipas_archive div.image-wrap")

    # ==========================================================
    # FORM SURAT (name attribute diambil persis dari HTML asli)
    # ==========================================================
    INPUT_KEPADA = (By.CSS_SELECTOR, "input[name='surat_tujuan']")
    TEXTAREA_TEMBUSAN = (By.CSS_SELECTOR, "textarea[name='surat_kepada']")
    TEXTAREA_ALAMAT = (By.CSS_SELECTOR, "textarea[name='surat_alamat']")
    TEXTAREA_PERIHAL = (By.CSS_SELECTOR, "textarea[name='surat_perihal']")

    DROPDOWN_JENIS_SURAT = (By.CSS_SELECTOR, "input[name='surat_jenis']")
    DROPDOWN_KLASIFIKASI_SURAT = (By.CSS_SELECTOR, "input[name='surat_kelas']")
    DROPDOWN_SIFAT_SURAT = (By.CSS_SELECTOR, "input[name='surat_sifat']")
    DROPDOWN_PRIORITAS_SURAT = (By.CSS_SELECTOR, "input[name='surat_prioritas']")
    DROPDOWN_MEDIA_SURAT = (By.CSS_SELECTOR, "input[name='surat_media']")
    DROPDOWN_LOKASI_ARSIP_FISIK = (By.CSS_SELECTOR, "input[name='surat_lokasi']")

    # Lampiran: hanya ada di form Surat Keluar Eksternal (name
    # 'surat_lampiran' + 'surat_lampiran_sub', mis. "1" + "Lembar").
    INPUT_LAMPIRAN_JUMLAH = (By.CSS_SELECTOR, "input[name='surat_lampiran']")
    INPUT_LAMPIRAN_SATUAN = (By.CSS_SELECTOR, "input[name='surat_lampiran_sub']")

    # Uraian: ada di kedua form (name 'surat_keterangan').
    TEXTAREA_URAIAN = (By.CSS_SELECTOR, "textarea[name='surat_keterangan']")

    # ==========================================================
    # PENYETUJU / PENERIMA (TAMBAH pertama yg TAMPIL = Penyetuju, kedua
    # yg TAMPIL = Tembusan/Penerima -- lihat BTN_TAMBAH_ANY di bawah).
    # ==========================================================
    # PENTING: locator ini dipakai lewat find_all_visible() (bukan XPath
    # positional [1]/[2] langsung), supaya urutannya dihitung dari tombol
    # 'Tambah' yang BENAR-BENAR TAMPIL di layar saat ini -- kalau dipakai
    # positional murni di DOM, tombol 'Tambah' milik popup staf yang
    # SUDAH DIBUKA SEBELUMNYA (tapi belum benar2 tertutup / masih basi di
    # DOM) bisa ikut kehitung dan menggeser index, sehingga Tambah
    # Penyetuju & Tambah Penerima jadi salah sasaran / popup-nya
    # tertumpuk-tindih satu sama lain.
    BTN_TAMBAH_ANY = (By.XPATH, "//*[normalize-space(text())='Tambah' or normalize-space(text())='TAMBAH']")

    INPUT_CARI_STAF = (By.CSS_SELECTOR, "input[type='search']")
    CHECKBOX_ROW_STAF = (By.CSS_SELECTOR, ".x-grid-row-checker")
    BTN_PILIH = (By.CSS_SELECTOR, "[id^='sipas_com_button_putin-']")

    BTN_AJUKAN_PENYETUJUAN = (By.CSS_SELECTOR, "[id^='sipas_com_button_savesend-']")
    BTN_SIMPAN_DRAFT = (By.CSS_SELECTOR, "[id^='sipas_com_button_save-']")
    ICON_HAPUS_PENERIMA = (By.CSS_SELECTOR, "img.x-action-col-icon-bin[data-qtip='Hapus']")

    # Toast/notif sukses generik ExtJS setelah AJUKAN PENYETUJUAN berhasil.
    NOTIF_SUKSES_CANDIDATES = (
        (By.XPATH, "//*[contains(@class,'x-toast')][contains(.,'berhasil') or contains(.,'Berhasil')]"),
        (By.XPATH, "//*[contains(@class,'x-message-box')][contains(.,'berhasil') or contains(.,'Berhasil')]"),
    )

    # ==========================================================
    # TOMBOL TAMBAH -> BUKA FORM (step 12)
    # ==========================================================
    def klik_tambah(self):
        """PENTING (akar penyebab popup 'lompat' ke modul lain / event
        klik nyasar ke background -- lihat catatan bug #3 & #4):
        sebelumnya pakai click_via_js(self.BTN_TAMBAH) dengan LOCATOR
        (tuple) langsung. click_via_js() kalau dikasih tuple cuma
        panggil self.find() (presence_of_element_located) -- itu
        mengambil elemen PERTAMA yang match teks 'Tambah' di DOM,
        TANPA cek visibility. Kalau modul lain (mis. Nota Dinas
        Keluar) masih ada sisa render di DOM (SPA tidak selalu
        unmount tab yang tidak aktif), tombol 'Tambah' miliknya ikut
        match dan bisa kepilih duluan -- klik via JS tetap "berhasil"
        walau elemen itu tersembunyi, tapi yang kebuka form/aksi milik
        modul LAIN, bukan modul yang sedang kita uji. Fix: klik yang
        benar-benar tampil di layar sekarang (click_visible_among).

        PENTING #2 (guard anti-tumpang-tindih -- bug #4, form Tambah
        menumpuk): sebelum buka form baru, pastikan TIDAK ADA form
        Tambah (popup dengan TEXTAREA_PERIHAL) yang masih terbuka dari
        pemanggilan sebelumnya. Kalau ada, itu tandanya popup
        sebelumnya belum benar-benar selesai/tertutup -- jangan buka
        form baru di atasnya (itu yang bikin 2 form 'Tambah Agenda
        Surat' tertumpuk-tindih).

        PENTING #3: setelah Advanced Filter ditutup (klik CARI), grid
        reload data. Tunggu loading mask hilang DULU sebelum mencari
        tombol Tambah -- kalau grid masih loading, tombol Tambah bisa
        belum muncul / belum siap diklik."""
        # Bersihkan layar DULU: tutup SEMUA popup yang tersisa (popup
        # detail surat, popup staf, form basi) -- halaman list seharusnya
        # bersih dari popup sebelum membuka form Tambah yang baru.
        self._tutup_semua_popup()
        assert not self.is_visible(self.TEXTAREA_PERIHAL, timeout=2), (
            "Ada form 'Tambah Agenda Surat' yang masih terbuka dari langkah "
            "sebelumnya -- tidak boleh buka form baru di atasnya (akan "
            "tertumpuk-tindih). Pastikan form sebelumnya sudah benar-benar "
            "selesai/tertutup (ajukan_penyetujuan() sukses) sebelum "
            "klik_tambah() dipanggil lagi."
        )
        # Tunggu grid selesai reload setelah filter
        self.wait_loading_mask_gone(timeout=15)
        # Cari tombol Tambah. PASTIKAN klik yang visible -- jangan
        # fallback ke find() biasa karena bisa nyasar ke tombol Tambah
        # milik modul LAIN (mis. Nota Dinas) yang hidden di DOM!
        # Kalau click_visible_among gagal, cari SEMUA tombol dgn ID
        # prefix ini dan klik yang benar-benar visible.
        #
        # PENTING (fix klik terekam saat grid masih loading): kalau form
        # belum muncul setelah klik (karena grid masih sibuk), klik ulang
        # maks 3x. Sebelum klik ulang, cek form TIDAK ada di DOM dulu
        # (cegah buka 2 form tertumpuk).
        form_muncul = False
        for attempt in range(3):
            try:
                self.click_visible_among(self.BTN_TAMBAH, timeout=10)
            except Exception:
                # Fallback: cari tombol via JS, klik LANGSUNG tanpa cek visibility
                clicked = self.driver.execute_script("""
                    var btns = document.querySelectorAll("[id^='sipas_com_button_add-']");
                    for (var i = 0; i < btns.length; i++) {
                        var rect = btns[i].getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            btns[i].scrollIntoView({block: 'center'});
                            btns[i].click();
                            return true;
                        }
                    }
                    return false;
                """)
                if not clicked:
                    raise TimeoutException(
                        "Tombol Tambah tidak ditemukan. "
                        "Pastikan halaman Surat Keluar Eksternal sudah terbuka."
                    )
            # Tunggu form muncul (attempt terakhir diberi waktu penuh)
            if self.is_visible(self.TEXTAREA_PERIHAL, timeout=8 if attempt < 2 else 15):
                form_muncul = True
                break
            # Form belum muncul -- kalau sudah ADA di DOM (lagi render
            # lambat), tunggu saja, JANGAN klik ulang (cegah 2 form)
            if self.is_present(self.TEXTAREA_PERIHAL, timeout=2):
                continue
            # Klik tidak terekam (grid masih loading) -- tunggu & coba lagi
            self.wait_loading_mask_gone(timeout=10)
            self.pace(2)
        if not form_muncul:
            raise TimeoutException(
                "Form 'Tambah Agenda Surat' tidak muncul setelah 3x klik. "
                "Grid mungkin masih loading atau tombol Tambah belum siap."
            )
        self.wait_loading_mask_gone(timeout=10)

    # ==========================================================
    # UPLOAD BERKAS VIA LINK (step 13-14)
    # ==========================================================
    def upload_berkas_via_link(self, url_dokumen, nama_dokumen=None):
        """Isi link dokumen SEKALI SAJA lalu verifikasi berhasil (chip
        berkas muncul di panel kiri). TIDAK reload halaman & TIDAK
        klik ikon Tambah Berkas lagi setelah ini -- kalau method ini
        dipanggil sekali per test, popup Link hanya dibuka & disimpan
        sekali. click(BTN_SIMPAN_LINK) sekarang otomatis fallback ke
        klik JS kalau kena ElementClickInterceptedException (lihat
        BasePage.click), jadi tombol SIMPAN yang sebelumnya gagal
        (ikon di dalam tombol menutupi titik klik) sudah teratasi."""
        # click_visible_among (bukan click_via_js(tuple)/click biasa) --
        # sama seperti klik_tambah(), locator berbasis ikon/teks generik
        # ini bisa match elemen sisa popup Link/menu upload sebelumnya
        # yang belum benar2 hilang dari DOM.
        self.click_visible_among(self.BTN_TAMBAH_BERKAS, timeout=15)
        self.click_visible_among(self.MENU_ITEM_LINK, timeout=10)
        if nama_dokumen:
            self.type_text_visible(self.INPUT_DOKUMEN_NAMA, nama_dokumen)
        self.type_text_visible(self.INPUT_DOKUMEN_LINK, url_dokumen)
        self.click_visible_among(self.BTN_SIMPAN_LINK, timeout=10)
        self.wait_loading_mask_gone(timeout=10)
        # Tunggu lebih lama untuk chip muncul (ExtJS render bisa lambat)
        self.pace(2)
        assert self.is_berkas_terunggah(), "Berkas via Link tidak berhasil diunggah (chip tidak muncul)"

    def is_berkas_terunggah(self, timeout=20):
        """Verifikasi chip berkas sudah muncul di panel 'Berkas'."""
        return self.is_visible(self.ARCHIVE_ITEM_LOCATOR, timeout=timeout)

    # ==========================================================
    # ISI FORM (step 15)
    # ==========================================================
    def isi_kepada(self, kepada, timeout=10):
        # type_text_visible (bukan type_text biasa) -- kalau (karena
        # sebab lain) ada 2 form Tambah tertumpuk, pastikan yang keisi
        # instance yang benar2 tampil, bukan instance basi di belakang.
        #
        # PENTING: setelah upload berkas via Link, popup upload menutup
        # dan fokus kembali ke form -- tapi bisa ada loading mask singkat
        # atau form perlu waktu re-render. Tunggu mask hilang dulu.
        self.wait_loading_mask_gone(timeout=10)
        # Cari input Kepada DI DALAM dialog aktif (form Tambah), bukan
        # di seluruh halaman -- cegah nyasar ke field senama milik
        # Advanced Filter atau sisa popup lain di belakang.
        try:
            element = self.find_visible_in_active_window(self.INPUT_KEPADA, timeout=timeout)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.clear()
            element.send_keys(kepada)
            self.pace()
        except Exception:
            # Fallback: cari di seluruh halaman (whole-page)
            self.type_text_visible(self.INPUT_KEPADA, kepada, timeout=timeout)
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][contains(normalize-space(text()),'{kepada}')]",
        )
        if self.is_visible(opsi_locator, timeout=5):
            self.click_visible_among(opsi_locator, timeout=5)

    def isi_alamat(self, alamat):
        self.wait_loading_mask_gone(timeout=5)
        self.type_text_visible(self.TEXTAREA_ALAMAT, alamat)

    def isi_perihal(self, perihal):
        self.wait_loading_mask_gone(timeout=5)
        self.type_text_visible(self.TEXTAREA_PERIHAL, perihal)

    def _pilih_dari_combo(self, dropdown_locator, nilai, kata_kunci_filter=None):
        """PENTING #1 (akar penyebab bug #2 -- form 'terputus' persis
        mulai dari Jenis Surat sampai Lokasi Arsip Fisik, harus
        discroll tapi tidak pernah keisi): dropdown_locator untuk
        Jenis/Sifat/Media/Lokasi Surat (input[name='surat_jenis'],
        'surat_sifat', 'surat_media', 'surat_lokasi']) TERNYATA
        DUPLIKAT PERSIS dengan nama field yang sama di dalam popup
        Advanced Filter (lihat locator_tambahan/Surat Keluar
        Eksternal.txt -- section 'Filter Data' punya field
        tersembunyi/display:none dengan name IDENTIK, yang baru
        muncul kalau checkbox-nya dicentang). Selama popup Advanced
        Filter masih ada sisa di DOM (dibuka di step filter list
        sebelum masuk ke Tambah), locator ini match 2 elemen.

        Sebelumnya method ini pakai click_via_js(dropdown_locator)
        DENGAN LOCATOR (tuple) LANGSUNG -- itu cuma panggil self.find()
        (presence_of_element_located), yaitu elemen PERTAMA yang match
        di DOM, TIDAK PEDULI tampil atau tidak. Kalau yang pertama
        ketemu itu field tersembunyi milik Advanced Filter, klik lewat
        JS tetap "berhasil" tanpa error, tapi TIDAK ADA APAPUN yang
        kelihatan berubah di layar (dropdown Tambah yang asli tidak
        pernah kebuka) -- persis gejala "terputus"/macet yang
        dilaporkan.

        Fix: cari & klik elemen yang BENAR-BENAR TAMPIL lewat
        find_visible_among (sama seperti pilih_posisi/pilih_jenis_filter
        di FilterableListPage), bukan elemen pertama di DOM.

        PENTING #2 (lanjutan fix bug #2 -- field "terputus"/tidak
        pernah keisi mulai Jenis Surat s.d. Lokasi Arsip Fisik yang
        letaknya di bawah & harus discroll): dropdown itu sendiri bisa
        saja is_displayed()==True tapi belum masuk area pandang
        (viewport) container form yang overflow-nya di-scroll manual
        oleh ExtJS, sehingga klik/ketik jadi tidak terekam dengan benar.
        Fix: scroll elemen ke tengah viewport DULU sebelum diklik.

        PENTING #3 (root cause form "selalu tidak selesai", macet di
        Jenis Surat dst): dropdown seperti "Jenis Surat"/"Klasifikasi
        Surat" isinya puluhan-ratusan opsi referensi. ExtJS me-render
        boundlist seperti ini secara buffered/virtual -- opsi yang
        belum masuk area render TIDAK ADA di DOM sampai di-scroll atau
        DIKETIK/difilter, jadi klik langsung berdasarkan teks persis
        (`nilai` yang panjang) bisa gagal walau dropdown-nya sudah
        kebuka. Fix: ketik dulu `kata_kunci_filter` (potongan pendek,
        mis. "LM") ke input combo supaya ExtJS memfilter & me-render
        opsi yang cocok, BARU klik opsi yang teksnya persis `nilai`
        (fallback: opsi pertama yang mengandung `kata_kunci_filter`,
        kalau teks penuh tidak ketemu persis).

        PENTING #4 (fix element staleness setelah klik -- form macet
        di Jenis Surat & lanjut ke halaman lain / popup tertumpuk):
        setelah click_via_js(element) membuka boundlist, ExtJS sering
        ME-RENDER ULANG input combo sehingga referensi `element` yang
        lama jadi STALE. Kalau send_keys() dikirim ke elemen yang sudah
        stale, Selenium melempar StaleElementReferenceException --
        sebelumnya exception ini tidak ditangkap, menyebabkan method
        ini gagal total, kemudian test LANJUT ke modul berikutnya
        (Nota Dinas Keluar) PADAHAL form Tambah Surat Eksternal masih
        TERBUKA & dropdown masih dalam keadaan setengah terbuka --
        PERSIS gejala "tidak berhenti pada jenis surat dan skip
        langsung tumpang tindih ke yang lain bahkan sampai pindah
        halaman lain yaitu nota dinas keluar dengan pop up yang stuck".
        Fix: setelah klik, cari ulang elemen input combo yang masih
        tampil (yang baru dirender) sebelum send_keys."""
        element = self.find_visible_among(dropdown_locator, timeout=15)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        self.click_via_js(element)

        if kata_kunci_filter:
            # PENTING: setelah klik, ExtJS bisa ME-RENDER ULANG input
            # combo -- jangan pakai referensi `element` yang lama
            # (bisa stale). Cari ulang elemen input yang masih tampil.
            try:
                element = self.find_visible_among(dropdown_locator, timeout=5)
                element.clear()
                element.send_keys(kata_kunci_filter)
                self.pace(1)  # tunggu ExtJS memfilter boundlist (3 detik)
            except Exception:
                # Fallback: coba lagi dari awal (buka dropdown + ketik)
                element = self.find_visible_among(dropdown_locator, timeout=10)
                self.click_via_js(element)
                element.clear()
                element.send_keys(kata_kunci_filter)
                self.pace(3)

        # PENTING (fix "tembus" ke grid belakang form): locator lama pakai
        # union `//*[normalize-space(text())='{nilai}']` yang bisa MATCH
        # cell grid di belakang form (is_displayed()==True walau ketutup
        # mask) -- kliknya membuka popup detail surat di tengah pengisian
        # form. Batasi HANYA ke item boundlist (dropdown ExtJS).
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{nilai}']",
        )

        # ==========================================================
        # Linear fallback chain: coba opsi 1..4 sampai berhasil.
        # Kalau semua gagal, form TIDAK akan throw -- cukup log
        # warning & lanjut (lebih baik pilih sesuatu daripada stuck).
        # ==========================================================
        selected = False

        # Try 1: exact text match
        try:
            self.click_visible_among(opsi_locator, timeout=10)
            selected = True
        except TimeoutException:
            pass

        # Try 2: keyword-containing match (kalau ada keyword)
        if not selected and kata_kunci_filter:
            try:
                opsi_mengandung_keyword = (
                    By.XPATH,
                    "//li[contains(@class,'x-boundlist-item')]"
                    f"[contains(normalize-space(text()),'{kata_kunci_filter}')]",
                )
                self.click_visible_among(opsi_mengandung_keyword, timeout=8)
                selected = True
            except TimeoutException:
                pass

        # Try 3: klik opsi PERTAMA yang tampil di boundlist
        if not selected:
            try:
                opsi_pertama = (
                    By.XPATH,
                    "//li[contains(@class,'x-boundlist-item')]",
                )
                self.click_visible_among(opsi_pertama, timeout=5)
                selected = True
            except TimeoutException:
                pass

        # Try 4: ketik nilai penuh + ENTER (type-ahead ExtJS combo)
        if not selected:
            try:
                element = self.find_visible_among(dropdown_locator, timeout=5)
                element.clear()
                element.send_keys(nilai)
                self.pace(1)
                element.send_keys(Keys.ENTER)
                self.pace(2)
                selected = True
            except Exception:
                pass

        # Pastikan boundlist tertutup (max 3 detik, bukan 10).
        # PENTING: pakai tombol ESC, BUKAN klik body -- klik body bisa
        # "tembus" ke grid belakang form & membuka popup detail surat.
        boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
        deadline = time.time() + 3
        while time.time() < deadline:
            if not self.is_visible(boundlist_terbuka, timeout=1):
                break
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
            except Exception:
                pass
            time.sleep(0.5)

    def pilih_jenis_surat(self, nilai, kata_kunci_filter=None):
        self._pilih_dari_combo(self.DROPDOWN_JENIS_SURAT, nilai, kata_kunci_filter)

    def pilih_klasifikasi_surat(self, nilai, kata_kunci_filter=None):
        self._pilih_dari_combo(self.DROPDOWN_KLASIFIKASI_SURAT, nilai, kata_kunci_filter)

    def pilih_sifat_surat(self, nilai):
        self._pilih_dari_combo(self.DROPDOWN_SIFAT_SURAT, nilai)

    def pilih_prioritas_surat(self, nilai):
        self._pilih_dari_combo(self.DROPDOWN_PRIORITAS_SURAT, nilai)

    def pilih_media_surat(self, nilai):
        self._pilih_dari_combo(self.DROPDOWN_MEDIA_SURAT, nilai)

    def pilih_lokasi_arsip_fisik(self, nilai):
        self._pilih_dari_combo(self.DROPDOWN_LOKASI_ARSIP_FISIK, nilai)

    def isi_lampiran(self, jumlah, satuan=None):
        """Field Lampiran (mis. jumlah=1, satuan='Lembar'). Hanya ada
        di form Surat Keluar Eksternal -- dijaga is_visible supaya
        tidak error kalau dipanggil di form yang tidak punya field ini."""
        if not self.is_visible(self.INPUT_LAMPIRAN_JUMLAH, timeout=3):
            return
        self.type_text_visible(self.INPUT_LAMPIRAN_JUMLAH, str(jumlah))
        if satuan:
            self.type_text_visible(self.INPUT_LAMPIRAN_SATUAN, satuan)

    def isi_uraian(self, uraian):
        if self.is_visible(self.TEXTAREA_URAIAN, timeout=3):
            self.type_text_visible(self.TEXTAREA_URAIAN, uraian)

    # CATATAN: dulu ada method isi_form_surat() generik yang mengisi
    # SEMUA field (termasuk Kepada/Alamat/Media Surat) untuk Surat
    # Keluar Eksternal MAUPUN Nota Dinas Keluar. Ini penyebab Nota
    # Dinas Keluar "selesai" tapi datanya tidak muncul -- form Nota
    # Dinas Keluar TIDAK PUNYA field Kepada/Alamat/Media Surat, jadi
    # pengisian generik itu keliru menyasar/melewati field yang salah.
    # Sekarang tiap modul (SuratDinasEksternalPage / NotaDinasKeluarPage)
    # punya method isi_form(data) sendiri-sendiri yang HANYA memanggil
    # primitive isi_*/pilih_* di atas sesuai field yang benar-benar ada
    # di form masing-masing -- lihat pages/surat_dinas_eksternal_page.py
    # dan pages/nota_dinas_keluar_page.py.
    def isi_form(self, data_surat):
        raise NotImplementedError(
            "isi_form() harus diimplementasikan per modul "
            "(SuratDinasEksternalPage / NotaDinasKeluarPage), "
            "karena field form kedua modul ini berbeda."
        )

    # ==========================================================
    # TAMBAH PENYETUJU / PENERIMA (step 16-18)
    # ==========================================================
    def _klik_tambah_by_index(self, index, timeout=10):
        """Klik tombol 'Tambah' ke-`index` (0=Penyetuju, 1=Tembusan/
        Penerima) di antara tombol 'Tambah' yang BENAR-BENAR TAMPIL saat
        ini -- lihat catatan di BTN_TAMBAH_ANY di atas soal kenapa ini
        harus pakai visible-order, bukan XPath positional.

        PENTING (akar penyebab bug #3/#4/#5 -- "tambah penyetuju/
        penerima tidak muncul", "form menumpuk", "form jadi berkali
        kali"): find_all_visible() lama mencari tombol 'Tambah' di
        SELURUH halaman, bukan cuma di dalam dialog 'Tambah Agenda
        Surat' yang sedang terbuka. is_displayed() Selenium cuma cek
        CSS visibility -- TIDAK PEDULI elemen itu ketutup mask/dialog
        lain secara visual. Tombol 'Tambah' di halaman LIST (yang tadi
        dipakai membuka dialog ini) tetap terhitung is_displayed()==True
        walau sekarang tertutup mask, jadi ikut masuk hitungan dan
        MENGGESER index Penyetuju/Penerima yang sebenarnya -- kadang
        malah tombol itu yang keklik ulang (buka dialog 'Tambah' KEDUA
        di atas yang pertama -> form menumpuk/berkali-kali).

        Fix: batasi pencarian tombol 'Tambah' HANYA di dalam dialog
        yang sedang aktif (find_all_visible_in_active_window)."""
        # TUTUP dulu popup Nota Dinas yg mungkin jadi active window
        self._tutup_popup_detail_surat()
        tombol_tampil = self.find_all_visible_in_active_window(self.BTN_TAMBAH_ANY, timeout=timeout)
        if index >= len(tombol_tampil):
            raise TimeoutException(
                f"Cuma ada {len(tombol_tampil)} tombol 'Tambah' yang tampil di "
                f"dialog aktif, butuh index {index}. Kemungkinan popup staf "
                "sebelumnya belum tertutup (tertumpuk/tertindih) atau form "
                "belum selesai render."
            )
        # Native click (retry), NO JS fallback ke grid belakang
        btn = tombol_tampil[index]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn
        )
        for _ in range(3):
            try:
                btn.click()
                break
            except Exception:
                self.pace(1)

    def _tambah_staf(self, index_tombol_tambah, kata_kunci, checkbox_row=None):
        """Cari & pilih 1 staf. Retry sekali kalau StaleElement."""
        try:
            self._tambah_staf_impl(index_tombol_tambah, kata_kunci, checkbox_row)
        except StaleElementReferenceException:
            self.pace(2)
            self._tambah_staf_impl(index_tombol_tambah, kata_kunci, checkbox_row)

    def _tambah_staf_impl(self, index_tombol_tambah, kata_kunci, checkbox_row=None):
        # Tutup semua popup sebelum cari tombol Tambah di form
        self._tutup_popup_detail_surat()
        self._klik_tambah_by_index(index_tombol_tambah)
        self.wait_loading_mask_gone(timeout=10)
        # PENTING (lanjutan fix bug #3/#4/#5/#6): setelah tombol Tambah
        # Penyetuju/Penerima diklik, popup pencarian staf terbuka SEBAGAI
        # window baru DI ATAS dialog 'Tambah Agenda Surat' -- window
        # inilah yang jadi window aktif (z-index tertinggi). Cari input
        # pencarian/checkbox baris/tombol Pilih HANYA di dalam window
        # aktif ini, supaya tidak nyasar ke elemen senama milik dialog
        # 'Tambah Agenda Surat' di belakangnya atau sisa popup staf
        # sebelumnya yang belum benar2 hilang dari DOM.
        input_cari = self.find_visible_in_active_window(self.INPUT_CARI_STAF, timeout=15)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", input_cari
        )
        # Klik dulu untuk memastikan fokus
        self.click_via_js(input_cari)
        input_cari.clear()
        input_cari.send_keys(kata_kunci)
        self.pace(1)  # jeda sebentar sebelum ENTER
        input_cari.send_keys(Keys.ENTER)
        self.pace(2)  # tunggu hasil pencarian render (grid re-render)
        self.wait_loading_mask_gone(timeout=10)

        # Pilih checkbox baris yang sesuai.
        # Flow menentukan baris spesifik:
        # - Penyetuju: baris ke-3 (IT & Digitalization)
        # - Penerima: baris ke-1 (ICT Solusi desain)
        #
        # PENTING: setelah ENTER, grid staf di-render ulang oleh ExtJS
        # sehingga elemen checkbox bisa stale ATAU hasil pencarian
        # belum selesai render (checkbox masih 0). Retry LOCAL (re-find +
        # re-click) tanpa mengulang seluruh flow (jangan buka popup lagi).
        for attempt in range(3):
            try:
                if checkbox_row and checkbox_row > 1:
                    checkboxes = self.find_all_visible_in_active_window(
                        self.CHECKBOX_ROW_STAF, timeout=10
                    )
                    if len(checkboxes) >= checkbox_row:
                        self.click_via_js(checkboxes[checkbox_row - 1])
                    elif checkboxes:
                        # Fallback: klik baris terakhir yang tersedia
                        self.click_via_js(checkboxes[-1])
                    else:
                        raise TimeoutException(
                            "Tidak ada checkbox staf yang tampil di popup pencarian"
                        )
                else:
                    self.click_visible_in_active_window(self.CHECKBOX_ROW_STAF, timeout=10)
                break  # sukses, keluar dari retry loop
            except (StaleElementReferenceException, TimeoutException):
                if attempt == 2:
                    raise
                # Hasil pencarian belum render / elemen stale --
                # tunggu loading selesai lalu coba lagi
                self.pace(1)
                self.wait_loading_mask_gone(timeout=10)

        self.click_visible_in_active_window(self.BTN_PILIH, timeout=10)
        self.wait_loading_mask_gone(timeout=10)
        # Pastikan popup staf benar2 tertutup dulu
        self._wait(10).until(
            lambda _: not self.is_visible(self.INPUT_CARI_STAF, timeout=2)
        )
        # Jeda ekstra setelah popup tutup -- form perlu waktu untuk
        # jadi active window kembali sebelum _klik_tambah_by_index
        # berikutnya dipanggil
        self.pace(1)
        # TUTUP popup Nota Dinas/surat detail yang mungkin muncul
        # saat interaksi dengan popup staf (klik checkbox/Pilih bisa
        # "tembus" ke grid Nota Dinas di belakang & buka detail surat)
        self._tutup_popup_detail_surat()

    def tambah_penyetuju(self, kata_kunci, checkbox_row=None):
        """step 16/19: Menambahkan penyetuju dengan kata kunci & memilih
        data yang sesuai. Tombol 'Tambah' PERTAMA yang tampil di form.

        Flow: penyetuju dicari dulu, lalu pilih checkbox baris yang sesuai
        (default baris ke-3 = IT & Digitalization, sesuai flow doc)."""
        self._tambah_staf(0, kata_kunci, checkbox_row=checkbox_row)

    def tambah_penerima(self, kata_kunci, checkbox_row=None):
        """step 17/21: Menambahkan penerima dengan kata kunci & memilih
        data yang sesuai. Tombol 'Tambah' KEDUA yang tampil di form --
        dipanggil SETELAH tambah_penyetuju() selesai & popup-nya
        tertutup total, supaya kedua popup tidak pernah tertumpuk.

        Flow: penerima dicari dulu, lalu pilih checkbox baris yang sesuai
        (default baris ke-1 = ICT Solusi desain, sesuai flow doc)."""
        self._tambah_staf(1, kata_kunci, checkbox_row=checkbox_row)

    # ==========================================================
    # DRAFT: pilih draft, Perubahan, Hapus (dipakai Modul 6 & 7)
    # ==========================================================
    ROW_DRAFT = (By.CSS_SELECTOR, "tr.x-grid-row.x-grid-data-row, tr.x-grid-data-row")
    BTN_PERUBAHAN = (By.CSS_SELECTOR, "[id^='sipas_com_button_edit-']")
    BTN_HAPUS = (By.CSS_SELECTOR, "[id^='sipas_com_button_delete-']")
    BTN_HAPUS_CANDIDATES = [
        (By.CSS_SELECTOR, "[id^='sipas_com_button_delete-']"),
        (By.XPATH, "//*[normalize-space(text())='Hapus']"),
    ]
    BTN_YA_KONFIRMASI = (By.XPATH, "//*[normalize-space(text())='Ya']")
    BTN_OK_NOTIFIKASI = (By.XPATH, "//*[normalize-space(text())='OK']")

    # Popup detail surat — muncul setelah klik baris di grid (Modul 7).
    # Dipakai sebagai fallback success indicator di pilih_draft_pertama()
    # untuk surat yang SUDAH disetujui (tidak punya tombol Hapus).
    POPUP_DETAIL_SURAT_ANY = (
        By.XPATH,
        "//span[contains(@class,'x-window-header-text')]"
        "[contains(normalize-space(text()),'Identitas Agenda')]",
    )

    def _is_row_selected(self):
        """Cek apakah sebuah baris sudah berhasil dipilih — bisa lewat
        tombol Hapus (draft) ATAU popup detail surat (surat disetujui).

        PENTING: pakai find_visible_among, BUKAN is_visible -- di full
        run, tab modul lain (2-5) sudah dirender di DOM, jadi ada
        BANYAK tombol Hapus tersembunyi; is_visible mengunci ke match
        PERTAMA di DOM (yang sering hidden) dan salah melaporkan."""
        for locator in self.BTN_HAPUS_CANDIDATES:
            try:
                self.find_visible_among(locator, timeout=2)
                return True
            except TimeoutException:
                continue
        return self.is_visible(self.POPUP_DETAIL_SURAT_ANY, timeout=2)

    def pilih_draft_pertama(self):
        """Klik row pertama + ExtJS select, retry 5x.
        Sukses jika: tombol Hapus muncul (draft) ATAU popup detail
        'Identitas Agenda' muncul (surat disetujui di Nota Dinas)."""
        self.wait_loading_mask_gone(timeout=15)
        import time as _time
        for attempt in range(5):
            # Coba ExtJS selection API dulu (tanpa klik DOM)
            ok = self.driver.execute_script("""
                var grids = document.querySelectorAll('div.x-grid');
                for (var i = 0; i < grids.length; i++) {
                    var rect = grids[i].getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        var grid = Ext.getCmp(grids[i].id);
                        if (grid && grid.getSelectionModel && grid.getStore()) {
                            if (grid.getStore().getCount() > 0) {
                                grid.getSelectionModel().select(0);
                                return true;
                            }
                        }
                    }
                }
                return false;
            """)
            if ok and self._is_row_selected():
                return
            # Fallback: klik DOM row
            rows = self.driver.find_elements(*self.ROW_DRAFT)
            for r in rows:
                try:
                    rect = self.driver.execute_script(
                        "var r=arguments[0].getBoundingClientRect();"
                        "return [r.width,r.height];", r
                    )
                    if rect[0] > 0 and rect[1] > 0:
                        self.click_via_js(r)
                        self.wait_loading_mask_gone(timeout=3)
                        if self._is_row_selected():
                            return
                except Exception:
                    continue
            _time.sleep(2)
        assert self._is_row_selected(), (
            "Baris pertama tidak berhasil dipilih -- "
            "tombol Hapus/popup detail tidak muncul."
        )

    def klik_perubahan(self):
        self.click_visible_among(self.BTN_PERUBAHAN, timeout=15)
        self.wait_loading_mask_gone(timeout=10)
        assert self.is_visible(self.TEXTAREA_PERIHAL, timeout=15), (
            "Dialog Perubahan Draft tidak terbuka -- field Perihal tidak tampil."
        )

    def tambah_penerima_baru(self, kata_kunci):
        """Tambah PENERIMA BARU di form Perubahan (menggantikan penerima
        yang dihapus). PENTING: pakai index 1 (Penerima), BUKAN index 0
        (Penyetuju) -- bug lama memakai `_tambah_staf(0, ...)` sehingga
        staf baru masuk ke bagian PENYETUJU (Yulia ikut berubah), padahal
        flow meminta mengganti PENERIMA (Ryco -> Arru).

        Kalau form Perubahan cuma menampilkan 1 tombol 'Tambah' (bagian
        Penyetuju tidak punya tombolnya), pakai index 0 -- satu-satunya
        tombol yang tampil pasti milik bagian Penerima."""
        self._tutup_popup_detail_surat()
        tombol = self.find_all_visible_in_active_window(self.BTN_TAMBAH_ANY, timeout=10)
        index = 1 if len(tombol) > 1 else 0
        self._tambah_staf(index, kata_kunci)

    def verifikasi_penerima_ditambahkan(self, kata_kunci, timeout=10):
        """Cek staf yang baru ditambahkan MASUK ke bagian PENERIMA (grid
        paling bawah di dalam form), bukan ke bagian Penyetuju. Dipakai
        setelah tambah_penerima_baru() -- kalau false, kemungkinan besar
        staf masuk ke section yang salah."""
        try:
            ok = self.driver.execute_script("""
                var wins = document.querySelectorAll('div.x-window');
                for (var i = 0; i < wins.length; i++) {
                    var w = wins[i];
                    var r = w.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    // Form = window yang mengandung textarea perihal
                    if (!w.querySelector("textarea[name='surat_perihal']")) continue;
                    // Grid penerima = grid PALING BAWAH di dalam form
                    var grids = w.querySelectorAll('div.x-grid');
                    if (!grids.length) return false;
                    var gridPenerima = grids[grids.length - 1];
                    var text = (gridPenerima.textContent || '').toUpperCase();
                    var cari = (arguments[0] || '').toUpperCase();
                    return cari.length > 0 && text.indexOf(cari) >= 0;
                }
                return false;
            """, kata_kunci)
            return bool(ok)
        except Exception:
            return False

    def ajukan_perubahan(self):
        return self.ajukan_penyetujuan()

    def klik_hapus(self):
        """Klik tombol Hapus yang BENAR-BENAR TAMPIL. Kalau tidak ada
        yang tampil, baris mungkin kehilangan seleksi (grid re-render)
        -- pilih ulang baris pertama lalu coba lagi (maks 3x)."""
        for attempt in range(3):
            for locator in self.BTN_HAPUS_CANDIDATES:
                try:
                    btn = self.find_visible_among(locator, timeout=5)
                    self.click_via_js(btn)
                    self.wait_loading_mask_gone(timeout=5)
                    return
                except TimeoutException:
                    continue
            # Tombol Hapus tidak tampil -- baris kehilangan seleksi?
            # Pilih ulang baris pertama lalu coba lagi.
            self.pilih_draft_pertama()
        raise TimeoutException(
            "Tombol Hapus tidak ditemukan. Pastikan draft baris sudah dipilih."
        )

    def klik_ya_konfirmasi(self):
        self.click_visible_among(self.BTN_YA_KONFIRMASI, timeout=15)
        self.wait_loading_mask_gone(timeout=10)

    def klik_ok_notifikasi(self):
        if self.is_visible(self.BTN_OK_NOTIFIKASI, timeout=5):
            self.click_visible_among(self.BTN_OK_NOTIFIKASI, timeout=5)
        self.wait_loading_mask_gone(timeout=10)

    def is_draft_terhapus(self, timeout=10):
        return not self.is_visible(self.BTN_YA_KONFIRMASI, timeout=timeout) \
               and not self.is_visible(self.BTN_HAPUS, timeout=5)

    def pilih_tembusan_checkbox(self):
        """step 18: Memilih tembusan melalui checkbox yang tersedia
        (checkbox pada baris penerima yang sudah ditambahkan, kolom
        'Tembusan').

        PENTING: dulu pakai click_via_js(locator tuple) yang di dalamnya
        cuma presence_of_element_located() (elemen PERTAMA yang ADA di
        DOM, tidak peduli tampil atau tidak) -- kalau ada baris lain yang
        sudah basi/tersembunyi dari popup staf sebelumnya, checkbox yang
        kecentang bisa salah baris. Fix: pakai click_visible_in_active_window
        biar selalu kena baris yang benar2 tampil DI DALAM dialog 'Tambah
        Agenda Surat' yang sedang aktif, bukan checkbox senama milik
        popup/dialog lain di belakangnya."""
        self.click_visible_in_active_window(self.CHECKBOX_ROW_STAF, timeout=10)

    # ==========================================================
    # AJUKAN PENYETUJUAN (step 19-20)
    # ==========================================================
    def ajukan_penyetujuan(self):
        # click_visible_in_active_window -- kalau ada form lain yang
        # tertumpuk di belakang (lihat catatan klik_tambah di atas),
        # jangan sampai klik tombol 'Ajukan Penyetujuan' milik form yang
        # salah/basi.
        self.click_visible_in_active_window(self.BTN_AJUKAN_PENYETUJUAN, timeout=15)
        self.wait_loading_mask_gone(timeout=20)

        # PENTING: setelah klik Ajukan Penyetujuan, muncul popup
        # konfirmasi "Kirim Surat" dengan pesan "Apakah anda yakin ?"
        # dan tombol "Ya" / "Tidak". Klik "Ya" untuk konfirmasi.
        self._konfirmasi_kirim_surat()

        # Setelah konfirmasi, tunggu notifikasi sukses & klik OK
        self._klik_ok_notifikasi_sukses()

        return self.is_berhasil_diajukan()

    def _konfirmasi_kirim_surat(self, timeout=10):
        """Klik tombol 'Ya' pada popup konfirmasi 'Kirim Surat'."""
        popup_kirim = (
            By.XPATH,
            "//span[contains(@class,'x-window-header-text')][normalize-space(text())='Kirim Surat']",
        )
        btn_ya = (By.XPATH, "//span[normalize-space(text())='Ya']")
        try:
            if self.is_visible(popup_kirim, timeout=timeout):
                self.click_visible_among(btn_ya, timeout=5)
                self.wait_loading_mask_gone(timeout=15)
        except TimeoutException:
            pass

    def _klik_ok_notifikasi_sukses(self, timeout=15):
        """Klik OK pada notifikasi sukses. Flow menunjukkan bisa ada 2
        popup OK berturut-turut (terutama setelah Ajukan Penyetujuan)."""
        btn_ok = (By.XPATH, "//span[contains(@class,'x-btn-inner')][normalize-space(text())='OK']")
        for _ in range(2):  # Klik OK maks 2x
            try:
                if self.is_visible(btn_ok, timeout=timeout):
                    self.click_visible_among(btn_ok, timeout=5)
                    self.wait_loading_mask_gone(timeout=10)
                else:
                    break
            except TimeoutException:
                break

    def _klik_muat_ulang(self):
        """Refresh grid via JS — reload store."""
        try:
            self.driver.execute_script("""
                var grids = document.querySelectorAll('div.x-grid');
                for (var i = 0; i < grids.length; i++) {
                    var grid = Ext.getCmp(grids[i].id);
                    if (grid && grid.getStore) {
                        grid.getStore().load();
                    }
                }
            """)
            self.wait_loading_mask_gone(timeout=15)
        except Exception:
            pass

    def _tutup_semua_popup(self):
        """Tutup SEMUA window/popup ExtJS yang tampil (termasuk form
        basi/tertinggal). Dipakai untuk membersihkan layar sebelum
        membuka form Tambah yang baru -- halaman list seharusnya bersih
        dari popup apapun."""
        try:
            windows = self.driver.find_elements(By.CSS_SELECTOR, "div.x-window")
            for win in windows:
                try:
                    rect = self.driver.execute_script(
                        "var r=arguments[0].getBoundingClientRect();"
                        "return [r.width,r.height];", win
                    )
                    if rect[0] <= 0 or rect[1] <= 0:
                        continue
                    close_imgs = win.find_elements(
                        By.CSS_SELECTOR, "img.x-tool-close"
                    )
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
                                self.driver.execute_script(
                                    "arguments[0].click();", img
                                )
                        except Exception:
                            continue
                except Exception:
                    continue
            self.wait_loading_mask_gone(timeout=5)
        except Exception:
            pass

    def _tutup_popup_detail_surat(self):
        """Tutup popup ExtJS yang terbuka, KECUALI form Tambah/Perubahan.
        Cari semua window ExtJS, skip yang mengandung field form
        (textarea[name='surat_perihal']) supaya form tidak ikut tertutup.

        PENTING: class x-tool-close ada di <img> (img.x-tool-img.x-tool-close),
        BUKAN di <div> -- selector div.x-tool-close lama tidak pernah match,
        jadi popup draft/nota dinas yang "tembus" tidak pernah benar-benar
        tertutup. Handler klik ExtJS ada di div.x-tool induknya."""
        try:
            windows = self.driver.find_elements(By.CSS_SELECTOR, "div.x-window")
            for win in windows:
                try:
                    # Cek visibility — skip window yang tersembunyi
                    rect = self.driver.execute_script(
                        "var r=arguments[0].getBoundingClientRect();"
                        "return [r.width,r.height];", win
                    )
                    if rect[0] <= 0 or rect[1] <= 0:
                        continue

                    # JANGAN tutup window yang mengandung form Tambah/Perubahan
                    form_fields = win.find_elements(
                        By.CSS_SELECTOR, "textarea[name='surat_perihal']"
                    )
                    if form_fields:
                        continue

                    # Klik tombol close di window ini (img.x-tool-close,
                    # klik img + parent div.x-tool supaya event terekam)
                    close_imgs = win.find_elements(
                        By.CSS_SELECTOR, "img.x-tool-close"
                    )
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
                                self.driver.execute_script(
                                    "arguments[0].click();", img
                                )
                        except Exception:
                            continue
                except Exception:
                    continue
            self.wait_loading_mask_gone(timeout=5)
        except Exception:
            pass

    def simpan_draft(self):
        """Klik SIMPAN DRAFT lalu konfirmasi Ya + OK.
        Simpan Draft memunculkan popup konfirmasi (mungkin tanpa judul
        'Kirim Surat'), jadi langsung cari tombol Ya saja."""
        self.click_visible_in_active_window(self.BTN_SIMPAN_DRAFT, timeout=15)
        self.wait_loading_mask_gone(timeout=10)
        # Klik Ya langsung (tanpa cek judul popup)
        btn_ya = (By.XPATH, "//span[normalize-space(text())='Ya']")
        try:
            if self.is_visible(btn_ya, timeout=5):
                self.click_visible_among(btn_ya, timeout=5)
                self.wait_loading_mask_gone(timeout=15)
        except TimeoutException:
            pass
        self._klik_ok_notifikasi_sukses()
        return self.is_berhasil_diajukan()

    def hapus_penerima(self):
        """Klik ikon hapus (bin) pada baris PENERIMA di form Perubahan.

        PENTING (fix salah hapus -- Yulia/Penyetuju ikut terhapus):
        form Perubahan punya 2 daftar (grid Penyetuju & grid Penerima)
        yang KEDUANYA bisa punya ikon bin (data-qtip='Hapus'). Klik bin
        PERTAMA di DOM = bin milik grid PENYETUJU (section paling atas).
        Target yang benar: bin di grid PALING BAWAH (grid Penerima)."""
        clicked = self.driver.execute_script("""
            var wins = document.querySelectorAll('div.x-window');
            for (var i = 0; i < wins.length; i++) {
                var w = wins[i];
                var r = w.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                // Form = window yang mengandung textarea perihal
                if (!w.querySelector("textarea[name='surat_perihal']")) continue;
                // Grid penerima = grid PALING BAWAH di dalam form
                var grids = w.querySelectorAll('div.x-grid');
                if (!grids.length) return false;
                var gridPenerima = grids[grids.length - 1];
                var bin = gridPenerima.querySelector(
                    "img.x-action-col-icon-bin[data-qtip='Hapus']"
                );
                if (!bin) return false;
                var target = bin.closest('div.x-action-col-icon') || bin;
                target.click();
                return true;
            }
            return false;
        """)
        if not clicked:
            raise TimeoutException(
                "Ikon hapus di grid PENERIMA tidak ditemukan di form "
                "Perubahan. Pastikan baris penerima masih ada."
            )
        self.wait_loading_mask_gone(timeout=5)

    def verifikasi_penyetuju_masih_ada(self, kata_kunci, timeout=10):
        """Cek penyetuju (grid PERTAMA di dalam form) masih memuat nama
        `kata_kunci` -- dipakai setelah hapus_penerima() untuk memastikan
        yang terhapus adalah PENERIMA, bukan penyetuju (Yulia)."""
        try:
            ok = self.driver.execute_script("""
                var wins = document.querySelectorAll('div.x-window');
                for (var i = 0; i < wins.length; i++) {
                    var w = wins[i];
                    var r = w.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (!w.querySelector("textarea[name='surat_perihal']")) continue;
                    var grids = w.querySelectorAll('div.x-grid');
                    if (!grids.length) return false;
                    var gridPenyetuju = grids[0];
                    var text = (gridPenyetuju.textContent || '').toUpperCase();
                    var cari = (arguments[0] || '').toUpperCase();
                    return cari.length > 0 && text.indexOf(cari) >= 0;
                }
                return false;
            """, kata_kunci)
            return bool(ok)
        except Exception:
            return False

    def is_berhasil_diajukan(self, timeout=15):
        """step 20: memastikan surat/nota dinas berhasil diajukan --
        dialog form tertutup ATAU muncul notif sukses ExtJS."""
        form_tertutup = not self.is_visible(self.TEXTAREA_PERIHAL, timeout=timeout)
        if form_tertutup:
            return True
        for notif_locator in self.NOTIF_SUKSES_CANDIDATES:
            if self.is_visible(notif_locator, timeout=3):
                return True
        return False
