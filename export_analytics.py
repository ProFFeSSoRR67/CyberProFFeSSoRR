
import json
from datetime import date, timedelta
from pathlib import Path

from googleapiclient.discovery import build
from analytics import get_credentials

OUTPUT_FILE = Path("data/analytics.json")


def export_analytics():
    credentials = get_credentials()

    api = build(
        "youtubeAnalytics",
        "v2",
        credentials=credentials
    )

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=27)

    report = api.reports().query(
        ids="channel==MINE",
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        metrics=(
            "views,estimatedMinutesWatched,"
            "subscribersGained,subscribersLost"
        ),
        dimensions="day",
        sort="day"
    ).execute()

    daily = []

    for row in report.get("rows", []):
        day, views, minutes, gained, lost = row

        gained = int(gained)
        lost = int(lost)

        daily.append({
            "date": day,
            "views": int(views),
            "minutes": float(minutes),
            "subscribers_gained": gained,
            "subscribers_lost": lost,
            "subscribers_net": gained - lost
        })

    result = {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "last_data_date": (
            daily[-1]["date"] if daily else None
        ),
        "views_28": sum(
            day["views"] for day in daily
        ),
        "watch_hours_28": round(
            sum(day["minutes"] for day in daily) / 60, 1
        ),
        "subscribers_gained_28": sum(
            day["subscribers_gained"] for day in daily
        ),
        "subscribers_lost_28": sum(
            day["subscribers_lost"] for day in daily
        ),
        "subscribers_net_28": sum(
            day["subscribers_net"] for day in daily
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

    print("Экспорт завершён!")
    print("Просмотры:", result["views_28"])
    print("Прирост подписчиков:", result["subscribers_net_28"])
    print("Файл:", OUTPUT_FILE)


if __name__ == "__main__":
    export_analytics()
