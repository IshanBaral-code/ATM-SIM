"""
Domain exceptions for Apex Federal Bank ATM Simulation.
"""


class BankingError(Exception):
    """Base exception for all banking and ATM domain errors."""
    def __init__(self, message: str, user_friendly_message: str | None = None):
        super().__init__(message)
        self.user_friendly_message = user_friendly_message or message


class CardNotFoundError(BankingError):
    """Raised when card number cannot be found in the banking directory."""
    pass


class CardBlockedError(BankingError):
    """Raised when an attempt is made to use a locked/blocked card."""
    pass


class CardExpiredError(BankingError):
    """Raised when an inserted card has expired."""
    pass


class InvalidPINError(BankingError):
    """Raised when the PIN provided fails authentication."""
    def __init__(self, message: str, attempts_remaining: int):
        super().__init__(message)
        self.attempts_remaining = attempts_remaining


class InsufficientFundsError(BankingError):
    """Raised when an account has inadequate balance for withdrawal or transfer."""
    def __init__(self, requested: float, available: float):
        super().__init__(
            f"Insufficient funds: requested {requested:.2f}, available {available:.2f}",
            user_friendly_message=f"Insufficient funds. Your available balance is ${available:,.2f}."
        )
        self.requested = requested
        self.available = available


class DailyLimitExceededError(BankingError):
    """Raised when transaction would exceed the 24-hour ATM limit."""
    def __init__(self, requested: float, already_withdrawn: float, limit: float):
        remaining = max(0.0, limit - already_withdrawn)
        super().__init__(
            f"Daily withdrawal limit of ${limit:.2f} exceeded.",
            user_friendly_message=f"Daily limit reached. Remaining limit today: ${remaining:,.2f}."
        )
        self.requested = requested
        self.already_withdrawn = already_withdrawn
        self.limit = limit


class SingleWithdrawalLimitExceededError(BankingError):
    """Raised when single withdrawal exceeds machine limit."""
    pass


class InvalidAmountError(BankingError):
    """Raised when amount is negative, zero, or not a multiple of valid denominations."""
    pass


class AccountNotFoundError(BankingError):
    """Raised when target or source account is missing."""
    pass


class AccountFrozenError(BankingError):
    """Raised when an account is restricted or frozen."""
    pass


class ATMOutOfCashError(BankingError):
    """Raised when the ATM vault does not have sufficient cash."""
    pass


class DenominationNotPossibleError(BankingError):
    """Raised when the exact amount cannot be formed using available cassette bills."""
    pass


class HardwareFaultError(BankingError):
    """Raised on simulated hardware failures (shutter jam, printer out of paper)."""
    pass
