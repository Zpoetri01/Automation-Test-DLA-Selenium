# 🤖 Automation Testing NewDLA

> **Selenium + Python + Pytest** · Pengujian end-to-end aplikasi **NewDLA** (SPA ExtJS)
> dengan pendekatan **Page Object Model (POM)** dan **data-driven testing**.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13.2-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.13.2">
  <img src="https://img.shields.io/badge/Selenium-4.45.0-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium 4.45.0">
  <img src="https://img.shields.io/badge/Pytest-9.1.1-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="Pytest 9.1.1">
  <img src="https://img.shields.io/badge/Status-20%20passed%20%C2%B7%200%20failed-2EA043?style=flat-square" alt="Status: 20 passed, 0 failed">
</p>

---

## 📌 Ringkasan

Proyek ini adalah automation testing untuk aplikasi **NewDLA** yang dibangun
dengan **Python** dan **Selenium WebDriver** di atas framework **Pytest**.
Seluruh alur pengujian end-to-end (dari **Login** hingga **Logout**)
dijalankan dalam **satu sesi browser** tanpa perlu me-refresh halaman.

| Aspek | Penerapan |
|---|---|
| **Pola desain** | Page Object Model (POM) — setiap modul memiliki kelas page-nya sendiri |
| **Data uji** | Terpusat di `data/test_data.json` — ganti data tanpa mengubah kode |
| **Sesi browser** | `scope="session"` — Chrome dibuka sekali untuk seluruh alur |
| **Laporan** | HTML otomatis (`reports/report.html`) + screenshot saat test gagal |
| **Fleksibilitas** | 6 environment variable untuk menyesuaikan URL, profil Chrome, timeout, dll. |

## ✅ Status Pengujian

> **Status terakhir: 20 test steps (14 modul) passed, 0 failed** — durasi ±12–13 menit.

```
========================================
       AUTOMATION TESTING RESULT
========================================
V [Login] berhasil
V [Dashboard] berhasil
V [Tugas] berhasil
V [Masuk] berhasil
V [Disposisi Keluar] berhasil
V [Progress Surat] berhasil
V [Surat Keluar Eksternal] berhasil
V [Tambah Surat] berhasil
V [Hapus Draft] berhasil
V [Perubahan Surat] berhasil
V [Nota Dinas Keluar] berhasil
V [Detail Surat] berhasil
V [Topbar] berhasil
V [Logout] berhasil
========================================
TOTAL TEST : 14
PASSED     : 14
FAILED     : 0
STATUS     : PASSED
========================================
```

## 📑 Daftar Isi

