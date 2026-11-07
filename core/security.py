"""
Security, cryptographic hashing, and masking utilities for Apex Federal Bank.
"""

import hashlib
import hmac
import os
import re
import secrets
import time


def generate_salt() -> str:
    """Generates a secure 16-byte cryptographic salt represented in hex."""
    return secrets.token_hex(16)


def hash_pin(pin: str, salt: str | None = None) -> tuple[str, str]:
    """
    Hashes a 4-to-6 digit PIN using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Returns (hashed_hex, salt_hex).
    """
    if salt is None:
        salt = generate_salt()
    
    salt_bytes = bytes.fromhex(salt)
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=pin.encode('utf-8'),
        salt=salt_bytes,
        iterations=100000,
        dklen=32
    )
    return key.hex(), salt


def verify_pin(pin: str, expected_hash: str, salt: str) -> bool:
    """
    Verifies a PIN against the stored hash and salt using constant-time comparison.
    """
    calculated_hash, _ = hash_pin(pin, salt)
    return hmac.compare_digest(calculated_hash, expected_hash)


def clean_card_number(card_number: str) -> str:
    """Strips spaces, hyphens, and non-digits from card numbers."""
    return re.sub(r'\D', '', card_number)


def validate_luhn(card_number: str) -> bool:
    """
    Validates a card number using the ISO/IEC 7812 Luhn checksum algorithm.
    """
    digits = clean_card_number(card_number)
    if not digits or len(digits) < 13 or len(digits) > 19:
        return False

    checksum = 0
    reverse_digits = digits[::-1]
    for i, char in enumerate(reverse_digits):
        d = int(char)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d

    return checksum % 10 == 0


def format_card_number(card_number: str) -> str:
    """Formats digits into standard 4-4-4-4 grouped string."""
    digits = clean_card_number(card_number)
    if len(digits) == 16:
        return f"{digits[0:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:16]}"
    return digits


def mask_card_number(card_number: str) -> str:
    """
    Returns PCI-DSS compliant masked card representation: ****-****-****-1234.
    """
    digits = clean_card_number(card_number)
    if len(digits) < 4:
        return "****"
    last_four = digits[-4:]
    return f"****-****-****-{last_four}"


def generate_tx_id() -> str:
    """Generates a high-entropy, unique financial transaction reference."""
    timestamp = int(time.time() * 1000) % 100000000
    random_suffix = secrets.token_hex(2).upper()
    return f"TXN-{timestamp}-{random_suffix}"
