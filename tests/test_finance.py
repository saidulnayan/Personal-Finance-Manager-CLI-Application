import os
import pytest
from datetime import datetime

from managers.account_manager import AccountManager
from managers.transaction_manager import TransactionManager
from managers.budget_manager import BudgetManager

from models.account import Account, CashAccount, BankAccount
from models.transaction import Transaction
from models.budget import Budget

from exceptions import ValidationError, NotFoundError


# ============================================================
# 1. UNIT TESTS
# ============================================================

def test_account_validation():
    """Unit test: Validate individual fields"""
    # invalid currency (should be alphabetic)
    with pytest.raises(ValidationError):
        Account("A1", "Wallet", "cash", "123", 100)

    # invalid name (too long)
    with pytest.raises(ValidationError):
        Account("A1", "ThisNameIsWayTooLong123", "cash", "HUF", 100)

    # invalid balance (negative)
    with pytest.raises(ValidationError):
        Account("A1", "Wallet", "cash", "HUF", -10)


def test_transaction_validation():
    with pytest.raises(ValidationError):
        Transaction("T1", "A1", "INVALID-DATE", 100, "income", "Test")

    with pytest.raises(ValidationError):
        Transaction("T2", "A1", "2025-01-01", -5, "income", "Test")


def test_budget_validation():
    with pytest.raises(ValidationError):
        Budget("B1", "2025-30", "Food", 200)

    with pytest.raises(ValidationError):
        Budget("B2", "2025-02", "Food", -10)


# ============================================================
# 2. INTEGRATION TESTS
# ============================================================

def test_account_transaction_integration():
    """Test interaction: transaction updates account balance."""
    am = AccountManager()
    tm = TransactionManager()

    acc = CashAccount("A1", "Wallet", "HUF", 1000)
    am.create(acc)

    tx = Transaction("T1", "A1", "2025-01-01", 200, "income", "Salary")
    tm.create(tx)

    # simulate main.py logic
    acc.balance += tx.amount
    assert acc.balance == 1200

    tx2 = Transaction("T2", "A1", "2025-01-02", 100, "expense", "Groceries")
    tm.create(tx2)

    acc.balance -= tx2.amount
    assert acc.balance == 1100


def test_budget_manager_integrates_with_save_load(tmp_path):
    bm = BudgetManager()
    csv_path = tmp_path / "budget.csv"

    b = Budget("B1", "2025-01", "Food", 200)
    bm.create(b)

    bm.save_csv(str(csv_path))
    assert os.path.exists(csv_path)

    bm2 = BudgetManager()
    bm2.load_csv(str(csv_path))

    assert bm2.get("B1").category == "Food"
    assert bm2.get("B1").limit_amount == 200


# ============================================================
# 3. SYSTEM-LEVEL TESTS
# ============================================================

def test_full_system_flow(tmp_path):
    """
    System test:
    - Create account
    - Create transactions
    - Create budget
    - Save all CSV
    - Load all CSV
    - Verify final balance + stored data
    """
    acc_csv = tmp_path / "accounts.csv"
    tx_csv = tmp_path / "transactions.csv"
    bud_csv = tmp_path / "budgets.csv"

    am = AccountManager()
    tm = TransactionManager()
    bm = BudgetManager()

    # Create system objects
    a = BankAccount("AC1", "MainAcc", "EUR", 500)
    am.create(a)

    t1 = Transaction("T1", "AC1", "2025-01-01", 300, "income", "Salary")
    tm.create(t1)
    a.balance += t1.amount  # simulate main.py logic

    t2 = Transaction("T2", "AC1", "2025-01-02", 100, "expense", "Shopping")
    tm.create(t2)
    a.balance -= t2.amount

    b = Budget("B1", "2025-01", "General", 800)
    bm.create(b)

    # Save all
    am.save_csv(str(acc_csv))
    tm.save_csv(str(tx_csv))
    bm.save_csv(str(bud_csv))

    # Load all into new managers
    am2 = AccountManager()
    tm2 = TransactionManager()
    bm2 = BudgetManager()

    am2.load_csv(str(acc_csv))
    tm2.load_csv(str(tx_csv))
    bm2.load_csv(str(bud_csv))

    # Verify system-level results
    acc2 = am2.get("AC1")
    assert acc2.balance == 700  # 500 + 300 - 100

    assert any(t.id == "T1" for t in tm2.list_all())
    assert any(t.id == "T2" for t in tm2.list_all())
    assert bm2.get("B1").limit_amount == 800


# ============================================================
# 4. EDGE CASE TESTS
# ============================================================

def test_duplicate_ids():
    am = AccountManager()
    acc = CashAccount("A1", "Wallet", "HUF", 100)
    am.create(acc)

    with pytest.raises(ValidationError):
        am.create(acc)  # duplicate ID


def test_not_found_errors():
    am = AccountManager()
    with pytest.raises(NotFoundError):
        am.get("UNKNOWN-ID")

    with pytest.raises(NotFoundError):
        am.delete("UNKNOWN-ID")
