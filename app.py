
import json
from pathlib import Path
import os
import time

import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

CHANNEL_ID = "UCP60ZnjF8PQDYMjMgOU3x7g"

_cache = {
    "data": None,
    "expires": 0
}


def get_youtube_stats():
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY не настроен")

    # Обновляем данные не чаще одного раза в 10 минут
    if _cache["data"] and time.time() < _cache["expires"]:
        return _cache["data"]

    response = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "snippet,statistics",
            "id": CHANNEL_ID,
            "key": api_key
        },
        timeout=15
    )

    response.raise_for_status()

    channels = response.json().get("items", [])

    if not channels:
        raise RuntimeError("YouTube-канал не найден")

    channel = channels[0]
    stats = channel["statistics"]

    data = {
        "channel": channel["snippet"]["title"],
        "subscribers": (
            None if stats.get("hiddenSubscriberCount")
            else int(stats.get("subscriberCount", 0))
        ),
        "videos": int(stats.get("videoCount", 0)),
        "total_views": int(stats.get("viewCount", 0))
    }

    _cache["data"] = data
    _cache["expires"] = time.time() + 600

    return data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    try:
        return jsonify(get_youtube_stats())
    except (requests.RequestException, RuntimeError, ValueError):
        app.logger.exception("Ошибка получения статистики")
        return jsonify({
            "error": "Статистика временно недоступна"
        }), 503

@app.route("/api/analytics")
def api_analytics():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "analytics.json"
    )

    if not file_path.exists():
        return jsonify({
            "error": "Отчёт пока не создан"
        }), 404

    try:
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        return jsonify(data)

    except (OSError, ValueError):
        app.logger.exception(
            "Ошибка чтения отчёта Analytics"
        )
        return jsonify({
            "error": "Не удалось загрузить аналитику"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
