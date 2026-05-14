'''def main():
    print("Hello from natural-lanuage-date-parser!")'''

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
    m = re.match(r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s)
    if m:
        return _next_weekday(today, m.group(1))

    # --- last weekday ---
    m = re.match(r"last (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s)
    if m:
        return _last_weekday(today, m.group(1))

    # --- this weekday ---
    m = re.match(r"this (monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s)
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

    # --- absolute date ---
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    raise ValueError(f"Cannot parse: {s}")


# ---------------- helpers ----------------

def _weekday_index(name: str) -> int:
    return ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"].index(name)

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

'''if __name__ == "__main__":
    main()'''
