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

    def test_02_kampot_and_sihanoukville_districts(self):
        """Verify Kampot (9) and Preah Sihanouk (5) coastal districts."""
        kp_path = os.path.join(DATA_DIR, "kampot_districts.json")
        sh_path = os.path.join(DATA_DIR, "preah_sihanouk_districts.json")
        with open(kp_path, "r", encoding="utf-8") as f:
            kp = json.load(f)
        with open(sh_path, "r", encoding="utf-8") as f:
            sh = json.load(f)
        self.assertEqual(len(kp), 9)
        self.assertEqual(len(sh), 5)
        self.assertIn("0708", {d["code"] for d in kp})
        self.assertIn("1801", {d["code"] for d in sh})

    def test_03_khmer_33_consonants_phonetics(self):
        """Verify full set of 33 standard Khmer consonants and series classification."""
        cs_path = os.path.join(DATA_DIR, "khmer_consonants.json")
        self.assertTrue(os.path.exists(cs_path))
        with open(cs_path, "r", encoding="utf-8") as f:
            cs = json.load(f)
        self.assertEqual(len(cs), 33)
        series1 = [c for c in cs if c["series"] == 1]
        series2 = [c for c in cs if c["series"] == 2]
        self.assertEqual(len(series1), 15)
        self.assertEqual(len(series2), 18)
        self.assertEqual(cs[0]["char"], "ក")
        self.assertEqual(cs[-1]["char"], "អ")

