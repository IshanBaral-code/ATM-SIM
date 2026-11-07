"""
Data models and enumerations for Apex Federal Bank ATM Simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class AccountType(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEY MARKET"


class TransactionType(str, Enum):
    WITHDRAWAL = "CASH WITHDRAWAL"
    FAST_CASH = "FAST CASH"
    DEPOSIT = "CASH DEPOSIT"
    TRANSFER_OUT = "TRANSFER TO"
    TRANSFER_IN = "TRANSFER FROM"
    BALANCE_INQUIRY = "BALANCE INQUIRY"
    PIN_CHANGE = "PIN CHANGE"


@dataclass
class Account:
    account_number: str
    holder_name: str
    account_type: AccountType
    balance: float
    daily_withdrawn_today: float = 0.0
    is_frozen: bool = False

    @property
    def formatted_balance(self) -> str:
        return f"${self.balance:,.2f}"


@dataclass
class Card:
    card_number: str
    holder_name: str
    hashed_pin: str
    salt: str
    expiry_date: str  # MM/YY
    is_blocked: bool = False
    failed_attempts: int = 0
    primary_account_number: str = ""
    linked_account_numbers: List[str] = field(default_factory=list)


@dataclass
class Transaction:
    tx_id: str
    card_number: str
    account_number: str
    tx_type: TransactionType
    amount: float
    balance_after: float
    timestamp: datetime
    description: str = ""
    notes_dispensed: Optional[Dict[int, int]] = None
    fee: float = 0.0


@dataclass
class DispenseResult:
    amount: float
    bills: Dict[int, int]
    fee: float = 0.0

    @property
    def total_bills_count(self) -> int:
        return sum(self.bills.values())
