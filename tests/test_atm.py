import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from classes.ATMConfig import ATM
from classes.UserConfig import User


class ATMTestCase(unittest.TestCase):
    """Unit tests for validation and core ATM operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)

        self.atm = ATM()
        self.atm.accounts_file = temp_path / "accounts.json"
        self.atm.transactions_file = temp_path / "transactions.json"
        self.atm.accounts_file.write_text("[]\n", encoding="utf-8")
        self.atm.transactions_file.write_text("[]\n", encoding="utf-8")

        self.user = User(
            account_number=100000000001,
            name="Test User",
            phone="9876543210",
            email="test@example.com",
            pin="1234",
            password="Strong@123",
            balance=1000.0,
            created_at=self.atm.get_current_datetime(),
        )

        self.atm.current_user = self.user
        self.atm.save_data([
            {
                "account_number": self.user.account_number,
                "name": self.user.name,
                "phone": self.user.phone,
                "email": self.user.email,
                "pin": self.user.pin,
                "password": self.user.password,
                "balance": self.user.balance,
                "created_at": self.user.created_at,
            }
        ])

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validation_rules(self):
        self.assertTrue(self.atm.is_valid_name("Alok Agarwal"))
        self.assertFalse(self.atm.is_valid_name("1"))

        self.assertTrue(self.atm.is_valid_phone("9876543210"))
        self.assertFalse(self.atm.is_valid_phone("98AB765432"))

        self.assertTrue(self.atm.is_valid_email("alok@example.com"))
        self.assertFalse(self.atm.is_valid_email("alok@"))

        self.assertTrue(self.atm.is_valid_password("Strong@123"))
        self.assertFalse(self.atm.is_valid_password("weak"))

        self.assertTrue(self.atm.is_valid_pin("1234"))
        self.assertFalse(self.atm.is_valid_pin("12A4"))

        self.assertTrue(self.atm.is_valid_amount(100.0))
        self.assertFalse(self.atm.is_valid_amount(0))
        self.assertFalse(self.atm.is_valid_amount(-10))
        self.assertFalse(self.atm.is_valid_amount(float("nan")))
        self.assertFalse(self.atm.is_valid_amount(float("inf")))

    def test_first_account_number(self):
        self.atm.accounts_file.write_text("[]\n", encoding="utf-8")
        self.assertEqual(self.atm.generate_account_number(), 100000000001)

    def test_account_number_increments(self):
        self.assertEqual(self.atm.generate_account_number(), 100000000002)

    @patch("builtins.input", return_value="250")
    def test_deposit_updates_balance_and_json(self, _mock_input):
        self.atm.deposit()

        self.assertEqual(self.atm.current_user.balance, 1250.0)
        saved_account = self.atm.load_data()[0]
        self.assertEqual(saved_account["balance"], 1250.0)

        transactions = self.atm.load_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["transaction_type"], "Deposit")
        self.assertEqual(transactions[0]["amount"], 250.0)

    @patch("builtins.input", return_value="400")
    def test_withdraw_updates_balance_and_json(self, _mock_input):
        self.atm.withdraw()

        self.assertEqual(self.atm.current_user.balance, 600.0)
        saved_account = self.atm.load_data()[0]
        self.assertEqual(saved_account["balance"], 600.0)

        transactions = self.atm.load_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["transaction_type"], "Withdraw")
        self.assertEqual(transactions[0]["amount"], 400.0)

    @patch("builtins.input", return_value="1500")
    def test_withdraw_rejects_insufficient_balance(self, _mock_input):
        self.atm.withdraw()

        self.assertEqual(self.atm.current_user.balance, 1000.0)
        saved_account = self.atm.load_data()[0]
        self.assertEqual(saved_account["balance"], 1000.0)
        self.assertEqual(self.atm.load_transactions(), [])

    @patch("builtins.input", side_effect=["1234", "5678"])
    def test_change_pin_updates_user_and_json(self, _mock_input):
        self.atm.change_pin()

        self.assertEqual(self.atm.current_user.pin, "5678")
        saved_account = self.atm.load_data()[0]
        self.assertEqual(saved_account["pin"], "5678")

    @patch("builtins.input", return_value="9999")
    def test_change_pin_rejects_wrong_current_pin(self, _mock_input):
        self.atm.change_pin()

        self.assertEqual(self.atm.current_user.pin, "1234")
        saved_account = self.atm.load_data()[0]
        self.assertEqual(saved_account["pin"], "1234")


if __name__ == "__main__":
    unittest.main()
