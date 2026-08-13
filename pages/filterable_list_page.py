"""
pages/filterable_list_page.py
==============================
Modul 2 (Tugas), 3 (Masuk), 4 (Disposisi Keluar), 5 (Progress Surat) di
Flow_Automation_Testing_DLA.md punya LANGKAH YANG PERSIS SAMA (12 step):

    1. Membuka halaman.
    2. Klik dropdown Posisi.
    3. Memilih opsi Primary Position.
    4. Memilih opsi Secondary Position.
    5. Memilih opsi Semua.
    6. Melakukan pencarian dengan mengisi kata kunci otomatis (contoh: "1").
    7. Klik tombol Filter.
    8. Memastikan pop-up Advanced Filter muncul.
    9. Memilih jenis filter.
    10. Mengisi data filter.
    11. Klik tombol Cari pada pop-up Advanced Filter.
    12. Memastikan data berhasil difilter sesuai kriteria.

Daripada menulis ulang 12 langkah ini di 4 page object berbeda, semua
logic generic-nya ditaruh di sini. Page object per modul (tugas_page.py,
masuk_page.py, dst) tinggal isi 2 locator yang beda-beda per modul (menu
navigasi & header halaman) dengan extend class ini.

LOCATOR YANG DIPAKAI (dikonfirmasi lewat locator/*.md hasil scan_locators,
BUKAN id ExtJS yang auto-generate/berubah tiap render):
- Dropdown Posisi: tidak ada data-qtip/name yang stabil di semua modul,
  jadi dicocokkan lewat VALUE yang sedang tampil (Semua/Primary Position/
  Secondary Position) -- ini teks yang benar-benar dirender, bukan id
  tebakan, jadi tetap valid dipakai walau elemen di-render ulang.
- Tombol FILTER: teks "FILTER" (konsisten UPPERCASE di semua modul).
- Popup Advanced Filter: dikenali dari munculnya tombol RESET & CARI
  (selalu ada di semua popup Advanced Filter, lihat *_locator.md).
- Dropdown "jenis filter" (tipe surat / status koreksi / dst): semua
  modul memakai name='tampilcombo' yang SAMA (lihat tugas_locator.md,
  disposisikeluar_locator.md, progresssurat_locator.md).
- Input pencarian: input[type='search'] -- pola ExtJS yang konsisten di
  semua modul (lihat progresssurat_locator.md / suratkeluareksternal_locator.md).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class FilterableListPage(BasePage):

    # Diisi ulang (override) oleh masing-masing subclass.
    MENU_LOCATOR = None
    HEADER_LOCATOR = None

    # Urutan opsi filter posisi sesuai MD (Primary -> Secondary -> Semua).
    POSISI_FILTER_OPTIONS = ["Primary Position", "Secondary Position", "Semua"]

    # ==========================================================
    # FILTER POSISI
    # ==========================================================
    # Tidak ada locator stabil untuk combo Posisi selain value yang
    # sedang tampil -- cocokkan ketiga kemungkinan value sekaligus.
    # CATATAN Modul 6 (Surat Keluar Eksternal) & Modul 7 (Nota Dinas
    # Keluar): berdasarkan notadinaskeluar_locator.md, opsi "Primary
    # Position" di 2 modul ini TIDAK tampil sebagai teks literal itu,
    # melainkan sebagai JABATAN ASLI user yang sedang login (contoh:
    # "ICT Solution Design Senior Specialist - ICT Business Solution
    # Bureau (Primary)") -- jadi value awal combo BUKAN 'Semua' dan
    # locator by-value di bawah tidak pernah match utk 2 modul itu.
    # Fallback kedua: combo trigger PERTAMA yang tampil di toolbar atas
    # (elemen readonly bertipe combo/trigger sebelum tombol FILTER).
    # PENTING: fallback ini masih tebakan struktural (belum dikonfirmasi
    # scan_locators.py di halaman LIST Surat Keluar Eksternal/Nota Dinas
    # Keluar -- yang tersedia baru locator popup "Tambah"-nya). Kalau
    # masih gagal di 2 modul ini, kirim hasil scan DROPDOWN_POSISI utk
    # halaman list-nya (bukan popup Tambah) supaya locator ini diganti
    # yang pasti.
    # FIX (root cause dropdown Posisi timeout Modul 6 & 7): fallback lama
    # pakai axis XPath `preceding-sibling::input` dari trigger panah
    # pertama di SELURUH halaman. Secara struktur ExtJS, trigger panah
    # (<a>) dan input combo-nya ada di <td> BERBEDA dalam satu <table>
    # yang sama -- bukan sibling langsung -- jadi axis itu tidak pernah
    # match apapun, selalu timeout.
    # Fix: fallback sekarang cari input combo yang ada di dalam TOOLBAR
    # yang sama dengan tombol FILTER (ancestor terdekat berclass
    # 'x-toolbar' dari tombol FILTER), bukan asal ambil trigger pertama
    # di seluruh dokumen. Ini lebih terarah karena dropdown Posisi selalu
    # satu toolbar dengan tombol FILTER di semua modul.
    DROPDOWN_FILTER_POSISI = (
        By.XPATH,
        "//input[@value='Semua' or @value='Primary Position' or @value='Secondary Position']"
        " | //*[normalize-space(text())='FILTER' or normalize-space(text())='Filter']"
        "/ancestor::*[contains(@class,'x-toolbar')][1]"
        "//input[contains(@class,'x-form-text')]",
    )

    # ==========================================================
    # PENCARIAN OTOMATIS
    # ==========================================================
    INPUT_PENCARIAN = (By.CSS_SELECTOR, "input[type='search']")

    # ==========================================================
    # ADVANCED FILTER
    # ==========================================================
    # Tombol FILTER -- dikonfirmasi lewat diagnostik: di halaman Tugas,
    # tombol FILTER adalah anchor dengan class 'x-btn-bordered x-btn-primary'
    # berisi span dengan teks "FILTER". Locator ini sama untuk SEMUA modul.
    BTN_FILTER = (By.XPATH, "//*[normalize-space(text())='FILTER' or normalize-space(text())='Filter']")

    # Dropdown "jenis filter" (nama field-nya konsisten 'tampilcombo' di
    # semua modul Advanced Filter -- lihat catatan module docstring &
    # locator_tambahan/*.txt yang dikirim per modul).
    DROPDOWN_JENIS_FILTER = (By.CSS_SELECTOR, "input[name='tampilcombo']")

    BTN_CARI_FILTER = (
        By.XPATH,
        "//a[contains(@class,'x-btn')]//span[normalize-space(text())='CARI' or normalize-space(text())='Cari']"
        " | //span[contains(@class,'x-btn-inner')][normalize-space(text())='CARI' or normalize-space(text())='Cari']"
        " | //*[normalize-space(text())='CARI' or normalize-space(text())='Cari']",
    )

    # FIX (root cause AttributeError yang bikin Modul 2-5 crash duluan
    # sebelum sempat cek popup): BTN_RESET_FILTER dipakai di
    # is_popup_advanced_filter_terbuka() TAPI tidak pernah didefinisikan
    # sama sekali di codebase manapun -- bug murni di kode, bukan gagal
    # cari elemen di browser. Locator di bawah masih TEBAKAN (belum
    # dikonfirmasi scan_locators.py) -- kirim hasil scan tombol RESET di
    # popup Advanced Filter kalau masih meleset.
    BTN_RESET_FILTER = (By.XPATH, "//*[normalize-space(text())='RESET' or normalize-space(text())='Reset']")

    # ==========================================================
    # ADVANCED FILTER -- "Filter Data" (checkbox + field yang muncul)
    # ==========================================================
    # PENTING (dikonfirmasi dari locator_tambahan/*.txt, HTML popup
    # Advance Filter): field "Mengisi data filter" BUKAN input
    # type='search' seperti sebelumnya -- popup ini tidak punya
    # input[type='search'] sama sekali. Yang benar: pilih checkbox
    # (mis. "Nomor Surat", "Jenis Surat") di section "Filter Data",
    # yang lalu MEMUNCULKAN 1 field text/combo persis di sebelahnya
    # (setiap checkbox ada di <table> yang diikuti <table> field-nya,
    # awalnya display:none, baru muncul setelah checkbox dicentang).
    # Locator checkbox pakai LABEL yang tampil ke user -- 'name' dari
    # checkbox itu sendiri auto-generate (checkbox-2037, dst, TIDAK
    # STABIL), tapi labelnya ('Nomor Surat', 'Jenis Surat', dst) SAMA
    # di semua modul (lihat locator_tambahan/*.txt).
    CHECKBOX_FILTER_LABELS_DEFAULT = ("Nomor Surat", "Jenis Surat")

    # ==========================================================
    # NAVIGASI & HEADER
    # ==========================================================
    def open_menu(self):
        self.wait_loading_mask_gone(timeout=10)
        el = self.find_visible_among(self.MENU_LOCATOR, timeout=10)
        self.click_via_js(el)
        self.wait_loading_mask_gone(timeout=10)

    def is_halaman_loaded(self, timeout=20):
        return self.is_visible(self.HEADER_LOCATOR, timeout=timeout)

    # ==========================================================
    # FILTER POSISI (step 2-5)
    # ==========================================================
    def klik_dropdown_posisi(self):
        """PENTING: locator DROPDOWN_FILTER_POSISI dicocokkan lewat
        value ('Semua'/'Primary Position'/'Secondary Position') -- di
        modul Disposisi Keluar, Progress Surat & Surat Keluar
        Eksternal/Nota Dinas, ada elemen LAIN di DOM (mis. combo lain
        yang defaultnya juga 'Semua', tapi sedang disembunyikan) yang
        ikut cocok. Sebelumnya klik_via_js() pakai find() yang cuma
        cek elemen ADA di DOM (tidak cek benar-benar tampil), jadi bisa
        salah klik elemen tersembunyi itu -- efeknya dropdown/boundlist
        yang muncul jadi salah posisi ("muncul di samping sendiri").
        Fix: pastikan yang diklik elemen yang BENAR-BENAR tampil."""
        element = self.find_visible_among(self.DROPDOWN_FILTER_POSISI, timeout=15)
        self.click_via_js(element)

    def pilih_posisi(self, opsi_posisi):
        """opsi_posisi salah satu dari POSISI_FILTER_OPTIONS.

        PENTING (akar penyebab TimeoutException di modul 2-7 sebelumnya):
        teks opsi ('Primary Position' dst) sering muncul LEBIH DARI
        SEKALI di DOM (boundlist lain yang sedang tersembunyi tapi
        masih ada di halaman). click() versi lama mengambil elemen
        PERTAMA yang match tanpa cek visibility, jadi kalau elemen
        pertama itu kebetulan yang tersembunyi, dia menunggu sampai
        timeout tanpa pernah mencoba elemen lain yang benar-benar
        tampil. Fix: selalu klik lewat find_visible_among (dibungkus
        click_visible_among di BasePage).

        Fallback tambahan (khusus modul 6 & 7 -- lihat catatan di
        DROPDOWN_FILTER_POSISI): kalau opsi tidak ketemu lewat teks
        literal (karena render-nya jabatan asli user, bukan teks
        'Primary Position'), pilih berdasarkan URUTAN tampil di
        boundlist yang sedang terbuka -- urutannya konsisten mengikuti
        POSISI_FILTER_OPTIONS (Primary -> Secondary -> Semua)."""
        self.klik_dropdown_posisi()
        # HANYA boundlist item — union `//*[text()=...]` lama bisa match
        # elemen lain (cell grid, label) dan klik "tembus" ke tempat lain.
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{opsi_posisi}']",
        )
        try:
            self.click_visible_among(opsi_locator, timeout=6)
        except TimeoutException:
            self._pilih_opsi_posisi_by_index(opsi_posisi, timeout=10)

        # FIX (gejala "bisa klik dropdown tapi opsi tidak kepilih"):
        # click_visible_among() bisa saja "berhasil" secara Selenium
        # (tidak exception) tapi event pilih combo-nya ExtJS tidak
        # benar-benar terekam -- salah satu bukti paling jelas kalau ini
        # terjadi: boundlist-nya MASIH TERBUKA setelah diklik (harusnya
        # otomatis tertutup begitu 1 opsi terpilih). Kalau masih terbuka,
        # anggap klik pertama tidak "kena" & coba sekali lagi lewat
        # fallback berbasis index (lebih pasti karena klik elemen boundlist
        # langsung, bukan tergantung teks).
        boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
        if self.is_visible(boundlist_terbuka, timeout=2):
            self._pilih_opsi_posisi_by_index(opsi_posisi, timeout=10)
        self.wait_loading_mask_gone(timeout=15)

    def _pilih_opsi_posisi_by_index(self, opsi_posisi, timeout=10):
        """Fallback posisi opsi berdasarkan urutan (lihat docstring
        pilih_posisi di atas)."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        index = self.POSISI_FILTER_OPTIONS.index(opsi_posisi)
        items = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.x-boundlist-item")
            )
        )
        visible_items = [item for item in items if item.is_displayed()]
        if index >= len(visible_items):
            raise TimeoutException(
                f"Boundlist Posisi cuma punya {len(visible_items)} opsi tampil, "
                f"butuh index {index} untuk opsi '{opsi_posisi}'. "
                "Tolong kirim hasil scan_locators.py DROPDOWN_POSISI utk halaman ini."
            )
        self.click_via_js(visible_items[index])

    # ==========================================================
    # PENCARIAN OTOMATIS (step 6)
    # ==========================================================
    def cari_otomatis(self, kata_kunci="1"):
        # PENTING: pakai find_visible_among (bukan type_text biasa) -- di
        # ExtJS input[type='search'] sering dirender GANDA (satu
        # tersembunyi lebih dulu di DOM, satu lagi yang aktif/tampil).
        # type_text biasa mengunci ke elemen PERTAMA yang match lalu
        # menunggu elemen ITU tampil -- kalau yang pertama justru
        # tersembunyi, dia timeout tanpa pernah mencoba yang benar-benar
        # tampil. Ini akar penyebab flow modul 2-5 tidak pernah sampai ke
        # Advanced Filter (step 7-12).
        #
        # PENTING #2 (fix search tidak muncul sesuai keyword): mengetik
        # teks saja TIDAK memicu pencarian di ExtJS search field ini --
        # request ke server baru terkirim saat user menekan ENTER (event
        # 'specialkey'). Sebelumnya kode cuma clear()+send_keys(keyword)
        # lalu langsung nunggu mask hilang -- karena tidak ada request
        # yang pernah terkirim, mask juga tidak pernah muncul, jadi
        # method ini "sukses" tanpa error padahal grid TIDAK pernah
        # benar-benar difilter sesuai keyword. Fix: kirim Keys.ENTER
        # setelah mengetik.
        element = self.find_visible_among(self.INPUT_PENCARIAN, timeout=15)
        element.clear()
        element.send_keys(kata_kunci)
        element.send_keys(Keys.ENTER)
        self.pace()
        self.wait_loading_mask_gone(timeout=15)

    def clear_pencarian(self):
        """Hapus keyword pencarian & kembalikan grid ke semula (step 7
        di flow: 'lalu kembali ke semula (hapus keyword)')."""
        element = self.find_visible_among(self.INPUT_PENCARIAN, timeout=10)
        element.clear()
        element.send_keys(Keys.ENTER)
        self.pace()
        self.wait_loading_mask_gone(timeout=15)

    # ==========================================================
    # ADVANCED FILTER (step 7-12)
    # ==========================================================
    def klik_filter(self):
        """KLIK tombol FILTER untuk membuka popup Advanced Filter.

        PENTING: pakai click_visible_among (BUKAN click biasa atau
        find_first_visible). click_visible_among iterasi melalui SEMUA
        elemen yang cocok dan klik yang BENAR-BENAR tampil. Ini penting
        karena di DOM SPA ini, ada 4+ span dengan teks "FILTER" (dari
        modul/tab lain) -- click biasa / find_first_visible mengunci ke
        elemen PERTAMA yang match (yang seringkali hidden), sedangkan
        click_visible_among mencari yang benar-benar visible.

        PENTING #2: tunggu loading mask hilang DULU sebelum klik. Setelah
        clear_pencarian() atau operasi grid lainnya, grid reload dan
        loading mask bisa muncul lagi -- kalau tombol FILTER diklik saat
        mask masih ada, klik tidak terekam & popup tidak muncul.

        PENTING #3 (fix klik FILTER kedua setelah CARI gagal): setelah
        CARI, toolbar bisa dalam keadaan visibility:hidden (is_displayed
        False tapi ukuran rect > 0 & handler ExtJS masih berfungsi).
        Fallback: klik via JS tombol dengan id prefix stabil
        'sipas_com_filter_button-' (id asli: sipas_com_filter_button-XXXX)."""
        self.wait_loading_mask_gone(timeout=10)
        try:
            self.click_visible_among(self.BTN_FILTER, timeout=10)
        except Exception:
            # Fallback: klik via JS -- tombol bisa visibility:hidden
            # setelah CARI tapi tetap berfungsi kalau diklik via JS.
            clicked = self.driver.execute_script("""
                var btns = document.querySelectorAll("[id^='sipas_com_filter_button-']");
                for (var i = 0; i < btns.length; i++) {
                    var rect = btns[i].getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        btns[i].scrollIntoView({block: 'center'});
                        btns[i].click();
                        return true;
                    }
                }
                // Fallback kedua: span berisi teks persis FILTER
                var spans = document.querySelectorAll("span.x-btn-inner");
                for (var i = 0; i < spans.length; i++) {
                    var t = (spans[i].textContent || '').trim().toUpperCase();
                    var r = spans[i].getBoundingClientRect();
                    if (t === 'FILTER' && r.width > 0 && r.height > 0) {
                        spans[i].click();
                        return true;
                    }
                }
                return false;
            """)
            if not clicked:
                raise TimeoutException(
                    "Tombol FILTER tidak ditemukan (visible maupun via JS)."
                )
        self.wait_loading_mask_gone(timeout=15)

    def is_popup_advanced_filter_terbuka(self, timeout=15):
        """Popup dikenali dari munculnya tombol CARI + dropdown 'jenis
        filter' (name='tampilcombo'), yang hanya muncul saat popup
        Advanced Filter sedang terbuka.

        PENTING: pakai find_visible_among (BUKAN is_visible biasa).
        is_visible pakai visibility_of_element_located yang mengunci
        ke elemen PERTAMA yang match di DOM -- kalau ada sisa elemen
        CARI/tampilcombo dari popup sebelumnya yang masih hidden di
        DOM, is_visible akan menunggu elemen ITU sampai timeout.
        find_visible_among mencari di antara SEMUA elemen yang cocok
        dan ambil yang benar-benar tampil."""
        self.pace(1)
        try:
            cari_tampil = self.find_visible_among(self.BTN_CARI_FILTER, timeout=timeout)
            combo_tampil = self.find_visible_among(self.DROPDOWN_JENIS_FILTER, timeout=5)
            return cari_tampil is not None and combo_tampil is not None
        except TimeoutException:
            return False

    def pilih_jenis_filter(self, nilai):
        """Pilih jenis filter (contoh: 'Disposisi', 'Surat Disetujui', dll)
        dari dropdown 'tampilcombo' di popup Advanced Filter.

        PENTING: setelah opsi dipilih, boundlist dropdown harus benar-benar
        TERTUTUP sebelum langkah berikutnya (isi_data_filter). Kalau
        boundlist masih terbuka, interaksi berikutnya (klik checkbox, isi
        field) bisa salah sasaran karena ExtJS masih dalam mode 'dropdown
        terbuka' dan event click bisa jatuh ke boundlist item, bukan ke
        checkbox yang dimaksud."""
        element = self.find_visible_among(self.DROPDOWN_JENIS_FILTER, timeout=15)
        self.click_via_js(element)
        # HANYA boundlist item — union `//*[text()=...]` lama bisa match
        # elemen lain dan klik "tembus" ke tempat lain.
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{nilai}']",
        )
        # Sama seperti pilih_posisi(): teks opsi bisa duplikat di DOM
        # (boundlist lain yang tersembunyi) -- klik yang benar2 tampil.
        self.click_visible_among(opsi_locator, timeout=10)
        # Pastikan boundlist dropdown sudah benar-benar tertutup.
        # Kalau masih terbuka, klik area kosong (body) untuk menutupnya,
        # lalu coba klik opsi sekali lagi.
        boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
        if self.is_visible(boundlist_terbuka, timeout=3):
            # Klik area kosong untuk menutup boundlist yang mungkin
            # stuck/macet (gagal tertutup setelah opsi dipilih).
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.driver.execute_script("arguments[0].click();", body)
            except Exception:
                pass
            self.pace(1)
            # Coba sekali lagi klik opsi dari dropdown yang baru dibuka
            element = self.find_visible_among(self.DROPDOWN_JENIS_FILTER, timeout=10)
            self.click_via_js(element)
            self.click_visible_among(opsi_locator, timeout=10)
        self.wait_loading_mask_gone(timeout=10)

    def _label_checkbox_filter_locator(self, label_checkbox):
        return (
            By.XPATH,
            "//label[contains(@class,'x-form-cb-label')]"
            f"[normalize-space(text())='{label_checkbox}']",
        )

    def centang_checkbox_filter(self, label_checkbox):
        """Centang 1 checkbox di section 'Filter Data' popup Advanced
        Filter, dicari lewat LABEL yang tampil ke user (stabil di semua
        modul -- lihat locator_tambahan/*.txt). Checkbox ExtJS ini
        bukan native <input type=checkbox>, jadi tidak bisa diklik
        labelnya langsung -- ambil id lewat atribut 'for' pada label,
        lalu klik elemen checkbox aslinya."""
        label_el = self.find_visible_among(
            self._label_checkbox_filter_locator(label_checkbox), timeout=10
        )
        checkbox_id = label_el.get_attribute("for")
        checkbox_el = self.find((By.ID, checkbox_id), timeout=5)
        self.click_via_js(checkbox_el)
        return label_el

    def _revealed_field_locator(self, label_checkbox):
        """Field/dropdown yang MUNCUL tepat di sebelah checkbox setelah
        checkbox 'label_checkbox' dicentang (lihat catatan struktur
        <table> checkbox diikuti <table> field di docstring
        centang_checkbox_filter()). Field ini awalnya display:none,
        baru tampil setelah checkbox dicentang -- dicari lewat baris
        <tr> checkbox lalu <tr> berikutnya yang berisi field-nya."""
        return (
            By.XPATH,
            "//label[contains(@class,'x-form-cb-label')]"
            f"[normalize-space(text())='{label_checkbox}']"
            "/ancestor::tr[1]/following-sibling::tr[1]"
            "//input[not(@type='hidden')]",
        )

    def isi_field_filter_terungkap(self, label_checkbox, kata_kunci):
        """PENTING (akar penyebab bug #1 -- "tidak memfilter atau tidak
        memilih dropdown yg ada di dalamnya da checkbox nya"): dulu
        centang_checkbox_filter() HANYA mencentang checkbox lalu
        berhenti -- popup Advanced Filter memang "berhasil menampilkan
        filternya" (field/dropdown-nya muncul), tapi field yang muncul
        itu TIDAK PERNAH diisi/dipilih, jadi filter tidak benar-benar
        diterapkan sesuai kriteria walau tombol CARI tetap "berhasil"
        diklik.

        Fix: setelah checkbox dicentang & field/dropdown-nya muncul,
        field itu diisi. Kalau field-nya combo/dropdown (readonly,
        pola yang sama dipakai di semua dropdown lain project ini --
        lihat DROPDOWN_* di surat_form_base_page.py), klik lalu pilih
        opsi lewat boundlist. Kalau field teks biasa, ketik kata_kunci
        langsung."""
        field_locator = self._revealed_field_locator(label_checkbox)
        if not self.is_visible(field_locator, timeout=5):
            return  # checkbox ini tidak memunculkan field tambahan apapun

        field_el = self.find_visible_among(field_locator, timeout=5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", field_el
        )
        is_combo = field_el.get_attribute("readonly") is not None
        if is_combo:
            self.click_via_js(field_el)
            opsi_locator = (
                By.XPATH,
                "//li[contains(@class,'x-boundlist-item')]",
            )
            opsi_tampil = self.find_all_visible(opsi_locator, timeout=8)
            if not opsi_tampil:
                return
            match = next(
                (opsi for opsi in opsi_tampil if kata_kunci and kata_kunci.lower() in opsi.text.lower()),
                opsi_tampil[0],
            )
            self.click_via_js(match)
        else:
            field_el.clear()
            field_el.send_keys(kata_kunci)
            self.pace()

    def isi_data_filter(self, kata_kunci=None, checkbox_labels=None):
        """'Mengisi data filter': centang checkbox filter yang sesuai
        (default: 'Nomor Surat' & 'Jenis Surat', persis seperti catatan
        di locator_tambahan/Tugas.txt), LALU isi/pilih field yang
        muncul tepat setelah checkbox itu dicentang (lihat
        isi_field_filter_terungkap() -- ini yang sebelumnya hilang,
        akar penyebab bug #1).

        `kata_kunci` dipakai sebagai nilai yang diisi/dicari ke
        field/dropdown yang terungkap tsb (default "1" kalau None,
        supaya pemanggil lama yang masih kirim None tetap jalan).

        `checkbox_labels` bisa dioverride per modul kalau checkbox yang
        mau dicentang beda (semua modul di locator_tambahan/*.txt
        konsisten punya checkbox 'Nomor Surat' & 'Jenis Surat', jadi
        default ini aman dipakai di semua modul 2-7)."""
        labels = checkbox_labels or self.CHECKBOX_FILTER_LABELS_DEFAULT
        nilai = kata_kunci if kata_kunci else "1"
        for label_checkbox in labels:
            if not self.is_visible(
                self._label_checkbox_filter_locator(label_checkbox), timeout=3
            ):
                continue  # modul ini tidak punya checkbox filter dengan label ini
            self.centang_checkbox_filter(label_checkbox)
            self.isi_field_filter_terungkap(label_checkbox, nilai)

    def klik_cari_popup(self):
        """Klik tombol CARI pada popup Advanced Filter & pastikan
        popup benar-benar tertutup setelahnya.

        PENTING (fix toolbar jadi visibility:hidden setelah CARI):
        sebelumnya ada ESC + JS click pada body untuk "dismiss overlay"
        -- ternyata itu yang merusak state toolbar (tombol FILTER/TAMBAH
        jadi tersembunyi, lihat diagnose_toolbar_buttons.py). Popup
        Advanced Filter ternyata MENUTUP SENDIRI setelah CARI, jadi
        dismissal paksa TIDAK diperlukan dan malah berbahaya."""
        self.click_visible_among(self.BTN_CARI_FILTER, timeout=15)
        self.wait_loading_mask_gone(timeout=15)
        self.pace(1)

    def klik_reset_filter(self):
        """Klik tombol RESET pada popup Advanced Filter -- menghapus
        semua filter & mengembalikan grid ke data semula (dipakai Modul
        6: filter dulu, buka Advanced Filter lagi, RESET, baru Tambah).

        Tombol di aplikasi berteks 'Reset' (id auto-generate button-XXXX,
        tidak stabil -- cocokkan via teks)."""
        try:
            self.click_visible_among(self.BTN_RESET_FILTER, timeout=10)
        except Exception:
            # Fallback JS: cari span berisi teks 'Reset' yang punya ukuran
            clicked = self.driver.execute_script("""
                var spans = document.querySelectorAll("span.x-btn-inner");
                for (var i = 0; i < spans.length; i++) {
                    var t = (spans[i].textContent || '').trim().toLowerCase();
                    var r = spans[i].getBoundingClientRect();
                    if (t === 'reset' && r.width > 0 && r.height > 0) {
                        spans[i].click();
                        return true;
                    }
                }
                return false;
            """)
            if not clicked:
                raise TimeoutException("Tombol Reset tidak ditemukan di popup Advanced Filter.")
        self.wait_loading_mask_gone(timeout=15)
        # Kalau popup masih terbuka setelah RESET, tutup dengan ESC
        if self.is_popup_advanced_filter_terbuka(timeout=3):
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
            except Exception:
                pass
            self.wait_loading_mask_gone(timeout=10)
