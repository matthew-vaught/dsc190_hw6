from datetime import date
import nldate
import pytest


@pytest.mark.parametrize(
    ("text", "today", "expected"),
    [
        ("tomorrow", date(2025, 12, 1), date(2025, 12, 2)),
        ("yesterday", date(2025, 12, 1), date(2025, 11, 30)),
        ("today", date(2025, 12, 1), date(2025, 12, 1)),
        ("in 3 days", date(2025, 12, 1), date(2025, 12, 4)),
        ("3 days from now", date(2025, 12, 1), date(2025, 12, 4)),
        ("2 weeks ago", date(2025, 12, 1), date(2025, 11, 17)),
        ("next monday", date(2025, 12, 1), date(2025, 12, 8)),
        ("Next Monday", date(2025, 12, 1), date(2025, 12, 8)),
        ("next Tuesday", date(2025, 12, 1), date(2025, 12, 2)),
        ("last friday", date(2025, 12, 1), date(2025, 11, 28)),
        ("next Tuesday", date(2025, 12, 30), date(2026, 1, 6)),
        ("tomorrow", date(2024, 2, 28), date(2024, 2, 29)),
    ],
)
def test_relative_dates_use_explicit_today(text, today, expected):
    assert nldate.parse(text, today=today) == expected
