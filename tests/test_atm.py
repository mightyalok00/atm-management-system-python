import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from classes.ATMConfig import ATM
from classes.UserConfig import User


class ATMFullChecklistTests(unittest.TestCase):
    """Covers the project guide's full testing checklist."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.accounts_file = self.temp_path / "accounts.json"
        self.transactions_file = self.temp_path / "transactions.json"
        self.accounts_file.write_text("[]\n", encoding="utf-8")
        self.transactions_file.write_text("[]\n", encoding="utf-8")

        self.atm = ATM()
        self.atm.accounts_file = self.accounts_file
        self.atm.transactions_file = self.transactions_file

    def tearDown(self):
        self.temp_dir.cleanup()

    def seed_user(self, balance=1000.0, pin="1234", password="Strong@123"):
        user = User(
            100000000001,
            "Test User",
            "9876543210",
            "test@example.com",
            pin,
            password,
            balance,
            self.atm.get_current_datetime(),
        )
        self.atm.current_user = user
        self.atm.save_data([
            {
                "account_number": user.account_number,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "pin": user.pin,
                "password": user.password,
                "balance": user.balance,
                "created_at": user.created_at,
            }
        ])
        return user

    def test_no_accounts_exist(self):
        self.assertEqual(self.atm.load_data(), [])

    @patch(
        "builtins.input",
        side_effect=[
            "First User",
            "9876543210",
            "first@example.com",
            "Strong@123",
            "1234",
        ],
    )
    def test_register_first_account_uses_starting_number(self, _mock_input):
        self.atm.register()
        accounts = self.atm.load_data()
        self.assertEqual(accounts[0]["account_number"], 100000000001)

    @patch(
        "builtins.input",
        side_effect=[
            "Second User",
            "9876543211",
            "second@example.com",
            "Strong@456",
            "5678",
        ],
    )
    def test_register_second_account_increments_number(self, _mock_input):
        self.atm.save_data([
            {
                "account_number": 100000000001,
                "name": "First User",
                "phone": "9876543210",
                "email": "first@example.com",
                "pin": "1234",
                "password": "Strong@123",
                "balance": 0.0,
                "created_at": self.atm.get_current_datetime(),
            }
        ])
        self.atm.register()
        self.assertEqual(self.atm.load_data()[-1]["account_number"], 100000000002)

    def test_restart_preserves_existing_accounts(self):
        self.seed_user(balance=750.0)
        restarted = ATM()
        restarted.accounts_file = self.accounts_file
        restarted.transactions_file = self.transactions_file
        self.assertEqual(restarted.load_data()[0]["balance"], 750.0)

    @patch("builtins.input", side_effect=["999999999999", "Strong@123"])
    def test_login_rejects_incorrect_account_number(self, _mock_input):
        self.seed_user()
        self.atm.current_user = None
        self.atm.login()
        self.assertIsNone(self.atm.current_user)

    @patch("builtins.input", side_effect=["100000000001", "Wrong@123"])
    def test_login_rejects_incorrect_password(self, _mock_input):
        self.seed_user()
        self.atm.current_user = None
        self.atm.login()
        self.assertIsNone(self.atm.current_user)

    @patch.object(ATM, "atm_menu", return_value=None)
    @patch("builtins.input", side_effect=["100000000001", "Strong@123"])
    def test_login_succeeds_with_correct_credentials(self, _mock_input, _mock_menu):
        self.seed_user()
        self.atm.current_user = None
        self.atm.login()
        self.assertEqual(self.atm.current_user.account_number, 100000000001)

    def test_check_balance_displays_current_balance(self):
        self.seed_user(balance=1234.5)
        with patch("builtins.print") as mock_print:
            self.atm.check_balance()
        mock_print.assert_called_with("Current balance: Rs. 1234.50")

    @patch("builtins.input", return_value="250")
    def test_deposit_valid_amount(self, _mock_input):
        self.seed_user()
        self.atm.deposit()
        self.assertEqual(self.atm.load_data()[0]["balance"], 1250.0)

    @patch("builtins.input", side_effect=["0", "-50", "100"])
    def test_deposit_rejects_zero_and_negative(self, _mock_input):
        self.seed_user()
        self.atm.deposit()
        self.assertEqual(self.atm.current_user.balance, 1100.0)

    @patch("builtins.input", return_value="400")
    def test_withdraw_valid_amount(self, _mock_input):
        self.seed_user()
        self.atm.withdraw()
        self.assertEqual(self.atm.load_data()[0]["balance"], 600.0)

    @patch("builtins.input", return_value="1500")
    def test_withdraw_rejects_more_than_balance(self, _mock_input):
        self.seed_user()
        self.atm.withdraw()
        self.assertEqual(self.atm.current_user.balance, 1000.0)
        self.assertEqual(self.atm.load_transactions(), [])

    @patch("builtins.input", side_effect=["0", "-50", "100"])
    def test_withdraw_rejects_zero_and_negative(self, _mock_input):
        self.seed_user()
        self.atm.withdraw()
        self.assertEqual(self.atm.current_user.balance, 900.0)

    @patch("builtins.input", side_effect=["1234", "5678"])
    def test_change_pin_with_correct_old_pin(self, _mock_input):
        self.seed_user()
        self.atm.change_pin()
        self.assertEqual(self.atm.load_data()[0]["pin"], "5678")

    @patch("builtins.input", return_value="9999")
    def test_change_pin_rejects_incorrect_old_pin(self, _mock_input):
        self.seed_user()
        self.atm.change_pin()
        self.assertEqual(self.atm.current_user.pin, "1234")

    @patch("builtins.input", side_effect=["1234", "12A4", "1234", "5678"])
    def test_change_pin_rejects_invalid_and_same_new_pin(self, _mock_input):
        self.seed_user()
        self.atm.change_pin()
        self.assertEqual(self.atm.current_user.pin, "5678")

    @patch("builtins.input", return_value="200")
    def test_restart_preserves_balance_change(self, _mock_input):
        self.seed_user()
        self.atm.deposit()
        restarted = ATM()
        restarted.accounts_file = self.accounts_file
        restarted.transactions_file = self.transactions_file
        self.assertEqual(restarted.load_data()[0]["balance"], 1200.0)

    @patch("builtins.input", side_effect=["1234", "5678"])
    def test_restart_preserves_pin_change(self, _mock_input):
        self.seed_user()
        self.atm.change_pin()
        restarted = ATM()
        restarted.accounts_file = self.accounts_file
        restarted.transactions_file = self.transactions_file
        self.assertEqual(restarted.load_data()[0]["pin"], "5678")

    @patch("builtins.input", return_value="100")
    def test_deposit_creates_transaction_record(self, _mock_input):
        self.seed_user()
        self.atm.deposit()
        transaction = self.atm.load_transactions()[0]
        self.assertEqual(transaction["transaction_type"], "Deposit")
        self.assertEqual(transaction["amount"], 100.0)
        self.assertEqual(transaction["balance_after_transaction"], 1100.0)

    @patch("builtins.input", return_value="100")
    def test_withdraw_creates_transaction_record(self, _mock_input):
        self.seed_user()
        self.atm.withdraw()
        transaction = self.atm.load_transactions()[0]
        self.assertEqual(transaction["transaction_type"], "Withdraw")
        self.assertEqual(transaction["amount"], 100.0)
        self.assertEqual(transaction["balance_after_transaction"], 900.0)

    def test_validation_helpers(self):
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
        self.assertFalse(self.atm.is_valid_amount(-1))


if __name__ == "__main__":
    unittest.main()
