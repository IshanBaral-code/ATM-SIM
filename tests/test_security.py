"""
Unit tests for security, hashing, and Luhn algorithms.
"""

import unittest
from core.security import (
    clean_card_number,
    format_card_number,
    generate_salt,
    generate_tx_id,
    hash_pin,
    mask_card_number,
    validate_luhn,
    verify_pin,
)


class TestSecurity(unittest.TestCase):

    def test_pin_hashing_and_verification(self):
        pin = "1234"
        hashed, salt = hash_pin(pin)
        self.assertIsNotNone(hashed)
        self.assertIsNotNone(salt)
        self.assertEqual(len(hashed), 64)  # 32-byte sha256 hex is 64 chars

        # Valid verification
        self.assertTrue(verify_pin("1234", hashed, salt))

        # Invalid verification
        self.assertFalse(verify_pin("0000", hashed, salt))
        self.assertFalse(verify_pin("1235", hashed, salt))

    def test_salt_randomness(self):
        s1 = generate_salt()
        s2 = generate_salt()
        self.assertNotEqual(s1, s2)

    def test_clean_and_format_card_number(self):
        raw = "4532-0150-1122-3341"
        cleaned = clean_card_number(raw)
        self.assertEqual(cleaned, "4532015011223341")
        self.assertEqual(format_card_number(cleaned), "4532-0150-1122-3341")

    def test_luhn_validation(self):
        # Known valid cards
        self.assertTrue(validate_luhn("4532015011223341"))
        self.assertTrue(validate_luhn("4532-8820-1122-3344"))
        self.assertTrue(validate_luhn("4532-0091-1122-3343"))
        self.assertTrue(validate_luhn("4000-1234-1122-3342"))

        # Invalid checksum
        self.assertFalse(validate_luhn("4532015011223349"))
        self.assertFalse(validate_luhn("1234567812345671"))
        self.assertFalse(validate_luhn("123"))

    def test_mask_card_number(self):
        self.assertEqual(mask_card_number("4532-0150-1122-3341"), "****-****-****-3341")
        self.assertEqual(mask_card_number("4532015011223341"), "****-****-****-3341")

    def test_generate_tx_id(self):
        tx1 = generate_tx_id()
        tx2 = generate_tx_id()
        self.assertTrue(tx1.startswith("TXN-"))
        self.assertNotEqual(tx1, tx2)


if __name__ == "__main__":
    unittest.main()
