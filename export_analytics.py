
import json
from datetime import date, timedelta
from pathlib import Path

from googleapiclient.discovery import build

from analytics import get_credentials


OUTPUT_FILE = Path("data/analytics.json")


def export_analytics():
    credentials = get_credentials()

    youtube_analytics = build(
        "youtubeAnalytics",
        "v2",
        credentials=credentials
    )

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=27)

    report = youtube_analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        metrics="views,estimatedMinutesWatched",
        dimensions="day",
        sort="day"
    ).execute()

    rows = report.get("rows", [])

    daily = [
        {
            "date": row[0],
            "views": int(row[1]),
            "minutes": float(row[2])
        }
        for row in rows
    ]

    result = {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "last_data_date": daily[-1]["date"] if daily else None,
        "views_28": sum(day["views"] for day in daily),
        "watch_hours_28": round(
            sum(day["minutes"] for day in daily) / 60, 1
        ),
        "daily": daily
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Статистика успешно экспортирована!")
    print("Файл:", OUTPUT_FILE)
    print("Просмотры:", result["views_28"])
    print("Часы просмотра:", result["watch_hours_28"])
    print("Последний день данных:", result["last_data_date"])


if __name__ == "__main__":
    export_analytics()
