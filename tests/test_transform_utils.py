import pytest
from etl.transform_utils import iso2, to_date, split_name, parse_classes

def test_iso2():
    assert iso2("United States") == "US"
    assert iso2("Deutschland") == "DE"
    assert iso2("") is None

def test_to_date():
    assert to_date("2024-01-05") == "2024-01-05"
    assert to_date("05/01/2024") in ("2024-05-01","2024-01-05")  # parser ambiguity
    assert to_date("") is None

def test_split_name():
    assert split_name("Smith, Mia") == "Mia Smith"
    assert split_name("Aarav Singh") == "Aarav Singh"
    assert split_name("") == ""

def test_parse_classes():
    assert parse_classes("9, 35") == [9,35]
    assert parse_classes("  ") == []
