# Automation Testing NewDLA (Selenium + Python + Pytest)

Framework **Page Object Model (POM)** + data-driven (JSON) + Pytest +
pytest-html. Satu sesi browser menjalankan seluruh alur E2E dari Login
sampai Logout, **tanpa refresh halaman**.

> **Status terakhir: 20 test passed, 0 failed (±12-13 menit).**

---

## Ringkasan folder

| Bagian | Fungsinya |
|---|---|
| `pages/` | Locator + aksi/interaksi halaman |
| `base_page.py` | Fungsi dasar Selenium |
| `tests/` | Menjalankan skenario test |
| `conftest.py` | Driver, fixture, hasil PASS/FAIL, screenshot |
| `data/` | Data yang dipakai untuk testing |
| `config/` | URL, timeout, konfigurasi |
| `tools/` | Membantu mencari locator |
| `reports/` | Hasil/laporan testing |

## Alur test (urut sesuai file)

| Step | Test method | Isi |
|---|---|---|
| 1 | `test_login` | Login SSO Google |
| 2 | `test_dashboard_buka` | Dashboard tampil |
| 3 | `test_dashboard_widget` | 4 widget tampil |
| 4 | `test_dashboard_rentang_tanggal` | Klik ikon Rentang Tanggal |
| 5 | `test_dashboard_popup_tanggal` | Pop-up tanggal muncul |
| 6 | `test_dashboard_pilih_tanggal` | Isi tanggal awal & akhir |
| 7 | `test_dashboard_cari` | Klik Cari |
| 8 | `test_dashboard_verifikasi` | Data dashboard diperbarui |
| 9 | `test_tugas` | Modul 2: posisi → pencarian → Advanced Filter |
| 10 | `test_masuk` | Modul 3: posisi → pencarian → Advanced Filter |
| 11 | `test_disposisi_keluar` | Modul 4: posisi → pencarian → Advanced Filter |
| 12 | `test_progress_surat` | Modul 5: posisi → pencarian → Advanced Filter |
| 13 | `test_surat_keluar_eksternal` | Modul 6: pencarian → Advanced Filter → CARI → buka filter lagi → **RESET** |
| 14 | `test_simpan_draft_pertama` | Tambah → upload via Link → isi form → penyetuju (Yulia) → penerima (Ryco) → Simpan Draft |
| 15 | `test_hapus_draft` | Pilih draft → Hapus → Ya → OK |
| 16 | `test_ubah_dan_ajukan` | Draft kedua → Perubahan → hapus penerima Ryco → tambah Arru → Ajukan Penyetujuan |
| 17 | `test_nota_dinas_keluar` | Modul 7: pencarian → Advanced Filter (Disetujui) |
| 18 | `test_detail_surat` | Modul 7: detail surat → Log Aktifitas → tutup popup |
| 19 | `test_topbar` | Topbar: 4 dropdown (lonceng, notifikasi agenda, kelola surat, pengaturan) |
| 20 | `test_logout` | Logout → kembali ke halaman login |

Di akhir sesi, terminal mencetak ringkasan:

```
========================================
       AUTOMATION TESTING RESULT
========================================
V [Login] berhasil
V [Dashboard] berhasil
...
========================================
TOTAL TEST : 14
PASSED     : 14
FAILED     : 0
STATUS     : PASSED
========================================
```

---

## Struktur folder

