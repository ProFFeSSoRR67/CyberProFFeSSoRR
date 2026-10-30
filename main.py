import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_channel_info(channel_id: str) -> dict:
    if not API_KEY:
        raise RuntimeError(
            "Не найден YOUTUBE_API_KEY в файле .env"
        )

    url = "https://www.googleapis.com/youtube/v3/channels"

    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY,
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    items = response.json().get("items", [])

    if not items:
        raise ValueError(
            "Канал не найден или данные недоступны"
        )

    channel = items[0]
    stats = channel["statistics"]

    return {
        "Название": channel["snippet"]["title"],
        "ID канала": channel["id"],
        "Подписчики": stats.get("subscriberCount", "Скрыто"),
        "Просмотры": stats.get("viewCount", 0),
        "Видео": stats.get("videoCount", 0),
    }


if __name__ == "__main__":
    # Тестовый публичный канал Google Developers
    channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

    try:
        info = get_channel_info(channel_id)

        print("\n=== YouTube Analytics ===")
        for name, value in info.items():
            print(f"{name}: {value}")

    except requests.HTTPError as error:
        print("Ошибка HTTP:", error.response.status_code)
        print(error.response.text[:1000])