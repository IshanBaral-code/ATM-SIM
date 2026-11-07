"""
Repository / Data Access Object (DAO) for Apex Federal Bank entities.
"""

from datetime import datetime, date
import json
import sqlite3
from typing import Dict, List, Optional

from core.models import Account, AccountType, Card, Transaction, TransactionType
from core.security import clean_card_number


class BankRepository:
    """Manages transactional database queries for cards, accounts, cassettes, and logs."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_card(self, raw_card_number: str) -> Optional[Card]:
        card_num = clean_card_number(raw_card_number)
        cur = self.conn.execute(
            """SELECT card_number, holder_name, hashed_pin, salt, expiry_date,
                      is_blocked, failed_attempts, primary_account_number
               FROM cards WHERE card_number = ?""",
            (card_num,)
        )
        row = cur.fetchone()
        if not row:
            return None

        # Fetch linked accounts
        acc_cur = self.conn.execute(
            "SELECT account_number FROM card_accounts WHERE card_number = ?",
            (card_num,)
        )
        linked = [r["account_number"] for r in acc_cur.fetchall()]

        return Card(
            card_number=row["card_number"],
            holder_name=row["holder_name"],
            hashed_pin=row["hashed_pin"],
            salt=row["salt"],
            expiry_date=row["expiry_date"],
            is_blocked=bool(row["is_blocked"]),
            failed_attempts=row["failed_attempts"],
            primary_account_number=row["primary_account_number"],
            linked_account_numbers=linked
        )

    def update_card_security(self, card_number: str, failed_attempts: int, is_blocked: bool) -> None:
        card_num = clean_card_number(card_number)
        with self.conn:
            self.conn.execute(
                """UPDATE cards 
                   SET failed_attempts = ?, is_blocked = ?
                   WHERE card_number = ?""",
                (failed_attempts, 1 if is_blocked else 0, card_num)
            )

    def update_card_pin(self, card_number: str, hashed_pin: str, salt: str) -> None:
        card_num = clean_card_number(card_number)
        with self.conn:
            self.conn.execute(
                """UPDATE cards 
                   SET hashed_pin = ?, salt = ?, failed_attempts = 0
                   WHERE card_number = ?""",
                (hashed_pin, salt, card_num)
            )

    def get_account(self, account_number: str) -> Optional[Account]:
        cur = self.conn.execute(
            """SELECT account_number, holder_name, account_type, balance,
                      daily_withdrawn_today, last_withdrawal_date, is_frozen
               FROM accounts WHERE account_number = ?""",
            (account_number,)
        )
        row = cur.fetchone()
        if not row:
            return None

        # Reset daily withdrawn if day changed
        today_str = date.today().isoformat()
        daily_withdrawn = row["daily_withdrawn_today"]
        if row["last_withdrawal_date"] != today_str:
            daily_withdrawn = 0.0
            with self.conn:
                self.conn.execute(
                    """UPDATE accounts 
                       SET daily_withdrawn_today = 0.0, last_withdrawal_date = ?
                       WHERE account_number = ?""",
                    (today_str, account_number)
                )

        return Account(
            account_number=row["account_number"],
            holder_name=row["holder_name"],
            account_type=AccountType(row["account_type"]),
            balance=row["balance"],
            daily_withdrawn_today=daily_withdrawn,
            is_frozen=bool(row["is_frozen"])
        )

    def get_accounts_for_card(self, raw_card_number: str) -> List[Account]:
        card_num = clean_card_number(raw_card_number)
        cur = self.conn.execute(
            """SELECT a.account_number, a.holder_name, a.account_type, a.balance,
                      a.daily_withdrawn_today, a.last_withdrawal_date, a.is_frozen
               FROM accounts a
               JOIN card_accounts ca ON a.account_number = ca.account_number
               WHERE ca.card_number = ?""",
            (card_num,)
        )
        today_str = date.today().isoformat()
        accounts = []
        for row in cur.fetchall():
            daily = row["daily_withdrawn_today"]
            if row["last_withdrawal_date"] != today_str:
                daily = 0.0
            accounts.append(
                Account(
                    account_number=row["account_number"],
                    holder_name=row["holder_name"],
                    account_type=AccountType(row["account_type"]),
                    balance=row["balance"],
                    daily_withdrawn_today=daily,
                    is_frozen=bool(row["is_frozen"])
                )
            )
        return accounts

    def update_account_balance(
        self,
        account_number: str,
        new_balance: float,
        daily_withdrawn_increment: float = 0.0
    ) -> None:
        today_str = date.today().isoformat()
        with self.conn:
            self.conn.execute(
                """UPDATE accounts 
                   SET balance = ?, 
                       daily_withdrawn_today = daily_withdrawn_today + ?,
                       last_withdrawal_date = ?
                   WHERE account_number = ?""",
                (new_balance, daily_withdrawn_increment, today_str, account_number)
            )

    def record_transaction(self, tx: Transaction) -> None:
        notes_json = json.dumps(tx.notes_dispensed) if tx.notes_dispensed else None
        with self.conn:
            self.conn.execute(
                """INSERT INTO transactions
                   (tx_id, card_number, account_number, tx_type, amount, balance_after,
                    timestamp, description, notes_dispensed_json, fee)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    tx.tx_id,
                    clean_card_number(tx.card_number),
                    tx.account_number,
                    tx.tx_type.value,
                    tx.amount,
                    tx.balance_after,
                    tx.timestamp.isoformat(),
                    tx.description,
                    notes_json,
                    tx.fee
                )
            )

    def get_transaction_history(self, raw_card_number: str, limit: int = 10) -> List[Transaction]:
        card_num = clean_card_number(raw_card_number)
        cur = self.conn.execute(
            """SELECT tx_id, card_number, account_number, tx_type, amount, balance_after,
                      timestamp, description, notes_dispensed_json, fee
               FROM transactions
               WHERE card_number = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (card_num, limit)
        )
        transactions = []
        for r in cur.fetchall():
            notes = json.loads(r["notes_dispensed_json"]) if r["notes_dispensed_json"] else None
            transactions.append(
                Transaction(
                    tx_id=r["tx_id"],
                    card_number=r["card_number"],
                    account_number=r["account_number"],
                    tx_type=TransactionType(r["tx_type"]),
                    amount=r["amount"],
                    balance_after=r["balance_after"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                    description=r["description"] or "",
                    notes_dispensed=notes,
                    fee=r["fee"] or 0.0
                )
            )
        return transactions

    def get_cassettes(self) -> Dict[int, int]:
        cur = self.conn.execute("SELECT denomination, count FROM cassettes ORDER BY denomination DESC")
        return {row["denomination"]: row["count"] for row in cur.fetchall()}

    def update_cassettes(self, inventory: Dict[int, int]) -> None:
        with self.conn:
            for denom, count in inventory.items():
                self.conn.execute(
                    """INSERT INTO cassettes (denomination, count)
                       VALUES (?, ?)
                       ON CONFLICT(denomination) DO UPDATE SET count = excluded.count""",
                    (denom, count)
                )

    def get_all_demo_cards(self) -> List[dict]:
        cur = self.conn.execute(
            """SELECT c.card_number, c.holder_name, c.expiry_date, c.is_blocked, c.primary_account_number,
                      a.balance, a.account_type
               FROM cards c
               LEFT JOIN accounts a ON c.primary_account_number = a.account_number"""
        )
        return [dict(r) for r in cur.fetchall()]

    def get_audit_logs(self, limit: int = 50) -> List[dict]:
        cur = self.conn.execute(
            """SELECT id, timestamp, event_type, card_masked, details, severity
               FROM audit_logs
               ORDER BY id DESC
               LIMIT ?""",
            (limit,)
        )
        return [dict(r) for r in cur.fetchall()]
