"""
test_phone_normalization.py - Tests for Cambodian phone number normalization, lengths, and prefix handling.

Tests verify:
1. Normalization pipeline (independent of volatile carrier prefix tables):
   - Strips whitespace, hyphens, parentheses, and dots.
   - Converts Khmer numerals (០-៩) to ASCII digits (0-9).
   - Handles +855, 00855, 855, domestic 0, and accidental '+8550' inputs.
2. Different number lengths under the ITU-T / TRC National Numbering Plan:
   - 8-digit NSN (standard 9-digit domestic, e.g. 012 xxx xxx).
   - 9-digit NSN (extended 10-digit domestic, e.g. 096 xxx xxxx).
   - Rejection of invalid lengths (too short or too long).
3. Separation of normalization from prefix tables:
   - Verifies that syntax normalization is decoupled from carrier prefix mapping.
4. Verification boundary:
   - Confirms that syntax validation never asserts an active SIM or user ownership.
"""

import unittest
from typing import Dict, Optional, Tuple


def normalize_cambodian_phone(input_str: str) -> Dict[str, Optional[object]]:
    """
    Reference normalization algorithm for Cambodian phone numbers.
    Decoupled from carrier prefix assignment tables.
    """
    if not input_str or not isinstance(input_str, str):
        return {
            "raw": input_str,
            "nsn": None,
            "e164": None,
            "domestic": None,
            "is_valid_syntax": False,
            "requires_otp_verification": True,
            "is_active_sim": False,  # Never claim active status from syntax alone
            "error": "Input is empty or not a string",
        }

    # 1. Strip whitespace, hyphens, parentheses, and dots
    cleaned = "".join(c for c in input_str if c not in " \t\n\r-().")

    # 2. Convert Khmer digits (០-៩) to ASCII (0-9)
    khmer_zero = ord("០")
    converted = []
    for c in cleaned:
        if "០" <= c <= "៩":
            converted.append(str(ord(c) - khmer_zero))
        else:
            converted.append(c)
    cleaned = "".join(converted)

    # 3. Handle country code and trunk prefix
    if cleaned.startswith("+855"):
        national = cleaned[4:]
    elif cleaned.startswith("00855"):
        national = cleaned[5:]
    elif cleaned.startswith("855"):
        national = cleaned[3:]
    elif cleaned.startswith("0"):
        national = cleaned[1:]
    else:
        national = cleaned

    # Handle erroneous redundant zero after country code (e.g. +855012...)
    if national.startswith("0"):
        national = national[1:]

    # 4. Check for non-digit characters
    if not national.isdigit():
        return {
            "raw": input_str,
            "nsn": None,
            "e164": None,
            "domestic": None,
            "is_valid_syntax": False,
            "requires_otp_verification": True,
            "is_active_sim": False,
            "error": "Number contains non-digit characters after prefix extraction",
        }

    # 5. Length check: Cambodian National Significant Number (NSN) is 8 or 9 digits
    # (Domestic format with leading 0 is 9 or 10 digits)
    if len(national) not in (8, 9):
        return {
            "raw": input_str,
            "nsn": national,
            "e164": None,
            "domestic": None,
            "is_valid_syntax": False,
            "requires_otp_verification": True,
            "is_active_sim": False,
            "error": f"Invalid NSN length: {len(national)} digits (expected 8 or 9)",
        }

    return {
        "raw": input_str,
        "nsn": national,
        "e164": f"+855{national}",
        "domestic": f"0{national}",
        "is_valid_syntax": True,
        "requires_otp_verification": True,  # Liveness/ownership requires OTP
        "is_active_sim": False,             # Syntax check CANNOT prove SIM is active
        "error": None,
    }


# Separate pluggable carrier prefix lookup (TRC Baseline, verified October 2026)
TRC_MOBILE_OPERATOR_PREFIXES = {
    "Cellcard": ["11", "12", "14", "17", "61", "76", "77", "78", "85", "89", "92", "95", "99"],
    "Smart": ["10", "15", "16", "69", "70", "81", "86", "87", "93", "96", "98"],
    "Metfone": ["31", "60", "66", "67", "68", "71", "88", "90", "97"],
    "Seatel": ["18"],
}


