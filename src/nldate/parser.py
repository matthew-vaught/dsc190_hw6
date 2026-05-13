from __future__ import annotations

import calendar
import re
from datetime import date, timedelta


MONTHS = {
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
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

_ABSOLUTE_DATE_RE = re.compile(
    r"^(?P<month>[a-z]+)\.?\s+"
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?"
    r"(?:,?\s+(?P<year>\d{4}))?$"
)
_DAY_MONTH_DATE_RE = re.compile(
    r"^(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(?P<month>[a-z]+)\.?"
    r"(?:,?\s+(?P<year>\d{4}))?$"
)
_YEAR_MONTH_DATE_RE = re.compile(
    r"^(?P<year>\d{4})\s+"
    r"(?P<month>[a-z]+)\.?\s+"
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?$"
)
_YEAR_FIRST_DATE_RE = re.compile(
    r"^(?P<year>\d{4})(?P<separator>[-/.\s])"
    r"(?P<month>\d{1,2})(?P=separator)"
    r"(?P<day>\d{1,2})$"
)
_US_NUMERIC_DATE_RE = re.compile(
    r"^(?P<month>\d{1,2})(?P<separator>[-/.])"
    r"(?P<day>\d{1,2})(?P=separator)"
    r"(?P<year>\d{4})$"
)
_COMPACT_YEAR_FIRST_DATE_RE = re.compile(
    r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})$"
)

_OFFSET_RE = re.compile(r"(?P<count>\d+)\s+(?P<unit>days?|weeks?|months?|years?)")
_IN_OFFSET_RE = re.compile(r"^in\s+(?P<offset>.+)$")
_OFFSET_FROM_NOW_RE = re.compile(r"^(?P<offset>.+)\s+from\s+now$")
_OFFSET_AGO_RE = re.compile(r"^(?P<offset>.+)\s+ago$")
_DELTA_RE = re.compile(
    r"^(?P<offset>.+?)\s+(?P<direction>before|after)\s+(?P<base>.+)$"
)


def _normalize(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _resolve_today(today: date | None) -> date:
    return today if today is not None else date.today()


def _add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))


def _month_number(month_name: str) -> int | None:
    return MONTHS.get(month_name.rstrip("."))


def _date_from_match(match: re.Match[str]) -> date | None:
    month_text = match.group("month")
    month = int(month_text) if month_text.isdecimal() else _month_number(month_text)
    if month is None:
        return None
    return date(int(match.group("year")), month, int(match.group("day")))


def _date_from_named_match(match: re.Match[str], today: date | None) -> date | None:
    month = _month_number(match.group("month"))
    if month is None:
        return None

    year_text = match.group("year")
    year = int(year_text) if year_text is not None else _resolve_today(today).year
    return date(year, month, int(match.group("day")))


def _parse_absolute(s: str, today: date | None) -> date | None:
    for pattern in (
        _YEAR_FIRST_DATE_RE,
        _US_NUMERIC_DATE_RE,
        _COMPACT_YEAR_FIRST_DATE_RE,
    ):
        match = pattern.fullmatch(s)
        if match is not None:
            return _date_from_match(match)

    for pattern in (
        _ABSOLUTE_DATE_RE,
        _DAY_MONTH_DATE_RE,
        _YEAR_MONTH_DATE_RE,
    ):
        match = pattern.fullmatch(s)
        if match is not None:
            return _date_from_named_match(match, today)

    return None


def _parse_offset(s: str) -> tuple[int, int]:
    months = 0
    days = 0
    matches = list(_OFFSET_RE.finditer(s))
    if not matches:
        raise ValueError(f"Unsupported date offset: {s!r}")

    leftover = _OFFSET_RE.sub("", s)
    leftover = leftover.replace("and", "").strip()
    if leftover:
        raise ValueError(f"Unsupported date offset: {s!r}")

    for match in matches:
        count = int(match.group("count"))
        unit = match.group("unit").rstrip("s")
        if unit == "day":
            days += count
        elif unit == "week":
            days += count * 7
        elif unit == "month":
            months += count
        elif unit == "year":
            months += count * 12

    return months, days


def _apply_offset(start: date, offset: str, sign: int) -> date:
    months, days = _parse_offset(offset)
    result = _add_months(start, sign * months)
    return result + timedelta(days=sign * days)


def _parse_relative(s: str, today: date) -> date | None:
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

    for pattern, sign in (
        (_IN_OFFSET_RE, 1),
        (_OFFSET_FROM_NOW_RE, 1),
        (_OFFSET_AGO_RE, -1),
    ):
        match = pattern.fullmatch(s)
        if match is not None:
            return _apply_offset(today, match.group("offset"), sign)

    for prefix, direction in (("next ", 1), ("last ", -1)):
        if not s.startswith(prefix):
            continue
        weekday_name = s.removeprefix(prefix)
        weekday = WEEKDAYS.get(weekday_name)
        if weekday is None:
            return None
        days = (weekday - today.weekday()) % 7
        if direction == 1:
            return today + timedelta(days=days or 7)
        days = (today.weekday() - weekday) % 7
        return today - timedelta(days=days or 7)

    return None


def parse(s: str, today: date | None = None) -> date:
    """Given a date and a string of a natural language date, return a datetime.date object representing the date that the input string refers to.

    The today parameter is used as a reference point for relative date expressions (like "next Tuesday" or "in 3 days"). If today is not provided, it should default to the current date.
    """
    normalized = _normalize(s)
    reference = _resolve_today(today)

    delta_match = _DELTA_RE.fullmatch(normalized)
    if delta_match is not None:
        base = parse(delta_match.group("base"), today=reference)
        sign = 1 if delta_match.group("direction") == "after" else -1
        return _apply_offset(base, delta_match.group("offset"), sign)

    relative = _parse_relative(normalized, reference)
    if relative is not None:
        return relative

    absolute = _parse_absolute(normalized, reference)
    if absolute is not None:
        return absolute

    raise ValueError(f"Unsupported date expression: {s!r}")
