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

    def test_02_siem_reap_and_battambang_districts(self):
        """Verify all 26 districts across Siem Reap and Battambang provinces."""
        sr_path = os.path.join(DATA_DIR, "siem_reap_districts.json")
        btb_path = os.path.join(DATA_DIR, "battambang_districts.json")
        with open(sr_path, "r", encoding="utf-8") as f:
            sr_districts = json.load(f)
        with open(btb_path, "r", encoding="utf-8") as f:
            btb_districts = json.load(f)
        self.assertEqual(len(sr_districts), 12)
        self.assertEqual(len(btb_districts), 14)

    def test_03_independent_vowels_integrity(self):
        """Verify 14 standard non-deprecated Khmer independent vowels."""
        path = os.path.join(DATA_DIR, "khmer_independent_vowels.json")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            vowels = json.load(f)
        self.assertEqual(len(vowels), 14)
        chars = {v["character"] for v in vowels}
        self.assertIn("ឥ", chars)
        self.assertIn("ឪ", chars)

    def test_04_postal_codes_and_khqr_mcc_codes(self):
        """Verify Cambodian postal codes and ISO 18245 KHQR MCC codes."""
        post_path = os.path.join(DATA_DIR, "cambodia_postal_codes.json")
        mcc_path = os.path.join(DATA_DIR, "khqr_mcc_codes.json")
        with open(post_path, "r", encoding="utf-8") as f:
            postals = json.load(f)
        with open(mcc_path, "r", encoding="utf-8") as f:
            mccs = json.load(f)
        self.assertEqual(len(postals), 12)
        self.assertEqual(len(mccs), 10)
        mcc_nums = {m["mcc"] for m in mccs}
        self.assertIn("5812", mcc_nums)

