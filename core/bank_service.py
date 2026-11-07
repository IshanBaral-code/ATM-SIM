"""
Core banking service orchestrating accounts, limits, transactions, and security.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import (
    DAILY_WITHDRAWAL_LIMIT,
    MAX_PIN_ATTEMPTS,
    MAX_SINGLE_WITHDRAWAL,
    MIN_WITHDRAWAL_AMOUNT,
)
from core.exceptions import (
    AccountFrozenError,
    AccountNotFoundError,
    CardBlockedError,
    DailyLimitExceededError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPINError,
    SingleWithdrawalLimitExceededError,
)
from core.models import Account, Card, DispenseResult, Transaction, TransactionType
from core.security import (
    clean_card_number,
    generate_tx_id,
    hash_pin,
    verify_pin,
)
from hardware.cash_dispenser import CashDispenser
from storage.audit_logger import AuditLogger
from storage.repository import BankRepository


class BankService:
    """Manages transactional banking domain operations with full integrity guarantees."""

    def __init__(self, repo: BankRepository, dispenser: CashDispenser, audit: AuditLogger):
        self.repo = repo
        self.dispenser = dispenser
        self.audit = audit

    def authenticate_card(self, card_number: str, pin: str) -> Card:
        """
        Authenticates a card using salted PBKDF2 hash comparison.
        Tracks consecutive failures and locks card if MAX_PIN_ATTEMPTS is reached.
        """
        card_num = clean_card_number(card_number)
        card = self.repo.get_card(card_num)
        if not card:
            self.audit.log_event("AUTH_FAILED", card_num, "Card record not found", "WARNING")
            raise CardBlockedError("Card not recognized by system.")

        if card.is_blocked:
            self.audit.log_event("AUTH_BLOCKED", card_num, "Access attempted on locked card", "SECURITY")
            raise CardBlockedError("Card is locked due to security policy. Please contact customer support.")

        if not verify_pin(pin, card.hashed_pin, card.salt):
            new_attempts = card.failed_attempts + 1
            if new_attempts >= MAX_PIN_ATTEMPTS:
                self.repo.update_card_security(card_num, new_attempts, is_blocked=True)
                self.audit.log_event(
                    "CARD_LOCKED", card_num,
                    f"Card locked after {new_attempts} consecutive failed PIN attempts",
                    "SECURITY"
                )
                raise CardBlockedError(
                    f"Incorrect PIN. Your card has been locked after {MAX_PIN_ATTEMPTS} failed attempts."
                )
            else:
                self.repo.update_card_security(card_num, new_attempts, is_blocked=False)
                remaining = MAX_PIN_ATTEMPTS - new_attempts
                self.audit.log_event(
                    "AUTH_INCORRECT_PIN", card_num,
                    f"Incorrect PIN entered. {remaining} attempt(s) remaining.",
                    "WARNING"
                )
                raise InvalidPINError(
                    f"Invalid PIN. {remaining} attempt(s) remaining before card lockout.",
                    attempts_remaining=remaining
                )

        # Successful authentication: reset failed attempts counter
        if card.failed_attempts > 0:
            self.repo.update_card_security(card_num, failed_attempts=0, is_blocked=False)

        self.audit.log_event("AUTH_SUCCESS", card_num, f"Card authenticated for holder {card.holder_name}", "INFO")
        return self.repo.get_card(card_num)

    def get_account(self, account_number: str) -> Account:
        acc = self.repo.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return acc

    def get_accounts_for_card(self, card_number: str) -> List[Account]:
        return self.repo.get_accounts_for_card(card_number)

    def withdraw(
        self,
        card_number: str,
        account_number: str,
        amount: float,
        is_fast_cash: bool = False
    ) -> Tuple[Transaction, DispenseResult]:
        """
        Executes a cash withdrawal:
        1. Validates limits & balance.
        2. Solves note distribution & dispenses cash from machine.
        3. Updates account balance & logs transaction.
        """
        card_num = clean_card_number(card_number)
        account = self.get_account(account_number)

        if account.is_frozen:
            raise AccountFrozenError(f"Account {account_number} is frozen. Transaction declined.")

        if amount < MIN_WITHDRAWAL_AMOUNT:
            raise InvalidAmountError(f"Minimum withdrawal amount is ${MIN_WITHDRAWAL_AMOUNT:.2f}.")

        if amount > MAX_SINGLE_WITHDRAWAL:
            raise SingleWithdrawalLimitExceededError(
                f"Maximum single withdrawal is ${MAX_SINGLE_WITHDRAWAL:.2f}."
            )

        if (account.daily_withdrawn_today + amount) > DAILY_WITHDRAWAL_LIMIT:
            raise DailyLimitExceededError(
                requested=amount,
                already_withdrawn=account.daily_withdrawn_today,
                limit=DAILY_WITHDRAWAL_LIMIT
            )

        if account.balance < amount:
            raise InsufficientFundsError(requested=amount, available=account.balance)

        # Calculate and execute cash dispense
        dispense_res = self.dispenser.dispense(amount, fee=0.0)

        # Update database balance
        new_balance = round(account.balance - amount, 2)
        self.repo.update_account_balance(account_number, new_balance, daily_withdrawn_increment=amount)

        tx_type = TransactionType.FAST_CASH if is_fast_cash else TransactionType.WITHDRAWAL
        tx = Transaction(
            tx_id=generate_tx_id(),
            card_number=card_num,
            account_number=account_number,
            tx_type=tx_type,
            amount=amount,
            balance_after=new_balance,
            timestamp=datetime.now(),
            description=f"ATM Cash Withdrawal: {dispense_res.bills}",
            notes_dispensed=dispense_res.bills,
            fee=0.0
        )
        self.repo.record_transaction(tx)

        self.audit.log_event(
            "WITHDRAWAL", card_num,
            f"Dispensed ${amount:,.2f} from {account_number}. New bal: ${new_balance:,.2f}",
            "INFO"
        )
        return tx, dispense_res

    def deposit(self, card_number: str, account_number: str, amount: float) -> Transaction:
        """
        Processes cash deposit into an account and replenishes the ATM cassettes.
        """
        card_num = clean_card_number(card_number)
        account = self.get_account(account_number)

        if account.is_frozen:
            raise AccountFrozenError(f"Account {account_number} is frozen. Deposits declined.")

        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive.")

        if amount % 10 != 0:
            raise InvalidAmountError("Deposited bills must be in multiples of $10 ($10, $20, $50, $100).")

        new_balance = round(account.balance + amount, 2)
        self.repo.update_account_balance(account_number, new_balance, daily_withdrawn_increment=0.0)

        # Add deposited bills to dispenser cassettes (simulated standard distribution)
        current_inv = self.dispenser.inventory
        rem = int(amount)
        for denom in [100, 50, 20, 10]:
            add_count = rem // denom
            if add_count > 0:
                current_inv[denom] = current_inv.get(denom, 0) + add_count
                rem -= add_count * denom
        self.dispenser.reload_cassettes(current_inv)

        tx = Transaction(
            tx_id=generate_tx_id(),
            card_number=card_num,
            account_number=account_number,
            tx_type=TransactionType.DEPOSIT,
            amount=amount,
            balance_after=new_balance,
            timestamp=datetime.now(),
            description="ATM Cash Deposit Accepted",
            notes_dispensed=None,
            fee=0.0
        )
        self.repo.record_transaction(tx)

        self.audit.log_event(
            "DEPOSIT", card_num,
            f"Deposited ${amount:,.2f} into {account_number}. New bal: ${new_balance:,.2f}",
            "INFO"
        )
        return tx

    def transfer(
        self,
        card_number: str,
        source_account_number: str,
        target_account_number: str,
        amount: float
    ) -> Transaction:
        """
        Executes an atomic funds transfer between two accounts.
        """
        card_num = clean_card_number(card_number)
        if source_account_number == target_account_number:
            raise InvalidAmountError("Source and destination accounts must be different.")

        source = self.get_account(source_account_number)
        target = self.get_account(target_account_number)

        if source.is_frozen or target.is_frozen:
            raise AccountFrozenError("One of the transfer accounts is restricted.")

        if amount <= 0:
            raise InvalidAmountError("Transfer amount must be greater than zero.")

        if source.balance < amount:
            raise InsufficientFundsError(requested=amount, available=source.balance)

        # Debit source
        new_source_bal = round(source.balance - amount, 2)
        self.repo.update_account_balance(source_account_number, new_source_bal, 0.0)

        # Credit target
        new_target_bal = round(target.balance + amount, 2)
        self.repo.update_account_balance(target_account_number, new_target_bal, 0.0)

        tx_id = generate_tx_id()
        # Record source transfer-out
        tx_out = Transaction(
            tx_id=tx_id,
            card_number=card_num,
            account_number=source_account_number,
            tx_type=TransactionType.TRANSFER_OUT,
            amount=amount,
            balance_after=new_source_bal,
            timestamp=datetime.now(),
            description=f"Transfer to {target_account_number}",
            fee=0.0
        )
        self.repo.record_transaction(tx_out)

        # Record target transfer-in
        tx_in = Transaction(
            tx_id=f"{tx_id}-IN",
            card_number=card_num,
            account_number=target_account_number,
            tx_type=TransactionType.TRANSFER_IN,
            amount=amount,
            balance_after=new_target_bal,
            timestamp=datetime.now(),
            description=f"Transfer from {source_account_number}",
            fee=0.0
        )
        self.repo.record_transaction(tx_in)

        self.audit.log_event(
            "TRANSFER", card_num,
            f"Transferred ${amount:,.2f} from {source_account_number} to {target_account_number}",
            "INFO"
        )
        return tx_out

    def change_pin(self, card_number: str, old_pin: str, new_pin: str) -> None:
        """
        Validates the existing PIN, validates the format of new PIN, and saves the new hash.
        """
        card_num = clean_card_number(card_number)
        card = self.repo.get_card(card_num)
        if not card:
            raise CardBlockedError("Card not found.")

        if not verify_pin(old_pin, card.hashed_pin, card.salt):
            raise InvalidPINError("Current PIN is incorrect.", attempts_remaining=0)

        if not new_pin.isdigit() or len(new_pin) not in (4, 6):
            raise InvalidAmountError("New PIN must be 4 or 6 digits.")

        if old_pin == new_pin:
            raise InvalidAmountError("New PIN cannot be identical to the current PIN.")

        # Weak PIN checks
        if new_pin in ("0000", "1234", "1111", "9999", "123456"):
            raise InvalidAmountError("PIN is too simple. Choose a stronger combination.")

        new_hash, new_salt = hash_pin(new_pin)
        self.repo.update_card_pin(card_num, new_hash, new_salt)

        self.audit.log_event("PIN_CHANGE", card_num, "Card PIN updated successfully.", "SECURITY")

    def get_statement(self, card_number: str, limit: int = 10) -> List[Transaction]:
        return self.repo.get_transaction_history(card_number, limit)
