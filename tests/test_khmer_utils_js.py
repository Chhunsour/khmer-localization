"""
test_khmer_utils_js.py - Automated Unit Tests for Isomorphic JavaScript/TypeScript Utilities

Runs Node.js subprocess calls to assert parity between Python and JavaScript
implementations of khmer_utils.
"""

import json
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

JS_UTILS_PATH = os.path.join(REPO_ROOT, "scripts", "khmer_utils.js")


def run_node_eval(js_code: str) -> str:
    """Execute a Node.js snippet that requires khmer_utils.js and returns stdout."""
    script = f"""
    const u = require({json.dumps(JS_UTILS_PATH)});
    {js_code}
    """
    proc = subprocess.run(
        ["node", "-e", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


class TestKhmerUtilsJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify node is available
        try:
            res = subprocess.run(["node", "-v"], capture_output=True, text=True, check=True)
            cls.node_version = res.stdout.strip()
        except Exception as e:
            raise unittest.SkipTest(f"Node.js is not available in environment: {e}")

    def test_phone_normalization(self):
        """Test Cambodian phone number normalization across standard & international formats."""
        code = """
        const r1 = u.normalizeCambodianPhone("012 345 678");
        const r2 = u.normalizeCambodianPhone("+855 97 123 4567");
        const r3 = u.normalizeCambodianPhone("0971234567");
        const r4 = u.normalizeCambodianPhone("12345");
        console.log(JSON.stringify({ r1, r2, r3, r4 }));
        """
        out = json.loads(run_node_eval(code))
        # r1: 8 digits
        self.assertTrue(out["r1"]["is_valid_syntax"])
        self.assertEqual(out["r1"]["normalized_e164"], "+85512345678")
        self.assertEqual(out["r1"]["normalized_domestic"], "012345678")
        self.assertEqual(out["r1"]["length_category"], "8_digits")

        # r2: 9 digits
        self.assertTrue(out["r2"]["is_valid_syntax"])
        self.assertEqual(out["r2"]["normalized_e164"], "+855971234567")
        self.assertEqual(out["r2"]["normalized_domestic"], "0971234567")
        self.assertEqual(out["r2"]["length_category"], "9_digits")

        # r3: 9 digits domestic
        self.assertTrue(out["r3"]["is_valid_syntax"])
        self.assertEqual(out["r3"]["normalized_e164"], "+855971234567")

        # r4: invalid length
        self.assertFalse(out["r4"]["is_valid_syntax"])
        self.assertIsNotNone(out["r4"]["error"])

    def test_currency_formatting(self):
        """Test KHR whole-riel and USD 2-decimal formatting."""
        code = """
        const khr1 = u.formatKHR(15000);
        const khr2 = u.formatKHR(15000.75, false);
        const usd = u.formatUSD(25.5);
        console.log(JSON.stringify({ khr1, khr2, usd }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["khr1"], "15,000៛")
        self.assertEqual(out["khr2"], "15,000.75៛")
        self.assertEqual(out["usd"], "$25.50")

    def test_date_and_buddhist_era(self):
        """Test Buddhist Era calculation and Khmer date string generation."""
        code = """
        const be = u.toBuddhistEra(2026);
        const d = new Date(2026, 9, 26); // Oct 26, 2026
        const dateStr = u.formatKhmerDate(d, { includeBE: true });
        console.log(JSON.stringify({ be, dateStr }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["be"], 2569)
        self.assertIn("តុលា", out["dateStr"])
        self.assertIn("ព.ស. 2569", out["dateStr"])

    def test_safe_truncate(self):
        """Test grapheme truncation does not corrupt Coeng clusters."""
        code = """
        const text = "សួស្តីកម្ពុជា";
        const truncated = u.safeTruncateKhmer(text, 3);
        console.log(JSON.stringify({ truncated }));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["truncated"].endswith("…"))
        # Must not end with broken Coeng (U+17D2) before ellipsis
        prefix = out["truncated"][:-1]
        self.assertFalse(prefix.endswith("\u17d2"))

    def test_number_to_khmer_words(self):
        """Test spelled-out Khmer numbers and currency words."""
        code = """
        const zero = u.integerToKhmerWords(0);
        const w1 = u.integerToKhmerWords(25000);
        const w2 = u.formatCurrencyKhmerWords(25000, "KHR");
        const w3 = u.formatCurrencyKhmerWords(10.5, "USD");
        console.log(JSON.stringify({ zero, w1, w2, w3 }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["zero"], "សូន្យ")
        self.assertEqual(out["w1"], "ពីរម៉ឺនប្រាំពាន់")
        self.assertEqual(out["w2"], "ពីរម៉ឺនប្រាំពាន់រៀលគត់")
        self.assertEqual(out["w3"], "ដប់ដុល្លារអាមេរិក និងហាសិបសេន")

    def test_khqr_crc16(self):
        """Test KHQR CRC16 calculation and verification."""
        code = """
        // Standard EMVCo test vector
        const payload = "00020101021138580010A000000727012600120102030405060708091011125204581253031165405100005802KH5911TEST VENDOR6010PHNOM PENH6304";
        const crc = u.calculateKhqrCrc16(payload);
        const fullKhqr = payload + crc;
        const verifyRes = u.verifyKhqr(fullKhqr);
        console.log(JSON.stringify({ crc, verifyRes }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(len(out["crc"]), 4)
        self.assertTrue(out["verifyRes"]["isValid"])
        self.assertIsNone(out["verifyRes"]["error"])

    def test_character_stats(self):
        """Test Khmer character detection and composition statistics."""
        code = """
        const isKm = u.isKhmerText("សួស្តី Cambodia");
        const stats = u.getKhmerCharacterStats("សួស្តី");
        console.log(JSON.stringify({ isKm, stats }));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["isKm"])
        self.assertGreater(out["stats"]["totalKhmer"], 0)
        self.assertGreater(out["stats"]["consonants"], 0)
        self.assertGreater(out["stats"]["coengSubscripts"], 0)


if __name__ == "__main__":
    unittest.main()
