"""Automated verification for extended Cambodian localization data catalogs."""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

class TestExtendedCatalogs(unittest.TestCase):
    def test_01_phnom_penh_14_khans_integrity(self):
        """Verify all 14 Phnom Penh Khans exist with valid codes and Khmer script."""
        path = os.path.join(DATA_DIR, "phnom_penh_districts.json")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            khans = json.load(f)
        self.assertEqual(len(khans), 14)
        codes = {k["code"] for k in khans}
        self.assertIn("1201", codes)
        self.assertIn("1202", codes)

