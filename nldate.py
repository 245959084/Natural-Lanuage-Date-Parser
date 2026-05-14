from datetime import date, timedelta
import re
import calendar


def parse(s: str, today: date | None = None, _depth: int = 0) -> date:
    if today is None:
        today = date.today()

    if _depth > 5:
        raise ValueError("Too many nested date expressions")

    s = s.lower().strip()

    # -----------------------------
    # NORMALIZATION
    # -----------------------------

    # remove punctuation that breaks matching
    s = s.replace(".", "")

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

    s = re.sub(r"\b(a|an)\b", "1", s)
    s = re.sub(r"\bcouple of\b", "2", s)

    # -----------------------------
    # BASIC WORDS
    # -----------------------------
    if s == "today":
        return today

    if s == "yesterday":
        return today - timedelta(days=1)

    if s == "tomorrow":
        return today + timedelta(days=1)

    # -----------------------------
    # RELATIVE FUTURE
    # -----------------------------
    m = re.match(r"in (\d+) days?", s)
    if m:
        return today + timedelta(days=int(m.group(1)))

    m = re.match(r"in (\d+) weeks?", s)
    if m:
        return today + timedelta(weeks=int(m.group(1)))

    m = re.match(r"in (\d+) months?", s)
    if m:
        return _add_months(today, int(m.group(1)))

    m = re.match(r"in (\d+) years?", s)
    if m:
        return _add_years(today, int(m.group(1)))

    m = re.match(r"(\d+) (day|week|month|year)s? from now", s)
    if m:
        n = int(m.group(1))
        unit = m.group(2)

        if unit == "day":
            return today + timedelta(days=n)

        if unit == "week":
            return today + timedelta(weeks=n)

        if unit == "month":
            return _add_months(today, n)

        if unit == "year":
            return _add_years(today, n)

    # -----------------------------
    # RELATIVE PAST
    # -----------------------------
    m = re.match(r"(\d+) days? ago", s)
    if m:
        return today - timedelta(days=int(m.group(1)))

    m = re.match(r"(\d+) weeks? ago", s)
    if m:
        return today - timedelta(weeks=int(m.group(1)))

    m = re.match(r"(\d+) months? ago", s)
    if m:
        return _add_months(today, -int(m.group(1)))

    m = re.match(r"(\d+) years? ago", s)
    if m:
        return _add_years(today, -int(m.group(1)))

    # -----------------------------
    # WEEKDAY LOGIC
    # -----------------------------
    m = re.match(
        r"(next|last|this) "
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        s,
    )

    if m:
        mode, day = m.groups()

        if mode == "next":
            return _next_weekday(today, day)

        if mode == "last":
            return _last_weekday(today, day)

        return _this_weekday(today, day)

    # -----------------------------
    # WEEK LEVEL
    # -----------------------------
    if s == "next week":
        return today + timedelta(weeks=1)

    if s == "last week":
        return today - timedelta(weeks=1)

    if s == "this week":
        return today - timedelta(days=today.weekday())

    # -----------------------------
    # MONTH BOUNDARIES
    # -----------------------------
    if s == "start of month":
        return today.replace(day=1)

    if s == "end of month":
        last_day = calendar.monthrange(today.year, today.month)[1]
        return today.replace(day=last_day)

    # -----------------------------
    # COMBINED DURATIONS
    # Example:
    # "2 years, 3 months before Dec 1, 2025"
    # -----------------------------
    m = re.match(
        r"(?:(\d+)\s+years?,?\s*)?"
        r"(?:(\d+)\s+months?,?\s*)?"
        r"(?:(\d+)\s+weeks?,?\s*)?"
        r"(?:(\d+)\s+days?,?\s*)?"
        r"(before|after)\s+(.+)",
        s,
    )

    if m:
        years, months, weeks, days, direction, anchor_expr = m.groups()

        years = int(years or 0)
        months = int(months or 0)
        weeks = int(weeks or 0)
        days = int(days or 0)

        anchor = parse(anchor_expr, today, _depth + 1)

        sign = -1 if direction == "before" else 1

        result = anchor

        if years:
            result = _add_years(result, sign * years)

        if months:
            result = _add_months(result, sign * months)

        if weeks:
            result += timedelta(weeks=sign * weeks)

        if days:
            result += timedelta(days=sign * days)

        return result

    # -----------------------------
    # SIMPLE BEFORE / AFTER
    # -----------------------------
    m = re.match(r"(\d+) days? before (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return anchor - timedelta(days=n)

    m = re.match(r"(\d+) weeks? before (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return anchor - timedelta(weeks=n)

    m = re.match(r"(\d+) months? before (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return _add_months(anchor, -n)

    m = re.match(r"(\d+) years? before (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return _add_years(anchor, -n)

    m = re.match(r"(\d+) days? after (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return anchor + timedelta(days=n)

    m = re.match(r"(\d+) weeks? after (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return anchor + timedelta(weeks=n)

    m = re.match(r"(\d+) months? after (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return _add_months(anchor, n)

    m = re.match(r"(\d+) years? after (.+)", s)
    if m:
        n = int(m.group(1))
        anchor = parse(m.group(2), today, _depth + 1)
        return _add_years(anchor, n)

    # -----------------------------
    # ABSOLUTE DATES
    # -----------------------------
    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", s)
    if m:
        y, mo, d = map(int, m.groups())
        return date(y, mo, d)

    # Month-name format
    m = re.match(
        r"^(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+"
        r"(\d{1,2})(st|nd|rd|th)?,\s*(\d{4})$",
        s,
    )

    if m:
        month_str, day, _, year = m.groups()

        month_map = {
            "jan": 1,
            "january": 1,
            "feb": 2,
            "february": 2,
            "mar": 3,
            "march": 3,
            "apr": 4,
            "april": 4,
            "may": 5,
            "jun": 6,
            "june": 6,
            "jul": 7,
            "july": 7,
            "aug": 8,
            "august": 8,
            "sep": 9,
            "september": 9,
            "oct": 10,
            "october": 10,
            "nov": 11,
            "november": 11,
            "dec": 12,
            "december": 12,
        }

        return date(int(year), month_map[month_str], int(day))

    # -----------------------------
    # ISO FORMAT
    # -----------------------------
    try:
        return date.fromisoformat(s)

    except ValueError:
        pass

    raise ValueError(f"Cannot parse: {s}")


# -----------------------------
# HELPERS
# -----------------------------


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

    diff = (target - today.weekday() + 7) % 7

    if diff == 0:
        diff = 7

    return today + timedelta(days=diff)


def _last_weekday(today: date, name: str) -> date:
    target = _weekday_index(name)

    diff = (today.weekday() - target + 7) % 7

    if diff == 0:
        diff = 7

    return today - timedelta(days=diff)


def _this_weekday(today: date, name: str) -> date:
    target = _weekday_index(name)

    return today + timedelta(days=(target - today.weekday()))