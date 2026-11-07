"""
System configuration for the Apex Federal Bank ATM Simulation.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "atm_banking.db"
AUDIT_LOG_PATH = DATA_DIR / "atm_audit.log"

# Bank Identity
BANK_NAME = "APEX FEDERAL BANK"
BANK_TAGLINE = "Security, Integrity & Modern Banking"
TERMINAL_ID = "APX-4821"
TERMINAL_LOCATION = "Financial Center - Main Concourse"
SUPPORT_PHONE = "1-800-555-APEX (2739)"

# Currency & Formats
CURRENCY_SYMBOL = "$"
CURRENCY_CODE = "USD"

# Operational Limits
MAX_PIN_ATTEMPTS = 3
DAILY_WITHDRAWAL_LIMIT = 1500.00
MIN_WITHDRAWAL_AMOUNT = 10.00
MAX_SINGLE_WITHDRAWAL = 800.00
FAST_CASH_AMOUNTS = [20, 40, 60, 100, 200, 400]

# Hardware Denominations (in order of preference for greedy dispense)
SUPPORTED_DENOMINATIONS = [100, 50, 20, 10]
DEFAULT_CASSETTE_INVENTORY = {
    100: 80,   # $8,000
    50: 100,   # $5,000
    20: 250,   # $5,000
    10: 200,   # $2,000
}              # Total Vault: $20,000

# Audio / Voice Assistance
DEFAULT_TTS_ENABLED = True
TTS_SPEECH_RATE = 165  # Words per minute, natural pacing
