"""
test_khmer_utils.py - Comprehensive Unit Tests for scripts/khmer_utils.py

Tests:
1. Phone normalization (8 vs 9 digits, Khmer digits, domestic vs international).
2. Currency formatting (KHR whole-riel vs ISO decimals, USD).
3. Calendar, date formatting, and Buddhist Era (BE).
4. Safe text truncation preserving Khmer syllables.
5. Number-to-words conversion in Khmer (GDT tax invoice compliance).
6. Bakong KHQR EMVCo CRC16 calculation and verification.
"""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.khmer_utils import (
    calculate_khqr_crc16,
    format_currency_khmer_words,
    format_khr,
    format_khmer_date,
    format_khmer_relative_time,
    format_usd,
    integer_to_khmer_words,
    normalize_cambodian_phone,
    safe_truncate_khmer,
    to_buddhist_era,
    verify_khqr,
)


class TestPhoneNormalization(unittest.TestCase):
    def test_standard_8_digit_nsn(self):
        res = normalize_cambodian_phone("012 345 678")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "12345678")
        self.assertEqual(res["normalized_e164"], "+85512345678")
        self.assertEqual(res["normalized_domestic"], "012345678")
        self.assertEqual(res["length_category"], "8_digits")
        self.assertTrue(res["requires_otp_verification"])
        self.assertFalse(res["is_active_sim"])

    def test_extended_9_digit_nsn(self):
        res = normalize_cambodian_phone("+855 96 123 4567")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "961234567")
        self.assertEqual(res["normalized_e164"], "+855961234567")
        self.assertEqual(res["length_category"], "9_digits")

    def test_khmer_numerals_conversion(self):
        res = normalize_cambodian_phone("០១២ ៣៤៥ ៦៧៨")
        self.assertTrue(res["is_valid_syntax"])
        self.assertEqual(res["nsn"], "12345678")
        self.assertEqual(res["normalized_e164"], "+85512345678")

    def test_invalid_lengths(self):
        too_short = normalize_cambodian_phone("012 345")
        self.assertFalse(too_short["is_valid_syntax"])
        self.assertEqual(too_short["length_category"], "invalid")

        too_long = normalize_cambodian_phone("012 3456 78901")
        self.assertFalse(too_long["is_valid_syntax"])


class TestCurrencyFormatting(unittest.TestCase):
    def test_khr_whole_riel_default(self):
        self.assertEqual(format_khr(25000), "25,000៛")
        self.assertEqual(format_khr(0), "0៛")
        self.assertEqual(format_khr(-5000), "-5,000៛")

    def test_khr_rounding(self):
        self.assertEqual(format_khr(25000.75), "25,001៛")

    def test_khr_fractional(self):
        self.assertEqual(format_khr(25000.5, whole_riel=False), "25,000.50៛")

    def test_khr_khmer_numerals(self):
        self.assertEqual(format_khr(25000, use_khmer_digits=True), "២៥.០០០៛")

    def test_usd_formatting(self):
        self.assertEqual(format_usd(12.5), "$12.50")
        self.assertEqual(format_usd(1000), "$1,000.00")
        self.assertEqual(format_usd(0), "$0.00")


class TestCalendarAndDates(unittest.TestCase):
    def test_buddhist_era(self):
        self.assertEqual(to_buddhist_era(2026), 2569)
        self.assertEqual(to_buddhist_era(2024), 2567)

    def test_format_khmer_date(self):
        d = datetime.date(2026, 10, 20)
        self.assertEqual(format_khmer_date(d), "ថ្ងៃទី 20 ខែតុលា ឆ្នាំ 2026")
        self.assertEqual(
            format_khmer_date(d, include_be=True),
            "ថ្ងៃទី 20 ខែតុលា ឆ្នាំ 2026 (ព.ស. 2569)",
        )

    def test_relative_time(self):
        self.assertEqual(format_khmer_relative_time(20), "មុននេះបន្តិច")
        self.assertEqual(format_khmer_relative_time(180), "3 នាទីមុន")
        self.assertEqual(format_khmer_relative_time(7200), "2 ម៉ោងមុន")
        self.assertEqual(format_khmer_relative_time(86400), "ម្សិលមិញ")


