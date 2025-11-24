# main.py (updated)
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from managers.account_manager import AccountManager
from managers.transaction_manager import TransactionManager
from managers.budget_manager import BudgetManager
from models.account import Account, CashAccount, BankAccount
from models.transaction import Transaction
from models.budget import Budget

from validators import (
    validate_name, validate_currency, validate_positive_int,
    validate_date_ymd, validate_month_yyyy_mm, validate_category_choice
)
from exceptions import ValidationError

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ACC_CSV = os.path.join(DATA_DIR, "accounts.csv")
TX_CSV = os.path.join(DATA_DIR, "transactions.csv")
BUD_CSV = os.path.join(DATA_DIR, "budgets.csv")

console = Console()

def main_menu():
    table = Table(expand=True, show_header=False, box=None)
    table.add_column(justify="center")
    inner = Table(expand=True)
    inner.add_column("Option", justify="center", style="bold green")
    inner.add_column("Description", style="bold white")
    inner.add_row("1", "Manage Accounts")
    inner.add_row("2", "Manage Transactions")
    inner.add_row("3", "Manage Budgets")
    inner.add_row("4", "Check Balance Summary")
    inner.add_row("5", "Save to CSV")
    inner.add_row("6", "Load from CSV")
    inner.add_row("7", "Exit")
    table.add_row(inner)
    console.print(Panel(table, title="[bold cyan]Personal Finance Manager[/bold cyan]", title_align="center", border_style="cyan"))


def accounts_menu():
    table = Table(title="[bold yellow]Accounts Menu[/bold yellow]", title_justify="center")
    table.add_column("Option", justify="center", style="bold green")
    table.add_column("Action", style="bold white")
    table.add_row("1", "List accounts")
    table.add_row("2", "Create account")
    table.add_row("3", "Update account")
    table.add_row("4", "Delete account")
    table.add_row("5", "Back")
    console.print(table)


def transactions_menu():
    table = Table(title="[bold magenta]Transactions Menu[/bold magenta]", title_justify="center")
    table.add_column("Option", justify="center", style="bold green")
    table.add_column("Action", style="bold white")
    table.add_row("1", "List transactions")
    table.add_row("2", "Create transaction")
    table.add_row("3", "Update transaction")
    table.add_row("4", "Delete transaction")
    table.add_row("5", "Back")
    console.print(table)


def budgets_menu():
    table = Table(title="[bold blue]Budgets Menu[/bold blue]", title_justify="center")
    table.add_column("Option", justify="center", style="bold green")
    table.add_column("Action", style="bold white")
    table.add_row("1", "List budgets")
    table.add_row("2", "Create budget")
    table.add_row("3", "Update budget")
    table.add_row("4", "Delete budget")
    table.add_row("5", "Back")
    console.print(table)


def print_accounts(am: AccountManager):
    table = Table(title="[bold green]Accounts[/bold green]", title_justify="center")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="white")
    table.add_column("Type", style="yellow", justify="center")
    table.add_column("Balance", style="green", justify="right")
    table.add_column("Currency", style="white", justify="center")
    table.add_column("Class", style="magenta", justify="center")
    for a in am.list_all():
        table.add_row(a.id, a.name, a.account_type, f"{a.balance:.2f} {a.currency}", a.currency, a.__class__.__name__)
    console.print(table)


