"""
Unit tests for data/ui_terms.json UI localization dictionary.
Validates structural schema, uniqueness of keys, presence of Khmer characters,
and strict absence of royal vocabulary in UI translations.
"""

import json
import os
import sys
import unittest

# Ensure repo root is in python path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class TestUiTermsJson(unittest.TestCase):
    def setUp(self):
        self.dict_path = os.path.join(REPO_ROOT, "data", "ui_terms.json")
        self.assertTrue(os.path.exists(self.dict_path), "data/ui_terms.json must exist")
        with open(self.dict_path, "r", encoding="utf-8") as f:
            self.terms = json.load(f)

    def test_term_count(self):
        """Must contain at least 250 high-frequency UI terms."""
        self.assertGreaterEqual(len(self.terms), 250, f"Expected >= 250 terms, got {len(self.terms)}")

    def test_schema_conformance(self):
        """Every entry must contain key, en, km, category, avoid."""
        expected_fields = {"key", "en", "km", "category", "avoid"}
        valid_categories = {
            "authentication",
            "navigation",
            "actions",
            "commerce_payments",
            "status_feedback",
            "forms_inputs",
            "privacy_terms",
        }

        seen_keys = set()
        for idx, item in enumerate(self.terms):
            self.assertIsInstance(item, dict, f"Item at index {idx} must be a dict")
            self.assertEqual(
                set(item.keys()),
                expected_fields,
                f"Item {item.get('key', idx)} has unexpected keys: {set(item.keys())}",
            )
            key = item["key"]
            self.assertNotIn(key, seen_keys, f"Duplicate key found: {key}")
            seen_keys.add(key)

            self.assertIn(
                item["category"],
                valid_categories,
                f"Invalid category '{item['category']}' for key '{key}'",
            )
            self.assertTrue(len(item["en"].strip()) > 0, f"Empty 'en' for key '{key}'")
            self.assertTrue(len(item["km"].strip()) > 0, f"Empty 'km' for key '{key}'")
            self.assertTrue(len(item["avoid"].strip()) > 0, f"Empty 'avoid' for key '{key}'")

    def test_khmer_characters_present(self):
        """All 'km' entries must contain valid Khmer Unicode characters (U+1780 to U+17FF)."""
        for item in self.terms:
            km_text = item["km"]
            has_khmer = any(0x1780 <= ord(c) <= 0x17FF for c in km_text)
            self.assertTrue(has_khmer, f"No Khmer characters found in km text for key '{item['key']}': {km_text}")

    def test_no_royal_register_hallucinations(self):
        """Digital UI strings must never use royal/monastic register."""
        forbidden_royal_terms = ["យាង", "សោយ", "ព្រះរាជ", "ទ្រង់"]
        for item in self.terms:
            km_text = item["km"]
            for forbidden in forbidden_royal_terms:
                self.assertNotIn(
                    forbidden,
                    km_text,
                    f"Forbidden royal term '{forbidden}' detected in key '{item['key']}': '{km_text}'",
                )


if __name__ == "__main__":
    unittest.main()
