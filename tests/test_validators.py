# tests/test_validators_and_account.py
import pytest
from validators import (
    validate_name, validate_currency, validate_positive_int,
    validate_date_ymd, validate_month_yyyy_mm, validate_category_choice
)
from exceptions import ValidationError
from managers.account_manager import AccountManager
from models.account import CashAccount

def test_validate_name_ok():
    assert validate_name("John Doe") == "John Doe"

def test_validate_name_fail():
    with pytest.raises(ValidationError):
        validate_name("John_Doe!")  # invalid char

def test_currency_ok():
    assert validate_currency("huf") == "HUF"

def test_currency_fail():
    with pytest.raises(ValidationError):
        validate_currency("123")

def test_positive_int_ok():
    assert validate_positive_int("100") == 100

def test_positive_int_fail_zero():
    with pytest.raises(ValidationError):
        validate_positive_int("0")

def test_date_ok():
    assert validate_date_ymd("2025-01-05") == "2025-01-05"

def test_date_fail():
    with pytest.raises(ValidationError):
        validate_date_ymd("05-01-2025")

def test_month_ok():
    assert validate_month_yyyy_mm("2025-01") == "2025-01"

def test_category_choice():
    assert validate_category_choice("1") == "income"
    assert validate_category_choice("expense") == "expense"

def test_account_save_load(tmp_path):
    am = AccountManager()
    acc = CashAccount("A1","Test","HUF",100.0)
    am.create(acc)
    p = tmp_path / "accounts.csv"
    am.save(str(p))
    am2 = AccountManager()
    am2.load(str(p))
    assert len(am2.list_all()) == 1
    assert am2.list_all()[0].balance == 100.0
