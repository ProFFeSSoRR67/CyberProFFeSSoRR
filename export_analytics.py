
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
    # Последние 12 месяцев, включая последний завершённый день.
    try:
        previous_year = end_date.replace(year=end_date.year - 1)
    except ValueError:
        previous_year = end_date.replace(year=end_date.year - 1, day=28)
    start_date = previous_year + timedelta(days=1)
    recent_start = end_date - timedelta(days=27)

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

    recent = [day for day in daily if day["date"] >= recent_start.isoformat()]
    result = {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "last_data_date": (
            daily[-1]["date"] if daily else None
        ),
        "views_28": sum(
            day["views"] for day in recent
        ),
        "watch_hours_28": round(
            sum(day["minutes"] for day in recent) / 60, 1
        ),
        "subscribers_gained_28": sum(
            day["subscribers_gained"] for day in recent
        ),
        "subscribers_lost_28": sum(
            day["subscribers_lost"] for day in recent
        ),
        "subscribers_net_28": sum(
            day["subscribers_net"] for day in recent
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