```
project/
├── conftest.py                       <- driver session-scoped + ringkasan hasil terminal
├── pytest.ini                        <- konfigurasi pytest + laporan HTML otomatis
├── requirements.txt
├── config/
│   └── config.py                     <- URL, timeout, chrome profile, headless
├── data/
│   └── test_data.json                <- SEMUA data uji (keyword, isian form, staf, dll)
├── pages/
│   ├── base_page.py                  <- fungsi dasar Selenium (klik, ketik, tunggu)
│   ├── login_page.py                 <- Login + Logout
│   ├── dashboard_page.py             <- Modul 1 (widget, rentang tanggal)
│   ├── filterable_list_page.py       <- logic filter bersama Modul 2-5
│   ├── tugas_page.py                 <- Modul 2
│   ├── masuk_page.py                 <- Modul 3
│   ├── disposisi_keluar_page.py      <- Modul 4
│   ├── progress_surat_page.py        <- Modul 5
│   ├── surat_form_base_page.py       <- logic form surat bersama Modul 6-7
│   ├── surat_dinas_eksternal_page.py <- Modul 6
│   ├── nota_dinas_keluar_page.py     <- Modul 7
│   └── topbar_page.py                <- Modul Topbar (4 dropdown bar atas)
├── tests/
│   ├── test_e2e_dla.py               <- SATU file, alur berurutan semua modul
│   ├── diagnose.py                   <- script debug dump state halaman (bukan pytest)
│   ├── diagnose_filter_state.py      <- script debug state toolbar setelah filter+CARI
│   └── diagnose_toolbar_buttons.py   <- script debug atribut tombol toolbar
├── tools/
│   ├── scan_locators_v2.py           <- scan locator halaman aktif (butuh Chrome port 9222)
│   └── scan_topbar_sekarang.py       <- scan khusus topbar
└── reports/
    ├── report.html                   <- laporan HTML hasil pytest
    ├── screenshots/                  <- screenshot otomatis saat test gagal
    └── locator_scan*.txt             <- hasil scan locator
```

---

## Cara membaca kode

### Peta kelas (inheritance)

```
BasePage                          <- Fondasi SEMUA halaman
├── LoginPage                     <- Login + Logout
├── DashboardPage                 <- Modul 1
├── TopbarPage                    <- Modul Topbar (4 dropdown bar atas)
└── FilterableListPage            <- Logic FILTER (Modul 2-5)
    ├── TugasPage                 <- Modul 2
    ├── MasukPage                 <- Modul 3
    ├── DisposisiKeluarPage       <- Modul 4
    ├── ProgressSuratPage         <- Modul 5
    └── SuratFormBasePage         <- Logic FORM surat (Modul 6-7)
        ├── SuratDinasEksternalPage  <- Modul 6
        └── NotaDinasKeluarPage      <- Modul 7
```

Yang di bawah mewarisi semua method yang di atas. Contoh:
`SuratDinasEksternalPage` otomatis punya method dari `SuratFormBasePage`
+ `FilterableListPage` + `BasePage`.

### Isi tiap file penting

| File | Isi method utama |
|---|---|
| `base_page.py` | `click()`, `click_via_js()`, `type_text()`, `is_visible()`, `wait_loading_mask_gone()`, `find_visible_among()` (cari elemen yang benar-benar tampil) |
| `filterable_list_page.py` | `open_menu()`, `cari_otomatis()`, `clear_pencarian()`, `klik_filter()`, `pilih_jenis_filter()`, `isi_data_filter()`, `klik_cari_popup()`, `klik_reset_filter()` |
| `surat_form_base_page.py` | `klik_tambah()`, `upload_berkas_via_link()`, `isi_kepada()`/`pilih_jenis_surat()`/dll, `tambah_penyetuju()`/`tambah_penerima()`, `simpan_draft()`, `ajukan_penyetujuan()`, `pilih_draft_pertama()`, `klik_hapus()`, `klik_perubahan()` |
| `topbar_page.py` | `buka_semua_menu()` — klik tiap tombol topbar sekali untuk buka, cek dropdown, klik sekali lagi untuk tutup (toggle) |
| `conftest.py` | Fixture `driver` (session), fixture `test_data`, hook screenshot saat gagal, ringkasan hasil per modul (`STEP_LABELS`) + kotak "AUTOMATION TESTING RESULT" |

### Pola alur 1 test

Test cuma memanggil method "level tinggi" dari page object; method itu
di dalamnya memakai method dasar dari `BasePage`:

```
test → page method (level tinggi) → BasePage method (level rendah)
```

Kalau sebuah method tidak ada di file page yang sedang dibaca, berarti
diwarisi dari parent-nya (naik satu tingkat sesuai peta kelas di atas).

---

## Setup

### 1. Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Login Google SSO (sekali saja)

NewDLA login memakai tombol "Login with Google". Selenium tidak mengetik
email/password Google (diblokir Google) — solusinya Chrome yang dipakai
Selenium memakai profile yang session Google-nya sudah aktif:

1. Tutup semua jendela Chrome.
2. Jalankan Chrome dengan folder profile khusus:
   - Windows: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="D:\selenium-chrome-profile"`
   - Mac: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir="/Users/NAMA_KAMU/selenium-chrome-profile"`
