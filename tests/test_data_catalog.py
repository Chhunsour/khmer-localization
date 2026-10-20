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

