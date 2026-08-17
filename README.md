# Episode Downloader

Selenium script that scrapes an episode directory page, opens every episode
in its own Firefox tab, runs a fixed click sequence per tab (dismiss iframe
overlay → start playback → trigger Video DownloadHelper), then sends a
Pushover notification once all tabs are processed.

Runs on Linux, against your existing Firefox profile that already has Video
DownloadHelper (VDH) installed and configured to auto-save downloads (no
Save As dialog).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in .env: PUSHOVER_USER_KEY, PUSHOVER_APP_TOKEN
```

Getting Pushover credentials:
1. Log in / sign up at pushover.net.
2. Your **User Key** is on the dashboard — that's `PUSHOVER_USER_KEY`.
3. Under "Your Applications" → "Create an Application/API Token", name it
   (e.g. "Episode Downloader") and submit. The resulting **API Token/Key**
   is `PUSHOVER_APP_TOKEN`.

You'll also need `geckodriver` on PATH, and — depending on which VDH-trigger
technique the Stage 3 spike settles on — `xdotool` (`apt install xdotool`)
plus a real X11/Wayland display or `Xvfb`.

## Before running the full thing: build up confidence in stages

Do not skip straight to running `main.py` against the real episode list.
The VDH toolbar-popup click is a known hard problem (WebDriver can't click
browser chrome) — validate it in isolation first. See the plan doc this was
built from for full reasoning; short version:

1. **Stage 0** — `python spikes/spike_manifest_inspect.py <path-to-vdh.xpi>`
   Checks whether VDH has a custom keyboard shortcut for downloading
   directly (best case, avoids the whole coordinate-clicking problem).
   Find the `.xpi` under your profile's `extensions/` folder; find the
   profile via `about:support` → Profile Folder.

2. **Stage 1** — sanity check the scrape:
   ```bash
   python -c "
   from selenium import webdriver
   from selenium.webdriver.firefox.options import Options
   from scraper import scrape_episode_links
   opts = Options(); opts.profile = '<your-profile-path>'
   d = webdriver.Firefox(options=opts)
   print(scrape_episode_links(d, '<directory-url>'))
   d.quit()
   "
   ```
   Confirm the count and URLs match what you see on the page.

3. **Stage 2** — dry run (opens every tab, dismisses iframe, starts
   playback, skips VDH and the notification):
   ```bash
   python main.py --directory-url <url> --firefox-profile-path <path> --dry-run
   ```
   Get this fully solid across every tab before touching VDH.

4. **Stage 3** — isolate the VDH click on ONE tab. Try
   `spikes/spike_popup_tab.py` first (cheap, likely fails per the research
   — don't debug it hard). If it fails, calibrate and run
   `spikes/spike_xdotool_click.py`. Fill in the coordinates in
   `vdh_trigger.py`'s `TOOLBAR_ICON_POS` / `POPUP_DOWNLOAD_BTN_POS` (or
   implement `shortcut_trigger` if Stage 0 found a usable shortcut) once you
   have a technique that reliably works.

5. **Stage 4** — full loop, small batch first:
   ```bash
   python main.py --directory-url <url> --firefox-profile-path <path>
   ```
   Try it against 2-3 episodes' worth of a directory page before running
   against the full list. Check files land in the expected download folder
   with correct names.

6. **Stage 5** — Pushover fires once all tabs' clicks are issued (not once
   downloads are verified complete on disk — see main.py). Test standalone
   if you want to confirm delivery before a full run:
   ```bash
   python -c "
   from notifier import notify_pushover
   import os
   from dotenv import load_dotenv
   load_dotenv()
   notify_pushover(os.environ['PUSHOVER_USER_KEY'], os.environ['PUSHOVER_APP_TOKEN'], 'test')
   "
   ```

## Known open items (need the real machine to resolve)

- `click_sequence.py`'s iframe locator is generic (`iframe`) — tighten it
  if the real page has more than one iframe.
- `POST_PLAY_SETTLE_SECONDS` (currently a 3s sleep) is a placeholder for
  "how long until VDH detects the stream" — tune based on observed
  behavior, or replace with a poll on the video element's `currentTime`.
- Toolbar icon / popup button coordinates in `vdh_trigger.py` need
  calibrating on your actual screen/window layout (fixed Firefox window
  size, no other extensions shifting icon position).
