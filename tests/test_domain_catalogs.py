"""Automated unit verification for domain catalogs: districts, consonants, logistics, ministries."""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

class TestDomainCatalogs(unittest.TestCase):
    def test_01_kandal_and_kampong_cham_districts(self):
        """Verify Kandal (11) and Kampong Cham (10) districts catalog."""
        kd_path = os.path.join(DATA_DIR, "kandal_districts.json")
        kc_path = os.path.join(DATA_DIR, "kampong_cham_districts.json")
        with open(kd_path, "r", encoding="utf-8") as f:
            kd = json.load(f)
        with open(kc_path, "r", encoding="utf-8") as f:
            kc = json.load(f)
        self.assertEqual(len(kd), 11)
        self.assertEqual(len(kc), 10)
        self.assertIn("0811", {d["code"] for d in kd})
        self.assertIn("0305", {d["code"] for d in kc})

