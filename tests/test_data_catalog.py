"""Unit tests for offline Cambodian localization data catalogs."""
import os
import json
import unittest

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

class TestDataCatalogIntegrity(unittest.TestCase):
    def test_01_provinces_count_and_iso_codes(self):
        """Verify all 25 Cambodian provinces/capitals are defined with valid ISO 3166-2:KH codes."""
        path = os.path.join(DATA_DIR, "provinces.json")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            provinces = json.load(f)
        self.assertEqual(len(provinces), 25)
        codes = {p["code"] for p in provinces}
        self.assertIn("KH-12", codes)
        self.assertIn("KH-17", codes)

    def test_02_provinces_khmer_script_presence(self):
        """Ensure all administrative divisions include valid native Khmer script names."""
        path = os.path.join(DATA_DIR, "provinces.json")
        with open(path, "r", encoding="utf-8") as f:
            provinces = json.load(f)
        for p in provinces:
            self.assertTrue(p["name_km"].startswith("ខេត្ត") or p["name_km"].startswith("រាជធានី"))

    def test_03_banknote_denominations_validity(self):
        """Verify all 11 active Cambodian Riel (KHR) banknote denominations are registered."""
        path = os.path.join(DATA_DIR, "banknotes.json")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            notes = json.load(f)
        self.assertEqual(len(notes), 11)
        denominations = [n["denomination"] for n in notes]
        self.assertIn(100, denominations)
        self.assertIn(100000, denominations)

    def test_04_telecom_operators_and_prefixes(self):
        """Verify major Cambodian telecommunication and internet service providers."""
        path = os.path.join(DATA_DIR, "telecom_operators.json")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            operators = json.load(f)
        self.assertEqual(len(operators), 10)
        smart = next(o for o in operators if o["brand"] == "Smart")
        self.assertIn("010", smart["prefixes"])

