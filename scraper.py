from urllib.parse import urljoin

from selenium.webdriver.common.by import By


def scrape_episode_links(driver, directory_url: str) -> list[str]:
    """Load the directory page and return absolute URLs for every
    a.dark-episode-item inside #episodeList, in DOM order."""
    driver.get(directory_url)

    links = driver.find_elements(By.CSS_SELECTOR, "#episodeList a.dark-episode-item")
    hrefs = [link.get_attribute("href") for link in links]

    return [urljoin(directory_url, href) for href in hrefs if href]
