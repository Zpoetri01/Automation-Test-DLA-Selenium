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

    # -------------------------------- Filter posisi --------------------------------
    # Combo Posisi tidak punya locator stabil selain value yang sedang tampil.
    # Fallback: input combo readonly di toolbar yang sama dengan tombol FILTER.
    DROPDOWN_FILTER_POSISI = (
        By.XPATH,
        "//input[@value='Semua' or @value='Primary Position' or @value='Secondary Position']"
        " | //*[normalize-space(text())='FILTER' or normalize-space(text())='Filter']"
        "/ancestor::*[contains(@class,'x-toolbar')][1]"
        "//input[contains(@class,'x-form-text')]",
    )

    # ------------------------------- Pencarian otomatis -------------------------------
    INPUT_PENCARIAN = (By.CSS_SELECTOR, "input[type='search']")

    # -------------------------------- Advanced filter --------------------------------
    # Tombol FILTER (teks sama di semua modul).
    BTN_FILTER = (By.XPATH, "//*[normalize-space(text())='FILTER' or normalize-space(text())='Filter']")

    # Dropdown "jenis filter" (name='tampilcombo' konsisten di semua modul).
    DROPDOWN_JENIS_FILTER = (By.CSS_SELECTOR, "input[name='tampilcombo']")

    BTN_CARI_FILTER = (
        By.XPATH,
        "//a[contains(@class,'x-btn')]//span[normalize-space(text())='CARI' or normalize-space(text())='Cari']"
        " | //span[contains(@class,'x-btn-inner')][normalize-space(text())='CARI' or normalize-space(text())='Cari']"
        " | //*[normalize-space(text())='CARI' or normalize-space(text())='Cari']",
    )

    BTN_RESET_FILTER = (By.XPATH, "//*[normalize-space(text())='RESET' or normalize-space(text())='Reset']")

    # ----------- "Filter Data" popup Advanced Filter (checkbox + field-nya) -----------
    # Field filter BUKAN input type='search': centang checkbox (mis. "Nomor
    # Surat") lalu field text/combo di sebelahnya baru muncul & diisi.
    CHECKBOX_FILTER_LABELS_DEFAULT = ("Nomor Surat", "Jenis Surat")

    # ------------------------------ Navigasi & header ------------------------------
    def open_menu(self):
        self.wait_loading_mask_gone(timeout=10)
        el = self.find_visible_among(self.MENU_LOCATOR, timeout=10)
        self.click_via_js(el)
        self.wait_loading_mask_gone(timeout=10)

    def is_halaman_loaded(self, timeout=20):
        return self.is_visible(self.HEADER_LOCATOR, timeout=timeout)

    # ----------------------------- Filter posisi (step 2-5) -----------------------------
    def klik_dropdown_posisi(self):
        """Klik combo Posisi yang benar2 tampil (bukan match hidden di DOM)."""
        element = self.find_visible_among(self.DROPDOWN_FILTER_POSISI, timeout=15)
        self.click_via_js(element)

    def pilih_posisi(self, opsi_posisi):
        """Pilih opsi Posisi. Teks opsi bisa duplikat di DOM, jadi selalu
        klik yang benar2 tampil; fallback pilih berdasarkan urutan tampil."""
        self.klik_dropdown_posisi()
        # HANYA item boundlist -- union //*[text()=...] bisa "tembus" ke elemen lain.
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{opsi_posisi}']",
        )
        try:
            self.click_visible_among(opsi_locator, timeout=6)
        except TimeoutException:
            self._pilih_opsi_posisi_by_index(opsi_posisi, timeout=10)

        # Kalau boundlist masih terbuka, berarti event pilih belum terekam
        # -- coba sekali lagi lewat fallback index.
        boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
        if self.is_visible(boundlist_terbuka, timeout=2):
            self._pilih_opsi_posisi_by_index(opsi_posisi, timeout=10)
        self.wait_loading_mask_gone(timeout=15)

    def _pilih_opsi_posisi_by_index(self, opsi_posisi, timeout=10):
        """Fallback: pilih opsi berdasarkan urutan tampil di boundlist."""
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

    # -------------------------- Pencarian otomatis (step 6) --------------------------
    def cari_otomatis(self, kata_kunci="1"):
        # find_visible_among karena input[type='search'] sering dirender
        # ganda (satu hidden) + ENTER wajib untuk memicu request ExtJS.
        element = self.find_visible_among(self.INPUT_PENCARIAN, timeout=15)
        element.clear()
        element.send_keys(kata_kunci)
        element.send_keys(Keys.ENTER)
        self.pace()
        self.wait_loading_mask_gone(timeout=15)

    def clear_pencarian(self):
        """Hapus keyword & kembalikan grid ke semula (step 7)."""
        element = self.find_visible_among(self.INPUT_PENCARIAN, timeout=10)
        element.clear()
        element.send_keys(Keys.ENTER)
        self.pace()
        self.wait_loading_mask_gone(timeout=15)

    # ------------------------- Advanced filter (step 7-12) -------------------------
    def klik_filter(self):
        """Buka popup Advanced Filter. Fallback JS kalau tombol jadi
        visibility:hidden setelah CARI (handler ExtJS masih berfungsi)."""
        self.wait_loading_mask_gone(timeout=10)
        try:
            self.click_visible_among(self.BTN_FILTER, timeout=10)
        except Exception:
            # Fallback: klik via JS tombol dengan id prefix stabil.
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
        """Popup terbuka = tombol CARI + dropdown 'tampilcombo' tampil.
        (find_visible_among, bukan is_visible yang terkunci match pertama)."""
        self.pace(1)
        try:
            cari_tampil = self.find_visible_among(self.BTN_CARI_FILTER, timeout=timeout)
            combo_tampil = self.find_visible_among(self.DROPDOWN_JENIS_FILTER, timeout=5)
            return cari_tampil is not None and combo_tampil is not None
        except TimeoutException:
            return False

    def pilih_jenis_filter(self, nilai):
        """Pilih jenis filter dari dropdown 'tampilcombo', lalu pastikan
        boundlist benar2 tertutup sebelum langkah berikutnya."""
        element = self.find_visible_among(self.DROPDOWN_JENIS_FILTER, timeout=15)
        self.click_via_js(element)
        # HANYA item boundlist -- union //*[text()=...] bisa "tembus" ke elemen lain.
        opsi_locator = (
            By.XPATH,
            f"//li[contains(@class,'x-boundlist-item')][normalize-space(text())='{nilai}']",
        )
        # Teks opsi bisa duplikat di DOM -- klik yang benar2 tampil.
        self.click_visible_among(opsi_locator, timeout=10)
        # Kalau boundlist masih terbuka (stuck), tutup via klik body
        # lalu ulangi klik opsi sekali lagi.
        boundlist_terbuka = (By.CSS_SELECTOR, "ul.x-boundlist-list, div.x-boundlist")
        if self.is_visible(boundlist_terbuka, timeout=3):
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.driver.execute_script("arguments[0].click();", body)
            except Exception:
                pass
            self.pace(1)
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
        """Centang checkbox 'Filter Data' lewat LABEL (stabil di semua
        modul); checkbox ExtJS bukan native input, jadi klik via id 'for'."""
        label_el = self.find_visible_among(
            self._label_checkbox_filter_locator(label_checkbox), timeout=10
        )
        checkbox_id = label_el.get_attribute("for")
        checkbox_el = self.find((By.ID, checkbox_id), timeout=5)
        self.click_via_js(checkbox_el)
        return label_el

    def _revealed_field_locator(self, label_checkbox):
        """Field/dropdown yang muncul tepat setelah checkbox dicentang."""
        return (
            By.XPATH,
            "//label[contains(@class,'x-form-cb-label')]"
            f"[normalize-space(text())='{label_checkbox}']"
            "/ancestor::tr[1]/following-sibling::tr[1]"
            "//input[not(@type='hidden')]",
        )

    def isi_field_filter_terungkap(self, label_checkbox, kata_kunci):
        """Isi field yang muncul setelah checkbox dicentang: kalau combo
        (readonly) pilih dari boundlist, kalau teks biasa ketik langsung."""
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
        """Centang checkbox filter (default: Nomor Surat & Jenis Surat)
        lalu isi field yang muncul. kata_kunci default "1"."""
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
        """Klik CARI di popup Advanced Filter (popup menutup sendiri)."""
        self.click_visible_among(self.BTN_CARI_FILTER, timeout=15)
        self.wait_loading_mask_gone(timeout=15)
        self.pace(1)

    def klik_reset_filter(self):
        """Klik RESET di popup Advanced Filter; kalau popup masih terbuka, tutup ESC."""
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
        if self.is_popup_advanced_filter_terbuka(timeout=3):
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
            except Exception:
                pass
            self.wait_loading_mask_gone(timeout=10)
