import csv
import os
from typing import List, Optional

from models.account import Account, CashAccount, BankAccount
from exceptions import ValidationError, NotFoundError, StorageError

# helper validators
def _validate_name(name: str):
    if not isinstance(name, str):
        raise ValidationError("Name must be a string")
    trimmed = name.strip()
    if len(trimmed) == 0 or len(trimmed) > 15:
        raise ValidationError("Name must be 1..15 characters long")
    # allow letters and spaces only
    if not all(ch.isalpha() or ch.isspace() for ch in trimmed):
        raise ValidationError("Name must contain alphabetic characters and spaces only")
    return trimmed

def _validate_currency(currency: str):
    if not isinstance(currency, str):
        raise ValidationError("Currency must be a string")
    cur = currency.strip().upper()
    if len(cur) == 0 or len(cur) > 3:
        raise ValidationError("Currency must be 1..3 characters")
    if not cur.isalpha():
        raise ValidationError("Currency must be alphabetic")
    return cur

def _validate_balance(balance):
    try:
        b = float(balance)
    except Exception:
        raise ValidationError("Balance must be a number")
    if b < 0:
        raise ValidationError("Balance must be non-negative")
    # tests expect integers sometimes; but we accept floats too
    return b

class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []

    def create(self, acc: Account):
        # validate id uniqueness
        if any(a.id == acc.id for a in self.accounts):
            raise ValidationError(f"Account with id {acc.id} already exists")

        # validate fields
        acc.name = _validate_name(acc.name)
        acc.currency = _validate_currency(acc.currency)
        acc.balance = _validate_balance(acc.balance)

        # ensure proper subclass based on account_type
        atype = (acc.account_type or "").lower()
        if atype == "cash" and not isinstance(acc, CashAccount):
            acc = CashAccount(acc.id, acc.name, acc.currency, acc.balance)
        elif atype == "bank" and not isinstance(acc, BankAccount):
            acc = BankAccount(acc.id, acc.name, acc.currency, acc.balance)

        self.accounts.append(acc)

    def list_all(self) -> List[Account]:
        return list(self.accounts)

    def get(self, account_id: str) -> Account:
        for a in self.accounts:
            if a.id == account_id:
                return a
        raise NotFoundError(f"Account {account_id} not found")

    def get_by_id(self, account_id: str) -> Optional[Account]:
        for a in self.accounts:
            if a.id == account_id:
                return a
        return None

    def update(self, account_id: str, **kwargs):
        """
        Update attributes of an account. Validates name and currency and balance when provided.
        """
        acc = self.get(account_id)
        if "name" in kwargs and kwargs["name"] is not None:
            acc.name = _validate_name(kwargs["name"])
        if "currency" in kwargs and kwargs["currency"] is not None:
            acc.currency = _validate_currency(kwargs["currency"])
        if "balance" in kwargs and kwargs["balance"] is not None:
            acc.balance = _validate_balance(kwargs["balance"])
        return acc

    def delete(self, account_id: str):
        acc = self.get(account_id)
        self.accounts.remove(acc)

    # backward-compatible save/load names expected by tests
    def save_csv(self, path: str):
        return self.save(path)

    def load_csv(self, path: str):
        return self.load(path)

    # actual implementations
    def save(self, path: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "name", "account_type", "currency", "balance"])
                writer.writeheader()
                for acc in self.accounts:
                    writer.writerow(acc.to_dict())
        except Exception as e:
            raise StorageError(e)

    def load(self, path: str):
        self.accounts = []
        if not os.path.exists(path):
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # safe parsing with defaults
                    balance = float(row.get("balance") or 0.0)
                    atype = (row.get("account_type") or "").lower()
                    name = row.get("name") or ""
                    currency = row.get("currency") or ""
                    # validate loaded data (will raise ValidationError if file corrupt)
                    name = _validate_name(name)
                    currency = _validate_currency(currency)
                    balance = _validate_balance(balance)

                    if atype == "cash":
                        acc = CashAccount(row["id"], name, currency, balance)
                    elif atype == "bank":
                        acc = BankAccount(row["id"], name, currency, balance)
                    else:
                        acc = Account(row["id"], name, row.get("account_type", ""), currency, balance)

                    self.accounts.append(acc)
        except ValidationError:
            # re-raise validation errors to caller
            raise
        except Exception as e:
            raise StorageError(e)
