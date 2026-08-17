import requests

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def notify_pushover(user_key: str, app_token: str, message: str, title: str = "Episode Downloader") -> None:
    response = requests.post(
        PUSHOVER_URL,
        data={
            "token": app_token,
            "user": user_key,
            "title": title,
            "message": message,
        },
        timeout=10,
    )
    response.raise_for_status()
