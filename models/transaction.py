import re
from datetime import datetime
from exceptions import ValidationError


class Transaction:
    def __init__(self, id, account_id, date, amount, category, description):
        self.id = id
        self.account_id = account_id
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description
        self.validate()

    def validate(self):
        if not self.id.strip():
            raise ValidationError("Transaction ID cannot be empty")

        # Date must be YYYY-MM-DD
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except Exception:
            raise ValidationError("Invalid date format (expected YYYY-MM-DD)")

        # Amount must be positive
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise ValidationError("Amount must be a positive number")

        # Category must be string
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("Category cannot be empty")

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }