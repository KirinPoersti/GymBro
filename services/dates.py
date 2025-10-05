from datetime import date, timedelta, datetime
import calendar


def week_dates(offset_weeks: int = 0):
    today = date.today()
    monday = today - timedelta(days=today.isoweekday() - 1) + timedelta(weeks=offset_weeks)
    return [monday + timedelta(days=i) for i in range(7)]


def month_grid(year: int, month: int):
    """Return 42 dates (6x7) starting on Monday for given month."""
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(year, month))
    if len(days) < 42:
        days += [days[-1] + timedelta(days=i + 1) for i in range(42 - len(days))]
    return days[:42]


def valid_iso_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

