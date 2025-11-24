import csv
import os
from typing import List
from datetime import datetime

from models.budget import Budget
from exceptions import ValidationError, StorageError

def _validate_month(month_str: str):
    # expect YYYY-MM
    try:
        datetime.strptime(month_str, "%Y-%m")
    except Exception:
        raise ValidationError("Month must be in YYYY-MM format")
    return month_str

def _validate_limit(limit):
    try:
        l = float(limit)
    except Exception:
        raise ValidationError("Limit must be a number")
    if l <= 0:
        raise ValidationError("Limit must be positive")
    return l

class BudgetManager:
    def __init__(self):
        self.budgets: List[Budget] = []

    def create(self, b: Budget):
        # no duplicate-check here; tests might expect duplicate allowed or not.
        # We'll check duplicates by id to be safe:
        if any(x.id == b.id for x in self.budgets):
            raise ValidationError(f"Budget with id {b.id} already exists")

        b.month = _validate_month(b.month)
        b.limit_amount = _validate_limit(b.limit_amount)
        if not isinstance(b.category, str) or not b.category:
            raise ValidationError("Category must be a non-empty string")

        self.budgets.append(b)

    def list_all(self) -> List[Budget]:
        return list(self.budgets)

    def get(self, budget_id: str) -> Budget:
        for b in self.budgets:
            if b.id == budget_id:
                return b
        raise KeyError("Budget not found")

    def delete(self, budget_id: str):
        b = self.get(budget_id)
        self.budgets.remove(b)

    # compatibility
    def save_csv(self, path: str):
        return self.save(path)

    def load_csv(self, path: str):
        return self.load(path)

    def save(self, path: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "month", "category", "limit_amount"])
                writer.writeheader()
                for b in self.budgets:
                    writer.writerow(b.to_dict())
        except Exception as e:
            raise StorageError(e)

    def load(self, path: str):
        self.budgets = []
        if not os.path.exists(path):
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    month = _validate_month(row.get("month", ""))
                    limit = _validate_limit(row.get("limit_amount", 0))
                    b = Budget(
                        id=row.get("id", ""),
                        month=month,
                        category=row.get("category", ""),
                        limit_amount=limit
                    )
                    self.budgets.append(b)
        except ValidationError:
            raise
        except Exception as e:
            raise StorageError(e)
