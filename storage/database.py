"""
Database connection and schema initialization for Apex Federal Bank.
"""

import json
import sqlite3
from datetime import datetime, date
from pathlib import Path

from config import DB_PATH, DEFAULT_CASSETTE_INVENTORY
from core.models import AccountType
from core.security import hash_pin


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with foreign keys enabled and row_factory set."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH, seed_if_empty: bool = True) -> None:
    """Initializes tables and optionally seeds default demo accounts."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number TEXT PRIMARY KEY,
                    holder_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    balance REAL NOT NULL,
                    daily_withdrawn_today REAL NOT NULL DEFAULT 0.0,
                    last_withdrawal_date TEXT,
                    is_frozen INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS cards (
                    card_number TEXT PRIMARY KEY,
                    holder_name TEXT NOT NULL,
                    hashed_pin TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    is_blocked INTEGER NOT NULL DEFAULT 0,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    primary_account_number TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS card_accounts (
                    card_number TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    PRIMARY KEY (card_number, account_number),
                    FOREIGN KEY (card_number) REFERENCES cards(card_number) ON DELETE CASCADE,
                    FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    tx_id TEXT PRIMARY KEY,
                    card_number TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    tx_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    balance_after REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    notes_dispensed_json TEXT,
                    fee REAL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS cassettes (
                    denomination INTEGER PRIMARY KEY,
                    count INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    card_masked TEXT,
                    details TEXT,
                    severity TEXT DEFAULT 'INFO'
                );
            """)

            # Initialize Cassettes if empty
            cur = conn.execute("SELECT COUNT(*) FROM cassettes")
            if cur.fetchone()[0] == 0:
                for denom, count in DEFAULT_CASSETTE_INVENTORY.items():
                    conn.execute(
                        "INSERT INTO cassettes (denomination, count) VALUES (?, ?)",
                        (denom, count)
                    )

            if seed_if_empty:
                cur = conn.execute("SELECT COUNT(*) FROM cards")
                if cur.fetchone()[0] == 0:
                    _seed_initial_data(conn)
    finally:
        conn.close()


def _seed_initial_data(conn: sqlite3.Connection) -> None:
    """Populates realistic demo accounts and cards."""
    today_str = date.today().isoformat()
    now_str = datetime.now().isoformat()

    # 1. Accounts
    accounts_data = [
        # Vance
        ("ACT-1001-CHK", "Alexander Vance", AccountType.CHECKING.value, 4850.00, 0.0, today_str, 0),
        ("ACT-1002-SAV", "Alexander Vance", AccountType.SAVINGS.value, 15200.00, 0.0, today_str, 0),
        # Sterling
        ("ACT-2001-CHK", "Eleanor Sterling", AccountType.CHECKING.value, 85400.00, 0.0, today_str, 0),
        ("ACT-2002-MM", "Eleanor Sterling", AccountType.MONEY_MARKET.value, 150000.00, 0.0, today_str, 0),
        # Brody (Low balance)
        ("ACT-3001-CHK", "Marcus Brody", AccountType.CHECKING.value, 45.00, 0.0, today_str, 0),
        # Tech Vault Account
        ("ACT-9999-SYS", "SYSTEM ADMINISTRATOR", AccountType.CHECKING.value, 1000000.00, 0.0, today_str, 0),
    ]
    conn.executemany(
        """INSERT INTO accounts 
           (account_number, holder_name, account_type, balance, daily_withdrawn_today, last_withdrawal_date, is_frozen)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        accounts_data
    )

    # 2. Cards with PBKDF2 hashed PINs
    # Vance: PIN 1234
    h1, s1 = hash_pin("1234")
    # Sterling: PIN 9999
    h2, s2 = hash_pin("9999")
    # Brody: PIN 0000
    h3, s3 = hash_pin("0000")
    # Admin: PIN 7777
    h4, s4 = hash_pin("7777")

    cards_data = [
        ("4532015011223341", "Alexander Vance", h1, s1, "12/28", 0, 0, "ACT-1001-CHK"),
        ("4532882011223344", "Eleanor Sterling", h2, s2, "08/29", 0, 0, "ACT-2001-CHK"),
        ("4532009111223343", "Marcus Brody", h3, s3, "03/27", 0, 0, "ACT-3001-CHK"),
        ("4000123411223342", "SYSTEM ADMINISTRATOR", h4, s4, "12/30", 0, 0, "ACT-9999-SYS"),
    ]
    conn.executemany(
        """INSERT INTO cards
           (card_number, holder_name, hashed_pin, salt, expiry_date, is_blocked, failed_attempts, primary_account_number)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        cards_data
    )

    # 3. Card-Account Linkages
    card_accounts_data = [
        ("4532015011223341", "ACT-1001-CHK"),
        ("4532015011223341", "ACT-1002-SAV"),
        ("4532882011223344", "ACT-2001-CHK"),
        ("4532882011223344", "ACT-2002-MM"),
        ("4532009111223343", "ACT-3001-CHK"),
        ("4000123411223342", "ACT-9999-SYS"),
    ]
    conn.executemany(
        "INSERT INTO card_accounts (card_number, account_number) VALUES (?, ?)",
        card_accounts_data
    )

    # 4. Initial Audit entry
    conn.execute(
        """INSERT INTO audit_logs (timestamp, event_type, card_masked, details, severity)
           VALUES (?, 'SYSTEM_INIT', NULL, 'Apex Federal Bank database initialized and seeded.', 'INFO')""",
        (now_str,)
    )
