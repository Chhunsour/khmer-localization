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

    def test_05_koh_kong_and_pursat_districts(self):
        """Verify Koh Kong (7 districts) and Pursat (7 districts) catalogs."""
        kk_path = os.path.join(DATA_DIR, "koh_kong_districts.json")
        ps_path = os.path.join(DATA_DIR, "pursat_districts.json")
        with open(kk_path, "r", encoding="utf-8") as f:
            kk_districts = json.load(f)
        with open(ps_path, "r", encoding="utf-8") as f:
            ps_districts = json.load(f)

        self.assertEqual(len(kk_districts), 7)
        self.assertEqual(len(ps_districts), 7)

        # Check prefixes
        self.assertTrue(all(d["code"].startswith("09") for d in kk_districts))
        self.assertTrue(all(d["code"].startswith("15") for d in ps_districts))

        # Check municipality names
        kk_muni = next(d for d in kk_districts if d["type"] == "Municipality")
        self.assertEqual(kk_muni["name_km"], "ក្រុងខេមរភូមិន្ទ")

        ps_muni = next(d for d in ps_districts if d["type"] == "Municipality")
        self.assertEqual(ps_muni["name_km"], "ក្រុងពោធិ៍សាត់")

    def test_06_takeo_and_prey_veng_districts(self):
        """Verify Takeo (10 districts) and Prey Veng (13 districts) catalogs."""
        tk_path = os.path.join(DATA_DIR, "takeo_districts.json")
        pv_path = os.path.join(DATA_DIR, "prey_veng_districts.json")
        with open(tk_path, "r", encoding="utf-8") as f:
            tk_districts = json.load(f)
        with open(pv_path, "r", encoding="utf-8") as f:
            pv_districts = json.load(f)

        self.assertEqual(len(tk_districts), 10)
        self.assertEqual(len(pv_districts), 13)

        self.assertTrue(all(d["code"].startswith("21") for d in tk_districts))
        self.assertTrue(all(d["code"].startswith("14") for d in pv_districts))

        tk_muni = next(d for d in tk_districts if d["type"] == "Municipality")
        self.assertEqual(tk_muni["name_km"], "ក្រុងដូនកែវ")

        pv_muni = next(d for d in pv_districts if d["type"] == "Municipality")
        self.assertEqual(pv_muni["name_km"], "ក្រុងព្រៃវែង")

    def test_07_remaining_provincial_district_catalogs(self):
        """Verify district catalogs for Kampong Speu, Kampong Thom, Svay Rieng, Banteay Meanchey, etc."""
        provinces = [
            ("kampong_speu_districts.json", 9, "05"),
            ("kampong_thom_districts.json", 9, "06"),
            ("svay_rieng_districts.json", 8, "20"),
            ("banteay_meanchey_districts.json", 9, "01"),
            ("kratie_districts.json", 6, "10"),
            ("kampong_chhnang_districts.json", 8, "04"),
            ("tbong_khmum_districts.json", 7, "25"),
            ("preah_vihear_districts.json", 8, "13"),
            ("oddar_meanchey_districts.json", 5, "22"),
            ("kep_districts.json", 2, "23"),
            ("pailin_districts.json", 2, "24"),
            ("stung_treng_districts.json", 6, "19"),
            ("ratanakiri_districts.json", 9, "16"),
            ("mondulkiri_districts.json", 5, "11"),
        ]
        for filename, expected_count, prefix in provinces:
            path = os.path.join(DATA_DIR, filename)
            self.assertTrue(os.path.exists(path), f"{filename} should exist")
            with open(path, "r", encoding="utf-8") as f:
                districts = json.load(f)
            self.assertEqual(len(districts), expected_count, f"{filename} record count mismatch")
            self.assertTrue(all(d["code"].startswith(prefix) for d in districts))
            self.assertTrue(all("name_en" in d and "name_km" in d and "type" in d for d in districts))

