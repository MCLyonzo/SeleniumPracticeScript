import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Placeholder — replace with a poll on the video element's currentTime > 0
# via execute_script once real VDH detection timing is observed on the
# target machine.
POST_PLAY_SETTLE_SECONDS = 3


def dismiss_iframe_close_button(driver, timeout: int = 10) -> None:
    """#close-btn lives inside an iframe. Tighten the iframe locator here
    (by id/name/src) if the real page has more than one iframe."""
    iframe = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
    )
    driver.switch_to.frame(iframe)
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, "close-btn"))
    ).click()
    driver.switch_to.default_content()


def start_playback(driver, timeout: int = 10) -> None:
    """.vjs-big-play-button lives in normal page DOM, not in an iframe."""
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".vjs-big-play-button"))
    ).click()


def run_click_sequence(driver, tab_handle: str, vdh_trigger_fn=None) -> None:
    """Runs the fixed per-tab sequence: dismiss iframe overlay, start
    playback, then (if provided) trigger the VDH download.

    vdh_trigger_fn is optional so --dry-run can exercise steps 1-2 only.
    """
    driver.switch_to.window(tab_handle)

    dismiss_iframe_close_button(driver)
    start_playback(driver)

    time.sleep(POST_PLAY_SETTLE_SECONDS)

    if vdh_trigger_fn is not None:
        vdh_trigger_fn(driver)
