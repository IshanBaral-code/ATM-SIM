"""
End-to-End integration test simulating a complete user session via ATMController.
"""

from pathlib import Path
import tempfile
import unittest

from config import DEFAULT_CASSETTE_INVENTORY
from core.atm_controller import ATMController, ATMState
from storage.database import init_db


class TestATMIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "integ_atm.db"
        init_db(self.db_path, seed_if_empty=True)

        self.controller = ATMController(tts_enabled=False)
        # Override DB path for test isolation
        self.controller.conn.close()
        import sqlite3
        from storage.repository import BankRepository
        from storage.audit_logger import AuditLogger
        from hardware.card_reader import CardReader
        from hardware.cash_dispenser import CashDispenser
        from core.bank_service import BankService

        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        self.controller.conn = conn
        self.controller.repo = BankRepository(conn)
        self.controller.audit = AuditLogger(conn)
        self.controller.card_reader = CardReader(self.controller.repo)
        self.controller.cash_dispenser = CashDispenser(self.controller.repo)
        self.controller.bank_service = BankService(
            self.controller.repo,
            self.controller.cash_dispenser,
            self.controller.audit
        )

    def tearDown(self):
        self.controller.conn.close()
        self.temp_dir.cleanup()

    def test_full_user_session_journey(self):
        c = self.controller
        self.assertEqual(c.state, ATMState.IDLE)

        # 1. Insert Alexander Vance's Card
        c.insert_card("4532015011223341")
        self.assertEqual(c.state, ATMState.PIN_ENTRY)
        self.assertIsNotNone(c.current_card)

        # 2. Authenticate with PIN 1234
        c.enter_pin("1234")
        self.assertEqual(c.state, ATMState.ACCOUNT_SELECTION)
        self.assertEqual(len(c.available_accounts), 2)  # Checking and Savings

        # 3. Select Checking Account
        c.select_account("ACT-1001-CHK")
        self.assertEqual(c.state, ATMState.MAIN_MENU)
        self.assertEqual(c.current_account.balance, 4850.00)

        # 4. View Balance
        bal_receipt = c.view_balance()
        self.assertEqual(c.state, ATMState.BALANCE_DISPLAY)
        self.assertIn("$4,850.00", bal_receipt)

        # 5. Fast Cash $100
        tx, dispense = c.process_withdrawal(100.0, is_fast_cash=True)
        self.assertEqual(c.state, ATMState.DISPENSING)
        self.assertEqual(dispense.bills, {100: 1})
        self.assertEqual(c.current_account.balance, 4750.00)
        self.assertIn("$100.00", c.last_receipt)

        # 6. Mini-Statement
        txs = c.view_statement()
        self.assertEqual(c.state, ATMState.STATEMENT_DISPLAY)
        self.assertTrue(len(txs) >= 1)
        self.assertEqual(txs[0].amount, 100.0)

        # 7. Cash Deposit $300
        tx_dep = c.process_deposit(300.0)
        self.assertEqual(tx_dep.amount, 300.0)
        self.assertEqual(c.current_account.balance, 5050.00)

        # 8. Transfer $200 to Savings (ACT-1002-SAV)
        tx_tf = c.process_transfer("ACT-1002-SAV", 200.0)
        self.assertEqual(tx_tf.amount, 200.0)
        self.assertEqual(c.current_account.balance, 4850.00)

        # 9. Eject Card & Reset
        c.eject_and_reset()
        self.assertEqual(c.state, ATMState.IDLE)
        self.assertIsNone(c.current_card)
        self.assertIsNone(c.current_account)


if __name__ == "__main__":
    unittest.main()
