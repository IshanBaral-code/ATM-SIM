"""
ATM Session Controller orchestrating state transitions, hardware, and user actions.
"""

from enum import Enum
from typing import Callable, List, Optional, Tuple

from config import (
    BANK_NAME,
    DEFAULT_TTS_ENABLED,
    FAST_CASH_AMOUNTS,
    SUPPORTED_DENOMINATIONS,
)
from core.bank_service import BankService
from core.exceptions import BankingError, CardBlockedError, InvalidPINError
from core.models import Account, Card, DispenseResult, Transaction
from hardware.card_reader import CardReader
from hardware.cash_dispenser import CashDispenser
from hardware.receipt_printer import ReceiptPrinter
from hardware.speaker import AudioSpeaker
from storage.audit_logger import AuditLogger
from storage.database import get_connection, init_db
from storage.repository import BankRepository


class ATMState(str, Enum):
    IDLE = "IDLE"
    PIN_ENTRY = "PIN_ENTRY"
    ACCOUNT_SELECTION = "ACCOUNT_SELECTION"
    MAIN_MENU = "MAIN_MENU"
    WITHDRAW_SELECT = "WITHDRAW_SELECT"
    FAST_CASH_SELECT = "FAST_CASH_SELECT"
    DEPOSIT_INPUT = "DEPOSIT_INPUT"
    TRANSFER_INPUT = "TRANSFER_INPUT"
    BALANCE_DISPLAY = "BALANCE_DISPLAY"
    STATEMENT_DISPLAY = "STATEMENT_DISPLAY"
    PIN_CHANGE_INPUT = "PIN_CHANGE_INPUT"
    DISPENSING = "DISPENSING"
    RECEIPT_VIEW = "RECEIPT_VIEW"
    ADMIN_MENU = "ADMIN_MENU"


