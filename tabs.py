def open_tabs(driver, urls: list[str]) -> list[str]:
    """Open every URL in its own new tab. Returns window handles in the
    same order as urls — captured at creation time since window_handles
    order is not guaranteed to match creation order."""
    handles = []
    for url in urls:
        driver.switch_to.new_window("tab")
        driver.get(url)
        handles.append(driver.current_window_handle)
    return handles
