import json
import math
import re
import time
from pathlib import Path

from classes.UserConfig import User


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
        self.accounts_file.parent.mkdir(parents=True, exist_ok=True)

        for file_path in (self.accounts_file, self.transactions_file):
            if not file_path.exists():
                file_path.write_text("[]\n", encoding="utf-8")

    def load_data(self):
        try:
            with self.accounts_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("accounts.json contains invalid JSON.")
            return []
        except OSError as error:
            print(f"Could not read account data: {error}")
            return []

    def save_data(self, accounts):
        try:
            with self.accounts_file.open("w", encoding="utf-8") as file:
                json.dump(accounts, file, indent=4)
            return True
        except OSError as error:
            print(f"Could not save account data: {error}")
            return False

    def generate_account_number(self):
        numbers = []

        for account in self.load_data():
            try:
                numbers.append(int(account["account_number"]))
            except (KeyError, TypeError, ValueError):
                continue

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

            if any(account.get("phone") == phone for account in self.load_data()):
                print("Phone number already registered.")
                continue

            break

        while True:
            email = input("Enter email address: ").strip().lower()

            if not self.is_valid_email(email):
                print("Invalid email address.")
                continue

            if any(str(account.get("email", "")).lower() == email for account in self.load_data()):
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

        account_number = self.generate_account_number()

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

        accounts = self.load_data()
        accounts.append(new_account)

        if self.save_data(accounts):
            print("Account created successfully.")
            print(f"Your account number is: {account_number}")
        else:
            print("Account could not be saved.")

    def login(self):
        print("\n=== LOGIN ===")
        accounts = self.load_data()

        if not accounts:
            print("No accounts found. Register first.")
            return

        raw_account = input("Enter account number: ").strip()
        password = input("Enter password: ").strip()

        if not raw_account.isdigit() or not password:
            print("Invalid login details.")
            return

        account_number = int(raw_account)

        for account in accounts:
            try:
                saved_number = int(account.get("account_number"))
            except (TypeError, ValueError):
                continue

            if saved_number == account_number and account.get("password") == password:
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

    def withdraw(self):
        amount = self._read_amount("Enter withdrawal amount: ")

        if amount > self.current_user.balance:
            print("Insufficient balance.")
            return

        old_balance = self.current_user.balance
        self.current_user.balance = round(old_balance - amount, 2)

        if self.update_user_data():
            self.record_transaction("Withdraw", amount)
            print(f"Withdrawal successful: Rs. {amount:.2f}")
            print(f"Updated balance: Rs. {self.current_user.balance:.2f}")
        else:
            self.current_user.balance = old_balance
            print("Withdrawal could not be saved.")

    def check_balance(self):
        print(f"Current balance: Rs. {self.current_user.balance:.2f}")

    def change_pin(self):
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
        amount = self._read_amount("Enter deposit amount: ")
        old_balance = self.current_user.balance
        self.current_user.balance = round(old_balance + amount, 2)

        if self.update_user_data():
            self.record_transaction("Deposit", amount)
            print(f"Deposit successful: Rs. {amount:.2f}")
            print(f"Updated balance: Rs. {self.current_user.balance:.2f}")
        else:
            self.current_user.balance = old_balance
            print("Deposit could not be saved.")

    def update_user_data(self):
        accounts = self.load_data()

        for account in accounts:
            try:
                saved_number = int(account.get("account_number"))
            except (TypeError, ValueError):
                continue

            if saved_number == self.current_user.account_number:
                account["pin"] = self.current_user.pin
                account["balance"] = self.current_user.balance
                return self.save_data(accounts)

        return False

    def load_transactions(self):
        try:
            with self.transactions_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("transactions.json contains invalid JSON.")
            return []
        except OSError as error:
            print(f"Could not read transaction data: {error}")
            return []

    def save_transactions(self, transactions):
        try:
            with self.transactions_file.open("w", encoding="utf-8") as file:
                json.dump(transactions, file, indent=4)
            return True
        except OSError as error:
            print(f"Could not save transaction data: {error}")
            return False

    def record_transaction(self, transaction_type, amount):
        transactions = self.load_transactions()

        transactions.append({
            "account_number": self.current_user.account_number,
            "transaction_type": transaction_type,
            "amount": amount,
            "date_time": self.get_current_datetime(),
            "balance_after_transaction": self.current_user.balance,
        })

        return self.save_transactions(transactions)

    def show_transaction_history(self):
        user_transactions = []

        for item in self.load_transactions():
            try:
                account_number = int(item.get("account_number"))
            except (TypeError, ValueError):
                continue

            if account_number == self.current_user.account_number:
                user_transactions.append(item)

        if not user_transactions:
            print("No transaction history found.")
            return

        print("\n=== TRANSACTION HISTORY ===")

        for index, item in enumerate(user_transactions, start=1):
            print(
                f"{index}. {item.get('date_time')} | "
                f"{item.get('transaction_type')} | "
                f"Rs. {float(item.get('amount', 0)):.2f} | "
                f"Balance: Rs. {float(item.get('balance_after_transaction', 0)):.2f}"
            )
