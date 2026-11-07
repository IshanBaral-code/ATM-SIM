"""
Unit tests for CashDispenser denomination algorithms and inventory tracking.
"""

import sqlite3
import unittest
from core.exceptions import ATMOutOfCashError, DenominationNotPossibleError, InvalidAmountError
from hardware.cash_dispenser import CashDispenser
from storage.repository import BankRepository


class TestCashDispenser(unittest.TestCase):

    def setUp(self):
        # In-memory database for testing
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE cassettes (
                denomination INTEGER PRIMARY KEY,
                count INTEGER NOT NULL
            );
        """)
        # Seed test cassettes: 10x $100 ($1000), 10x $50 ($500), 20x $20 ($400), 20x $10 ($200)
        self.conn.executemany(
            "INSERT INTO cassettes (denomination, count) VALUES (?, ?)",
            [(100, 10), (50, 10), (20, 20), (10, 20)]
        )
        self.repo = BankRepository(self.conn)
        self.dispenser = CashDispenser(self.repo)

    def tearDown(self):
        self.conn.close()

    def test_total_cash_available(self):
        expected = (10 * 100) + (10 * 50) + (20 * 20) + (20 * 10)  # $2,100
        self.assertEqual(self.dispenser.total_cash_available, expected)

    def test_optimal_greedy_dispense(self):
        # Request $280 -> 2x $100, 1x $50, 1x $20, 1x $10
        bills = self.dispenser.calculate_dispense(280)
        self.assertEqual(bills, {100: 2, 50: 1, 20: 1, 10: 1})
        self.assertEqual(sum(d * c for d, c in bills.items()), 280)

    def test_dispense_non_multiple_of_ten_fails(self):
        with self.assertRaises(InvalidAmountError):
            self.dispenser.calculate_dispense(25)

    def test_dispense_negative_or_zero_fails(self):
        with self.assertRaises(InvalidAmountError):
            self.dispenser.calculate_dispense(0)
        with self.assertRaises(InvalidAmountError):
            self.dispenser.calculate_dispense(-50)

    def test_dispense_exceeding_total_vault_fails(self):
        with self.assertRaises(ATMOutOfCashError):
            self.dispenser.calculate_dispense(5000)

    def test_actual_dispense_decrements_inventory(self):
        initial_vault = self.dispenser.total_cash_available
        res = self.dispenser.dispense(180)
        self.assertEqual(res.amount, 180)
        self.assertEqual(self.dispenser.total_cash_available, initial_vault - 180)

        # Check in DB
        db_cassettes = self.repo.get_cassettes()
        self.assertEqual(db_cassettes[100], 9)  # 10 - 1
        self.assertEqual(db_cassettes[50], 9)   # 10 - 1
        self.assertEqual(db_cassettes[20], 19)  # 20 - 1
        self.assertEqual(db_cassettes[10], 19)  # 20 - 1


if __name__ == "__main__":
    unittest.main()
