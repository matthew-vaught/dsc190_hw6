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

_COUNT_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
_COUNT_WORD_RE = "|".join(_COUNT_WORDS)
_COUNT_RE = (
    rf"\d+|a\s+couple|couple|an?|"
    rf"(?:{_COUNT_WORD_RE})(?:[-\s](?:{_COUNT_WORD_RE}))?"
)
_OFFSET_RE = re.compile(
    rf"(?P<count>{_COUNT_RE})\s+(?:of\s+)?"
    r"(?P<unit>hours?|days?|fortnights?|weeks?|months?|years?)"
)
_OFFSET_SEPARATOR_RE = re.compile(r"^[\s,]*(?:and[\s,]*)?$")
_IN_OFFSET_RE = re.compile(r"^in\s+(?P<offset>.+)$")
_OFFSET_FROM_NOW_RE = re.compile(r"^(?P<offset>.+)\s+from\s+now$")
_OFFSET_AGO_RE = re.compile(r"^(?P<offset>.+)\s+ago$")
_IMPLICIT_DELTA_RE = re.compile(
    r"^(?:the\s+)?(?P<unit>day|week|month|year)"
    r"\s+(?P<direction>before|after)\s+(?P<base>.+)$"
)
_DELTA_RE = re.compile(
    r"^(?P<offset>.+?)\s+(?P<direction>before|after)\s+(?P<base>.+)$"
)

_RELATIVE_DAY_ALIASES = {
    "tonight": 0,
    "this morning": 0,
    "this afternoon": 0,
    "this evening": 0,
    "the next day": 1,
    "next day": 1,
    "the following day": 1,
    "following day": 1,
    "overmorrow": 2,
    "the day after tomorrow": 2,
    "day after tomorrow": 2,
    "the previous day": -1,
    "previous day": -1,
    "the prior day": -1,
    "prior day": -1,
    "ereyesterday": -2,
    "the day before yesterday": -2,
    "day before yesterday": -2,
}

_TIME_OF_DAY_SUFFIXES = (" morning", " afternoon", " evening", " night")


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
    if s == "fortnight":
        return 0, 14

    months = 0
    days = 0
    matches = list(_OFFSET_RE.finditer(s))
    if not matches:
        raise ValueError(f"Unsupported date offset: {s!r}")
    _validate_offset_separators(s, matches)

    for match in matches:
        count = _parse_count(match.group("count"))
        unit = match.group("unit").rstrip("s")
        if unit == "hour":
            continue
        if unit == "day":
            days += count
        elif unit == "fortnight":
            days += count * 14
        elif unit == "week":
            days += count * 7
        elif unit == "month":
            months += count
        elif unit == "year":
            months += count * 12

    return months, days


def _validate_offset_separators(s: str, matches: list[re.Match[str]]) -> None:
    if s[: matches[0].start()].strip() or s[matches[-1].end() :].strip():
        raise ValueError(f"Unsupported date offset: {s!r}")

    for previous, current in zip(matches, matches[1:]):
        separator = s[previous.end() : current.start()]
        if _OFFSET_SEPARATOR_RE.fullmatch(separator) is None:
            raise ValueError(f"Unsupported date offset: {s!r}")


def _parse_count(count_text: str) -> int:
    if count_text.isdecimal():
        return int(count_text)

    if count_text in {"a", "an"}:
        return 1
    if count_text in {"couple", "a couple"}:
        return 2

    words = count_text.replace("-", " ").split()
    values = []
    for word in words:
        value = _COUNT_WORDS.get(word)
        if value is None:
            raise ValueError(f"Unsupported date offset count: {count_text!r}")
        values.append(value)

    if len(values) == 1:
        return values[0]
    if len(values) == 2 and 20 <= values[0] <= 90 and 1 <= values[1] <= 9:
        return values[0] + values[1]

    raise ValueError(f"Unsupported date offset count: {count_text!r}")


def _apply_offset(start: date, offset: str, sign: int) -> date:
    months, days = _parse_offset(offset)
    result = _add_months(start, sign * months)
    return result + timedelta(days=sign * days)


def _strip_time_of_day_suffix(s: str) -> str | None:
    for suffix in _TIME_OF_DAY_SUFFIXES:
        if s.endswith(suffix):
            return s[: -len(suffix)]
    return None


def _parse_period_shorthand(s: str, today: date) -> date | None:
    for prefix, sign in (("next ", 1), ("last ", -1)):
        if not s.startswith(prefix):
            continue
        unit = s.removeprefix(prefix)
        if unit not in {"week", "month", "year", "fortnight"}:
            return None
        return _apply_offset(today, f"1 {unit}", sign)

    return None


def _parse_weekday_shorthand(s: str, today: date) -> date | None:
    for prefix, direction, include_today in (
        ("next ", 1, False),
        ("this ", 1, True),
        ("coming ", 1, True),
        ("upcoming ", 1, True),
        ("last ", -1, False),
        ("previous ", -1, False),
        ("past ", -1, False),
    ):
        if not s.startswith(prefix):
            continue
        weekday = WEEKDAYS.get(s.removeprefix(prefix))
        if weekday is None:
            return None
        if direction == 1:
            days = (weekday - today.weekday()) % 7
            return today + timedelta(days=days if include_today else days or 7)
        days = (today.weekday() - weekday) % 7
        return today - timedelta(days=days or 7)

    return None


def _parse_relative(s: str, today: date) -> date | None:
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

    day_alias = _RELATIVE_DAY_ALIASES.get(s)
    if day_alias is not None:
        return today + timedelta(days=day_alias)

    period = _parse_period_shorthand(s, today)
    if period is not None:
        return period

    for pattern, sign in (
        (_IN_OFFSET_RE, 1),
        (_OFFSET_FROM_NOW_RE, 1),
        (_OFFSET_AGO_RE, -1),
    ):
        match = pattern.fullmatch(s)
        if match is not None:
            return _apply_offset(today, match.group("offset"), sign)

    weekday = _parse_weekday_shorthand(s, today)
    if weekday is not None:
        return weekday

    return None


def parse(s: str, today: date | None = None) -> date:
    """Given a date and a string of a natural language date, return a datetime.date object representing the date that the input string refers to.

    The today parameter is used as a reference point for relative date expressions (like "next Tuesday" or "in 3 days"). If today is not provided, it should default to the current date.
    """
    normalized = _normalize(s)
    reference = _resolve_today(today)

    time_base = _strip_time_of_day_suffix(normalized)
    if time_base is not None:
        try:
            return parse(time_base, today=reference)
        except ValueError:
            pass

    implicit_delta_match = _IMPLICIT_DELTA_RE.fullmatch(normalized)
    if implicit_delta_match is not None:
        base = parse(implicit_delta_match.group("base"), today=reference)
        sign = 1 if implicit_delta_match.group("direction") == "after" else -1
        return _apply_offset(base, f"1 {implicit_delta_match.group('unit')}", sign)

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
