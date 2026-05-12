from datetime import date
import nldate
import pytest


def test_straightforward_date():
    assert nldate.parse("february 29 2024", None) == date(2024, 2, 29)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("February 29 2024", date(2024, 2, 29)),
        ("december 1st, 2025", date(2025, 12, 1)),
        ("December 1, 2025", date(2025, 12, 1)),
        ("jan 31 2025", date(2025, 1, 31)),
        ("July 4th 2026", date(2026, 7, 4)),
    ],
)
def test_absolute_dates_with_explicit_year(text, expected):
    assert nldate.parse(text) == expected
