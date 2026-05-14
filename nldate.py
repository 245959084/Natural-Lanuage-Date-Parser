from datetime import date, timedelta
import re


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()

    # --- normalize number words (NEW EDGE CASE FIX) ---
    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word, digit in number_words.items():
        s = re.sub(rf"\b{word}\b", digit, s)

    # normalize "a" -> 1 for time expressions
    s = re.sub(r"\ba\s+", "1 ", s)

    # --- basic words ---
    if s == "today":
        return today
    if s == "yesterday":
        return today - timedelta(days=1)
    if s == "tomorrow":
        return today + timedelta(days=1)

    # --- in X days ---
    m = re.match(r"in (\d+) days?", s)
    if m:
        return today + timedelta(days=int(m.group(1)))

    # --- in X weeks ---
    m = re.match(r"in (\d+) weeks?", s)
    if m:
        return today + timedelta(weeks=int(m.group(1)))

    # --- in X months ---
    m = re.match(r"in (\d+) months?", s)
    if m:
        return _add_months(today, int(m.group(1)))

    # --- in X years ---
    m = re.match(r"in (\d+) years?", s)
    if m:
        return _add_years(today, int(m.group(1)))

    # --- X days ago ---
    m = re.match(r"(\d+) days? ago", s)
    if m:
        return today - timedelta(days=int(m.group(1)))

    # --- X weeks ago (NEW WORKS FOR WORDS NOW) ---
    m = re.match(r"(\d+) weeks? ago", s)
    if m:
        return today - timedelta(weeks=int(m.group(1)))

    # --- X months ago ---
    m = re.match(r"(\d+) months? ago", s)
    if m:
        return _add_months(today, -int(m.group(1)))

    # --- X years ago ---
    m = re.match(r"(\d+) years? ago", s)
    if m:
        return _add_years(today, -int(m.group(1)))

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

    # Month formats (Dec, Dec., December + ordinals)
    m = re.match(
        r"^(jan(?:uary)?\.?|feb(?:ruary)?\.?|mar(?:ch)?\.?|apr(?:il)?\.?|may\.?|"
        r"jun(?:e)?\.?|jul(?:y)?\.?|aug(?:ust)?\.?|sep(?:tember)?\.?|"
        r"oct(?:ober)?\.?|nov(?:ember)?\.?|dec(?:ember)?\.?)\s+"
        r"(\d{1,2})(st|nd|rd|th)?,\s*(\d{4})$",
        s,
    )
    if m:
        month_str, day, _, year = m.groups()

        month_map = {
            "jan": 1, "jan.": 1, "january": 1,
            "feb": 2, "feb.": 2, "february": 2,
            "mar": 3, "mar.": 3, "march": 3,
            "apr": 4, "apr.": 4, "april": 4,
            "may": 5, "may.": 5,
            "jun": 6, "jun.": 6, "june": 6,
            "jul": 7, "jul.": 7, "july": 7,
            "aug": 8, "aug.": 8, "august": 8,
            "sep": 9, "sep.": 9, "september": 9,
            "oct": 10, "oct.": 10, "october": 10,
            "nov": 11, "nov.": 11, "november": 11,
            "dec": 12, "dec.": 12, "december": 12,
        }

        return date(int(year), month_map[month_str], int(day))

    # --- ISO format ---
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    raise ValueError(f"Cannot parse: {s}")


# ---------------- helpers ----------------


def _add_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    day = min(d.day, _days_in_month(year, month))
    return date(year, month, day)


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return date(d.year + years, 2, 28)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - timedelta(days=1)).day


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