def lookup_operator_baseline(nsn: str) -> Optional[str]:
    """Lookup carrier based on current TRC allocation data. Kept separate from normalization."""
    for op, prefixes in TRC_MOBILE_OPERATOR_PREFIXES.items():
        for p in prefixes:
            if nsn.startswith(p):
                return op
    return None


class TestCambodianPhoneNormalization(unittest.TestCase):
    def test_standard_8_digit_nsn(self):
        """Standard mobile number with 8-digit NSN (9 digits domestic)."""
        res = normalize_cambodian_phone("012 345 678")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "12345678")
        self.assertEqual(res["e164"], "+85512345678")
        self.assertEqual(res["domestic"], "012345678")
        # Ensure active SIM is not asserted
        self.assertFalse(res["is_active_sim"])
        self.assertTrue(res["requires_otp_verification"])

    def test_extended_9_digit_nsn(self):
        """Extended mobile number with 9-digit NSN (10 digits domestic, e.g. 096)."""
        res = normalize_cambodian_phone("096 123 4567")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "961234567")
        self.assertEqual(res["e164"], "+855961234567")
        self.assertEqual(res["domestic"], "0961234567")

    def test_international_prefix_variations(self):
        """Handles +855, 00855, and 855 seamlessly."""
        cases = [
            ("+85512345678", "12345678"),
            ("0085512345678", "12345678"),
            ("85512345678", "12345678"),
            ("+855 (0) 12 345 678", "12345678"),
            ("+855012345678", "12345678"),  # Erroneous leading zero after +855
        ]
        for raw, expected_nsn in cases:
            with self.subTest(raw=raw):
                res = normalize_cambodian_phone(raw)
                self.assertTrue(res["is_valid_syntax"])
                self.assertEqual(res["nsn"], expected_nsn)
                self.assertEqual(res["e164"], f"+855{expected_nsn}")

    def test_khmer_numerals_converted(self):
        """Normalizes Khmer digits (០-៩) to standard ASCII digits."""
        res = normalize_cambodian_phone("០១២ ៣៤៥ ៦៧៨")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "12345678")
        self.assertEqual(res["e164"], "+85512345678")
        self.assertEqual(res["domestic"], "012345678")

    def test_invalid_lengths_rejected(self):
        """Rejects numbers that are too short (e.g. 7 digits) or too long (10+ digits NSN)."""
        short_num = "012 345"       # NSN = 5 digits
        long_num = "012 345 678 901" # NSN = 11 digits

        res_short = normalize_cambodian_phone(short_num)
        self.assertFalse(res_short["is_valid_syntax"])
        self.assertIn("Invalid NSN length", res_short["error"])

        res_long = normalize_cambodian_phone(long_num)
        self.assertFalse(res_long["is_valid_syntax"])
        self.assertIn("Invalid NSN length", res_long["error"])

    def test_normalization_decoupled_from_prefix_data(self):
        """
        Normalization produces valid E.164 and domestic formats purely based on
        ITU-T E.164 length rules, without failing on unlisted/future carrier prefixes.
        """
        # Assume a hypothetical future prefix '045' with 8 digits NSN
        hypothetical = "045 123 456"
        res = normalize_cambodian_phone(hypothetical)
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "45123456")
        self.assertEqual(res["e164"], "+85545123456")

        # Carrier lookup is a separate concern
        self.assertIsNone(lookup_operator_baseline(res["nsn"]))

    def test_trc_operator_lookup_baseline(self):
        """Operator lookup correctly maps known TRC prefixes (as of October 2026)."""
        self.assertEqual(lookup_operator_baseline("12345678"), "Cellcard")
        self.assertEqual(lookup_operator_baseline("961234567"), "Smart")
        self.assertEqual(lookup_operator_baseline("881234567"), "Metfone")
        self.assertEqual(lookup_operator_baseline("181234567"), "Seatel")

    def test_never_claims_active_status(self):
        """Syntax validation explicitly flags that OTP verification is required."""
        res = normalize_cambodian_phone("012 345 678")
        self.assertFalse(res["is_active_sim"])
        self.assertTrue(res["requires_otp_verification"])


if __name__ == "__main__":
    unittest.main()
