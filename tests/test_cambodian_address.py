"""
test_cambodian_address.py - Unit tests for 4-tier Cambodian address formatting and parsing.

Validates:
1. format_cambodian_address() in Khmer and English.
2. Handling partial address components without None or undefined.
3. parse_cambodian_address() extracting street, sangkat, khan, province, postal code.
4. Postal code extraction (5-6 digits).
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import format_cambodian_address, parse_cambodian_address


class TestCambodianAddress(unittest.TestCase):
    def test_format_khmer_address(self):
        components = {
            "street": "ផ្ទះលេខ 42, ផ្លូវ 310",
            "sangkat": "សង្កាត់បឹងកេងកងទី១",
            "khan": "ខណ្ឌបឹងកេងកង",
            "province": "រាជធានីភ្នំពេញ",
            "postal_code": "120102",
        }
        formatted = format_cambodian_address(components, lang="km")
        expected = "ផ្ទះលេខ 42, ផ្លូវ 310, សង្កាត់បឹងកេងកងទី១, ខណ្ឌបឹងកេងកង, រាជធានីភ្នំពេញ, 120102"
        self.assertEqual(formatted, expected)

    def test_format_partial_address(self):
        # Missing postal code and village
        components = {
            "street": "ផ្លូវ ២០០៤",
            "khan": "ខណ្ឌសែនសុខ",
            "province": "រាជធានីភ្នំពេញ",
        }
        formatted = format_cambodian_address(components, lang="km")
        self.assertEqual(formatted, "ផ្លូវ ២០០៤, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")
        self.assertNotIn("None", formatted)

    def test_format_english_address(self):
        components = {
            "street": "#42, St. 310",
            "sangkat": "Sangkat Boeung Keng Kang 1",
            "khan": "Khan Boeung Keng Kang",
            "province": "Phnom Penh",
            "postal_code": "120102",
        }
        formatted = format_cambodian_address(components, lang="en")
        self.assertEqual(
            formatted,
            "#42, St. 310, Sangkat Boeung Keng Kang 1, Khan Boeung Keng Kang, Phnom Penh, 120102",
        )

    def test_parse_khmer_address(self):
        addr = "ផ្ទះលេខ 42, ផ្លូវ 310, សង្កាត់បឹងកេងកងទី១, ខណ្ឌបឹងកេងកង, រាជធានីភ្នំពេញ, 120102"
        parsed = parse_cambodian_address(addr)
        self.assertEqual(parsed["postal_code"], "120102")
        self.assertEqual(parsed["province"], "រាជធានីភ្នំពេញ")
        self.assertEqual(parsed["khan"], "ខណ្ឌបឹងកេងកង")
        self.assertEqual(parsed["sangkat"], "សង្កាត់បឹងកេងកងទី១")
        self.assertIn("ផ្ទះលេខ 42", parsed["street"])


if __name__ == "__main__":
    unittest.main()