1. [Ringkasan](#ringkasan)
2. [Status Pengujian](#status-pengujian)
3. [Alur Pengujian](#alur-pengujian)
4. [Arsitektur](#arsitektur)
5. [Struktur Kode](#struktur-kode)
6. [Struktur Folder](#struktur-folder)
7. [Setup](#setup) — install, environment variables, login SSO, menjalankan test, data uji, laporan

---

## 🧭 Alur Pengujian

Berikut urutan 20 langkah pengujian sesuai isi `tests/test_e2e_dla.py`,
dikelompokkan per modul:

| Step | Modul | Test method | Alur / yang diperiksa |
|:---:|---|---|---|
| 1 | Login | `test_login` | Login melalui SSO Google |
| 2 | Dashboard | `test_dashboard_buka` | Halaman dashboard tampil |
| 3 | Dashboard | `test_dashboard_widget` | 4 widget tampil |
| 4 | Dashboard | `test_dashboard_rentang_tanggal` | Klik ikon Rentang Tanggal |
| 5 | Dashboard | `test_dashboard_popup_tanggal` | Pop-up tanggal muncul |
| 6 | Dashboard | `test_dashboard_pilih_tanggal` | Isi tanggal awal & akhir |
| 7 | Dashboard | `test_dashboard_cari` | Klik tombol Cari |
| 8 | Dashboard | `test_dashboard_verifikasi` | Data dashboard telah diperbarui |
| 9 | Tugas | `test_tugas` | Buka menu → pencarian → Advanced Filter |
| 10 | Masuk | `test_masuk` | Buka menu → pencarian → Advanced Filter |
| 11 | Disposisi Keluar | `test_disposisi_keluar` | Buka menu → pencarian → Advanced Filter |
| 12 | Progress Surat | `test_progress_surat` | Buka menu → pencarian → Advanced Filter |
| 13 | Surat Keluar Eksternal | `test_surat_keluar_eksternal` | Pencarian → Advanced Filter → CARI → buka filter lagi → **RESET** |
| 14 | Surat Keluar Eksternal | `test_simpan_draft_pertama` | Tambah → upload via Link → isi form → penyetuju (Yulia) → penerima (Ryco) → Simpan Draft |
| 15 | Surat Keluar Eksternal | `test_hapus_draft` | Pilih draft → Hapus → Ya → OK |
| 16 | Surat Keluar Eksternal | `test_ubah_dan_ajukan` | Draft kedua → Perubahan → hapus penerima Ryco → tambah Arru → Ajukan Penyetujuan |
| 17 | Nota Dinas Keluar | `test_nota_dinas_keluar` | Pencarian → Advanced Filter (Disetujui) |
| 18 | Nota Dinas Keluar | `test_detail_surat` | Detail surat → Log Aktifitas → tutup pop-up |
| 19 | Topbar | `test_topbar` | 4 dropdown: lonceng, notifikasi agenda, kelola surat, pengaturan |
| 20 | Logout | `test_logout` | Logout → kembali ke halaman login |

> 💡 **Ketergantungan antar-langkah** — langkah dalam satu modul saling
> bergantung (misalnya `test_hapus_draft` memerlukan draft dari
> `test_simpan_draft_pertama`), sehingga satu modul sebaiknya dijalankan
> lengkap dan berurutan.

---

## 🏗️ Arsitektur

```
conftest.py (fixture driver session + test_data + hook screenshot)
    │
    ▼
tests/test_e2e_dla.py   ──memanggil──▶  page object (pages/*_page.py)
    │                                        │
    │  data dari test_data.json              ▼
    │                            base_page.py (helper Selenium + ExtJS)
    ▼
Selenium WebDriver ──▶ Chrome (aplikasi NewDLA, SPA ExtJS)
```

1. **Page Object Model (POM)** — setiap halaman/modul memiliki satu kelas di
   `pages/` yang berisi locator dan method aksi. Test tidak berinteraksi
   langsung dengan Selenium, melainkan hanya memanggil method "tingkat
   tinggi" dari page object.
2. **Inheritance bertingkat** — logic yang dipakai banyak modul dinaikkan ke
   parent class: `BasePage` (helper umum) → `FilterableListPage` (filter,
   Modul 2–5) → `SuratFormBasePage` (form surat, Modul 6–7).
3. **Data-driven** — seluruh data uji terpusat di `data/test_data.json` dan
   dimuat lewat fixture `test_data` di `conftest.py`, sehingga data uji
   dapat diganti tanpa mengubah kode.
4. **Satu sesi browser** — fixture `driver` ber-scope `session` di
   `conftest.py`, sehingga Chrome dibuka satu kali dari Login hingga
   Logout. Hook `pytest_runtest_makereport` otomatis mengambil screenshot
   saat test gagal dan mencetak kotak "AUTOMATION TESTING RESULT" di akhir
   pengujian.
5. **Helper khusus ExtJS** — karena NewDLA adalah SPA berbasis ExtJS
   (banyak elemen tersembunyi di DOM, id dibuat otomatis, loading mask),
   `BasePage` menyediakan helper seperti `find_visible_among()` (mencari
   elemen yang benar-benar tampil), `click_visible_among()`,
   `wait_loading_mask_gone()`, dan pencarian elemen di dalam *active
   window*.

## 🧬 Struktur Kode

### Peta Kelas (Inheritance)

```
BasePage                          <- Fondasi SEMUA halaman
├── LoginPage                     <- Login + Logout
├── DashboardPage                 <- Modul 1 (Dashboard)
├── TopbarPage                    <- Modul Topbar (4 dropdown bar atas)
└── FilterableListPage            <- Logic FILTER (Modul 2-5)
    ├── TugasPage                 <- Modul 2 (Tugas)
    ├── MasukPage                 <- Modul 3 (Masuk)
    ├── DisposisiKeluarPage       <- Modul 4 (Disposisi Keluar)
    ├── ProgressSuratPage         <- Modul 5 (Progress Surat)
    └── SuratFormBasePage         <- Logic FORM surat (Modul 6-7)
        ├── SuratDinasEksternalPage  <- Modul 6 (Surat Keluar Eksternal)
        └── NotaDinasKeluarPage      <- Modul 7 (Nota Dinas Keluar)
```

Kelas yang berada di bawah mewarisi seluruh method dari kelas di atasnya.
Sebagai contoh, `SuratDinasEksternalPage` otomatis memiliki method dari
`SuratFormBasePage`, `FilterableListPage`, dan `BasePage`.

### Isi Setiap File Penting

| File | Method utama |
|---|---|
| `base_page.py` | `click()`, `click_via_js()`, `type_text()`, `type_text_visible()`, `find()`, `find_all()`, `find_visible_among()`, `find_active_window()`, `click_visible_among()`, `wait_loading_mask_gone()`, `take_screenshot()`, `pace()`, `dump_network_requests()` |
| `filterable_list_page.py` | `open_menu()`, `pilih_posisi()`, `cari_otomatis()`, `clear_pencarian()`, `klik_filter()`, `pilih_jenis_filter()`, `centang_checkbox_filter()`, `isi_data_filter()`, `klik_cari_popup()`, `klik_reset_filter()` |
| `surat_form_base_page.py` | `klik_tambah()`, `upload_berkas_via_link()`, `isi_form()`, `tambah_penyetuju()`, `tambah_penerima()`, `tambah_penerima_baru()`, `simpan_draft()`, `pilih_draft_pertama()`, `klik_hapus()`, `klik_perubahan()`, `ajukan_perubahan()`, `ajukan_penyetujuan()`, `klik_ya_konfirmasi()`, `klik_ok_notifikasi()` |
| `topbar_page.py` | `buka_semua_menu()` — klik tiap tombol topbar satu kali untuk membuka dropdown, memeriksa isinya, lalu klik sekali lagi untuk menutup (toggle) |
| `conftest.py` | Fixture `driver` (session), fixture `test_data`, hook screenshot + dump DOM saat test gagal, ringkasan hasil per modul (`STEP_LABELS`) dan kotak "AUTOMATION TESTING RESULT" |

### Pola Alur Satu Test

Test hanya memanggil method "tingkat tinggi" dari page object; method
tersebut di dalamnya menggunakan method dasar dari `BasePage`:

```
test → page method (tingkat tinggi) → BasePage method (tingkat rendah)
```

Apabila sebuah method tidak ditemukan di file page yang sedang dibaca,
berarti method tersebut diwarisi dari parent class-nya (lihat peta kelas
di atas).

## 📁 Struktur Folder

```
test_fixed/
├── conftest.py                       <- driver session-scoped + ringkasan hasil terminal
├── pytest.ini                        <- konfigurasi pytest + laporan HTML otomatis
├── requirements.txt                  <- daftar dependency Python
├── README.md                         <- dokumentasi proyek (file ini)
├── .gitignore                        <- pola file yang tidak di-commit
├── selenium-chrome-profile/          <- profil Chrome untuk SSO Google (data mesin lokal, TIDAK di-commit)
├── config/
│   └── config.py                     <- URL, timeout, chrome profile, headless
├── data/
│   └── test_data.json                <- SEMUA data uji (keyword, isian form, staf, dll.)
├── pages/
│   ├── base_page.py                  <- fungsi dasar Selenium (klik, ketik, tunggu)
│   ├── login_page.py                 <- Login + Logout
│   ├── dashboard_page.py             <- Modul 1 (widget, rentang tanggal)
│   ├── filterable_list_page.py       <- logic filter bersama Modul 2-5
│   ├── tugas_page.py                 <- Modul 2 (Tugas)
│   ├── masuk_page.py                 <- Modul 3 (Masuk)
│   ├── disposisi_keluar_page.py      <- Modul 4 (Disposisi Keluar)
│   ├── progress_surat_page.py        <- Modul 5 (Progress Surat)
│   ├── surat_form_base_page.py       <- logic form surat bersama Modul 6-7
│   ├── surat_dinas_eksternal_page.py <- Modul 6 (Surat Keluar Eksternal)
│   ├── nota_dinas_keluar_page.py     <- Modul 7 (Nota Dinas Keluar)
│   └── topbar_page.py                <- Modul Topbar (4 dropdown bar atas)
├── tests/
│   └── test_e2e_dla.py               <- SATU file, alur berurutan semua modul
├── tools/
│   ├── scan_locators_v2.py           <- scan locator halaman aktif (butuh Chrome port 9222)
│   ├── scan_topbar_sekarang.py       <- scan locator topbar halaman aktif (butuh Chrome port 9222)
│   ├── scan_topbar_dropdown.py       <- scan isi dropdown topbar (Kelola Surat / Notifikasi)
│   └── scan_topbar_raw.py            <- dump HTML area topbar
└── reports/
    ├── report.html                   <- laporan HTML hasil pytest (self-contained)
    └── screenshots/                  <- screenshot otomatis saat test gagal (tidak di-commit)
```

| Bagian | Fungsi |
|---|---|
| `pages/` | Menyimpan locator serta aksi/interaksi pada setiap halaman |
| `tests/` | Berisi skenario pengujian |
| `conftest.py` | Mengatur driver, fixture, hasil PASS/FAIL, dan screenshot |
| `data/` | Menyimpan data yang digunakan untuk pengujian |
| `config/` | Menyimpan URL, timeout, dan konfigurasi lainnya |
| `tools/` | Alat bantu untuk mencari locator |
| `reports/` | Menyimpan hasil dan laporan pengujian |

---

## 🚀 Setup

### 1. Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

> ✅ **Versi teruji pada proyek ini:** Python 3.13.2 · Selenium 4.45.0 ·
> Pytest 9.1.1 · pytest-html 4.2.0
>
> ⚠️ **Prasyarat:** Google Chrome terinstal, dan akun Google yang
> terdaftar di NewDLA (untuk SSO).

### 2. Environment Variables (Opsional)

Project ini **TIDAK memakai file `.env`** — semua konfigurasi dibaca dari
environment variable lewat `os.getenv()` di `config/config.py`. Karena
setiap variabel punya nilai default, project bisa langsung dijalankan
tanpa menyetel apa pun:

| Variable | Default | Fungsi |
|---|---|---|
| `DLA_BASE_URL` | `https://qa-dla.antm.tech/` | URL aplikasi yang diuji |
| `DLA_CHROME_PROFILE` | `D:\selenium-chrome-profile` | Path profil Chrome yang sesi Google-nya sudah aktif |
| `DLA_HEADLESS` | `false` | `true` → Chrome tanpa jendela (untuk CI/CD) |
| `DLA_TIMEOUT` | `15` | Timeout default WebDriverWait (detik) |
| `DLA_LONG_TIMEOUT` | `30` | Timeout proses lambat (grid setelah CARI, upload dokumen) |
| `DLA_ACTION_PACE` | `2` | Jeda antar-aksi (detik) — kebutuhan visual saja, bukan untuk menunggu elemen |

Cara menyetel:

```powershell
# Windows PowerShell
$env:DLA_HEADLESS = "true"
$env:DLA_CHROME_PROFILE = "D:\Magang\ANTAM\test_fixed\selenium-chrome-profile"
```

```bash
# Mac/Linux
export DLA_HEADLESS=true
export DLA_CHROME_PROFILE="/Users/nama_kamu/selenium-chrome-profile"
```

> 💡 Variabel hanya berlaku di sesi terminal tempat ia disetel. Tulis di
> profil shell (mis. `$PROFILE` PowerShell) kalau ingin permanen.

### 3. Login Google SSO (Sekali Saja)

Aplikasi NewDLA memakai tombol **"Login with Google"**. Selenium tidak
mengetik email/password Google secara langsung karena diblokir oleh
Google — solusinya, Chrome yang dipakai Selenium menggunakan profile yang
sesi Google-nya sudah aktif.

Di mesin ini, folder profil sudah tersedia di dalam project
(`selenium-chrome-profile/`) dan otomatis dipakai bila
`DLA_CHROME_PROFILE` disetel ke path tersebut. Untuk mesin/anggota tim
baru, buat profilnya dulu:

1. Tutup semua jendela Chrome.
2. Jalankan Chrome dengan folder profile khusus:
   - **Windows:** `"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="D:\selenium-chrome-profile"`
   - **Mac:** `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir="/Users/NAMA_KAMU/selenium-chrome-profile"`
3. Login manual memakai akun Google yang terdaftar di NewDLA, lalu tutup Chrome.
4. Set environment variable `DLA_CHROME_PROFILE` ke path yang sama (lihat
   tabel di atas), ATAU ubah langsung nilai default `CHROME_PROFILE_PATH`
   di `config/config.py`.

> 🔒 Profil Chrome berisi data sesi pribadi — folder
> `selenium-chrome-profile/` sudah terdaftar di `.gitignore` dan tidak
> akan ikut ter-commit.

### 4. Menjalankan Test

```bash
# Seluruh alur E2E (semua modul, 1 browser session)
pytest

# Alternatif: lewat marker e2e (terdaftar di pytest.ini)
pytest -m e2e

# Hanya Modul 1 - Dashboard
pytest -k "test_login or test_dashboard"

# Hanya Modul 2 - Tugas
pytest -k "test_login or test_tugas"

# Hanya Modul 3 - Masuk
pytest -k "test_login or test_masuk"

# Hanya Modul 4 - Disposisi Keluar
pytest -k "test_login or test_disposisi_keluar"

# Hanya Modul 5 - Progress Surat
pytest -k "test_login or test_progress_surat"

# Hanya Modul 6 - Surat Keluar Eksternal (filter + draft + hapus + perubahan + ajukan)
pytest -k "test_login or test_surat_keluar_eksternal or test_simpan_draft_pertama or test_hapus_draft or test_ubah_dan_ajukan"

# Hanya Modul 7 - Nota Dinas Keluar (filter + detail surat)
pytest -k "test_login or test_nota_dinas_keluar or test_detail_surat"

# Hanya Topbar
pytest -k "test_login or test_topbar"

# Hanya Logout
pytest -k "test_login or test_logout"

# Satu step spesifik
pytest tests/test_e2e_dla.py::TestE2EDlaFlow::test_hapus_draft

# Headless (untuk CI/CD)
$env:DLA_HEADLESS = "true"; pytest        # Windows PowerShell
DLA_HEADLESS=true pytest                  # Mac/Linux
```

> 💡 Apabila hanya sebagian method yang dijalankan, browser tetap
> memerlukan login terlebih dahulu — sertakan `test_login` pada filter
> `-k`.

### 5. Data Uji

Seluruh data uji terpusat di `data/test_data.json`:

- Tanggal dashboard, keyword pencarian, dan jenis filter untuk setiap modul.
- Isian form Modul 6 (Kepada, Alamat, Perihal, Jenis Surat, dan
  lain-lain) di bagian `surat_dinas_eksternal`.
- Keyword staf: `kata_kunci_penyetuju` (Yulia), `kata_kunci_penerima`
  (Ryco), `kata_kunci_penerima_baru` (Arru) beserta nomor baris checkbox.
- Upload berkas memakai opsi **Link** (`url_dokumen`), bukan file lokal.

Untuk mengubah data uji, cukup mengedit file JSON ini — tidak perlu
mengubah kode.

### 6. Laporan

Setelah pytest selesai dijalankan, buka `reports/report.html` — laporan
**self-contained** yang berisi ringkasan PASS/FAIL, detail setiap step,
dan screenshot otomatis apabila ada test yang gagal.

---

<p align="center">
  <em>Dokumentasi ini mengikuti kondisi aktual repositori `test_fixed`.</em>
</p>
