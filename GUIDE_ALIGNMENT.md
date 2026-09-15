# ATM Project Guide Alignment

This document maps the repository to the supplied ATM Management System project guide.

## Core Requirements

- ✅ Console-based Python ATM application
- ✅ Object-Oriented Programming with separate `User` and `ATM` classes
- ✅ User-defined modules under `classes/`
- ✅ JSON file handling for persistent account storage
- ✅ Exception handling for invalid numeric input and file/JSON errors
- ✅ Time/date handling for account creation and transactions
- ✅ Menu-driven application flow
- ✅ Automatic account number generation starting at `100000000001`
- ✅ User registration
- ✅ Login using account number and password
- ✅ Withdraw
- ✅ Check Balance
- ✅ Change PIN
- ✅ Deposit
- ✅ Persistent balance and PIN updates
- ✅ `accounts.json` account storage

## Optional / Extra Requirement

- ✅ Transaction history implemented with `transactions.json`
- ✅ Successful deposits create transaction records
- ✅ Successful withdrawals create transaction records
- ✅ Transaction records include account number, type, amount, timestamp, and balance after transaction
- ✅ Transaction History is available from the ATM menu

## Testing Checklist Coverage

The automated test suite in `tests/test_atm.py` covers the complete checklist from the guide:

- ✅ Program state with no accounts
- ✅ First account generates `100000000001`
- ✅ Second account increments to the next number
- ✅ Existing account data remains available after reload/restart simulation
- ✅ Incorrect account number is rejected
- ✅ Incorrect password is rejected
- ✅ Correct credentials log in successfully
- ✅ Current balance can be displayed
- ✅ Valid deposit updates balance
- ✅ Zero and negative deposit values are rejected
- ✅ Valid withdrawal updates balance
- ✅ Withdrawal above available balance is rejected
- ✅ Zero and negative withdrawal values are rejected
- ✅ PIN changes with the correct old PIN
- ✅ Incorrect old PIN is rejected
- ✅ Invalid new PIN is rejected
- ✅ Reusing the old PIN is rejected
- ✅ Balance changes persist after reload/restart simulation
- ✅ PIN changes persist after reload/restart simulation
- ✅ Successful deposits create transaction records
- ✅ Successful withdrawals create transaction records
- ✅ Validation helpers cover expected invalid user input

## Test Result

The expanded suite was validated against the current project implementation:

```text
Ran 21 tests
OK
```

Run the same suite from the repository root with:

```powershell
python -B -m unittest discover -s tests -v
```

or:

```powershell
py -B -m unittest discover -s tests -v
```

## Alignment Status

| Area | Status |
|---|---|
| Core project requirements | ✅ 100% covered |
| Optional transaction history | ✅ Covered |
| Testing checklist automation | ✅ 100% covered |
| Overall guide alignment | ✅ 100% covered |

### Note about the ATM menu

The guide lists `Exit` as option 5 in the basic version. This project implements the guide's optional transaction-history extension, so the final menu uses:

```text
5. Transaction History
6. Logout
```

This preserves all required core operations while adding the documented optional feature.
