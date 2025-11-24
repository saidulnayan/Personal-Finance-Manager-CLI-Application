
# Personal Finance Manager

A small CLI-based personal finance manager written in Python for the course assignment.
A separate .exe file named Finance manager.exe is also included to run the application directly.

** [App.exe Download link]([Download](https://drive.google.com/file/d/1z06SPwhKnnyhDGbT0M09krx5_DCput2B/view?usp=sharing)) **

## Features

* Manage Accounts, Transactions, Budgets (CRUD)
* Check Balance Summary
* Save / Load CSV persistence
* Simple menu-driven CLI
* Tests with pytest included

## Project structure

```
personal_finance_project/
├── main.py
├── models/
│   ├── account.py
│   ├── transaction.py
│   └── budget.py
├── managers/
│   ├── account_manager.py
│   ├── transaction_manager.py
│   └── budget_manager.py
├── storage/
│   └── csv_storage.py
├── tests/
│   └── test_finance.py
│   └── test_validators.py
├── data/
│   ├── accounts.csv
│   ├── transactions.csv
│   └── budgets.csv
├── exceptions.py
├── validators.py
│
├── requirements.txt
└── README.md
```

## How to run

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      #  on Windows

pip install -r requirements.txt
python main.py
```

## Testing

Run tests with pytest:

```bash
pytest -v tests\test_finance.py
```
