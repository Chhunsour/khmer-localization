"""
test_khmer_classifiers.py - Unit tests for Khmer noun classifiers and counting syntax.

Validates:
1. data/khmer_classifiers.json existence and schema.
2. format_khmer_count() with classifiers ("អ្នកប្រើប្រាស់ 3 នាក់").
3. format_khmer_count() with Khmer numerals ("អ្នកប្រើប្រាស់ ៣ នាក់").
4. Classifier catalog coverage (16 items).
"""

import json
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import format_khmer_count


class TestKhmerClassifiers(unittest.TestCase):
    def test_catalog_file_and_schema(self):
        cat_path = os.path.join(REPO_ROOT, "data", "khmer_classifiers.json")
        self.assertTrue(os.path.exists(cat_path))
        with open(cat_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 16)
        for item in data:
            self.assertIn("classifier_km", item)
            self.assertIn("classifier_en", item)
            self.assertIn("category", item)
            self.assertIn("example_km", item)

    def test_format_khmer_count_with_classifier(self):
        # People
        res = format_khmer_count("អ្នកប្រើប្រាស់", 3, "នាក់")
        self.assertEqual(res, "អ្នកប្រើប្រាស់ 3 នាក់")

        # Phones
        res_phone = format_khmer_count("ទូរស័ព្ទ", 2, "គ្រឿង")
        self.assertEqual(res_phone, "ទូរស័ព្ទ 2 គ្រឿង")

    def test_format_khmer_count_khmer_digits(self):
        res = format_khmer_count("អ្នកប្រើប្រាស់", 3, "នាក់", use_khmer_digits=True)
        self.assertEqual(res, "អ្នកប្រើប្រាស់ ៣ នាក់")

    def test_format_khmer_count_without_classifier(self):
        res = format_khmer_count("សារ", 5)
        self.assertEqual(res, "សារ 5")


if __name__ == "__main__":
    unittest.main()
