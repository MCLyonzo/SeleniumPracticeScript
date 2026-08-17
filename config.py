import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    directory_url: str
    firefox_profile_path: str
    dry_run: bool
    pushover_user_key: str
    pushover_app_token: str


def load_config() -> Config:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Bulk episode downloader via Selenium + Video DownloadHelper")
    parser.add_argument("--directory-url", required=True, help="URL of the page containing #episodeList")
    parser.add_argument("--firefox-profile-path", required=True, help="Path to the existing Firefox profile with VDH installed")
    parser.add_argument("--dry-run", action="store_true", help="Scrape + open tabs + run iframe/play clicks only; skip VDH trigger and Pushover notification")
    args = parser.parse_args()

    return Config(
        directory_url=args.directory_url,
        firefox_profile_path=args.firefox_profile_path,
        dry_run=args.dry_run,
        pushover_user_key=os.environ.get("PUSHOVER_USER_KEY", ""),
        pushover_app_token=os.environ.get("PUSHOVER_APP_TOKEN", ""),
    )
