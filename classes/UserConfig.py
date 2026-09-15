class User:
    """Stores logged-in user account data."""

    def __init__(self, account_number, name, phone, email, pin, password, balance, created_at):
        self.account_number = int(account_number)
        self.name = name
        self.phone = phone
        self.email = email
        self.pin = pin
        self.password = password
        self.balance = float(balance)
        self.created_at = created_at
