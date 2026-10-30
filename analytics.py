
import os
from datetime import date, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ------------------------------------------
# НАСТРОЙКИ
# ------------------------------------------

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

# Отчёт за последние 28 завершённых дней.
# YouTube Analytics может обновлять данные с задержкой.
END_DATE = date.today() - timedelta(days=1)
START_DATE = END_DATE - timedelta(days=27)


# ------------------------------------------
# GOOGLE OAUTH
# ------------------------------------------

def get_credentials():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        try:
            credentials = Credentials.from_authorized_user_file(
                TOKEN_FILE, SCOPES
            )
        except (ValueError, OSError):
            credentials = None

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception:
            credentials = None

    if not credentials or not credentials.valid:
        if not os.path.exists(CLIENT_SECRET_FILE):
            raise FileNotFoundError(
                f"Не найден файл {CLIENT_SECRET_FILE}. "
                "Помести его в папку проекта."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES
        )

        credentials = flow.run_local_server(
            port=0,
            prompt="select_account consent"
        )

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(credentials.to_json())

    return credentials


# ------------------------------------------
# ИНФОРМАЦИЯ О КАНАЛЕ
# ------------------------------------------

def show_channel(youtube):
    response = youtube.channels().list(
        part="snippet,statistics",
        mine=True
    ).execute()

    channels = response.get("items", [])

    if not channels:
        print("Не удалось определить канал для этой авторизации.")
        return None

    # Обычно API возвращает канал, связанный с авторизацией.
    channel = channels[0]
    snippet = channel["snippet"]
    statistics = channel.get("statistics", {})
    channel_id = channel["id"]

    print("\n" + "=" * 45)
    print(" ИНФОРМАЦИЯ О КАНАЛЕ")
    print("=" * 45)
    print(f"Название: {snippet.get('title', 'Неизвестно')}")
    print(f"ID канала: {channel_id}")
    print(f"Ссылка: https://www.youtube.com/channel/{channel_id}")
    print(f"Пользовательский URL: {snippet.get('customUrl', 'Нет')}")
    print(f"Подписчики: {statistics.get('subscriberCount', 'Нет данных')}")
    print("=" * 45)

    return channel_id


# ------------------------------------------
# ЕЖЕДНЕВНАЯ АНАЛИТИКА
# ------------------------------------------

def show_analytics(analytics):
    start_date = START_DATE.isoformat()
    end_date = END_DATE.isoformat()

    print("\n" + "=" * 65)
    print(" АНАЛИТИКА КАНАЛА")
    print(f" Период: {start_date} — {end_date}")
    print("=" * 65)

    report = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date,
        endDate=end_date,
        metrics="views,estimatedMinutesWatched",
        dimensions="day",
        sort="day"
    ).execute()

    rows = report.get("rows", [])

    if not rows:
        print("За этот период API не вернул данных.")
        return

    total_views = 0
    total_minutes = 0

    print(f"{'Дата':<14}{'Просмотры':>14}{'Минуты просмотра':>22}")
    print("-" * 50)

    for row in rows:
        day, views, minutes = row

        views = int(views or 0)
        minutes = int(minutes or 0)

        total_views += views
        total_minutes += minutes

        print(f"{day:<14}{views:>14,}{minutes:>22,}")

    print("-" * 50)
    print(f"{'ИТОГО':<14}{total_views:>14,}{total_minutes:>22,}")
    print("=" * 65)


# ------------------------------------------
# ЗАПУСК ПРОГРАММЫ
# ------------------------------------------

def main():
    try:
        credentials = get_credentials()

        youtube = build(
            "youtube",
            "v3",
            credentials=credentials
        )

        analytics = build(
            "youtubeAnalytics",
            "v2",
            credentials=credentials
        )

        channel_id = show_channel(youtube)

        if not channel_id:
            return

        show_analytics(analytics)

    except HttpError as error:
        print("\nОшибка Google API:")
        print(error)

        print(
            "\nПроверь права доступа к каналу, настройки API "
            "и выбранный Google-аккаунт."
        )

    except FileNotFoundError as error:
        print(f"\nОшибка файла: {error}")

    except Exception as error:
        print(f"\nПроизошла ошибка: {error}")


if __name__ == "__main__":
    main()
