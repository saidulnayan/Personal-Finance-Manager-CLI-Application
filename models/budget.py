import re
from exceptions import ValidationError
from datetime import datetime


class Budget:
    def __init__(self, id, month, category, limit_amount):
        self.id = id
        self.month = month
        self.category = category
        self.limit_amount = limit_amount
        self.validate()

    def validate(self):
        if not self.id.strip():
            raise ValidationError("Budget ID cannot be empty")

        # Month must be YYYY-MM
        try:
            datetime.strptime(self.month, "%Y-%m")
        except Exception:
            raise ValidationError("Month must be in YYYY-MM format")

        # Limit must be positive
        if not isinstance(self.limit_amount, (int, float)) or self.limit_amount <= 0:
            raise ValidationError("Limit must be a positive number")

        # Category must be non-empty string
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("Category cannot be empty")

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.month,
            "category": self.category,
            "limit_amount": self.limit_amount,
        }
