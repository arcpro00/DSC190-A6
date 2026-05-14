# Options of parameters: with string(specific date, relative date) and reference date; with string, no reference date
from datetime import date, timedelta
from nldate.parser import parse
import pytest


def test_relative_today():
    relative_refs = [
        "5 days before now",
        "15 days before today",
        "In a week from now",
        "in 1 month",
        "in 1 year",
    ]
    actual_date = [
        date(2024, 12, 20),
        date.today() - timedelta(days=15),
        date(2025, 1, 1),
        date(
            date.today().year + (date.today().month // 12),
            date.today().month % 12 + 1,
            date.today().day,
        ),
        date(date.today().year + 1, date.today().month, date.today().day),
    ]
    today = [
        date(2024, 12, 25),
        None,
        date(2024, 12, 25),
        None,
        None,
    ]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i], today[i]) == actual_date[i]


def test_relative_noref():
    relative_refs = [
        "8 days before November 11th, 2027",
        "14 days before the second day of February in the first year of the 21st century",
        "In two weeks and a day from 1-4-2025",
    ]
    actual_date = [
        date(2027, 11, 11) - timedelta(days=8),
        date(2001, 2, 2) - timedelta(days=14),
        date(2025, 1, 4) + timedelta(days=15),
    ]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i]) == actual_date[i]


def test_exact_today():
    relative_refs = [
        "Lets aim for 5/16/1997",
        "how does 2023-12-24 sound",
        "Let's meet up on March third, 2016",
    ]
    actual_date = [date(1997, 5, 16), date(2023, 12, 24), date(2016, 3, 3)]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i], date.today()) == actual_date[i]


def test_exact_noref():
    relative_refs = [
        "Lets aim for 6/3/1997",
        "how does 2020-12-31 sound",
        "Let's meet up on March fifteenth, 2016",
        "Does the twenty fifth of april 2007 work?",
        "Does 2025/12/04 work",
        "how does 12-31-2020 sound",
        "Dec 1, 2025",
        "Dec. 2, 2025",
    ]
    actual_date = [
        date(1997, 6, 3),
        date(2020, 12, 31),
        date(2016, 3, 15),
        date(2007, 4, 25),
        date(2025, 12, 4),
        date(2020, 12, 31),
        date(2025, 12, 1),
        date(2025, 12, 2),
    ]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i]) == actual_date[i]


def test_invalid_day():
    with pytest.raises(ValueError):
        parse("How does December 50, 2020 sound")


def test_invalid_month():
    with pytest.raises(ValueError):
        parse("Want to meet up 13/4/2026")


def test_invalid_year():
    with pytest.raises(ValueError):
        parse("Want to meet up 13/4/2")


def test_leap_year():
    refs = [
        "February 29, 2024",
        "2/29/2024",
        "one day after February 28, 2024",
    ]
    actual = [
        date(2024, 2, 29),
        date(2024, 2, 29),
        date(2024, 2, 29),
    ]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]


def test_case_insensitivity():
    refs = [
        "MARCH THIRD 2016",
        "in A WEEK from NOW",
        "fIvE dAyS bEfOrE tOdAy",
    ]
    today_vals = [
        None,
        date(2024, 12, 25),
        date(2024, 12, 25),
    ]
    actual = [
        date(2016, 3, 3),
        date(2025, 1, 1),
        date(2024, 12, 20),
    ]
    for i in range(len(refs)):
        assert parse(refs[i], today_vals[i]) == actual[i]


def test_invalid_leap_dates():
    invalid_refs = [
        "February 29, 2023",
        "2/29/2021",
        "one day after February 28, 2023 but somehow February 29",
    ]
    for ref in invalid_refs:
        with pytest.raises(ValueError):
            parse(ref)


def test_abbreviated_month_period():
    refs = ["Jan. 15, 2024", "Feb. 29, 2024", "Dec. 1, 2025"]
    actual = [date(2024, 1, 15), date(2024, 2, 29), date(2025, 12, 1)]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]


def test_invalid_abbreviated_month():
    with pytest.raises(ValueError):
        parse("Mar. 32, 2023")


def test_relative_abbreviated():
    assert parse("3 days before Jan. 15, 2024") == date(2024, 1, 12)


def test_ordinal_suffix():
    refs = ["March 3rd, 2016", "April 1st, 2020", "May 22nd, 2021", "June 11th, 2022"]
    actual = [date(2016, 3, 3), date(2020, 4, 1), date(2021, 5, 22), date(2022, 6, 11)]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]


def test_the_x_of_month_abbreviated():
    refs = ["the 5th of Jan, 2024", "the 1st of Feb., 2025"]
    actual = [date(2024, 1, 5), date(2025, 2, 1)]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]


def test_in_days():
    assert parse("in 3 days") == date.today() + timedelta(days=3)


def test_days_ago():
    assert parse("3 days ago") == date.today() - timedelta(days=3)


def test_yesterday_tomorrow():
    assert parse("yesterday") == date.today() - timedelta(days=1)
    assert parse("tomorrow") == date.today() + timedelta(days=1)


def test_no_date_info():
    with pytest.raises(ValueError):
        parse("")
    with pytest.raises(ValueError):
        parse("no date here")


def test_zero_offset():
    assert parse("0 days from now") == date.today()


def test_multiple_dates():
    assert parse("Jan 1, 2024 and Feb 2, 2024") == date(2024, 1, 1)


def test_dd_mon_yyyy():
    refs = ["15-Jan-2024", "15 Jan 2024", "15xJan.2024"]
    actual = [date(2024, 1, 15), date(2024, 1, 15), date(2024, 1, 15)]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]


def test_whitespace():
    assert parse("  March 3, 2016  ") == date(2016, 3, 3)


def test_next_weekday():
    ref_today = date(2026, 5, 13)
    assert parse("next Tuesday", ref_today) == date(2026, 5, 19)
    assert parse("next Monday", ref_today) == date(2026, 5, 18)
    assert parse("next Friday", ref_today) == date(2026, 5, 15)


def test_last_weekday():
    ref_today = date(2026, 5, 13)
    assert parse("last Tuesday", ref_today) == date(2026, 5, 12)
    assert parse("last Monday", ref_today) == date(2026, 5, 11)
    assert parse("last Sunday", ref_today) == date(2026, 5, 10)


def test_composite_offset():
    assert parse("2 years, 3 months before Dec. 1, 2025") == date(2023, 9, 1)
    assert parse("1 year 2 months before Dec 1, 2025") == date(2024, 10, 1)
