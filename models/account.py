import re
from exceptions import ValidationError

class Account:
    def __init__(self, id, name, currency, balance=0, account_type="general"):
        self.id = id
        self.name = name
        self.currency = currency
        self.balance = balance
        self.account_type = account_type
        self.validate()

    def validate(self):
        # ID must be non-empty string
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("Account ID must be a non-empty string.")

        # Name must be non-empty
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("Account name must be a non-empty string.")

        # Currency must be alphabetic & max 3 chars
        if not isinstance(self.currency, str):
            raise ValidationError("Currency must be a string.")

        if not re.fullmatch(r"[A-Za-z]{1,3}", self.currency):
            raise ValidationError("Currency must be 1–3 alphabetic characters.")

        # Balance must be numeric
        if not isinstance(self.balance, (int, float)):
            raise ValidationError("Balance must be numeric.")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type,
            "currency": self.currency,
            "balance": self.balance,
        }


class CashAccount(Account):
    def __init__(self, id, name, currency, balance=0):
        super().__init__(id, name, currency, balance, account_type="cash")


class BankAccount(Account):
    def __init__(self, id, name, currency, balance=0):
        super().__init__(id, name, currency, balance, account_type="bank")