3. Login manual pakai akun Google yang terdaftar di NewDLA, lalu tutup Chrome.
4. Set environment variable `DLA_CHROME_PROFILE` ke path yang sama, ATAU
   ubah langsung nilai default `CHROME_PROFILE_PATH` di `config/config.py`.

```bash
# Windows PowerShell
$env:DLA_CHROME_PROFILE = "D:\selenium-chrome-profile"

# Mac/Linux
export DLA_CHROME_PROFILE="/Users/nama_kamu/selenium-chrome-profile"
```

### 3. Menjalankan test

```bash
# Seluruh alur E2E (semua modul, 1 browser session)
pytest

# Hanya Dashboard (login dulu, wajib)
pytest -k "test_login or test_dashboard"

# Hanya Modul 6 (filter + draft + perubahan)
pytest -k "test_login or test_surat_keluar_eksternal or test_simpan_draft_pertama or test_hapus_draft or test_ubah_dan_ajukan"

# Hanya Topbar
pytest -k "test_login or test_topbar"

# Satu step spesifik
pytest tests/test_e2e_dla.py::TestE2EDlaFlow::test_hapus_draft

# Headless (untuk CI/CD)
$env:DLA_HEADLESS = "true"; pytest        # Windows PowerShell
DLA_HEADLESS=true pytest                  # Mac/Linux
```

> Kalau menjalankan SEBAGIAN method saja, browser tetap butuh login dulu
> — sertakan `test_login` di filter `-k`.

### 4. Data uji

Semua data uji terpusat di `data/test_data.json`:

- Tanggal dashboard, keyword pencarian & jenis filter per modul.
- Isian form Modul 6 (Kepada, Alamat, Perihal, Jenis Surat, dst) di
  bagian `surat_dinas_eksternal`.
- Keyword staf: `kata_kunci_penyetuju` (Yulia), `kata_kunci_penerima`
  (Ryco), `kata_kunci_penerima_baru` (Arru) + nomor baris checkbox.
- Upload berkas memakai opsi **Link** (`url_dokumen`), bukan file lokal.

Mau ganti data uji cukup edit JSON ini — tidak perlu sentuh kode.

### 5. Laporan

Setelah pytest selesai, buka `reports/report.html` — laporan
self-contained berisi ringkasan PASS/FAIL, detail tiap step, dan
screenshot otomatis saat ada yang gagal.

---

## Bantuan locator

Kalau ada elemen yang locator-nya berubah / belum pasti:

1. Jalankan Chrome dengan `--remote-debugging-port=9222` (profil selenium),
   login manual, buka halaman yang mau discan.
2. Jalankan `python tools/scan_locators_v2.py` — hasil kandidat locator
   (menyaring id auto-generate ExtJS) ditulis ke `reports/locator_scan.txt`.
3. Atau manual: klik kanan → **Inspect**, cek `data-qtip`, `itemId`,
   `name`, atau `class` yang stabil (hindari id seperti `button-1042`).
4. Update locator terkait di `pages/*_page.py`.

Prioritas locator di project ini: `data-qtip` > `itemId`/`name` > id
stabil > css selector > xpath berbasis teks.

---

## Catatan penting (pelajaran dari debugging)

- **SPA ExtJS menyimpan banyak elemen tersembunyi di DOM.** Jangan pakai
  `is_visible`/`find_first_visible` yang mengunci ke match pertama (bisa
  hidden) — pakai `find_visible_among` yang mencari elemen yang
  benar-benar tampil.
- **Tombol close popup pakai `img.x-tool-close`** — class `x-tool-close`
  ada di `<img>`, bukan `<div>`.
- **Jangan `driver.refresh()`** — reload grid cukup via ExtJS store
  (`_klik_muat_ulang()`), supaya sesi SPA tidak terputus.
- **Popup Advanced Filter menutup sendiri setelah CARI** — tidak perlu
  ESC/klik body (justru merusak state toolbar).
- **Lonceng notifikasi hanya ada di halaman Dashboard** — test Topbar
  navigasi ke Dashboard dulu sebelum buka dropdown.
- **Form Tambah punya 2 tombol "Tambah"** — index 0 = Penyetuju,
  index 1 = Penerima. Salah index = staf masuk section yang salah.
