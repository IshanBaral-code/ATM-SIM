"""
Card Reader hardware emulation for Apex Federal Bank ATM.
"""

from datetime import datetime
from typing import Optional

from core.exceptions import CardBlockedError, CardExpiredError, CardNotFoundError, InvalidAmountError
from core.models import Card
from core.security import clean_card_number, validate_luhn
from storage.repository import BankRepository


class CardReader:
    """Emulates a motorized dip/smart-card reader."""

    def __init__(self, repo: BankRepository):
        self.repo = repo
        self._current_card: Optional[Card] = None

    @property
    def has_card(self) -> bool:
        return self._current_card is not None

    @property
    def current_card(self) -> Optional[Card]:
        return self._current_card

    def insert_card(self, raw_card_number: str) -> Card:
        """
        Validates card checksum, reads chip data, and checks status against the bank database.
        """
        card_num = clean_card_number(raw_card_number)
        if not validate_luhn(card_num):
            raise CardNotFoundError("Card read error: Invalid card number or checksum failed (Luhn check).")

        card = self.repo.get_card(card_num)
        if not card:
            raise CardNotFoundError("Card not recognized by Apex Federal Bank network.")

        if card.is_blocked:
            raise CardBlockedError(
                "Card is locked due to security restrictions or multiple failed attempts. "
                "Please contact customer service at 1-800-555-APEX."
            )

        # Check expiration (MM/YY)
        try:
            parts = card.expiry_date.split('/')
            exp_month = int(parts[0])
            exp_year = int("20" + parts[1]) if len(parts[1]) == 2 else int(parts[1])
            now = datetime.now()
            if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                raise CardExpiredError(f"Card expired in {card.expiry_date}.")
        except (ValueError, IndexError):
            pass

        self._current_card = card
        return card

    def eject_card(self) -> Optional[Card]:
        """Ejects the physical card from the reader."""
        card = self._current_card
        self._current_card = None
        return card

    def refresh_current_card(self) -> Optional[Card]:
        """Reloads card state from database (e.g. after PIN changes or lockouts)."""
        if self._current_card:
            self._current_card = self.repo.get_card(self._current_card.card_number)
        return self._current_card
