from datetime import date
import nldate
import pytest


@pytest.mark.parametrize(
    ("text", "today", "expected"),
    [
        (
            "5 days before December 1st, 2025",
            date(2025, 6, 15),
            date(2025, 11, 26),
        ),
        (
            "1 year and 2 months after yesterday",
            date(2025, 12, 1),
            date(2027, 1, 30),
        ),
        (
            "1 month after january 31",
            date(2025, 1, 15),
            date(2025, 2, 28),
        ),
        (
            "1 month after january 31",
            date(2024, 1, 15),
            date(2024, 2, 29),
        ),
        (
            "2 months before March 31, 2025",
            date(2025, 1, 1),
            date(2025, 1, 31),
        ),
        (
            "1 year after February 29 2024",
            date(2025, 1, 1),
            date(2025, 2, 28),
        ),
    ],
)
def test_date_delta_expressions(text, today, expected):
    assert nldate.parse(text, today=today) == expected