class TestSafeTextTruncation(unittest.TestCase):
    def test_preserves_coeng_subscript(self):
        text = "កម្ពុជា"
        truncated = safe_truncate_khmer(text, 3)
        self.assertNotIn("\u17D2…", truncated)
        self.assertTrue(truncated.endswith("…"))


class TestNumberToWords(unittest.TestCase):
    def test_zero_and_single_digits(self):
        self.assertEqual(integer_to_khmer_words(0), "សូន្យ")
        self.assertEqual(integer_to_khmer_words(5), "ប្រាំ")
        self.assertEqual(integer_to_khmer_words(9), "ប្រាំបួន")

    def test_tens(self):
        self.assertEqual(integer_to_khmer_words(10), "ដប់")
        self.assertEqual(integer_to_khmer_words(20), "ម្ភៃ")
        self.assertEqual(integer_to_khmer_words(25), "ម្ភៃប្រាំ")
        self.assertEqual(integer_to_khmer_words(99), "កៅសិបប្រាំបួន")

    def test_hundreds_and_thousands(self):
        self.assertEqual(integer_to_khmer_words(100), "មួយរយ")
        self.assertEqual(integer_to_khmer_words(500), "ប្រាំរយ")
        self.assertEqual(integer_to_khmer_words(1000), "មួយពាន់")
        self.assertEqual(integer_to_khmer_words(5500), "ប្រាំពាន់ប្រាំរយ")

    def test_ten_thousands_and_hundred_thousands(self):
        # 25,000 = 2 ten-thousands (ពីរម៉ឺន) + 5 thousands (ប្រាំពាន់)
        self.assertEqual(integer_to_khmer_words(25000), "ពីរម៉ឺនប្រាំពាន់")
        # 150,000 = 1 hundred-thousand (មួយសែន) + 5 ten-thousands (ប្រាំម៉ឺន)
        self.assertEqual(integer_to_khmer_words(150000), "មួយសែនប្រាំម៉ឺន")

    def test_millions(self):
        self.assertEqual(integer_to_khmer_words(1000000), "មួយលាន")
        self.assertEqual(integer_to_khmer_words(2500000), "ពីរលានប្រាំសែន")

    def test_currency_words_khr(self):
        self.assertEqual(format_currency_khmer_words(25000, "KHR"), "ពីរម៉ឺនប្រាំពាន់រៀលគត់")
        self.assertEqual(format_currency_khmer_words(150000, "KHR"), "មួយសែនប្រាំម៉ឺនរៀលគត់")

    def test_currency_words_usd(self):
        self.assertEqual(format_currency_khmer_words(100, "USD"), "មួយរយដុល្លារអាមេរិកគត់")
        self.assertEqual(
            format_currency_khmer_words(12.50, "USD"),
            "ដប់ពីរដុល្លារអាមេរិក និងហាសិបសេន",
        )


class TestBakongKhqrCrc16(unittest.TestCase):
    def test_crc16_calculation(self):
        # Sample payload up to Tag 6304
        payload = "00020101021129330017sokha_chhorn@devb5204541153031165405250005802KH5912AngkorCoffee6010Phnom Penh6304"
        crc = calculate_khqr_crc16(payload)
        self.assertEqual(len(crc), 4)
        self.assertTrue(all(c in "0123456789ABCDEF" for c in crc))

        # Test verification of valid QR string
        full_khqr = payload + crc
        is_valid, err = verify_khqr(full_khqr)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_crc16_tampered_payload_rejected(self):
        payload = "00020101021129330017sokha_chhorn@devb5204541153031165405250005802KH5912AngkorCoffee6010Phnom Penh6304"
        crc = calculate_khqr_crc16(payload)
        # Tamper with amount: change 25000 to 50000
        tampered = payload.replace("25000", "50000") + crc
        is_valid, err = verify_khqr(tampered)
        self.assertFalse(is_valid)
        self.assertIn("CRC mismatch", err)


if __name__ == "__main__":
    unittest.main()
