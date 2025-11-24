import csv
import os
from typing import List
from datetime import datetime

from models.transaction import Transaction
from exceptions import ValidationError, NotFoundError, StorageError

def _validate_amount(amount):
    try:
        a = float(amount)
    except Exception:
        raise ValidationError("Amount must be a number")
    if a <= 0:
        raise ValidationError("Amount must be positive")
    return a

def _validate_date(date_str: str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        raise ValidationError("Date must be in YYYY-MM-DD format")
    return date_str

class TransactionManager:
    def __init__(self):
        self.transactions: List[Transaction] = []

    def create(self, tx: Transaction):
        # unique id
        if any(t.id == tx.id for t in self.transactions):
            raise ValidationError(f"Transaction with id {tx.id} already exists")

        # validate fields
        tx.amount = _validate_amount(tx.amount)
        tx.date = _validate_date(tx.date)
        if not isinstance(tx.category, str) or not tx.category:
            raise ValidationError("Category must be a non-empty string")

        self.transactions.append(tx)

    def list_all(self) -> List[Transaction]:
        return list(self.transactions)

    def get(self, tx_id: str) -> Transaction:
        for t in self.transactions:
            if t.id == tx_id:
                return t
        raise NotFoundError(f"Transaction {tx_id} not found")

    def update(self, tx_id: str, **kwargs):
        tx = self.get(tx_id)
        if "amount" in kwargs and kwargs["amount"] is not None:
            tx.amount = _validate_amount(kwargs["amount"])
        if "date" in kwargs and kwargs["date"] is not None:
            tx.date = _validate_date(kwargs["date"])
        if "category" in kwargs and kwargs["category"] is not None:
            if not isinstance(kwargs["category"], str) or not kwargs["category"]:
                raise ValidationError("Category must be a non-empty string")
            tx.category = kwargs["category"]
        if "description" in kwargs and kwargs["description"] is not None:
            tx.description = str(kwargs["description"])
        return tx

    def delete(self, tx_id: str):
        tx = self.get(tx_id)
        self.transactions.remove(tx)

    # backward-compatible names
    def save_csv(self, path: str):
        return self.save(path)

    def load_csv(self, path: str):
        return self.load(path)

    def save(self, path: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "account_id", "date", "amount", "category", "description"])
                writer.writeheader()
                for t in self.transactions:
                    writer.writerow(t.to_dict())
        except Exception as e:
            raise StorageError(e)

    def load(self, path: str):
        self.transactions = []
        if not os.path.exists(path):
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # validate while loading to catch corrupt files
                    amt = _validate_amount(row.get("amount", 0))
                    date = _validate_date(row.get("date", ""))
                    tx = Transaction(
                        id=row.get("id", ""),
                        account_id=row.get("account_id", ""),
                        date=date,
                        amount=amt,
                        category=row.get("category", ""),
                        description=row.get("description", "")
                    )
                    self.transactions.append(tx)
        except ValidationError:
            raise
        except Exception as e:
            raise StorageError(e)
