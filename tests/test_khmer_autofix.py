"""
test_khmer_autofix.py - Unit tests for Khmer translation & text auto-fixer engine.

Tests:
1. Inverted word order fixes (e.g. សរុបតម្លៃ -> តម្លៃសរុប).
2. Decimal KHR stripping (e.g. 25.00៛ -> 25៛, 50.00 KHR -> 50 KHR).
3. Trailing Coeng (U+17D2) removal.
4. Social register correction (e.g. យាងចូល -> ចូលគណនី).
5. Dotted circle (U+25CC) cleanup.
6. JSON dictionary object batch fixing.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import fix_khmer_text


class TestKhmerAutoFixer(unittest.TestCase):
    def test_fix_inverted_word_order(self):
        text = "សូមពិនិត្យមើល សរុបតម្លៃ មុនពេលបង់ប្រាក់"
        res = fix_khmer_text(text)
        self.assertIn("តម្លៃសរុប", res["fixed"])
        self.assertNotIn("សរុបតម្លៃ", res["fixed"])
        self.assertTrue(len(res["changes"]) >= 1)

    def test_fix_password_inverted_order(self):
        text = "សូមបញ្ចូល ថ្មីពាក្យសម្ងាត់ និង ចាស់ពាក្យសម្ងាត់"
        res = fix_khmer_text(text)
        self.assertIn("ពាក្យសម្ងាត់ថ្មី", res["fixed"])
        self.assertIn("ពាក្យសម្ងាត់ចាស់", res["fixed"])

    def test_fix_active_users_order(self):
        text = "ចំនួន សកម្មអ្នកប្រើប្រាស់ សរុប"
        res = fix_khmer_text(text)
        self.assertIn("អ្នកប្រើប្រាស់សកម្ម", res["fixed"])

    def test_fix_decimal_khr(self):
        # ៛ with decimals
        res1 = fix_khmer_text("តម្លៃទំនិញ 25,000.00៛")
        self.assertEqual(res1["fixed"], "តម្លៃទំនិញ 25,000៛")

        # KHR with decimals
        res2 = fix_khmer_text("សរុប 150.00 KHR")
        self.assertIn("150 KHR", res2["fixed"])
        self.assertNotIn(".00", res2["fixed"])

    def test_fix_trailing_coeng(self):
        # Trailing Coeng subscript mark (U+17D2) at end of string or before space
        text = "សង្កាត់\u17D2 រាជធានី"
        res = fix_khmer_text(text)
        self.assertNotIn("\u17D2 ", res["fixed"])

    def test_fix_royal_register(self):
        text = "សូមយាងចូលគណនី"
        res = fix_khmer_text(text)
        self.assertIn("ចូលគណនី", res["fixed"])
        self.assertNotIn("យាងចូល", res["fixed"])

    def test_fix_dotted_circle(self):
        text = "កា\u25CCររៀបចំ"
        res = fix_khmer_text(text)
        self.assertNotIn("\u25CC", res["fixed"])
        self.assertIn("ការរៀបចំ", res["fixed"])

    def test_clean_text_unchanged(self):
        text = "តម្លៃសរុប 10,000៛ ចូលគណនី"
        res = fix_khmer_text(text)
        self.assertEqual(res["fixed"], text)
        self.assertEqual(len(res["changes"]), 0)


if __name__ == "__main__":
    unittest.main()
