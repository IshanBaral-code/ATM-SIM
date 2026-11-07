"""
Unit tests for BankService business logic, security policies, and transactions.
"""

from datetime import date
from pathlib import Path
import sqlite3
import tempfile
import unittest

from core.bank_service import BankService
from core.exceptions import (
    CardBlockedError,
    DailyLimitExceededError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPINError,
)
from core.models import TransactionType
from hardware.cash_dispenser import CashDispenser
from storage.audit_logger import AuditLogger
from storage.database import init_db, get_connection
from storage.repository import BankRepository


class TestBankService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_atm.db"
        init_db(self.db_path, seed_if_empty=True)
        self.conn = get_connection(self.db_path)
        self.repo = BankRepository(self.conn)
        self.audit = AuditLogger(self.conn)
        self.dispenser = CashDispenser(self.repo)
        self.service = BankService(self.repo, self.dispenser, self.audit)

        # Vance Card: 4532015011223341, PIN: 1234, Checking balance: 4850.00
        self.valid_card = "4532015011223341"
        self.valid_pin = "1234"
        self.checking_acc = "ACT-1001-CHK"
        self.savings_acc = "ACT-1002-SAV"

    def tearDown(self):
        self.conn.close()
        self.temp_dir.cleanup()

    def test_successful_authentication(self):
        card = self.service.authenticate_card(self.valid_card, self.valid_pin)
        self.assertIsNotNone(card)
        self.assertEqual(card.holder_name, "Alexander Vance")
        self.assertEqual(card.failed_attempts, 0)

    def test_failed_pin_attempt_lockout(self):
        # 1st wrong attempt
        with self.assertRaises(InvalidPINError) as ctx:
            self.service.authenticate_card(self.valid_card, "9998")
        self.assertEqual(ctx.exception.attempts_remaining, 2)

        # 2nd wrong attempt
        with self.assertRaises(InvalidPINError) as ctx:
            self.service.authenticate_card(self.valid_card, "9998")
        self.assertEqual(ctx.exception.attempts_remaining, 1)

        # 3rd wrong attempt -> locks card
        with self.assertRaises(CardBlockedError):
            self.service.authenticate_card(self.valid_card, "9998")

        # Now even with correct PIN, card is blocked
        with self.assertRaises(CardBlockedError):
            self.service.authenticate_card(self.valid_card, self.valid_pin)

    def test_successful_withdrawal(self):
        initial_acc = self.service.get_account(self.checking_acc)
        initial_balance = initial_acc.balance

        tx, dispense = self.service.withdraw(self.valid_card, self.checking_acc, 200.0)
        self.assertEqual(tx.amount, 200.0)
        self.assertEqual(dispense.amount, 200.0)

        # Verify updated balance
        updated_acc = self.service.get_account(self.checking_acc)
        self.assertEqual(updated_acc.balance, initial_balance - 200.0)
        self.assertEqual(updated_acc.daily_withdrawn_today, 200.0)

    def test_overdraft_prevention(self):
        # Brody card has only $45
        brody_card = "4532009111223343"
        brody_acc = "ACT-3001-CHK"
        with self.assertRaises(InsufficientFundsError):
            self.service.withdraw(brody_card, brody_acc, 60.0)

    def test_daily_withdrawal_limit(self):
        # Limit is $1500. Attempting $800 + $800 = $1600 should fail on second
        self.service.withdraw(self.valid_card, self.checking_acc, 800.0)
        with self.assertRaises(DailyLimitExceededError):
            self.service.withdraw(self.valid_card, self.checking_acc, 800.0)

    def test_transfer_between_accounts(self):
        chk_init = self.service.get_account(self.checking_acc).balance
        sav_init = self.service.get_account(self.savings_acc).balance

        tx = self.service.transfer(self.valid_card, self.checking_acc, self.savings_acc, 300.0)
        self.assertEqual(tx.amount, 300.0)

        chk_after = self.service.get_account(self.checking_acc).balance
        sav_after = self.service.get_account(self.savings_acc).balance

        self.assertEqual(chk_after, chk_init - 300.0)
        self.assertEqual(sav_after, sav_init + 300.0)

    def test_deposit(self):
        chk_init = self.service.get_account(self.checking_acc).balance
        tx = self.service.deposit(self.valid_card, self.checking_acc, 500.0)
        self.assertEqual(tx.amount, 500.0)

        chk_after = self.service.get_account(self.checking_acc).balance
        self.assertEqual(chk_after, chk_init + 500.0)

    def test_pin_change(self):
        self.service.change_pin(self.valid_card, self.valid_pin, "4829")
        # Old PIN fails
        with self.assertRaises(InvalidPINError):
            self.service.authenticate_card(self.valid_card, self.valid_pin)
        # New PIN succeeds
        card = self.service.authenticate_card(self.valid_card, "4829")
        self.assertIsNotNone(card)


if __name__ == "__main__":
    unittest.main()
