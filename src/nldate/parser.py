from datetime import date, timedelta
import re

MONTH_NAMES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

NUMBER_WORDS = {
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
    "a": 1,
    "an": 1,
}

ORDINAL_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "thirtieth": 30,
    "fortieth": 40,
    "fiftieth": 50,
    "sixtieth": 60,
    "seventieth": 70,
    "eightieth": 80,
    "ninetieth": 90,
    "hundredth": 100,
}


def _word_to_number(word: str) -> int | None:
    word = word.strip().lower()
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    if word in ORDINAL_WORDS:
        return ORDINAL_WORDS[word]
    m = re.match(r"^(\d+)(st|nd|rd|th)$", word)
    if m:
        return int(m.group(1))
    try:
        return int(word)
    except ValueError:
        pass
    if "-" in word:
        total = 0
        for part in word.split("-"):
            n = _word_to_number(part)
            if n is None:
                return None
            total += n
        return total
    return None


def _is_valid_date(y: int, m: int, d: int) -> bool:
    try:
        date(y, m, d)
        return True
    except (ValueError, OverflowError):
        return False


def _parse_number_phrase(text: str) -> int | None:
    words = text.strip().lower().split()
    total = 0
    for word in words:
        n = _word_to_number(word)
        if n is None:
            return None
        total += n
    return total


def _parse_offset_expression(text: str) -> int:
    text = text.strip().lower()
    total_days = 0
    parts = re.split(r"\s+and\s+", text)
    for part in parts:
        part = part.strip()
        m = re.match(r"(\S+)\s+(weeks?|days?)", part)
        if m:
            num_str = m.group(1)
            unit = m.group(2)
            n = _word_to_number(num_str)
            if n is not None:
                total_days += n * (7 if unit.startswith("week") else 1)
                continue
        n = _word_to_number(part)
        if n is not None:
            total_days += n
    return total_days


_MONTH_PAT = "|".join(MONTH_NAMES.keys())


_MONTH_DAY_RE = re.compile(
    rf"({'|'.join(MONTH_NAMES.keys())})\s+(\w+)",
    re.IGNORECASE,
)


def _has_invalid_refs(text: str, context_year: int) -> bool:
    for m in _MONTH_DAY_RE.finditer(text.lower().strip()):
        month_num = MONTH_NAMES[m.group(1)]
        day = _word_to_number(m.group(2))
        if (
            day is not None
            and day <= 31
            and not _is_valid_date(context_year, month_num, day)
        ):
            return True
    return False


def _parse_date_from_text(text: str) -> date | None:
    lower = text.strip().lower()

    if lower in ("now", "today"):
        return None

    m = re.search(
        rf"the\s+(\S+)\s+day\s+of\s+({_MONTH_PAT})\s+in\s+the\s+(\S+)\s+year\s+of\s+the\s+(\S+)\s+century",
        lower,
    )
    if m:
        day_num = _word_to_number(m.group(1))
        month_num = MONTH_NAMES[m.group(2)]
        year_in_century = _word_to_number(m.group(3))
        century_num = _word_to_number(m.group(4))
        if (
            day_num is not None
            and year_in_century is not None
            and century_num is not None
        ):
            year = (century_num - 1) * 100 + year_in_century
            if _is_valid_date(year, month_num, day_num):
                if not _has_invalid_refs(text, year):
                    return date(year, month_num, day_num)

    m = re.search(
        rf"the\s+(.+?)\s+of\s+({_MONTH_PAT})\s+(\d{{4}})",
        lower,
    )
    if m:
        day_words = m.group(1).strip()
        month_num = MONTH_NAMES[m.group(2)]
        year = int(m.group(3))
        day = _parse_number_phrase(day_words)
        if day is not None and _is_valid_date(year, month_num, day):
            if not _has_invalid_refs(text, year):
                return date(year, month_num, day)

    m = re.search(
        rf"({_MONTH_PAT})\s+(\w+),?\s*(\d{{4}})",
        lower,
    )
    if m:
        month_num = MONTH_NAMES[m.group(1)]
        day_str = m.group(2)
        year = int(m.group(3))
        day_num = _word_to_number(day_str)
        if day_num is not None and _is_valid_date(year, month_num, day_num):
            if not _has_invalid_refs(text, year):
                return date(year, month_num, day_num)

    m = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if 1 <= month <= 12 and _is_valid_date(year, month, day):
            if not _has_invalid_refs(text, year):
                return date(year, month, day)

    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", text)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        year = int(m.group(3))
        if 1 <= month <= 12 and _is_valid_date(year, month, day):
            if not _has_invalid_refs(text, year):
                return date(year, month, day)

    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if 1 <= month <= 12 and _is_valid_date(year, month, day):
            if not _has_invalid_refs(text, year):
                return date(year, month, day)

    m = re.search(r"(\d{1,2})-(\d{1,2})-(\d{2,4})", text)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        year = int(m.group(3))
        if 1 <= month <= 12 and _is_valid_date(year, month, day):
            if not _has_invalid_refs(text, year):
                return date(year, month, day)

    return None


def _resolve_date(date_text: str, today: date) -> date | None:
    lower = date_text.strip().lower()
    if lower in ("now", "today"):
        return today
    return _parse_date_from_text(date_text)


def _parse_relative(text: str, today: date) -> date | None:
    lower = text.strip().lower()

    m = re.search(r"\bin\b\s+(.+?)\s+from\s+(.+)", lower)
    if m:
        offset_text = m.group(1).strip()
        date_text = m.group(2).strip()
        offset = _parse_offset_expression(offset_text)
        base = _resolve_date(date_text, today)
        if base is not None:
            return base + timedelta(days=offset)

    for direction, sign in [("before", -1), ("after", 1), ("from", 1)]:
        m = re.search(rf"(.+?)\s+(days?|weeks?)\s+{direction}\s+(.+)", lower)
        if m:
            num_text = m.group(1).strip()
            unit = m.group(2)
            date_text = m.group(3).strip()
            num = _word_to_number(num_text)
            if num is not None:
                multiplier = 7 if unit.startswith("week") else 1
                offset = num * multiplier * sign
                base = _resolve_date(date_text, today)
                if base is not None:
                    return base + timedelta(days=offset)

    return None


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    result = _parse_relative(s, today)
    if result is not None:
        return result

    result = _parse_date_from_text(s)
    if result is not None:
        return result

    raise ValueError(f"Could not parse date: {s}")
