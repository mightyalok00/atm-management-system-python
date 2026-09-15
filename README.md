# ATM Management System in Python

A console-based ATM Management System built with Python to demonstrate object-oriented programming, user-defined modules, JSON file handling, input validation, exception handling, loops, and persistent data storage.

This project is designed as a practical portfolio project for learning how multiple Python concepts work together in a real-world style application.

## Project Objective

The objective is to build a menu-driven ATM application where users can register, log in, manage their balance, change their PIN, and review transaction history while keeping account data saved permanently in JSON files.

## Features

- User registration with validation
- Automatic account number generation starting from `100000000001`
- Login using account number and password
- Withdraw money with balance validation
- Deposit money
- Check current balance
- Change ATM PIN
- Transaction history
- JSON-based persistent account storage
- Separate `User` and `ATM` classes
- Exception handling for invalid input and file errors
- `while` and `for` loops for menu flow and account processing
- Portable file paths using `pathlib`
- Windows launcher with bytecode disabled

## Python Concepts Demonstrated

- Object-Oriented Programming (OOP)
- Classes and objects
- User-defined modules
- Functions and methods
- `while` loops and `for` loops
- Conditional statements
- Lists and dictionaries
- JSON file handling
- Exception handling
- Input validation
- Static methods
- Time/date handling
- Persistent storage
- Unit testing with Python `unittest`

## Project Structure

```text
atm-management-system-python/
├── main.py
├── run_atm.bat
├── README.md
├── requirements.txt
├── .gitignore
├── classes/
│   ├── __init__.py
│   ├── UserConfig.py
│   └── ATMConfig.py
├── data/
│   ├── accounts.json
│   └── transactions.json
└── tests/
    ├── __init__.py
    └── test_atm.py
```

## Application Flow

```text
Start Application
      |
      v
=== ATM MANAGEMENT SYSTEM ===
1. Register
2. Login
3. Exit
      |
      v
Successful Login
      |
      v
=== ATM MENU ===
1. Withdraw
2. Check Balance
3. Change PIN
4. Deposit
5. Transaction History
6. Logout
```

## Validation Rules

The application validates user input before saving or processing it.

- Name must contain valid alphabetic characters
- Phone number must contain 10-15 digits
- Email must match a valid email format
- Password must contain uppercase, lowercase, number, and special character
- PIN must contain exactly 4 digits
- Deposit and withdrawal amounts must be positive finite numbers
- Duplicate phone numbers and email addresses are rejected
- Withdrawal is blocked when the account balance is insufficient

## Data Storage

Account information is stored in:

```text
data/accounts.json
```

Transaction records are stored in:

```text
data/transactions.json
```

The project uses relative paths based on the project location, so it can be moved to another folder or drive without changing the Python source code.

## Run the Project

### Windows

Clone or download the repository, open the project folder, then run:

```powershell
python -B main.py
```

or:

```powershell
py -B main.py
```

You can also double-click:

```text
run_atm.bat
```

The `-B` option prevents creation of `.pyc` files and `__pycache__` directories.

## Run the Unit Tests

From the repository root:

```powershell
python -B -m unittest discover -s tests -v
```

or:

```powershell
py -B -m unittest discover -s tests -v
```

The tests use temporary JSON files so the real account and transaction data in the repository are not modified.

## Test Coverage

The unit tests cover:

- Name, phone, email, password, PIN, and amount validation
- First account number generation
- Incrementing account numbers
- Deposit operation
- Withdrawal operation
- Insufficient balance handling
- PIN change with a correct current PIN
- PIN rejection when the current PIN is incorrect
- JSON persistence during account updates

## Example Menus

### Main Menu

```text
=== ATM MANAGEMENT SYSTEM ===
1. Register
2. Login
3. Exit
Enter choice:
```

### ATM Menu

```text
=== ATM MENU ===
1. Withdraw
2. Check Balance
3. Change PIN
4. Deposit
5. Transaction History
6. Logout
Enter choice:
```

## Security Note

This is an educational project. Passwords and PINs are stored in JSON for learning purposes. A production banking system must never store credentials in plaintext and would use secure password hashing, encryption, access controls, database security, audit logging, and additional authentication measures.

## Technologies Used

- Python 3
- Python Standard Library
- JSON
- `pathlib`
- `re`
- `time`
- `math`
- `unittest`

No third-party packages are required.

## Learning Outcomes

This project demonstrates how to:

- Organize Python code into multiple modules
- Apply OOP to a practical application
- Build menu-driven console programs
- Validate user input safely
- Read and write persistent JSON data
- Synchronize in-memory objects with stored records
- Handle expected runtime errors
- Write isolated unit tests for application logic

## Author

**Alok Agarwal**

GitHub: [mightyalok00](https://github.com/mightyalok00)

---

If you find this project useful, consider starring the repository.