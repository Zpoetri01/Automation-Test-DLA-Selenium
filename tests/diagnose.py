"""
Diagnostic script -- capture page state to understand locator issues.
Jalankan satu per satu untuk debug: python tests/diagnose.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config import config

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(0)

try:
    # Login
    driver.get("https://qa-dla.antm.tech/")
    import time
    time.sleep(8)  # Wait for redirect/login

    print("=== CURRENT URL ===")
    print(driver.current_url)

    # Check if dashboard loaded
    dashboard = driver.find_elements(By.CSS_SELECTOR, "[data-qtip='Dashboard']")
    print(f"\n=== DASHBOARD TAB: {len(dashboard)} elements ===")

    # Check FILTER elements
    print("\n=== ELEMENTS WITH 'FILTER' TEXT ===")
    filter_els = driver.find_elements(By.XPATH, "//*[contains(normalize-space(text()),'FILTER') or contains(normalize-space(text()),'Filter')]")
    for el in filter_els:
        try:
            tag = el.tag_name
            cls = el.get_attribute("class") or ""
            visible = el.is_displayed()
            text = el.text.strip()[:80]
            print(f"  <{tag}> class='{cls[:60]}' visible={visible} text='{text}'")
        except:
            pass

    # Check for buttons in toolbar
    print("\n=== TOOLBAR BUTTONS (a.x-btn) ===")
    btns = driver.find_elements(By.CSS_SELECTOR, "a.x-btn")
    for btn in btns:
        try:
            visible = btn.is_displayed()
            text = btn.text.strip()[:80]
            cls = btn.get_attribute("class") or ""
            if visible:
                print(f"  VISIBLE: text='{text}' class='{cls[:60]}'")
        except:
            pass

    # Check sidebar menu items
    print("\n=== SIDEBAR MENU ITEMS (data-qtip) ===")
    menu_items = driver.find_elements(By.CSS_SELECTOR, "[data-qtip]")
    for item in menu_items:
        try:
            qtip = item.get_attribute("data-qtip") or ""
            visible = item.is_displayed()
            tag = item.tag_name
            if visible and qtip:
                print(f"  <{tag}> qtip='{qtip}'")
        except:
            pass

    # Try clicking Tugas menu
    print("\n=== TRY CLICK TUGAS MENU ===")
    tugas = driver.find_elements(By.CSS_SELECTOR, "[data-qtip='Tugas']")
    print(f"Tugas elements found: {len(tugas)}")
    for t in tugas:
        print(f"  visible={t.is_displayed()} displayed={t.is_displayed()}")

    # Check for loading masks
    print("\n=== LOADING MASKS ===")
    masks = driver.find_elements(By.CSS_SELECTOR, "div.x-mask, div.x-mask-msg")
    for m in masks:
        try:
            print(f"  visible={m.is_displayed()} class='{m.get_attribute('class')[:60]}'")
        except:
            pass

    # Check for advanced filter elements
    print("\n=== ADVANCED FILTER ELEMENTS ===")
    af_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='tampilcombo']")
    print(f"input[name='tampilcombo']: {len(af_inputs)}")
    for inp in af_inputs:
        print(f"  visible={inp.is_displayed()}")

    cari_btns = driver.find_elements(By.XPATH, "//*[contains(normalize-space(text()),'CARI') or contains(normalize-space(text()),'Cari')]")
    print(f"CARI buttons: {len(cari_btns)}")
    for btn in cari_btns:
        try:
            print(f"  visible={btn.is_displayed()} text='{btn.text.strip()[:60]}' tag={btn.tag_name}")
        except:
            pass

    # Navigate to Tugas page
    print("\n=== NAVIGATE TO TUGAS PAGE ===")
    tugas = driver.find_element(By.CSS_SELECTOR, "[data-qtip='Tugas']")
    driver.execute_script("arguments[0].click();", tugas)

    # Wait for page to load
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.x-mask"))
        )
        print("Loading mask cleared")
    except:
        print("Loading mask still present or timeout")

    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='Tugas']"))
        )
        print("Tugas header visible")
    except:
        print("Tugas header NOT visible")

    time.sleep(3)

    # Check ALL visible toolbar buttons on Tugas page
    print("\n=== ALL VISIBLE TOOLBAR BUTTONS ON TUGAS PAGE ===")
    all_btns = driver.find_elements(By.CSS_SELECTOR, "a.x-btn")
    for i, btn in enumerate(all_btns):
        try:
            visible = btn.is_displayed()
            if visible:
                text = btn.text.strip()[:80]
                qtip = btn.get_attribute("data-qtip") or ""
                cls = btn.get_attribute("class") or ""
                print(f"  [{i}] text='{text}' qtip='{qtip}' cls='{cls[:80]}'")
        except:
            pass

    # Check icon-only buttons specifically
    print("\n=== ICON-ONLY BUTTONS (x-btn-plain-t) ON TUGAS PAGE ===")
    plain_btns = driver.find_elements(By.CSS_SELECTOR, "a.x-btn-plain-t")
    for i, btn in enumerate(plain_btns):
        try:
            visible = btn.is_displayed()
            qtip = btn.get_attribute("data-qtip") or ""
            cls = btn.get_attribute("class") or ""
            print(f"  [{i}] visible={visible} qtip='{qtip}' cls='{cls[:80]}'")
        except:
            pass

    # Check for any filter-related elements
    print("\n=== FILTER-RELATED ON TUGAS PAGE ===")
    filter_qtip = driver.find_elements(By.CSS_SELECTOR, "[data-qtip*='ilter'], [data-qtip*='ILTER']")
    for el in filter_qtip:
        try:
            visible = el.is_displayed()
            qtip = el.get_attribute("data-qtip") or ""
            tag = el.tag_name
            print(f"  <{tag}> qtip='{qtip}' visible={visible}")
        except:
            pass
    if not filter_qtip:
        print("  NONE found!")

    # Check dropdown posisi
    print("\n=== DROPDOWN POSISI ON TUGAS PAGE ===")
    posisi_inputs = driver.find_elements(By.XPATH, "//input[@value='Semua' or @value='Primary Position' or @value='Secondary Position']")
    for inp in posisi_inputs:
        print(f"  visible={inp.is_displayed()} value='{inp.get_attribute('value')}'")

    # CLICK FILTER BUTTON and see what happens
    print("\n=== CLICK FILTER BUTTON ===")
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Find visible FILTER element
    filter_locator = (By.XPATH, "//*[normalize-space(text())='FILTER' or normalize-space(text())='Filter']")
    filter_els = driver.find_elements(*filter_locator)
    visible_filters = [e for e in filter_els if e.is_displayed()]
    print(f"FILTER elements: {len(filter_els)} total, {len(visible_filters)} visible")

    if visible_filters:
        el = visible_filters[0]
        print(f"Clicking: tag={el.tag_name} text='{el.text.strip()[:50]}'")
        driver.execute_script("arguments[0].click();", el)
        time.sleep(3)

        # Check what appeared
        masks = driver.find_elements(By.CSS_SELECTOR, "div.x-mask")
        visible_masks = [m for m in masks if m.is_displayed()]
        print(f"Visible loading masks: {len(visible_masks)}")

        # Check for CARI button
        cari = driver.find_elements(By.XPATH, "//*[normalize-space(text())='CARI' or normalize-space(text())='Cari']")
        visible_cari = [c for c in cari if c.is_displayed()]
        print(f"CARI buttons: {len(cari)} total, {len(visible_cari)} visible")
        for c in visible_cari:
            print(f"  visible CARI: tag={c.tag_name} text='{c.text.strip()[:50]}'")

        # Check for tampilcombo
        combo = driver.find_elements(By.CSS_SELECTOR, "input[name='tampilcombo']")
        visible_combo = [c for c in combo if c.is_displayed()]
        print(f"tampilcombo: {len(combo)} total, {len(visible_combo)} visible")

        # Check for any new popup/window
        windows = driver.find_elements(By.CSS_SELECTOR, "div.x-window")
        visible_windows = [w for w in windows if w.is_displayed()]
        print(f"ExtJS windows: {len(windows)} total, {len(visible_windows)} visible")

        # Dump ALL visible elements with text containing "filter" or "cari" or "reset"
        print("\n=== ALL VISIBLE ELEMENTS WITH KEYWORDS ===")
        for kw in ["FILTER", "Filter", "CARI", "Cari", "RESET", "Reset", "Advanced"]:
            els = driver.find_elements(By.XPATH, f"//*[contains(normalize-space(text()),'{kw}')]")
            for e in els:
                if e.is_displayed():
                    print(f"  '{kw}': <{e.tag_name}> text='{e.text.strip()[:60]}' class='{(e.get_attribute('class') or '')[:60]}'")

finally:
    print("\n=== DONE ===")
    driver.quit()
