"""
Cash Dispenser emulation with multi-denomination cassette inventory tracking.
"""

from typing import Dict, Tuple

from config import SUPPORTED_DENOMINATIONS
from core.exceptions import ATMOutOfCashError, DenominationNotPossibleError, InvalidAmountError
from core.models import DispenseResult
from storage.repository import BankRepository


class CashDispenser:
    """
    Simulates physical ATM cash cassettes.
    Optimizes note distribution across $100, $50, $20, $10 bills while respecting inventory limits.
    """

    def __init__(self, repo: BankRepository):
        self.repo = repo
        self._inventory = self.repo.get_cassettes()

    @property
    def inventory(self) -> Dict[int, int]:
        """Returns the current count of bills per denomination."""
        return self._inventory.copy()

    @property
    def total_cash_available(self) -> float:
        """Total monetary value in the dispenser vault."""
        return sum(denom * count for denom, count in self._inventory.items())

    def reload_cassettes(self, new_inventory: Dict[int, int]) -> None:
        """Replenishes dispenser cassettes (Admin operation)."""
        self._inventory = new_inventory.copy()
        self.repo.update_cassettes(self._inventory)

    def calculate_dispense(self, amount: float) -> Dict[int, int]:
        """
        Determines the optimal bill breakdown using a greedy backtracking approach.
        Raises InvalidAmountError or DenominationNotPossibleError if impossible.
        """
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")

        if amount % 10 != 0:
            raise InvalidAmountError(
                f"Amount ${amount:.2f} is not a multiple of $10. "
                f"ATM dispenses $10, $20, $50, and $100 notes."
            )

        if amount > self.total_cash_available:
            raise ATMOutOfCashError(
                f"The ATM does not have sufficient cash to dispense ${amount:.2f}. "
                f"Available in machine: ${self.total_cash_available:,.2f}."
            )

        # Greedy algorithm with backtracking
        remaining = int(amount)
        solution: Dict[int, int] = {}
        sorted_denoms = sorted(SUPPORTED_DENOMINATIONS, reverse=True)

        for denom in sorted_denoms:
            avail = self._inventory.get(denom, 0)
            if avail <= 0:
                continue

            needed = remaining // denom
            take = min(needed, avail)
            if take > 0:
                solution[denom] = take
                remaining -= take * denom

        if remaining != 0:
            # If simple greedy failed due to odd leftover (e.g. needing $20 but only $50 & $10),
            # try dynamic backtracking
            solution = self._backtrack_dispense(int(amount), sorted_denoms)
            if not solution:
                raise DenominationNotPossibleError(
                    f"Unable to dispense exact ${amount:.2f} with available bill combinations."
                )

        return solution

    def _backtrack_dispense(self, amount: int, denoms: list[int]) -> Dict[int, int] | None:
        """Fallback dynamic programming/backtracking solver for exact bill combinations."""
        # Find exact partition
        memo: dict = {}

        def search(rem: int, idx: int) -> dict | None:
            if rem == 0:
                return {}
            if idx >= len(denoms) or rem < 0:
                return None
            key = (rem, idx)
            if key in memo:
                return memo[key]

            denom = denoms[idx]
            avail = self._inventory.get(denom, 0)
            max_take = min(rem // denom, avail)

            # Try from max_take down to 0
            for take in range(max_take, -1, -1):
                sub = search(rem - take * denom, idx + 1)
                if sub is not None:
                    res = sub.copy()
                    if take > 0:
                        res[denom] = take
                    memo[key] = res
                    return res

            memo[key] = None
            return None

        return search(amount, 0)

    def dispense(self, amount: float, fee: float = 0.0) -> DispenseResult:
        """
        Executes physical cash dispense: calculates bills, decrements cassette inventory,
        and commits to persistence.
        """
        bills = self.calculate_dispense(amount)

        # Deduct from inventory
        for denom, count in bills.items():
            self._inventory[denom] -= count

        # Commit to database
        self.repo.update_cassettes(self._inventory)

        return DispenseResult(amount=amount, bills=bills, fee=fee)
