from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")


def days_before(anchor: date, days: int) -> date:
    return anchor - timedelta(days=days)


def random_datetime_on_date(base_date: date, hour: int = 9, minute: int = 0) -> datetime:
    return datetime.combine(base_date, time(hour=hour, minute=minute), tzinfo=PACIFIC_TZ)


def add_hours(ts: datetime, hours: int) -> datetime:
    return ts + timedelta(hours=hours)


def add_minutes(ts: datetime, minutes: int) -> datetime:
    return ts + timedelta(minutes=minutes)
