"""Isolated, swappable implementations for triggering Video DownloadHelper's
download action. Which one actually works can only be determined on the
target Linux machine (see spikes/) — this module exists so the rest of the
pipeline never needs to change once a technique is chosen.

Fill in TOOLBAR_ICON_POS / POPUP_DOWNLOAD_BTN_POS after calibrating with
`xdotool getmouselocation` on the real machine (see spikes/spike_xdotool_click.py).
"""

import subprocess
import time

# Calibrate these on the target machine before using xdotool_trigger.
TOOLBAR_ICON_POS = (0, 0)  # (x, y) screen coords of the VDH toolbar icon
POPUP_DOWNLOAD_BTN_POS = (0, 0)  # (x, y) screen coords of the Download button in the opened popup


def xdotool_trigger(driver) -> None:
    """Click the VDH toolbar icon, then the Download button in the popup,
    using real OS-level mouse clicks via xdotool. Requires a real X11/Wayland
    display (or Xvfb) and a fixed Firefox window size/position so the
    coordinates stay valid run to run.
    """
    if TOOLBAR_ICON_POS == (0, 0) or POPUP_DOWNLOAD_BTN_POS == (0, 0):
        raise RuntimeError(
            "TOOLBAR_ICON_POS / POPUP_DOWNLOAD_BTN_POS not calibrated. "
            "Run spikes/spike_xdotool_click.py first."
        )

    subprocess.run(["xdotool", "mousemove", str(TOOLBAR_ICON_POS[0]), str(TOOLBAR_ICON_POS[1])], check=True)
    subprocess.run(["xdotool", "click", "1"], check=True)
    time.sleep(1)  # let the popup panel render
    subprocess.run(["xdotool", "mousemove", str(POPUP_DOWNLOAD_BTN_POS[0]), str(POPUP_DOWNLOAD_BTN_POS[1])], check=True)
    subprocess.run(["xdotool", "click", "1"], check=True)


def popup_tab_trigger(driver, extension_uuid: str, popup_path: str) -> None:
    """Fallback: open VDH's popup.html directly as a Selenium tab and click
    its Download button as normal DOM. Flagged in planning as likely to
    break VDH's active-tab detection (tabs.query({active, currentWindow})
    resolves relative to the popup's own tab once it's opened this way) —
    try this first since it's cheap, but don't debug it hard if it fails.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver.switch_to.new_window("tab")
    driver.get(f"moz-extension://{extension_uuid}/{popup_path}")

    # Selector is a placeholder — inspect the real popup DOM (Stage 0) to
    # find the actual Download button's id/class before relying on this.
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-action='download']"))
    ).click()


def shortcut_trigger(driver, key_combo: str) -> None:
    """Best-case path: if Stage 0's manifest inspection finds a custom VDH
    `commands` entry with an assignable shortcut for downloading directly,
    bind it in Firefox (about:addons -> gear -> Manage Extension Shortcuts)
    and send it here instead of clicking anything.
    """
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys

    # Example only — replace with the real combo once confirmed, e.g.:
    # ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys("d").key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
    raise NotImplementedError("Fill in once Stage 0 confirms a usable shortcut exists.")