class ATMController:
    """Central state machine controlling user sessions and coordinating components."""

    def __init__(self, tts_enabled: bool = DEFAULT_TTS_ENABLED):
        # Database & Repo
        init_db()
        self.conn = get_connection()
        self.repo = BankRepository(self.conn)
        self.audit = AuditLogger(self.conn)

        # Hardware Emulation
        self.card_reader = CardReader(self.repo)
        self.cash_dispenser = CashDispenser(self.repo)
        self.printer = ReceiptPrinter()
        self.speaker = AudioSpeaker(tts_enabled=tts_enabled)

        # Core Service
        self.bank_service = BankService(self.repo, self.cash_dispenser, self.audit)

        # Session State
        self.state: ATMState = ATMState.IDLE
        self.current_card: Optional[Card] = None
        self.current_account: Optional[Account] = None
        self.available_accounts: List[Account] = []
        self.last_receipt: Optional[str] = None
        self.last_transaction: Optional[Transaction] = None
        self.last_dispense: Optional[DispenseResult] = None
        self.status_message: str = "Welcome! Please insert your debit/credit card to begin."

    def insert_card(self, card_number: str) -> None:
        """Inserts card into reader, transitions to PIN entry state."""
        self.speaker.play_key_beep()
        card = self.card_reader.insert_card(card_number)
        self.current_card = card
        self.state = ATMState.PIN_ENTRY
        self.status_message = f"Welcome, {card.holder_name}. Please enter your 4-digit PIN."
        self.speaker.speak(f"Welcome. Please enter your PIN and press Enter.")

    def enter_pin(self, pin: str) -> None:
        """Authenticates entered PIN and loads accounts."""
        if not self.current_card:
            raise BankingError("No card in reader.")

        try:
            self.speaker.play_key_beep()
            card = self.bank_service.authenticate_card(self.current_card.card_number, pin)
            self.current_card = card
            self.speaker.play_success_chime()

            # Check if Admin Card
            if self.current_card.card_number == "4000123411223342":
                self.state = ATMState.ADMIN_MENU
                self.status_message = "ATM Diagnostic & Administrator Console Active."
                self.speaker.speak("Administrator mode activated.")
                return

            # Fetch linked accounts
            self.available_accounts = self.bank_service.get_accounts_for_card(card.card_number)
            if not self.available_accounts:
                raise BankingError("No active bank accounts linked to this card.")

            if len(self.available_accounts) == 1:
                self.current_account = self.available_accounts[0]
                self.state = ATMState.MAIN_MENU
                self.status_message = "Select an operation from the menu."
                self.speaker.speak("Please select a transaction.")
            else:
                self.state = ATMState.ACCOUNT_SELECTION
                self.status_message = "Please select an account for this session."
                self.speaker.speak("Please select an account.")

        except (InvalidPINError, CardBlockedError) as e:
            self.speaker.play_error_tone()
            if isinstance(e, CardBlockedError):
                self.card_reader.eject_card()
                self.state = ATMState.IDLE
                self.current_card = None
                self.speaker.speak("Card locked. Please contact your bank.")
            else:
                self.speaker.speak("Incorrect PIN. Please try again.")
            raise

    def select_account(self, account_number: str) -> None:
        """Selects the active account for multi-account cards."""
        self.speaker.play_key_beep()
        acc = next((a for a in self.available_accounts if a.account_number == account_number), None)
        if not acc:
            raise BankingError(f"Account {account_number} not linked.")
        self.current_account = acc
        self.state = ATMState.MAIN_MENU
        self.status_message = f"Account active: {acc.account_type.value} (${acc.balance:,.2f})"
        self.speaker.speak("Select transaction.")

    def refresh_current_account(self) -> None:
        """Refreshes account balance from database."""
        if self.current_account:
            self.current_account = self.bank_service.get_account(self.current_account.account_number)

    def process_withdrawal(self, amount: float, is_fast_cash: bool = False) -> Tuple[Transaction, DispenseResult]:
        """Executes withdrawal, generates receipt, and updates state."""
        if not self.current_card or not self.current_account:
            raise BankingError("Session expired or card missing.")

        self.speaker.play_key_beep()
        tx, dispense = self.bank_service.withdraw(
            self.current_card.card_number,
            self.current_account.account_number,
            amount,
            is_fast_cash=is_fast_cash
        )
        self.last_transaction = tx
        self.last_dispense = dispense
        self.refresh_current_account()

        # Format receipt
        self.last_receipt = self.printer.format_withdrawal(tx, self.current_account, dispense.bills)

        # Trigger hardware sound and state
        self.speaker.play_cash_chime()
        self.speaker.speak(f"Please take your cash: ${amount:,.2f}.")
        self.state = ATMState.DISPENSING
        self.status_message = f"Dispensing ${amount:,.2f}. Please collect your cash."
        return tx, dispense

    def process_deposit(self, amount: float) -> Transaction:
        """Executes cash deposit and generates receipt."""
        if not self.current_card or not self.current_account:
            raise BankingError("Session expired or card missing.")

        self.speaker.play_key_beep()
        tx = self.bank_service.deposit(
            self.current_card.card_number,
            self.current_account.account_number,
            amount
        )
        self.last_transaction = tx
        self.refresh_current_account()
        self.last_receipt = self.printer.format_deposit(tx, self.current_account)

        self.speaker.play_success_chime()
        self.speaker.speak("Deposit accepted.")
        self.state = ATMState.RECEIPT_VIEW
        self.status_message = f"Successfully deposited ${amount:,.2f}."
        return tx

    def process_transfer(self, target_account_number: str, amount: float) -> Transaction:
        """Executes funds transfer to another account."""
        if not self.current_card or not self.current_account:
            raise BankingError("Session expired or card missing.")

        self.speaker.play_key_beep()
        tx = self.bank_service.transfer(
            self.current_card.card_number,
            self.current_account.account_number,
            target_account_number,
            amount
        )
        self.last_transaction = tx
        self.refresh_current_account()
        self.last_receipt = self.printer.format_transfer(tx, self.current_account, target_account_number)

        self.speaker.play_success_chime()
        self.speaker.speak("Funds transferred successfully.")
        self.state = ATMState.RECEIPT_VIEW
        self.status_message = f"Transferred ${amount:,.2f} to {target_account_number}."
        return tx

    def view_balance(self) -> str:
        """Loads balance inquiry and receipt."""
        if not self.current_card or not self.current_account:
            raise BankingError("Session expired or card missing.")

        self.refresh_current_account()
        self.speaker.play_key_beep()
        self.last_receipt = self.printer.format_balance_inquiry(
            self.current_card.card_number,
            self.current_account
        )
        self.state = ATMState.BALANCE_DISPLAY
        self.status_message = f"Available Balance: ${self.current_account.balance:,.2f}"
        return self.last_receipt

    def view_statement(self) -> List[Transaction]:
        """Loads mini-statement and receipt."""
        if not self.current_card or not self.current_account:
            raise BankingError("Session expired or card missing.")

        self.refresh_current_account()
        self.speaker.play_key_beep()
        txs = self.bank_service.get_statement(self.current_card.card_number, limit=8)
        self.last_receipt = self.printer.format_mini_statement(
            self.current_card.card_number,
            self.current_account,
            txs
        )
        self.state = ATMState.STATEMENT_DISPLAY
        self.status_message = "Displaying your recent transactions."
        return txs

    def process_pin_change(self, old_pin: str, new_pin: str) -> None:
        """Updates card PIN."""
        if not self.current_card:
            raise BankingError("Session expired.")

        self.speaker.play_key_beep()
        self.bank_service.change_pin(self.current_card.card_number, old_pin, new_pin)
        self.card_reader.refresh_current_card()
        self.speaker.play_success_chime()
        self.speaker.speak("PIN changed successfully.")
        self.state = ATMState.MAIN_MENU
        self.status_message = "Your PIN has been updated successfully."

    def eject_and_reset(self) -> None:
        """Ejects card and resets machine to standby."""
        self.speaker.play_key_beep()
        self.card_reader.eject_card()
        self.current_card = None
        self.current_account = None
        self.available_accounts = []
        self.last_receipt = None
        self.last_transaction = None
        self.last_dispense = None
        self.state = ATMState.IDLE
        self.status_message = "Please take your card. Thank you for choosing Apex Federal Bank."
        self.speaker.speak("Please take your card. Thank you for banking with us.")
