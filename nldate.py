from datetime import date, timedelta
import re


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()

    # --- basic words ---
    if s == "today":
        return today
    if s == "yesterday":
        return today - timedelta(days=1)
    if s == "tomorrow":
        return today + timedelta(days=1)

    # --- in X days/weeks/months/years ---
    m = re.match(r"in (\d+) days", s)
    if m:
        return today + timedelta(days=int(m.group(1)))

    # --- X days ago ---
    m = re.match(r"(\d+) days ago", s)
    if m:
        return today - timedelta(days=int(m.group(1)))

    # --- next weekday ---
    m = re.match(
        r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s
    )
    if m:
        return _next_weekday(today, m.group(1))

    # --- last weekday ---
    m = re.match(
        r"last (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s
    )
    if m:
        return _last_weekday(today, m.group(1))

    # --- this weekday ---
    m = re.match(
        r"this (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s
    )
    if m:
        return _this_weekday(today, m.group(1))

    # --- X days before DATE ---
    m = re.match(r"(\d+) days before (.+)", s)
    if m:
        days = int(m.group(1))
        anchor = parse(m.group(2), today)
        return anchor - timedelta(days=days)

    # --- X week(s) after DATE ---
    m = re.match(r"(\d+) week after (.+)", s)
    if m:
        weeks = int(m.group(1))
        anchor = parse(m.group(2), today)
        return anchor + timedelta(weeks=weeks)

    # --- absolute date (EDGE CASES) ---

    # YYYY/MM/DD
    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", s)
    if m:
        year, month, day = map(int, m.groups())
        return date(year, month, day)

    # "December 1, 2025"
    m = re.match(
        r"^(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),\s*(\d{4})$",
        s,
    )
    if m:
        month_str, day, year = m.groups()

        month_map = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        return date(int(year), month_map[month_str], int(day))

    # YYYY-MM-DD (ISO)
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    raise ValueError(f"Cannot parse: {s}")


# ---------------- helpers ----------------


def _weekday_index(name: str) -> int:
    return [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ].index(name)


def _next_weekday(today: date, name: str) -> date:
    target = _weekday_index(name)
    diff = (target - today.weekday()) % 7
    if diff == 0:
        diff = 7
    return today + timedelta(days=diff)


def _last_weekday(today: date, name: str) -> date:
    target = _weekday_index(name)
    diff = (today.weekday() - target) % 7
    if diff == 0:
        diff = 7
    return today - timedelta(days=diff)


def _this_weekday(today: date, name: str) -> date:
    target = _weekday_index(name)
    diff = (target - today.weekday()) % 7
    return today + timedelta(days=diff)