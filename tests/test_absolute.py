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
        ("2025-12-04", date(2025, 12, 4)),
        ("2025/12/04", date(2025, 12, 4)),
        ("2025.12.04", date(2025, 12, 4)),
        ("2025 12 04", date(2025, 12, 4)),
        ("20251204", date(2025, 12, 4)),
        ("12/04/2025", date(2025, 12, 4)),
        ("12-04-2025", date(2025, 12, 4)),
        ("12.04.2025", date(2025, 12, 4)),
        ("04 Dec 2025", date(2025, 12, 4)),
        ("4th December 2025", date(2025, 12, 4)),
        ("2025 December 4", date(2025, 12, 4)),
        ("2025 Dec 04", date(2025, 12, 4)),
        ("Dec. 4, 2025", date(2025, 12, 4)),
    ],
)
def test_absolute_dates_with_explicit_year(text, expected):
    assert nldate.parse(text) == expected


@pytest.mark.parametrize(
    ("text", "today", "expected"),
    [
        ("December 4", date(2025, 1, 1), date(2025, 12, 4)),
        ("4 Dec", date(2025, 1, 1), date(2025, 12, 4)),
        ("Dec. 4th", date(2025, 1, 1), date(2025, 12, 4)),
    ],
)
def test_absolute_dates_without_year_use_today_year(text, today, expected):
    assert nldate.parse(text, today=today) == expected
