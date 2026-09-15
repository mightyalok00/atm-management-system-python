import json
import math
import re
import time
from pathlib import Path

from classes.UserConfig import User


class DataStoreError(RuntimeError):
    """Raised when persistent JSON data cannot be read safely."""


class ATM:
    """Handles ATM operations and JSON file storage."""

    STARTING_ACCOUNT_NUMBER = 100000000001
    INITIAL_BALANCE = 0.0

    def __init__(self):
        root = Path(__file__).resolve().parent.parent
        self.accounts_file = root / "data" / "accounts.json"
        self.transactions_file = root / "data" / "transactions.json"
        self.current_user = None
        self._ensure_files()

    def _ensure_files(self):
        """Create the data folder and JSON files when they do not exist."""
        try:
            self.accounts_file.parent.mkdir(parents=True, exist_ok=True)
            for file_path in (self.accounts_file, self.transactions_file):
                if not file_path.exists():
                    file_path.write_text("[]\n", encoding="utf-8")
        except OSError as error:
            raise DataStoreError(f"Could not initialize data files: {error}") from error

    @staticmethod
    def _load_json_list(file_path, label):
        """Load a JSON list and distinguish missing files from damaged data."""
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as error:
            raise DataStoreError(
                f"{label} contains invalid JSON (line {error.lineno}, column {error.colno})."
            ) from error
        except OSError as error:
            raise DataStoreError(f"Could not read {label}: {error}") from error

        if not isinstance(data, list):
            raise DataStoreError(f"{label} must contain a JSON list.")

        return data

    @staticmethod
    def _save_json_list(file_path, data, label):
        """Save JSON safely and return False when writing fails."""
        temp_file = file_path.with_suffix(file_path.suffix + ".tmp")

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            temp_file.replace(file_path)
            return True
        except (OSError, TypeError, ValueError) as error:
            print(f"Could not save {label}: {error}")
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError:
                pass
            return False

    def load_data(self):
        return self._load_json_list(self.accounts_file, "accounts.json")

    def save_data(self, accounts):
        return self._save_json_list(self.accounts_file, accounts, "account data")

    def generate_account_number(self):
        numbers = []

        for index, account in enumerate(self.load_data(), start=1):
            try:
                numbers.append(int(account["account_number"]))
            except (KeyError, TypeError, ValueError):
                print(f"Warning: skipped malformed account record #{index}.")

        return self.STARTING_ACCOUNT_NUMBER if not numbers else max(numbers) + 1

    @staticmethod
    def get_current_datetime():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def is_valid_name(name):
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z '\-]{1,49}", name.strip()))

    @staticmethod
    def is_valid_phone(phone):
        return phone.isdigit() and 10 <= len(phone) <= 15

    @staticmethod
    def is_valid_email(email):
        return bool(re.fullmatch(
            r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$",
            email.strip()
        ))

    @staticmethod
    def is_valid_password(password):
        return (
            8 <= len(password) <= 64
            and any(ch.isupper() for ch in password)
            and any(ch.islower() for ch in password)
            and any(ch.isdigit() for ch in password)
            and any(not ch.isalnum() for ch in password)
            and not any(ch.isspace() for ch in password)
        )

    @staticmethod
    def is_valid_pin(pin):
        return pin.isdigit() and len(pin) == 4

    @staticmethod
    def is_valid_amount(amount):
        return math.isfinite(amount) and amount > 0

    def main_menu(self):
        while True:
            print("\n=== ATM MANAGEMENT SYSTEM ===")
            print("1. Register")
            print("2. Login")
            print("3. Exit")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                print("Thank you for using the ATM.")
                break
            else:
                print("Invalid choice. Enter 1, 2 or 3.")

    def register(self):
        print("\n=== USER REGISTRATION ===")

        try:
            accounts = self.load_data()
        except DataStoreError as error:
            print(f"Registration unavailable: {error}")
            return

        while True:
            name = input("Enter full name: ").strip()
            if self.is_valid_name(name):
                break
            print("Invalid name.")

        while True:
            phone = input("Enter phone number: ").strip()
            if not self.is_valid_phone(phone):
                print("Invalid phone number.")
                continue
            if any(account.get("phone") == phone for account in accounts if isinstance(account, dict)):
                print("Phone number already registered.")
                continue
            break

        while True:
            email = input("Enter email address: ").strip().lower()
            if not self.is_valid_email(email):
                print("Invalid email address.")
                continue
            if any(
                str(account.get("email", "")).lower() == email
                for account in accounts
                if isinstance(account, dict)
            ):
                print("Email already registered.")
                continue
            break

        while True:
            password = input("Create password: ").strip()
            if self.is_valid_password(password):
                break
            print("Use uppercase, lowercase, number, special character and at least 8 characters.")

        while True:
            pin = input("Create 4-digit PIN: ").strip()
            if self.is_valid_pin(pin):
                break
            print("PIN must contain exactly 4 digits.")

        valid_numbers = []
        for index, account in enumerate(accounts, start=1):
            try:
                valid_numbers.append(int(account["account_number"]))
            except (KeyError, TypeError, ValueError):
                print(f"Warning: skipped malformed account record #{index}.")

        account_number = (
            self.STARTING_ACCOUNT_NUMBER
            if not valid_numbers
            else max(valid_numbers) + 1
        )

        new_account = {
            "account_number": account_number,
            "name": name,
            "phone": phone,
            "email": email,
            "pin": pin,
            "password": password,
            "balance": self.INITIAL_BALANCE,
            "created_at": self.get_current_datetime(),
        }

        accounts.append(new_account)

        if self.save_data(accounts):
            print("Account created successfully.")
            print(f"Your account number is: {account_number}")
        else:
            print("Account could not be saved.")

    def login(self):
        print("\n=== LOGIN ===")

        try:
            accounts = self.load_data()
        except DataStoreError as error:
            print(f"Login unavailable: {error}")
            return

        if not accounts:
            print("No accounts found. Register first.")
            return

        raw_account = input("Enter account number: ").strip()
        password = input("Enter password: ").strip()

        if not raw_account.isdigit() or not password:
            print("Invalid login details.")
            return

        account_number = int(raw_account)

        for index, account in enumerate(accounts, start=1):
            if not isinstance(account, dict):
                print(f"Warning: skipped malformed account record #{index}.")
                continue

            try:
                saved_number = int(account.get("account_number"))
            except (TypeError, ValueError):
                print(f"Warning: skipped malformed account record #{index}.")
                continue

            if saved_number == account_number and account.get("password") == password:
                required = (
                    "account_number", "name", "phone", "email",
                    "pin", "password", "balance", "created_at"
                )
                if any(key not in account for key in required):
                    print("This account record is incomplete and cannot be used.")
                    return

                try:
                    self.current_user = User(
                        account["account_number"],
                        account["name"],
                        account["phone"],
                        account["email"],
                        account["pin"],
                        account["password"],
                        account["balance"],
                        account["created_at"],
                    )
                except (TypeError, ValueError) as error:
                    print(f"This account record contains invalid data: {error}")
                    return

                print(f"Login successful. Welcome, {self.current_user.name}!")
                self.atm_menu()
                return

        print("Invalid account number or password.")

    def atm_menu(self):
        while self.current_user is not None:
            print("\n=== ATM MENU ===")
            print("1. Withdraw")
            print("2. Check Balance")
            print("3. Change PIN")
            print("4. Deposit")
            print("5. Transaction History")
            print("6. Logout")

            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.withdraw()
            elif choice == "2":
                self.check_balance()
            elif choice == "3":
                self.change_pin()
            elif choice == "4":
                self.deposit()
            elif choice == "5":
                self.show_transaction_history()
            elif choice == "6":
                self.current_user = None
                print("Logged out successfully.")
            else:
                print("Invalid choice. Enter 1-6.")

    def _read_amount(self, prompt):
        while True:
            raw = input(prompt).strip()
            try:
                amount = float(raw)
            except ValueError:
                print("Enter a valid number.")
                continue

            if not self.is_valid_amount(amount):
                print("Amount must be greater than zero.")
                continue

            return round(amount, 2)

    def _save_balance_transaction(self, transaction_type, amount, new_balance):
        """Save balance and transaction together, rolling back on failure."""
        old_balance = self.current_user.balance
        self.current_user.balance = round(new_balance, 2)

        if not self.update_user_data():
            self.current_user.balance = old_balance
            print(f"{transaction_type} could not be saved.")
            return False

        if self.record_transaction(transaction_type, amount):
            return True

        print("Transaction history could not be saved. Rolling back balance change.")
        self.current_user.balance = old_balance

        if not self.update_user_data():
            print("CRITICAL: balance rollback could not be saved. Check accounts.json immediately.")

        return False

    def withdraw(self):
        if self.current_user is None:
            print("Please login first.")
            return

        amount = self._read_amount("Enter withdrawal amount: ")

        if amount > self.current_user.balance:
            print("Insufficient balance.")
            return

        new_balance = self.current_user.balance - amount
        if self._save_balance_transaction("Withdraw", amount, new_balance):
            print(f"Withdrawal successful: Rs. {amount:.2f}")
            print(f"Updated balance: Rs. {self.current_user.balance:.2f}")

    def check_balance(self):
        if self.current_user is None:
            print("Please login first.")
            return
        print(f"Current balance: Rs. {self.current_user.balance:.2f}")

    def change_pin(self):
        if self.current_user is None:
            print("Please login first.")
            return

        old_pin = input("Enter current PIN: ").strip()

        if old_pin != self.current_user.pin:
            print("Incorrect current PIN.")
            return

        while True:
            new_pin = input("Enter new 4-digit PIN: ").strip()
            if not self.is_valid_pin(new_pin):
                print("PIN must contain exactly 4 digits.")
                continue
            if new_pin == old_pin:
                print("New PIN cannot be same as old PIN.")
                continue
            break

        previous_pin = self.current_user.pin
        self.current_user.pin = new_pin

        if self.update_user_data():
            print("PIN changed successfully.")
        else:
            self.current_user.pin = previous_pin
            print("PIN change could not be saved.")

    def deposit(self):
        if self.current_user is None:
            print("Please login first.")
            return

        amount = self._read_amount("Enter deposit amount: ")
        new_balance = self.current_user.balance + amount

        if self._save_balance_transaction("Deposit", amount, new_balance):
            print(f"Deposit successful: Rs. {amount:.2f}")
            print(f"Updated balance: Rs. {self.current_user.balance:.2f}")

    def update_user_data(self):
        if self.current_user is None:
            print("No logged-in user to update.")
            return False

        try:
            accounts = self.load_data()
        except DataStoreError as error:
            print(f"Could not update account: {error}")
            return False

        for index, account in enumerate(accounts, start=1):
            if not isinstance(account, dict):
                print(f"Warning: skipped malformed account record #{index}.")
                continue

            try:
                saved_number = int(account.get("account_number"))
            except (TypeError, ValueError):
                print(f"Warning: skipped malformed account record #{index}.")
                continue

            if saved_number == self.current_user.account_number:
                account.update({
                    "name": self.current_user.name,
                    "phone": self.current_user.phone,
                    "email": self.current_user.email,
                    "pin": self.current_user.pin,
                    "password": self.current_user.password,
                    "balance": self.current_user.balance,
                    "created_at": self.current_user.created_at,
                })
                return self.save_data(accounts)

        print("Current account could not be found in accounts.json.")
        return False

    def load_transactions(self):
        return self._load_json_list(self.transactions_file, "transactions.json")

    def save_transactions(self, transactions):
        return self._save_json_list(
            self.transactions_file, transactions, "transaction data"
        )

    def record_transaction(self, transaction_type, amount):
        try:
            transactions = self.load_transactions()
        except DataStoreError as error:
            print(f"Could not load transaction history: {error}")
            return False

        transactions.append({
            "account_number": self.current_user.account_number,
            "transaction_type": transaction_type,
            "amount": amount,
            "date_time": self.get_current_datetime(),
            "balance_after_transaction": self.current_user.balance,
        })

        return self.save_transactions(transactions)

    def show_transaction_history(self):
        if self.current_user is None:
            print("Please login first.")
            return

        try:
            transactions = self.load_transactions()
        except DataStoreError as error:
            print(f"Transaction history unavailable: {error}")
            return

        user_transactions = []

        for index, item in enumerate(transactions, start=1):
            if not isinstance(item, dict):
                print(f"Warning: skipped malformed transaction record #{index}.")
                continue

            try:
                account_number = int(item.get("account_number"))
            except (TypeError, ValueError):
                print(f"Warning: skipped malformed transaction record #{index}.")
                continue

            if account_number == self.current_user.account_number:
                user_transactions.append(item)

        if not user_transactions:
            print("No transaction history found.")
            return

        print("\n=== TRANSACTION HISTORY ===")

        for index, item in enumerate(user_transactions, start=1):
            try:
                amount = float(item.get("amount", 0))
                balance = float(item.get("balance_after_transaction", 0))
            except (TypeError, ValueError):
                print(f"{index}. Invalid transaction data")
                continue

            print(
                f"{index}. {item.get('date_time', 'Unknown date')} | "
                f"{item.get('transaction_type', 'Unknown')} | "
                f"Rs. {amount:.2f} | Balance: Rs. {balance:.2f}"
            )
