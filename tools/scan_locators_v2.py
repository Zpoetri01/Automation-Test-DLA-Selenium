import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ==========================================================
# KONFIGURASI
# ==========================================================

REMOTE_DEBUGGING_ADDRESS = "127.0.0.1:9222"

SCAN_MODE = "all"  # all | popup

OUTPUT_FILE = "reports/locator_scan.txt"

POLA_ID_AUTO_GENERATE = re.compile(r"^[a-z]+-\d+$")


# ==========================================================
# CHROME
# ==========================================================

def sambungkan_ke_chrome():
    options = Options()
    options.debugger_address = REMOTE_DEBUGGING_ADDRESS
    return webdriver.Chrome(options=options)


# ==========================================================
# SCAN
# ==========================================================

def ambil_elemen(driver):

    css_scope = ".x-window" if SCAN_MODE == "popup" else ""

    script = r"""
    const scope = arguments[0]
        ? document.querySelector(arguments[0])
        : document;

    if (!scope) {
        return [];
    }

    const selector =
        'a, button, input, select, textarea,' +
        '[data-qtip], [onclick],' +
        '.x-btn, .x-form-field';

    const elements =
        Array.from(scope.querySelectorAll(selector));

    function getLabel(el){

        let label = '';

        try{

            if(el.labels && el.labels.length){
                label = el.labels[0].innerText;
            }

            if(!label && el.parentElement){
                label = el.parentElement.innerText;
            }

            if(!label){
                const row =
                    el.closest('div,td,tr');

                if(row){
                    label = row.innerText;
                }
            }

        }catch(e){}

        return (label || '')
            .replace(/\s+/g,' ')
            .trim()
            .slice(0,120);
    }

    return elements
        .filter(el => {

            const style =
                window.getComputedStyle(el);

            const rect =
                el.getBoundingClientRect();

            return (
                style.display !== 'none' &&
                style.visibility !== 'hidden' &&
                rect.width > 0 &&
                rect.height > 0
            );
        })
        .map(el => ({

            tag:
                el.tagName.toLowerCase(),

            type:
                el.getAttribute('type') || '',

            text:
                (el.innerText || el.value || '')
                    .replace(/\s+/g,' ')
                    .trim()
                    .slice(0,120),

            label:
                getLabel(el),

            id:
                el.getAttribute('id') || '',

            name:
                el.getAttribute('name') || '',

            item_id:
                el.getAttribute('itemid') || '',

            data_qtip:
                el.getAttribute('data-qtip') || '',

            class_name:
                el.getAttribute('class') || ''

        }));
    """

    return driver.execute_script(script, css_scope or None)


# ==========================================================
# LOCATOR
# ==========================================================

def kandidat_locator(e):

    hasil = []

    if e["data_qtip"]:
        hasil.append(
            f'(By.CSS_SELECTOR, "[data-qtip=\'{e["data_qtip"]}\']")'
        )

    if e["id"] and not POLA_ID_AUTO_GENERATE.match(e["id"]):
        hasil.append(
            f'(By.ID, "{e["id"]}")'
        )

    if e["name"]:
        hasil.append(
            f'(By.NAME, "{e["name"]}")'
        )

    if e["item_id"]:
        hasil.append(
            f'(By.CSS_SELECTOR, "[itemId=\'{e["item_id"]}\']")'
        )

    if e["text"]:
        text = e["text"].replace('"', "'")

        hasil.append(
            f'(By.XPATH, "//*[normalize-space(text())=\'{text}\']")'
        )

    if not hasil and e["class_name"]:
        cls = e["class_name"].split()[0]

        hasil.append(
            f'(By.CSS_SELECTOR, ".{cls}")'
        )

    return hasil


# ==========================================================
# KATEGORI
# ==========================================================

def kategori(e):

    tag = e["tag"]
    tipe = e["type"]

    if tag == "a":
        return "MENU_LINK"

    if tag == "button":
        return "BUTTON"

    if tipe == "checkbox":
        return "CHECKBOX"

    if tipe == "radio":
        return "RADIO"

    if tag == "select":
        return "DROPDOWN"

    if tag in ["input", "textarea"]:
        return "INPUT"

    return "LAINNYA"


# ==========================================================
# FORMAT OUTPUT
# ==========================================================

def format_output(data):

    lines = []

    grouped = {}

    for item in data:
        grouped.setdefault(
            kategori(item),
            []
        ).append(item)

    for cat, items in grouped.items():

        lines.append("")
        lines.append("=" * 100)
        lines.append(cat)
        lines.append("=" * 100)

        for e in items:

            title = (
                e["text"]
                or e["label"]
                or "(kosong)"
            )

            lines.append(
                f"<{e['tag']}> {title}"
            )

            if e["label"]:
                lines.append(
                    f"Label : {e['label']}"
                )

            for loc in kandidat_locator(e):
                lines.append(
                    f"    {loc}"
                )

            lines.append("-" * 100)

    return "\n".join(lines)


# ==========================================================
# MAIN
# ==========================================================

def main():

    print(
        f"Menyambung ke Chrome "
        f"{REMOTE_DEBUGGING_ADDRESS}"
    )

    driver = sambungkan_ke_chrome()

    print(
        f"Terhubung: {driver.title}"
    )

    data = ambil_elemen(driver)

    print(
        f"Elemen ditemukan: {len(data)}"
    )

    hasil = format_output(data)

    print("\n")
    print(hasil)

    Path("reports").mkdir(
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(hasil)

    print("\n")
    print(f"Hasil disimpan ke: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()