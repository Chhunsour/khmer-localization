"""
test_khmer_utils_extended.py - Unit Tests for Extended Localization Utilities

Tests:
1. Fixed-line telephone normalization and emergency short codes.
2. Large number spellout (millions, hundred millions, billions).
3. Minor-unit integer financial calculation engine (zero floating-point drift).
4. Full EMVCo KHQR TLV parsing and semantic field extraction.
5. Pure-Python Chuon Nath Khmer alphabetical collation.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import (
    calculate_money_total,
    integer_to_khmer_words,
    khmer_sort_key,
    normalize_cambodian_phone,
    parse_khqr,
    parse_khmer_license_plate,
    sort_khmer_words,
    validate_cambodian_id,
)


class TestKhmerUtilsExtended(unittest.TestCase):
    def test_fixed_line_and_short_codes(self):
        """Test geographic landlines (Phnom Penh 023, Siem Reap 063) and emergency short codes."""
        # 1. Phnom Penh landline
        r_pp = normalize_cambodian_phone("023 210 022")
        self.assertTrue(r_pp["is_valid_syntax"])
        self.assertEqual(r_pp["normalized_e164"], "+85523210022")
        self.assertEqual(r_pp["normalized_domestic"], "023210022")
        self.assertEqual(r_pp["line_type"], "fixed_line")
        self.assertIn("Phnom Penh", r_pp["area_name"])

        # 2. Siem Reap landline
        r_sr = normalize_cambodian_phone("+855 63 963 888")
        self.assertTrue(r_sr["is_valid_syntax"])
        self.assertEqual(r_sr["line_type"], "fixed_line")
        self.assertIn("Siem Reap", r_sr["area_name"])

        # 3. Emergency Short Code (117)
        r_117 = normalize_cambodian_phone("117")
        self.assertTrue(r_117["is_valid_syntax"])
        self.assertEqual(r_117["line_type"], "short_code")
        self.assertEqual(r_117["length_category"], "short_code")
        self.assertFalse(r_117["requires_otp_verification"])

    def test_large_numbers_to_khmer_words(self):
        """Test spellout for large numbers up to billions without recursion depth or index errors."""
        # 1. 100 Million
        w_100m = integer_to_khmer_words(100_000_000)
        self.assertEqual(w_100m, "មួយរយលាន")

        # 2. 1 Billion (1,000 Million)
        w_1b = integer_to_khmer_words(1_000_000_000)
        self.assertEqual(w_1b, "មួយពាន់លាន")

        # 3. 2.5 Billion
        w_2_5b = integer_to_khmer_words(2_500_000_000)
        self.assertEqual(w_2_5b, "ពីរពាន់ប្រាំរយលាន")

        # 4. Negative large number
        w_neg = integer_to_khmer_words(-5_000_000)
        self.assertEqual(w_neg, "ដកប្រាំលាន")

    def test_minor_unit_financial_precision(self):
        """Test financial arithmetic avoids IEEE 754 floating point imprecision."""
        # Cart with items: 3 * $0.10 + 2 * $0.20 = $0.70 (standard float drift test)
        items = [
            {"price": 0.10, "quantity": 3},
            {"price": 0.20, "quantity": 2},
        ]
        res_usd = calculate_money_total(items, currency="USD", tax_rate_percent=10.0)
        self.assertEqual(res_usd["subtotal"], 0.70)
        self.assertEqual(res_usd["subtotal_minor"], 70)
        self.assertEqual(res_usd["tax"], 0.07)
        self.assertEqual(res_usd["total"], 0.77)
        self.assertEqual(res_usd["total_formatted"], "$0.77")

        # KHR whole riel calculation
        khr_items = [
            {"price": 12500, "quantity": 2}, # 25,000
            {"price": 7500, "quantity": 1},  # 7,500
        ]
        res_khr = calculate_money_total(khr_items, currency="KHR", tax_rate_percent=10.0)
        self.assertEqual(res_khr["subtotal"], 32500)
        self.assertEqual(res_khr["tax"], 3250)
        self.assertEqual(res_khr["total"], 35750)
        self.assertEqual(res_khr["total_formatted"], "35,750៛")

    def test_khqr_full_parsing(self):
        """Test full TLV parsing of a real Bakong KHQR string."""
        sample_khqr = "00020101021129220010sokha@devb5204541153031165405250005802KH5912AngkorCoffee6010Phnom Penh6304"
        from scripts.khmer_utils import calculate_khqr_crc16
        crc = calculate_khqr_crc16(sample_khqr)
        full_khqr = f"{sample_khqr}{crc}"

        parsed = parse_khqr(full_khqr)
        self.assertTrue(parsed["is_valid_format"])
        self.assertTrue(parsed["is_valid_crc"])
        self.assertEqual(parsed["currency_name"], "KHR")
        self.assertEqual(parsed["currency_code"], "116")
        self.assertEqual(parsed["amount"], 25000.0)
        self.assertEqual(parsed["merchant_name"], "AngkorCoffee")
        self.assertEqual(parsed["merchant_city"], "Phnom Penh")
        self.assertEqual(parsed["country_code"], "KH")
        self.assertEqual(parsed["bakong_account_id"], "sokha@devb")

    def test_pure_python_khmer_collation(self):
        """Test Chuon Nath dictionary order sorting in pure Python standard library."""
        # Unsorted list of Khmer consonants and words
        # Chuon Nath order: ក (Ka), ខ (Kha), គ (Ko), ឃ (Kho), ង (Ngo), ច (Ca), ..., អ (Qa)
        words = ["ង៉ុក", "កម្ពុជា", "ខេត្ត", "គណនី", "ចាកចេញ"]
        # Expected: កម្ពុជា (Ka), ខេត្ត (Kha), គណនី (Ko), ង៉ុក (Ngo), ចាកចេញ (Ca)
        sorted_res = sort_khmer_words(words)
        self.assertEqual(sorted_res[0], "កម្ពុជា")
        self.assertEqual(sorted_res[1], "ខេត្ត")
        self.assertEqual(sorted_res[2], "គណនី")
        self.assertEqual(sorted_res[3], "ង៉ុក")
        self.assertEqual(sorted_res[4], "ចាកចេញ")

    def test_cambodian_national_id_validation(self):
        """Test Cambodian National ID card normalization (9-digit legacy & 10-digit smart ID)."""
        # 1. 9-digit legacy ID
        id9 = validate_cambodian_id("012345678")
        self.assertTrue(id9["is_valid"])
        self.assertEqual(id9["id_type"], "legacy_id")
        self.assertEqual(id9["province_code"], "01")
        self.assertEqual(id9["normalized"], "012345678")
        self.assertEqual(id9["khmer_digits"], "០១២៣៤៥៦៧៨")

        # 2. 10-digit smart biometric ID
        id10 = validate_cambodian_id("1201234567")
        self.assertTrue(id10["is_valid"])
        self.assertEqual(id10["id_type"], "smart_id")
        self.assertEqual(id10["province_code"], "12")
        self.assertEqual(id10["normalized"], "1201234567")

        # 3. Khmer numerals with dashes and spaces
        id_km = validate_cambodian_id("១២-០១២៣-៤៥៦៧")
        self.assertTrue(id_km["is_valid"])
        self.assertEqual(id_km["normalized"], "1201234567")
        self.assertEqual(id_km["id_type"], "smart_id")

        # 4. Invalid length
        id_inv_len = validate_cambodian_id("12345")
        self.assertFalse(id_inv_len["is_valid"])
        self.assertIn("Invalid ID length", id_inv_len["error"])

        # 5. Non-numeric
        id_alpha = validate_cambodian_id("120123456A")
        self.assertFalse(id_alpha["is_valid"])
        self.assertIn("non-numeric", id_alpha["error"])

    def test_cambodian_license_plate_parsing(self):
        """Test parsing of Cambodian civilian, motorcycle, and state license plates."""
        # 1. Civilian automobile
        p1 = parse_khmer_license_plate("ភ្នំពេញ 2BC-1234")
        self.assertTrue(p1["is_valid_format"])
        self.assertEqual(p1["plate_type"], "civilian_car")
        self.assertEqual(p1["province"], "ភ្នំពេញ")
        self.assertEqual(p1["series"], "2BC")
        self.assertEqual(p1["number"], "1234")

        # 2. Motorcycle with Khmer numbers
        p2 = parse_khmer_license_plate("1FD-៥៦៧៨")
        self.assertTrue(p2["is_valid_format"])
        self.assertEqual(p2["plate_type"], "motorcycle")
        self.assertEqual(p2["series"], "1FD")
        self.assertEqual(p2["number"], "5678")

        # 3. Commercial truck
        p3 = parse_khmer_license_plate("3A-9999")
        self.assertTrue(p3["is_valid_format"])
        self.assertEqual(p3["plate_type"], "commercial")

        # 4. State / Police / Military
        p_state = parse_khmer_license_plate("រដ្ឋ 01 2-1234")
        self.assertTrue(p_state["is_valid_format"])
        self.assertEqual(p_state["plate_type"], "state")

        p_police = parse_khmer_license_plate("ន.ប 1-2345")
        self.assertTrue(p_police["is_valid_format"])
        self.assertEqual(p_police["plate_type"], "police")

        p_mil = parse_khmer_license_plate("ខ.ម 02 1-2345")
        self.assertTrue(p_mil["is_valid_format"])
        self.assertEqual(p_mil["plate_type"], "military")

        # 5. Invalid
        p_inv = parse_khmer_license_plate("XYZ-ABC")
        self.assertFalse(p_inv["is_valid_format"])
        self.assertIsNotNone(p_inv["error"])


if __name__ == "__main__":
    unittest.main()
