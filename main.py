from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from click_sequence import run_click_sequence
from config import load_config
from notifier import notify_pushover
from scraper import scrape_episode_links
from tabs import open_tabs
from vdh_trigger import xdotool_trigger


def build_driver(firefox_profile_path: str) -> webdriver.Firefox:
    options = FirefoxOptions()
    options.profile = firefox_profile_path
    options.add_argument("--width=1600")
    options.add_argument("--height=1200")
    return webdriver.Firefox(options=options)


def main() -> None:
    config = load_config()
    driver = build_driver(config.firefox_profile_path)

    try:
        urls = scrape_episode_links(driver, config.directory_url)
        print(f"Scraped {len(urls)} episode links.")

        handles = open_tabs(driver, urls)
        print(f"Opened {len(handles)} tabs.")

        vdh_trigger_fn = None if config.dry_run else xdotool_trigger

        for i, handle in enumerate(handles, start=1):
            print(f"Processing tab {i}/{len(handles)}...")
            run_click_sequence(driver, handle, vdh_trigger_fn)

        if not config.dry_run:
            notify_pushover(
                config.pushover_user_key,
                config.pushover_app_token,
                f"Done — issued clicks for {len(handles)} episodes.",
            )
            print("Sent Pushover notification.")
        else:
            print("Dry run complete — skipped VDH trigger and notification.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
