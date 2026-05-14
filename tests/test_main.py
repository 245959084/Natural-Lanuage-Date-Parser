import main
from datetime import date


def test_today():
    assert main.parse("today", date(2025, 12, 1)) == date(2025, 12, 1)


def test_yesterday():
    assert main.parse("yesterday", date(2025, 12, 1)) == date(2025, 11, 30)


def test_tomorrow():
    assert main.parse("tomorrow", date(2025, 12, 1)) == date(2025, 12, 2)


def test_in_days():
    assert main.parse("in 3 days", date(2025, 12, 1)) == date(2025, 12, 4)


def test_days_ago():
    assert main.parse("2 days ago", date(2025, 12, 1)) == date(2025, 11, 29)


def test_next_monday():
    assert main.parse("next monday", date(2025, 12, 1)) == date(2025, 12, 8)


def test_last_monday():
    assert main.parse("last monday", date(2025, 12, 1)) == date(2025, 11, 24)


def test_this_wednesday():
    assert main.parse("this wednesday", date(2025, 12, 1)) == date(2025, 12, 3)


def test_absolute_date():
    assert main.parse("2025-12-25", date(2025, 12, 1)) == date(2025, 12, 25)


def test_before_expression():
    assert main.parse("5 days before 2025-12-10", date(2025, 12, 1)) == date(
        2025, 12, 5
    )


def test_after_expression():
    assert main.parse("1 week after 2025-12-01", date(2025, 12, 1)) == date(2025, 12, 8)
