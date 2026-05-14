#Options of parameters: with string(specific date, relative date) and reference date; with string, no reference date
from datetime import date, timedelta
from nldate.parser import parse
import pytest

def test_relative_today():
    relative_refs = ["5 days before now","15 days before today","In a week from now"]
    actual_date = [date(2024,12,20),date.today()-timedelta(days=15),date(2025,1,1)]
    today = [date(2024, 12, 25),None,date(2024, 12, 25)]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i],today[i]) == actual_date[i]

def test_relative_noref():
    relative_refs = ["8 days before November 11th, 2027","14 days before the second day of February in the first year of the 21st century","In two weeks and a day from 1-4-2025"]
    actual_date = [date(2027,11,11)-timedelta(days=8),date(2001,2,2)-timedelta(days=14),date(2025,1,4)+timedelta(days=15)]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i]) == actual_date[i]

def test_exact_today():
    relative_refs = ["Lets aim for 5/16/1997","how does 2023-12-24 sound","Let's meet up on March third, 2016"]
    actual_date = [date(1997,5,16),date(2023,12,24),date(2016,3,3)]
    for i in range(len(relative_refs)):
        assert parse(relative_refs[i],date.today()) == actual_date[i]

def test_exact_noref():
    relative_refs = ["Lets aim for 6/3/1997","how does 2020-12-31 sound","Let's meet up on March fifteenth, 2016","Does the twenty fifth of april 2007 work?"]
    actual_date = [date(1997,6,3),date(2020,12,31),date(2016,3,15),date(2007,4,25)]
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
    refs = ["February 29, 2024","2/29/2024","one day after February 28, 2024",]
    actual = [date(2024, 2, 29),date(2024, 2, 29),date(2024, 2, 29),]
    for i in range(len(refs)):
        assert parse(refs[i]) == actual[i]

def test_case_insensitivity():
    refs = ["MARCH THIRD 2016","in A WEEK from NOW","fIvE dAyS bEfOrE tOdAy",]
    today_vals = [None,date(2024, 12, 25),date(2024, 12, 25),]
    actual = [date(2016, 3, 3),date(2025, 1, 1),date(2024, 12, 20),]
    for i in range(len(refs)):
        assert parse(refs[i], today_vals[i]) == actual[i]

def test_invalid_leap_dates():
    invalid_refs = ["February 29, 2023","2/29/2021","one day after February 28, 2023 but somehow February 29",]
    for ref in invalid_refs:
        with pytest.raises(ValueError):
            parse(ref)