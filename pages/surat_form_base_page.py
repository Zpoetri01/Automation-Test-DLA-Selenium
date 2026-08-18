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

    # -------------------- OVERRIDE DROPDOWN POSISI (Modul 6 & 7) --------------------
    # Modul 6 & 7 tidak menampilkan teks "Primary Position"/"Secondary
    # Position"/"Semua" di dropdown Posisi -- yang tampil JABATAN ASLI
    # user. Locator parent (by-value) tidak pernah match, jadi combo
    # dibuka lewat TRIGGER ARROW pertama di toolbar atas.
    DROPDOWN_FILTER_POSISI = (
        By.CSS_SELECTOR,
        "div.x-toolbar input.x-form-text[readonly]",
    )

    # Trigger arrow combo posisi di toolbar yang sama dengan input combo.
    TRIGGER_POSISI = (
        By.CSS_SELECTOR,
        "div.x-toolbar a.x-form-arrow-trigger, "
        "div.x-toolbar div.x-form-trigger, "
        "div.x-toolbar a.x-form-trigger",
    )

    def klik_dropdown_posisi(self):
        """Override Modul 6 & 7: klik TRIGGER arrow combo Posisi (event
        handler ExtJS ada di trigger, bukan di input readonly)."""
        try:
            trigger = self.find_visible_among(self.TRIGGER_POSISI, timeout=10)
            self.click_via_js(trigger)
            self.pace(2)
            boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
            if self.is_visible(boundlist_terbuka, timeout=3):
                return
        except Exception:
            pass
        # Fallback: klik input combo langsung (cara lama)
        try:
            element = self.find_visible_among(self.DROPDOWN_FILTER_POSISI, timeout=10)
            self.click_via_js(element)
            self.pace(2)
        except Exception:
            # Fallback terakhir: klik combo pertama yang tampil di halaman
            combos = self.find_all_visible(
                (By.CSS_SELECTOR, "input.x-form-text[readonly]"), timeout=10
            )
            if combos:
                self.click_via_js(combos[0])
                self.pace(2)

    # ---------------------------- TOMBOL TAMBAH (buka form) ----------------------------
    # id ExtJS random, dicocokkan lewat prefix stabil "sipas_com_button_add-".
    BTN_TAMBAH = (By.CSS_SELECTOR, "[id^='sipas_com_button_add-']")

    # ------------------------------ UPLOAD BERKAS VIA LINK ------------------------------
    # Ikon "+" untuk membuka menu pilihan upload berkas (Link/File).
    BTN_TAMBAH_BERKAS = (By.CSS_SELECTOR, "span.ion-md-add-circle")

    MENU_ITEM_LINK = (By.XPATH, "//span[normalize-space(text())='Link']")

    # Field di dalam popup "Link": Tentang (nama) & Perihal (url).
    INPUT_DOKUMEN_NAMA = (By.CSS_SELECTOR, "input[name='dokumen_nama']")
    INPUT_DOKUMEN_LINK = (By.CSS_SELECTOR, "input[name='dokumen_file']")
    BTN_SIMPAN_LINK = (By.XPATH, "//span[normalize-space(text())='SIMPAN' or normalize-space(text())='Simpan']")

    # Chip berkas di panel kiri "Berkas" (muncul setelah upload sukses).
    ARCHIVE_ITEM_LOCATOR = (By.CSS_SELECTOR, "div.sipas_archive div.image-wrap")

    # ------------------------- FORM SURAT (name dari HTML asli) -------------------------
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

    # Lampiran: hanya ada di form Surat Keluar Eksternal.
    INPUT_LAMPIRAN_JUMLAH = (By.CSS_SELECTOR, "input[name='surat_lampiran']")
    INPUT_LAMPIRAN_SATUAN = (By.CSS_SELECTOR, "input[name='surat_lampiran_sub']")

    # Uraian: ada di kedua form.
    TEXTAREA_URAIAN = (By.CSS_SELECTOR, "textarea[name='surat_keterangan']")

    # ------------------------------ PENYETUJU / PENERIMA ------------------------------
    # Tombol 'Tambah' pertama yang TAMPIL = Penyetuju, kedua = Penerima.
    # Dicari lewat find_all_visible() (urutan TAMPIL, bukan urutan DOM) supaya
    # sisa popup staf lama yang masih basi di DOM tidak menggeser index.
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

    # -------------------------- TOMBOL TAMBAH -> BUKA FORM (step 12) --------------------------
    def klik_tambah(self):
        """Buka form Tambah. Guard anti-tumpang-tindih: pastikan TIDAK ada
        form Tambah yang masih terbuka, tunggu grid selesai reload, klik
        tombol Tambah yang benar2 TAMPIL (bukan yang hidden milik modul
        lain), retry maks 3x kalau klik tidak terekam."""
        # Bersihkan layar DULU: tutup SEMUA popup yang tersisa.
        self._tutup_semua_popup()
        assert not self.is_visible(self.TEXTAREA_PERIHAL, timeout=2), (
            "Ada form 'Tambah Agenda Surat' yang masih terbuka dari langkah "
            "sebelumnya -- tidak boleh buka form baru di atasnya (akan "
            "tertumpuk-tindih). Pastikan form sebelumnya sudah benar-benar "
            "selesai/tertutup (ajukan_penyetujuan() sukses) sebelum "
            "klik_tambah() dipanggil lagi."
        )
        # Tunggu grid selesai reload setelah filter.
        self.wait_loading_mask_gone(timeout=15)
        # Klik tombol Tambah yang visible -- jangan fallback ke find()
        # karena bisa nyasar ke tombol Tambah milik modul LAIN yang hidden.
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

    # ------------------------ UPLOAD BERKAS VIA LINK (step 13-14) ------------------------
    def upload_berkas_via_link(self, url_dokumen, nama_dokumen=None):
        """Isi link dokumen lalu verifikasi chip berkas muncul di panel
        kiri. Proses server ("Menyiapkan Surat") bisa lambat/macet --
        kalau chip tak muncul: dismiss dialog proses (OK), cek chip lagi,
        lalu ulang SELURUH alur upload maks 2x sebelum menyerah."""
        for percobaan in range(2):
            if percobaan > 0:
                print(f"    [debug upload] percobaan ulang ke-{percobaan}")
                self._tutup_popup_detail_surat()
                self.pace(5)
            self.click_visible_among(self.BTN_TAMBAH_BERKAS, timeout=15)
            self.click_visible_among(self.MENU_ITEM_LINK, timeout=10)
            if nama_dokumen:
                self.type_text_visible(self.INPUT_DOKUMEN_NAMA, nama_dokumen)
            self.type_text_visible(self.INPUT_DOKUMEN_LINK, url_dokumen)
            # Klik SIMPAN + pastikan popup Link benar2 tertutup. Kalau popup
            # masih terbuka (klik nyasar / event belum terekam), klik ulang
            # maks 3x.
            for _ in range(3):
                self.click_visible_among(self.BTN_SIMPAN_LINK, timeout=10)
                self.wait_loading_mask_gone(timeout=10)
                try:
                    self.find_visible_in_active_window(self.INPUT_DOKUMEN_LINK, timeout=3)
                except TimeoutException:
                    break  # input popup Link tidak tampil lagi = SIMPAN terekam
            # Tunggu chip berkas -- cek tiap 0,5 detik, selesai BEGITU chip
            # muncul (bukan jeda mati; kalau server cepat, lanjut dalam
            # hitungan detik). Batas 20 detik utk server yang agak lambat.
            if self.is_berkas_terunggah(timeout=20):
                break
            # Proses macet -- dismiss dialog proses (klik OK kalau tampil)
            # lalu cek chip sekali lagi sebelum ulang dari awal
            try:
                self.click_visible_among(self.BTN_OK_NOTIFIKASI, timeout=3)
                self.wait_loading_mask_gone(timeout=10)
            except TimeoutException:
                pass
            if self.is_berkas_terunggah(timeout=10):
                break
        assert self.is_berkas_terunggah(timeout=10), \
            "Berkas via Link tidak berhasil diunggah (chip tidak muncul)"
        # Pastikan dialog proses benar2 tertutup sebelum isi form
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                self.find_visible_among(self.POPUP_MENYIAPKAN_SURAT, timeout=3)
                self.pace(2)  # dialog proses masih menutup -- tunggu
            except TimeoutException:
                break

    def is_berkas_terunggah(self, timeout=20):
        """Verifikasi chip berkas muncul di panel 'Berkas' DI DALAM form
        yang sedang aktif. (is_visible() mengunci ke match PERTAMA di DOM
        yang bisa sisa panel hidden dari popup lama -- false negative di
        draft kedua; fallback cari yang tampil di seluruh halaman.)"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                ditemukan = self.driver.execute_script("""
                    var wins = document.querySelectorAll('div.x-window');
                    for (var i = 0; i < wins.length; i++) {
                        var w = wins[i];
                        var r = w.getBoundingClientRect();
                        if (r.width <= 0 || r.height <= 0) continue;
                        if (!w.querySelector("textarea[name='surat_perihal']")) continue;
                        var chip = w.querySelector("div.sipas_archive div.image-wrap");
                        if (chip) {
                            var c = chip.getBoundingClientRect();
                            if (c.width > 0 && c.height > 0) return true;
                        }
                    }
                    return false;
                """)
                if ditemukan:
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        # Fallback: form bukan window sendiri / struktur beda
        try:
            self.find_visible_among(self.ARCHIVE_ITEM_LOCATOR, timeout=3)
            return True
        except TimeoutException:
            return False

    # ------------------------------- ISI FORM (step 15) -------------------------------
    def isi_kepada(self, kepada, timeout=10):
        # type_text_visible -- kalau ada 2 form tertumpuk, pastikan yang
        # keisi instance yang benar2 tampil, bukan yang basi di belakang.
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
        """Pilih opsi dropdown ExtJS. Penting:
        1. Klik elemen yang benar2 TAMPIL (field duplikat hidden milik
           Advanced Filter punya name IDENTIK).
        2. Scroll ke tengah viewport DULU (container form di-scroll manual).
        3. Boundlist besar di-render buffered -- ketik keyword dulu supaya
           opsi yang cocok ter-render, baru klik (fallback: keyword-
           containing -> opsi pertama -> ketik penuh + ENTER).
        4. Tutup boundlist dengan ESC (klik body bisa "tembus" ke grid)."""
        element = self.find_visible_among(dropdown_locator, timeout=15)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        self.click_via_js(element)

        if kata_kunci_filter:
            # Setelah klik, ExtJS bisa re-render input combo -- cari ulang
            # elemen yang masih tampil sebelum send_keys (hindari stale).
            try:
                element = self.find_visible_among(dropdown_locator, timeout=5)
                element.clear()
                element.send_keys(kata_kunci_filter)
                self.pace(2)  # tunggu ExtJS memfilter boundlist
            except Exception:
                # Fallback: coba lagi dari awal (buka dropdown + ketik)
                element = self.find_visible_among(dropdown_locator, timeout=10)
                self.click_via_js(element)
                element.clear()
                element.send_keys(kata_kunci_filter)
                self.pace(3)

        # HANYA item boundlist -- union //*[text()=...] bisa match cell
        # grid di belakang form & membuka popup detail surat.
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{nilai}']",
        )

        # Fallback chain: exact text -> keyword-containing -> opsi pertama
        # -> ketik nilai penuh + ENTER. Tidak throw -- lebih baik pilih
        # sesuatu daripada stuck.
        selected = False

        try:
            self.click_visible_among(opsi_locator, timeout=10)
            selected = True
        except TimeoutException:
            pass

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

        if not selected:
            try:
                element = self.find_visible_among(dropdown_locator, timeout=5)
                element.clear()
                element.send_keys(nilai)
                self.pace(2)
                element.send_keys(Keys.ENTER)
                self.pace(2)
                selected = True
            except Exception:
                pass

        # Pastikan boundlist tertutup (max 3 detik). Pakai ESC, BUKAN klik
        # body -- klik body bisa "tembus" ke grid belakang form.
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
        """Field Lampiran (hanya ada di form Surat Keluar Eksternal)."""
        if not self.is_visible(self.INPUT_LAMPIRAN_JUMLAH, timeout=3):
            return
        self.type_text_visible(self.INPUT_LAMPIRAN_JUMLAH, str(jumlah))
        if satuan:
            self.type_text_visible(self.INPUT_LAMPIRAN_SATUAN, satuan)

    def isi_uraian(self, uraian):
        if self.is_visible(self.TEXTAREA_URAIAN, timeout=3):
            self.type_text_visible(self.TEXTAREA_URAIAN, uraian)

    # isi_form() diimplementasikan per modul karena field form keduanya
    # berbeda (SuratDinasEksternalPage / NotaDinasKeluarPage).
    def isi_form(self, data_surat):
        raise NotImplementedError(
            "isi_form() harus diimplementasikan per modul "
            "(SuratDinasEksternalPage / NotaDinasKeluarPage), "
            "karena field form kedua modul ini berbeda."
        )

    # ---------------------- TAMBAH PENYETUJU / PENERIMA (step 16-18) ----------------------
    def _is_popup_staf_terbuka(self, timeout=2):
        """True kalau popup pencarian staf masih jadi window AKTIF.
        Penandanya tombol PILIH (putin-) -- unik milik popup staf. JANGAN
        pakai input[type='search']: halaman list di belakang form juga
        punya search input sendiri yang selalu tampil, dan cek first-match
        di full run nyasar ke input hidden milik tab modul lain."""
        try:
            self.find_visible_in_active_window(self.BTN_PILIH, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def _tutup_popup_staf(self):
        """Tutup popup pencarian staf kalau masih terbuka. Klik Batal/Tutup
        dijalankan HANYA kalau window aktif masih memuat tombol PILIH
        (popup staf) -- aman dari salah klik Batal milik form."""
        if not self._is_popup_staf_terbuka(timeout=1):
            return
        self._tutup_popup_detail_surat()
        if not self._is_popup_staf_terbuka(timeout=2):
            return
        for teks in ("Batal", "Tutup"):
            try:
                self.click_visible_in_active_window(
                    (By.XPATH, f"//*[normalize-space(text())='{teks}']"), timeout=2
                )
                self.pace(2)
                break
            except TimeoutException:
                continue
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
        except Exception:
            pass

    def _tambah_buttons_di_form(self):
        """Tombol 'Tambah' yang tampil DI DALAM window form -- window yang
        memuat textarea[name='surat_perihal']. Tidak peduli window apa yang
        sedang teratas/aktif: di full run window teratas bisa popup staf /
        popup lain yang belum tertutup, bikin hitungan tombol 'Tambah'
        bergeser kalau dihitung dari window aktif."""
        try:
            return self.driver.execute_script("""
                var wins = document.querySelectorAll('div.x-window');
                for (var i = 0; i < wins.length; i++) {
                    var w = wins[i];
                    var r = w.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (!w.querySelector("textarea[name='surat_perihal']")) continue;
                    var btns = [];
                    var all = w.querySelectorAll('*');
                    for (var j = 0; j < all.length; j++) {
                        var t = (all[j].childNodes.length === 1
                            && all[j].firstChild
                            && all[j].firstChild.nodeType === 3)
                            ? all[j].textContent.trim().toUpperCase() : '';
                        if (t === 'TAMBAH') {
                            var rr = all[j].getBoundingClientRect();
                            if (rr.width > 0 && rr.height > 0) btns.push(all[j]);
                        }
                    }
                    return btns;
                }
                return [];
            """)
        except Exception:
            return []

    def _klik_tambah_by_index(self, index, timeout=10):
        """Klik tombol 'Tambah' ke-`index` (0=Penyetuju, 1=Penerima) di
        dalam WINDOW FORM. Di full run popup staf (mis. Penyetuju) menutup
        lebih lambat -- kalau tombol ke-index belum tampil, bersihkan
        popup staf & cari ulang sampai timeout, JANGAN langsung gagal."""
        # TUTUP dulu popup Nota Dinas yg mungkin jadi active window
        self._tutup_popup_detail_surat()
        deadline = time.time() + timeout
        tombol_tampil = []
        while time.time() < deadline:
            tombol_tampil = self._tambah_buttons_di_form()
            if index < len(tombol_tampil):
                break
            # Belum cukup -- popup staf sebelumnya mungkin masih menutup /
            # belum tertutup. Bersihkan & tunggu sebentar, coba lagi.
            self._tutup_popup_staf()
            self.pace(2)
        if index >= len(tombol_tampil):
            deskripsi_jendela = []
            try:
                for w in self.find_all_visible(self.WINDOW_LOCATOR, timeout=2):
                    try:
                        header = w.find_element(
                            By.CSS_SELECTOR, "span.x-window-header-text"
                        )
                        deskripsi_jendela.append(header.text.strip() or "(tanpa judul)")
                    except Exception:
                        deskripsi_jendela.append("(judul?)")
            except Exception:
                pass
            raise TimeoutException(
                f"Cuma ada {len(tombol_tampil)} tombol 'Tambah' yang tampil di "
                f"window form, butuh index {index}. Jendela tampil: {deskripsi_jendela}. "
                "Kemungkinan form belum selesai render atau popup lain masih "
                "menutup form (tertumpuk/tertindih)."
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
                self.pace(2)

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
        # Popup pencarian staf terbuka SEBAGAI window baru DI ATAS form --
        # cari elemen HANYA di window aktif (z-index tertinggi) supaya
        # tidak nyasar ke elemen senama milik form di belakangnya.
        input_cari = self.find_visible_in_active_window(self.INPUT_CARI_STAF, timeout=15)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", input_cari
        )
        self.click_via_js(input_cari)
        input_cari.clear()
        input_cari.send_keys(kata_kunci)
        self.pace(2)  # jeda sebentar sebelum ENTER
        input_cari.send_keys(Keys.ENTER)
        self.pace(2)  # tunggu hasil pencarian render (grid re-render)
        self.wait_loading_mask_gone(timeout=10)

        # Pilih checkbox baris sesuai flow (default: penyetuju baris 3,
        # penerima baris 1). Retry LOCAL kalau grid masih re-render/stale.
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
                # Hasil pencarian belum render / elemen stale -- tunggu
                # loading selesai lalu coba lagi
                self.pace(2)
                self.wait_loading_mask_gone(timeout=10)

        self.click_visible_in_active_window(self.BTN_PILIH, timeout=10)
        self.wait_loading_mask_gone(timeout=10)
        # Pastikan popup staf benar2 tertutup dulu. Di full run penutupan
        # popup bisa lebih lambat -- cek via tombol PILIH (unik popup staf),
        # bukan cek first-match input search yang bisa lolos/basi.
        deadline = time.time() + 15
        while time.time() < deadline:
            if not self._is_popup_staf_terbuka(timeout=2):
                break
            self._tutup_popup_staf()
        # Jeda ekstra -- form perlu waktu jadi active window kembali
        self.pace(2)
        # TUTUP popup detail surat yang mungkin "tembus" saat interaksi popup staf
        self._tutup_popup_detail_surat()

    def tambah_penyetuju(self, kata_kunci, checkbox_row=None):
        """step 16/19: Tambah penyetuju (tombol 'Tambah' PERTAMA di form)."""
        self._tambah_staf(0, kata_kunci, checkbox_row=checkbox_row)

    def tambah_penerima(self, kata_kunci, checkbox_row=None):
        """step 17/21: Tambah penerima (tombol 'Tambah' KEDUA di form)."""
        self._tambah_staf(1, kata_kunci, checkbox_row=checkbox_row)

    # ------------------ DRAFT: pilih draft, Perubahan, Hapus (Modul 6 & 7) ------------------
    ROW_DRAFT = (By.CSS_SELECTOR, "tr.x-grid-row.x-grid-data-row, tr.x-grid-data-row")
    BTN_PERUBAHAN = (By.CSS_SELECTOR, "[id^='sipas_com_button_edit-']")
    BTN_HAPUS = (By.CSS_SELECTOR, "[id^='sipas_com_button_delete-']")
    BTN_HAPUS_CANDIDATES = [
        (By.CSS_SELECTOR, "[id^='sipas_com_button_delete-']"),
        (By.XPATH, "//*[normalize-space(text())='Hapus']"),
    ]
    BTN_YA_KONFIRMASI = (By.XPATH, "//*[normalize-space(text())='Ya']")
    BTN_OK_NOTIFIKASI = (By.XPATH, "//*[normalize-space(text())='OK']")

    # Popup detail surat -- fallback sukses di pilih_draft_pertama() untuk
    # surat yang SUDAH disetujui (tidak punya tombol Hapus).
    POPUP_DETAIL_SURAT_ANY = (
        By.XPATH,
        "//span[contains(@class,'x-window-header-text')]"
        "[contains(normalize-space(text()),'Identitas Agenda')]",
    )

    # Popup proses upload berkas -- muncul setelah SIMPAN Link saat
    # aplikasi menyiapkan surat; kalau server lambat popup ini bisa
    # bertahan lama dan chip berkas belum tampil.
    POPUP_MENYIAPKAN_SURAT = (
        By.XPATH,
        "//span[contains(@class,'x-window-header-text')]"
        "[normalize-space(text())='Menyiapkan Surat']",
    )

    def _tombol_hapus_enabled(self, timeout=3):
        """Poll: tombol Hapus yang tampil di viewport ada & ENABLED
        (tombol belum dirender sebelum ada baris terpilih, dan state
        enable bisa tertunda sepersekian detik setelah select)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for locator in self.BTN_HAPUS_CANDIDATES:
                try:
                    btn = self.find_visible_in_viewport(locator, timeout=1)
                    enabled = self.driver.execute_script(
                        "var c = Ext.getCmp(arguments[0].id);"
                        "return !c || !c.isDisabled || !c.isDisabled();", btn
                    )
                    if enabled:
                        return True
                except TimeoutException:
                    continue
            time.sleep(0.5)
        return False

    def _is_row_selected(self):
        """True kalau ada baris DRAFT terpilih (tombol Hapus viewport
        ENABLED). Popup detail surat ikut dihitung sebagai sinyal baris
        terpilih (untuk surat yang sudah diajukan)."""
        if self._tombol_hapus_enabled(timeout=3):
            return True
        print("    [debug _is_row_selected] tombol Hapus belum enabled")
        try:
            self.find_visible_among(self.POPUP_DETAIL_SURAT_ANY, timeout=2)
            print("    [debug _is_row_selected] popup detail surat terbuka "
                  "(baris terpilih mungkin bukan draft)")
            return True
        except TimeoutException:
            return False

    def _grids_viewport(self):
        """List {id, count} grid yang tampil di viewport & tidak sedang
        loading (grid tab tersembunyi di luar viewport tidak dihitung)."""
        try:
            return self.driver.execute_script("""
                var vw = window.innerWidth, vh = window.innerHeight;
                var grids = document.querySelectorAll('div.x-grid');
                var out = [];
                for (var i = 0; i < grids.length; i++) {
                    var rect = grids[i].getBoundingClientRect();
                    if (rect.width <= 0 || rect.height <= 0) continue;
                    if (rect.left >= vw || rect.right <= 0
                        || rect.top >= vh || rect.bottom <= 0) continue;
                    var grid = Ext.getCmp(grids[i].id);
                    if (!grid || !grid.getSelectionModel || !grid.getStore) continue;
                    if (grid.getStore().isLoading()) return 'LOADING';
                    out.push({id: grids[i].id, count: grid.getStore().getCount()});
                }
                return out;
            """)
        except Exception:
            return []

    def pilih_draft_pertama(self, mulai_baris=0):
        """Pilih baris DRAFT secara deterministik: iterasi tiap baris
        (mulai dari `mulai_baris`) di tiap grid viewport -- select via
        selectionModel, lalu kalau tombol Hapus belum ENABLED dispatch
        klik row (handler rowclick app yang meng-enable tombol). Tombol
        Hapus ENABLED = baris draft terpilih. Return index baris yang
        terpilih (dipakai caller untuk geser ke baris berikutnya saat
        retry). Popup yang mungkin terbuka dari klik row langsung ditutup."""
        self.wait_loading_mask_gone(timeout=15)
        import time as _time
        dicoba = 0
        while dicoba < 60:
            grids = self._grids_viewport()
            if grids == 'LOADING' or not grids:
                _time.sleep(1)
                continue
            # Grid dengan baris terbanyak dulu (grid list utama)
            grids = sorted(grids, key=lambda g: -g['count'])
            for info in grids:
                for r in range(mulai_baris, info['count']):
                    dicoba += 1
                    hasil = self.driver.execute_script(
                        "var g = Ext.getCmp(arguments[0]);"
                        "if (!g) return 'NO_CMP';"
                        "g.getSelectionModel().select(arguments[1]);"
                        "return 'OK';",
                        info['id'], r,
                    )
                    print(f"    [debug pilih_draft] select grid="
                          f"{info['id'][:30]} row={r}/{info['count']} -> {hasil}")
                    if self._tombol_hapus_enabled(timeout=2):
                        return r
                    # select saja belum enable -- coba klik row (handler
                    # rowclick app yang meng-enable tombol Hapus)
                    diklik = self.driver.execute_script(
                        "var g = Ext.getCmp(arguments[0]);"
                        "if (!g) return false;"
                        "var node = g.getView().getNode(arguments[1]);"
                        "if (!node) return false;"
                        "node.click();"
                        "return true;",
                        info['id'], r,
                    )
                    if diklik:
                        if self._tombol_hapus_enabled(timeout=2):
                            return r
                        # Tutup popup detail / error yang terbuka dari klik
                        self._tutup_popup_detail_surat()
                    if dicoba >= 60:
                        break
                if dicoba >= 60:
                    break
            break
        assert self._tombol_hapus_enabled(timeout=3), (
            "Tidak ada baris draft yang bisa membuat tombol Hapus ENABLED."
        )
        return None

    def pilih_baris_pertama(self):
        """Pilih baris PERTAMA (surat apa saja) di grid viewport -- untuk
        Cek Detail Surat: popup 'Identitas Agenda' terbuka untuk semua
        jenis surat, bukan hanya draft. Berbeda dari pilih_draft_pertama()
        yang mensyaratkan tombol Hapus ENABLED."""
        self.wait_loading_mask_gone(timeout=15)
        import time as _time
        for _ in range(5):
            hasil = self.driver.execute_script("""
                var vw = window.innerWidth, vh = window.innerHeight;
                var grids = document.querySelectorAll('div.x-grid');
                for (var i = 0; i < grids.length; i++) {
                    var rect = grids[i].getBoundingClientRect();
                    if (rect.width <= 0 || rect.height <= 0) continue;
                    if (rect.left >= vw || rect.right <= 0
                        || rect.top >= vh || rect.bottom <= 0) continue;
                    var grid = Ext.getCmp(grids[i].id);
                    if (!grid || !grid.getSelectionModel || !grid.getStore) continue;
                    var store = grid.getStore();
                    if (store.isLoading()) return 'LOADING';
                    if (store.getCount() < 1) continue;
                    grid.getSelectionModel().select(0);
                    return 'SELECT count=' + store.getCount()
                        + ' grid=' + grids[i].id.slice(0, 30);
                }
                return 'NO_GRID';
            """)
            print(f"    [debug pilih_baris] {hasil}")
            if isinstance(hasil, str) and hasil.startswith("SELECT"):
                # Sukses kalau popup detail terbuka ATAU tombol Hapus muncul
                try:
                    self.find_visible_among(self.POPUP_DETAIL_SURAT_ANY, timeout=3)
                    return
                except TimeoutException:
                    pass
                if self._tombol_hapus_enabled(timeout=2):
                    return
                # Belum ada tanda baris terpilih -- klik row (handler
                # rowclick app yang membuka popup detail surat)
                diklik = self.driver.execute_script("""
                    var g = Ext.getCmp(arguments[0]);
                    if (!g) return false;
                    var node = g.getView().getNode(0);
                    if (!node) return false;
                    node.click();
                    return true;
                """, self.driver.execute_script("""
                    var vw = window.innerWidth, vh = window.innerHeight;
                    var grids = document.querySelectorAll('div.x-grid');
                    for (var i = 0; i < grids.length; i++) {
                        var rect = grids[i].getBoundingClientRect();
                        if (rect.width <= 0 || rect.height <= 0) continue;
                        if (rect.left >= vw || rect.right <= 0
                            || rect.top >= vh || rect.bottom <= 0) continue;
                        return grids[i].id;
                    }
                    return '';
                """))
                if diklik:
                    try:
                        self.find_visible_among(self.POPUP_DETAIL_SURAT_ANY, timeout=5)
                        return
                    except TimeoutException:
                        pass
            _time.sleep(2)
        raise AssertionError(
            "Baris pertama tidak berhasil dipilih untuk Cek Detail Surat."
        )

    def klik_perubahan(self):
        self.click_visible_among(self.BTN_PERUBAHAN, timeout=15)
        self.wait_loading_mask_gone(timeout=10)
        assert self.is_visible(self.TEXTAREA_PERIHAL, timeout=15), (
            "Dialog Perubahan Draft tidak terbuka -- field Perihal tidak tampil."
        )

    def tambah_penerima_baru(self, kata_kunci):
        """Tambah PENERIMA BARU di form Perubahan. Index 1 = Penerima,
        BUKAN index 0 (Penyetuju). Kalau form cuma menampilkan 1 tombol
        'Tambah', pakai index 0 (satu-satunya yang tampil pasti Penerima)."""
        self._tutup_popup_detail_surat()
        tombol = self.find_all_visible_in_active_window(self.BTN_TAMBAH_ANY, timeout=10)
        index = 1 if len(tombol) > 1 else 0
        self._tambah_staf(index, kata_kunci)

    def verifikasi_penerima_ditambahkan(self, kata_kunci, timeout=10):
        """Cek staf baru masuk ke bagian PENERIMA (grid paling bawah di
        form), bukan Penyetuju."""
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
        """Klik tombol Hapus yang benar2 tampil DI VIEWPORT (jangan sampai
        nyasar ke tombol Hapus milik tab modul lain yang tersembunyi).
        Kalau tidak ada, pilih ulang baris pertama lalu coba lagi (maks 3x)."""
        for attempt in range(3):
            for locator in self.BTN_HAPUS_CANDIDATES:
                try:
                    btn = self.find_visible_in_viewport(locator, timeout=5)
                    self.click_via_js(btn)
                    self.wait_loading_mask_gone(timeout=5)
                    return
                except TimeoutException:
                    continue
            # Tombol Hapus tidak tampil -- baris kehilangan seleksi?
            self.pilih_draft_pertama()
        raise TimeoutException(
            "Tombol Hapus tidak ditemukan. Pastikan draft baris sudah dipilih."
        )

    def _judul_window_elemen(self, element):
        """Judul + cuplikan isi window ExtJS yang memuat `element` (debug) --
        biar pesan dialog error (mis. 'Koneksi dengan server terputus')
        ikut tercetak di log."""
        try:
            return self.driver.execute_script(
                "var w = arguments[0].closest('div.x-window');"
                "if (!w) return '(bukan window)';"
                "var h = w.querySelector('span.x-window-header-text');"
                "var t = h ? h.textContent.trim() : '(tanpa judul)';"
                "var b = (w.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 120);"
                "return t + ' | isi: ' + b;", element
            )
        except Exception:
            return "(?)"

    def klik_ya_konfirmasi(self):
        btn = self.find_visible_among(self.BTN_YA_KONFIRMASI, timeout=15)
        print(f"    [debug klik_ya] tombol Ya di jendela: {self._judul_window_elemen(btn)}")
        self.click_via_js(btn)
        self.wait_loading_mask_gone(timeout=10)

    def klik_ok_notifikasi(self):
        if self.is_visible(self.BTN_OK_NOTIFIKASI, timeout=5):
            btn = self.find_visible_among(self.BTN_OK_NOTIFIKASI, timeout=5)
            print(f"    [debug klik_ok] tombol OK di jendela: {self._judul_window_elemen(btn)}")
            self.click_via_js(btn)
        self.wait_loading_mask_gone(timeout=10)

    def is_draft_terhapus(self, timeout=10):
        """Draft terhapus = dialog 'Ya' tidak tampil lagi di viewport DAN
        tombol Hapus di viewport tidak ada/disabled (tidak ada draft
        terpilih lagi)."""
        try:
            self.find_visible_in_viewport(self.BTN_YA_KONFIRMASI, timeout=timeout)
            return False
        except TimeoutException:
            pass
        try:
            btn = self.find_visible_in_viewport(self.BTN_HAPUS_CANDIDATES[0], timeout=5)
            enabled = self.driver.execute_script(
                "var c = Ext.getCmp(arguments[0].id);"
                "return !c || !c.isDisabled || !c.isDisabled();", btn
            )
            return not enabled
        except TimeoutException:
            return True

    def pilih_tembusan_checkbox(self):
        """step 18: Centang checkbox 'Tembusan' pada baris penerima, di
        dalam dialog form yang aktif (bukan checkbox senama di popup lain)."""
        self.click_visible_in_active_window(self.CHECKBOX_ROW_STAF, timeout=10)

    # -------------------------- AJUKAN PENYETUJUAN (step 19-20) --------------------------
    def ajukan_penyetujuan(self):
        # click_visible_in_active_window -- jangan klik tombol milik form
        # lain yang tertumpuk/basi di belakang.
        self.click_visible_in_active_window(self.BTN_AJUKAN_PENYETUJUAN, timeout=15)
        self.wait_loading_mask_gone(timeout=20)

        # Popup konfirmasi "Kirim Surat" ("Apakah anda yakin ?") -> klik Ya.
        self._konfirmasi_kirim_surat()

        # Tunggu notifikasi sukses & klik OK
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
        """Klik OK pada notifikasi sukses (bisa 2 popup OK berturut-turut)."""
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
        """Refresh grid via JS -- reload store."""
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
        """Tutup SEMUA window/popup ExtJS yang tampil (bersihkan layar
        sebelum membuka form Tambah yang baru)."""
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
        """Tutup popup ExtJS yang terbuka, KECUALI form Tambah/Perubahan
        (window yang mengandung textarea[name='surat_perihal']).

        Class x-tool-close ada di <img> (img.x-tool-img.x-tool-close),
        handler klik-nya di div.x-tool induknya -- klik keduanya supaya
        event terekam."""
        try:
            windows = self.driver.find_elements(By.CSS_SELECTOR, "div.x-window")
            for win in windows:
                try:
                    # Skip window yang tersembunyi
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

                    # Klik tombol close di window ini (img + parent div.x-tool)
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
        """Klik SIMPAN DRAFT lalu konfirmasi Ya + OK."""
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

        Form punya 2 grid (Penyetuju & Penerima) yang KEDUANYA bisa punya
        ikon bin -- target yang benar: bin di grid PALING BAWAH (Penerima)."""
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
        """Cek penyetuju (grid PERTAMA di form) masih memuat `kata_kunci`
        -- dipakai setelah hapus_penerima() untuk memastikan yang
        terhapus adalah PENERIMA, bukan penyetuju."""
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
        """step 20: surat berhasil diajukan = dialog form tertutup ATAU
        muncul notif sukses ExtJS."""
        form_tertutup = not self.is_visible(self.TEXTAREA_PERIHAL, timeout=timeout)
        if form_tertutup:
            return True
        for notif_locator in self.NOTIF_SUKSES_CANDIDATES:
            if self.is_visible(notif_locator, timeout=3):
                return True
        return False