def print_transactions(tm: TransactionManager, am: AccountManager):
    table = Table(title="[bold magenta]Transactions[/bold magenta]", title_justify="center")
    table.add_column("ID", justify="center")
    table.add_column("Account", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Amount", justify="right")
    table.add_column("Category", justify="center")
    table.add_column("Description", justify="left")
    for tx in tm.list_all():
        acc = am.get_by_id(tx.account_id)
        cur = acc.currency if acc else ""
        table.add_row(tx.id, tx.account_id, tx.date, f"{tx.amount:.2f} {cur}", tx.category, tx.description)
    console.print(table)


def print_budgets(bm: BudgetManager, am: AccountManager):
    table = Table(title="[bold blue]Budgets[/bold blue]", title_justify="center")
    table.add_column("ID", justify="center")
    table.add_column("Month", justify="center")
    table.add_column("Category")
    table.add_column("Limit", justify="right")
    default_cur = next((a.currency for a in am.list_all()), "N/A")
    for b in bm.list_all():
        table.add_row(b.id, b.month, b.category, f"{b.limit_amount:.2f} {default_cur}")
    console.print(table)


def show_balance_summary(am: AccountManager, tm: TransactionManager, bm: BudgetManager):
    currency_totals = {}
    for acc in am.list_all():
        currency_totals.setdefault(acc.currency, 0)
        currency_totals[acc.currency] += acc.balance
    income_totals = {}
    expense_totals = {}
    for tx in tm.list_all():
        acc = am.get_by_id(tx.account_id)
        if not acc:
            continue
        cur = acc.currency
        if tx.category.lower() == "income":
            income_totals.setdefault(cur, 0)
            income_totals[cur] += tx.amount
        else:
            expense_totals.setdefault(cur, 0)
            expense_totals[cur] += tx.amount
    budget_totals = {}
    default_cur = next((a.currency for a in am.list_all()), "N/A")
    for b in bm.list_all():
        budget_totals.setdefault(default_cur, 0)
        budget_totals[default_cur] += b.limit_amount
    table = Table(title="[bold cyan]Financial Summary[/bold cyan]", title_justify="center")
    table.add_column("Currency", justify="center")
    table.add_column("Total Budget", justify="center", style="yellow")
    table.add_column("Total Income", justify="center", style="green")
    table.add_column("Total Expense", justify="center", style="red")
    table.add_column("Total Balance inAccounts", justify="center", style="cyan")
    all_curr = set(currency_totals.keys()) | set(income_totals.keys()) | set(expense_totals.keys()) | set(budget_totals.keys())
    for cur in all_curr:
        table.add_row(
            cur,
            f"{budget_totals.get(cur, 0):.2f} {cur}",
            f"{income_totals.get(cur, 0):.2f} {cur}",
            f"{expense_totals.get(cur, 0):.2f} {cur}",
            f"{currency_totals.get(cur, 0):.2f} {cur}",
        )
    console.print(table)


def prompt_until_valid(prompt_text: str, validator_func, *vargs, **vkwargs):
    """
    Generic helper: keep prompting until validator_func returns a cleaned/parsed value
    or raise ValidationError to show message and ask again.
    """
    while True:
        value = Prompt.ask(prompt_text)
        try:
            return validator_func(value, *vargs, **vkwargs)
        except ValidationError as e:
            console.print(f"[red]Invalid input: {e}[/red]")


def run_cli():
    am = AccountManager()
    tm = TransactionManager()
    bm = BudgetManager()
    # auto-load if files exist
    am.load(ACC_CSV)
    tm.load(TX_CSV)
    bm.load(BUD_CSV)

    while True:
        main_menu()
        choice = Prompt.ask("Choose option", choices=[str(i) for i in range(1, 8)])
        if choice == "1":
            # Accounts
            while True:
                accounts_menu()
                c = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"])
                if c == "1":
                    print_accounts(am)
                elif c == "2":
                    # Create account with repeated validation prompts
                    id_ = Prompt.ask("Account ID").strip()
                    name = prompt_until_valid("Name", validate_name, "Name", 15)
                    acc_type = Prompt.ask("Type", choices=["cash", "bank", "other"], default="cash")
                    currency = prompt_until_valid("Currency (e.g. HUF, EUR, USD)", validate_currency)
                    balance = prompt_until_valid("Starting Balance (positive integer)", validate_positive_int, "Starting Balance")
                    # instantiate proper subclass
                    if acc_type == "cash":
                        acc = CashAccount(id_, name, currency, float(balance))
                    elif acc_type == "bank":
                        acc = BankAccount(id_, name, currency, float(balance))
                    else:
                        acc = Account(id_, name, acc_type, currency, float(balance))
                    try:
                        am.create(acc)
                        console.print("[green]Account created successfully![/green]")
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                elif c == "3":
                    id_ = Prompt.ask("Account ID to update").strip()
                    acc = am.get_by_id(id_)
                    if not acc:
                        console.print("[red]Account not found.[/red]")
                        continue
                    # new name (optional)
                    while True:
                        new_name = Prompt.ask("New name (leave blank to skip)", default="")
                        if not new_name:
                            break
                        try:
                            validated = validate_name(new_name, "New Name", 15)
                            acc.name = validated
                            console.print("[green]Name updated.[/green]")
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    # Adjust balance -> set new value (must be positive int)
                    while True:
                        new_bal = Prompt.ask("Set new balance (positive integer) (blank to skip)", default="")
                        if new_bal.strip() == "":
                            break
                        try:
                            nb = validate_positive_int(new_bal, "New Balance")
                            acc.balance = float(nb)
                            console.print("[green]Balance set.[/green]")
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                elif c == "4":
                    id_ = Prompt.ask("Account ID to delete").strip()
                    try:
                        am.delete(id_)
                        console.print("[green]Deleted.[/green]")
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                else:
                    break
        elif choice == "2":
            # Transactions
            while True:
                transactions_menu()
                c = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"])
                if c == "1":
                    print_transactions(tm, am)
                elif c == "2":
                    id_ = Prompt.ask("Transaction ID").strip()
                    account_id = Prompt.ask("Account ID").strip()
                    acc = am.get_by_id(account_id)
                    if not acc:
                        console.print("[red]Account not found.[/red]")
                        continue
                    date = prompt_until_valid("Date (YYYY-MM-DD)", validate_date_ymd, "Date")
                    amount = prompt_until_valid("Amount (positive integer)", validate_positive_int, "Amount")
                    console.print("[yellow]Select category: 1) income  2) expense[/yellow]")
                    cat_choice = prompt_until_valid("Enter 1 or 2", validate_category_choice)
                    description = Prompt.ask("Description", default="")
                    tx = Transaction(id_, account_id, date, float(amount), cat_choice, description)
                    try:
                        tm.create(tx)
                        # update balance
                        if cat_choice == "income":
                            acc.balance += float(amount)
                        else:
                            acc.balance -= float(amount)
                        console.print("[green]Transaction created and balance updated.[/green]")
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                elif c == "3":
                    # Update transaction (allow change of description, amount, date, and category)
                    txid = Prompt.ask("Transaction ID to update").strip()
                    try:
                        tx = tm.get(txid)
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                        continue
                    # We will allow editing date, amount, category, description.
                    # If amount or category change, we must adjust account balance accordingly.
                    acc = am.get_by_id(tx.account_id)
                    old_amount = tx.amount
                    old_category = tx.category.lower()
                    # Date
                    while True:
                        new_date = Prompt.ask(f"New date [{tx.date}] (blank to keep)")
                        if not new_date.strip():
                            break
                        try:
                            nx = validate_date_ymd(new_date, "Date")
                            tx.date = nx
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    # Amount
                    while True:
                        new_amt = Prompt.ask(f"New amount [{tx.amount}] (blank to keep)")
                        if not new_amt.strip():
                            break
                        try:
                            na = validate_positive_int(new_amt, "Amount")
                            tx.amount = float(na)
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    # Category
                    while True:
                        console.print("[yellow]Select category: 1) income  2) expense[/yellow]")
                        new_cat = Prompt.ask(f"New category [{tx.category}] (enter 1 or 2 or blank to keep)", default="")
                        if not new_cat.strip():
                            break
                        try:
                            nc = validate_category_choice(new_cat)
                            tx.category = nc
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    # Description
                    nd = Prompt.ask(f"New description [{tx.description}] (blank to keep)", default="")
                    if nd.strip():
                        tx.description = nd
                    # now adjust balance if category/amount changed
                    if acc:
                        # remove old effect
                        if old_category == "income":
                            acc.balance -= old_amount
                        else:
                            acc.balance += old_amount
                        # apply new effect
                        if tx.category.lower() == "income":
                            acc.balance += tx.amount
                        else:
                            acc.balance -= tx.amount
                    console.print("[green]Transaction updated.[/green]")
                elif c == "4":
                    txid = Prompt.ask("Transaction ID to delete").strip()
                    try:
                        # before deleting, reverse its effect on the account
                        tx = tm.get(txid)
                        acc = am.get_by_id(tx.account_id)
                        if acc:
                            if tx.category.lower() == "income":
                                acc.balance -= tx.amount
                            else:
                                acc.balance += tx.amount
                        tm.delete(txid)
                        console.print("[green]Transaction deleted and balance adjusted.[/green]")
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                else:
                    break
        elif choice == "3":
            # Budgets
            while True:
                budgets_menu()
                c = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"])
                if c == "1":
                    print_budgets(bm, am)
                elif c == "2":
                    id_ = Prompt.ask("Budget ID").strip()
                    month = prompt_until_valid("Month (YYYY-MM)", validate_month_yyyy_mm, "Month")
                    category = Prompt.ask("Category").strip()
                    limit = prompt_until_valid("Limit amount (positive integer)", validate_positive_int, "Limit amount")
                    b = Budget(id_, month, category, float(limit))
                    bm.create(b)
                    console.print("[green]Budget created.[/green]")
                elif c == "3":
                    bid = Prompt.ask("Budget ID to update").strip()
                    try:
                        b = bm.get(bid)
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                        continue
                    # update month
                    while True:
                        nm = Prompt.ask(f"New month [{b.month}] (blank to keep)", default="")
                        if not nm.strip():
                            break
                        try:
                            b.month = validate_month_yyyy_mm(nm, "Month")
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    # update limit
                    while True:
                        nl = Prompt.ask(f"New limit amount [{b.limit_amount}] (blank to keep)", default="")
                        if not nl.strip():
                            break
                        try:
                            b.limit_amount = float(validate_positive_int(nl, "Limit amount"))
                            break
                        except ValidationError as e:
                            console.print(f"[red]{e}[/red]")
                    console.print("[green]Budget updated.[/green]")
                elif c == "4":
                    bid = Prompt.ask("Budget ID to delete").strip()
                    try:
                        bm.delete(bid)
                        console.print("[green]Budget deleted.[/green]")
                    except Exception as e:
                        console.print(f"[red]{e}[/red]")
                else:
                    break
        elif choice == "4":
            show_balance_summary(am, tm, bm)
        elif choice == "5":
            am.save(ACC_CSV)
            tm.save(TX_CSV)
            bm.save(BUD_CSV)
            console.print("[green]All data saved to CSV![/green]")
        elif choice == "6":
            am.load(ACC_CSV)
            tm.load(TX_CSV)
            bm.load(BUD_CSV)
            console.print("[green]All data loaded from CSV![/green]")
        elif choice == "7":
            # auto-save on exit
            try:
                am.save(ACC_CSV)
                tm.save(TX_CSV)
                bm.save(BUD_CSV)
            except Exception:
                pass
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break

if __name__ == "__main__":
    run_cli()
