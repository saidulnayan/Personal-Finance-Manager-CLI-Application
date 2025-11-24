# validators.py
import re
from datetime import datetime
from exceptions import ValidationError

def validate_name(name: str, field_name="Name", max_len=15):
    if not isinstance(name, str):
        raise ValidationError(f"{field_name} must be text.")
    s = name.strip()
    if not s:
        raise ValidationError(f"{field_name} cannot be empty.")
    # allow letters and spaces only
    if not re.fullmatch(r"[A-Za-z ]{1,%d}" % max_len, s):
        raise ValidationError(f"{field_name} must be letters/spaces only and at most {max_len} characters.")
    return s

def validate_currency(cur: str):
    if not isinstance(cur, str):
        raise ValidationError("Currency must be alphabetic.")
    s = cur.strip().upper()
    if not s:
        raise ValidationError("Currency cannot be empty.")
    if not s.isalpha():
        raise ValidationError("Currency must contain alphabetic characters only.")
    if len(s) > 3:
        raise ValidationError("Currency must be at most 3 letters (e.g., HUF, USD).")
    return s

def validate_positive_int(value_str: str, field_name="Amount"):
    # Accept integers only (no decimals), must be > 0
    v = value_str.strip()
    if not v:
        raise ValidationError(f"{field_name} cannot be empty.")
    if not re.fullmatch(r"\d+", v):
        raise ValidationError(f"{field_name} must be a positive integer.")
    n = int(v)
    if n <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return n

def validate_nonnegative_int(value_str: str, field_name="Amount"):
    # Accept >= 0
    v = value_str.strip()
    if not v:
        raise ValidationError(f"{field_name} cannot be empty.")
    if not re.fullmatch(r"\d+", v):
        raise ValidationError(f"{field_name} must be a non-negative integer (0 or positive).")
    return int(v)

def validate_date_ymd(date_str: str, field_name="Date"):
    # YYYY-MM-DD
    s = date_str.strip()
    if not s:
        raise ValidationError(f"{field_name} cannot be empty.")
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        raise ValidationError(f"{field_name} must be in YYYY-MM-DD format.")
    return s

def validate_month_yyyy_mm(month_str: str, field_name="Month"):
    s = month_str.strip()
    if not s:
        raise ValidationError(f"{field_name} cannot be empty.")
    try:
        datetime.strptime(s, "%Y-%m")
    except Exception:
        raise ValidationError(f"{field_name} must be in YYYY-MM format.")
    return s

def validate_category_choice(choice_str: str):
    # Expect "1" or "2" (1-income,2-expense) or direct 'income'/'expense'
    s = choice_str.strip().lower()
    if s in ("1", "income"):
        return "income"
    if s in ("2", "expense"):
        return "expense"
    raise ValidationError("Category must be '1' (income) or '2' (expense).")
