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


import shutil

def get_js_runtime():
    for candidate in ["node", "bun", os.path.expanduser("~/.bun/bin/bun")]:
        path = shutil.which(candidate) if not os.path.isabs(candidate) else (candidate if os.path.exists(candidate) else None)
        if path:
            return path
    return None

JS_RUNTIME = get_js_runtime()


def run_node_eval(js_code: str) -> str:
    """Execute a JS snippet that requires khmer_utils.js and returns stdout."""
    script = f"""
    const u = require({json.dumps(JS_UTILS_PATH)});
    {js_code}
    """
    proc = subprocess.run(
        [JS_RUNTIME, "-e", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


class TestKhmerUtilsJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not JS_RUNTIME:
            raise unittest.SkipTest("Node.js or Bun is not available in environment")
        try:
            res = subprocess.run([JS_RUNTIME, "-v"], capture_output=True, text=True, check=True)
            cls.node_version = res.stdout.strip()
        except Exception as e:
            raise unittest.SkipTest(f"JS runtime execution failed: {e}")

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

    def test_fixed_line_and_short_codes(self):
        """Test geographic landlines and short codes in Node.js."""
        code = """
        const rPp = u.normalizeCambodianPhone("023 210 022");
        const r117 = u.normalizeCambodianPhone("117");
        console.log(JSON.stringify({ rPp, r117 }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["rPp"]["line_type"], "fixed_line")
        self.assertEqual(out["rPp"]["normalized_e164"], "+85523210022")
        self.assertEqual(out["r117"]["line_type"], "short_code")

    def test_money_total_precision(self):
        """Test financial minor unit arithmetic in Node.js."""
        code = """
        const items = [{ price: 0.1, quantity: 3 }, { price: 0.2, quantity: 2 }];
        const res = u.calculateMoneyTotal(items, "USD", 10.0);
        console.log(JSON.stringify(res));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["subtotal"], 0.7)
        self.assertEqual(out["tax"], 0.07)
        self.assertEqual(out["total"], 0.77)

    def test_khqr_full_parsing_js(self):
        """Test EMVCo TLV parser in Node.js."""
        code = """
        const payload = "00020101021129220010sokha@devb5204541153031165405250005802KH5912AngkorCoffee6010Phnom Penh6304";
        const crc = u.calculateKhqrCrc16(payload);
        const parsed = u.parseKhqr(payload + crc);
        console.log(JSON.stringify(parsed));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["is_valid_format"])
        self.assertTrue(out["is_valid_crc"])
        self.assertEqual(out["currency_name"], "KHR")
        self.assertEqual(out["amount"], 25000)
        self.assertEqual(out["merchant_name"], "AngkorCoffee")
        self.assertEqual(out["bakong_account_id"], "sokha@devb")

    def test_khmer_words_sorting_js(self):
        """Test Khmer word sorting with Intl.Collator in Node.js."""
        code = """
        const words = ["ចាកចេញ", "កម្ពុជា", "ខេត្ត"];
        const sorted = u.sortKhmerWords(words);
        console.log(JSON.stringify(sorted));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out[0], "កម្ពុជា")
        self.assertEqual(out[1], "ខេត្ត")
        self.assertEqual(out[2], "ចាកចេញ")

    def test_cambodian_national_id_validation_js(self):
        """Test National ID validation parity in JS runtime."""
        code = """
        const r1 = u.validateCambodianId("012345678");
        const r2 = u.validateCambodianId("១២-០១២៣-៤៥៦៧");
        const r3 = u.validateCambodianId("invalid");
        console.log(JSON.stringify({ r1, r2, r3 }));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["r1"]["is_valid"])
        self.assertEqual(out["r1"]["id_type"], "legacy_id")
        self.assertEqual(out["r1"]["khmer_digits"], "០១២៣៤៥៦៧៨")
        self.assertTrue(out["r2"]["is_valid"])
        self.assertEqual(out["r2"]["id_type"], "smart_id")
        self.assertEqual(out["r2"]["normalized"], "1201234567")
        self.assertFalse(out["r3"]["is_valid"])

    def test_cambodian_license_plate_parsing_js(self):
        """Test License Plate parsing parity in JS runtime."""
        code = """
        const p1 = u.parseKhmerLicensePlate("Phnom Penh 2BC-1234");
        const p2 = u.parseKhmerLicensePlate("1FD-5678");
        const p3 = u.parseKhmerLicensePlate("រដ្ឋ 01 2-1234");
        console.log(JSON.stringify({ p1, p2, p3 }));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["p1"]["is_valid_format"])
        self.assertEqual(out["p1"]["plate_type"], "civilian_car")
        self.assertEqual(out["p1"]["province"], "Phnom Penh")
        self.assertEqual(out["p1"]["series"], "2BC")
        self.assertTrue(out["p2"]["is_valid_format"])
        self.assertEqual(out["p2"]["plate_type"], "motorcycle")
        self.assertTrue(out["p3"]["is_valid_format"])
        self.assertEqual(out["p3"]["plate_type"], "state")

    def test_khqr_merchant_name_formatting_js(self):
        """Test Tag 59 formatting and dynamic QR generation in JS."""
        code = """
        const formatted = u.formatKhqrMerchantName("  Starbucks \\t \\"Coffee\\" \\n Phnom Penh  ");
        const emptyName = u.formatKhqrMerchantName("");
        const qr = u.generateKhqr({
          bakongAccountId: "merchant@abaa",
          merchantName: "Brown Coffee Roasters",
          amount: 15000,
          currency: "KHR",
        });
        const verified = u.verifyKhqr(qr);
        console.log(JSON.stringify({ formatted, emptyName, isValid: verified.isValid }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["formatted"], "Starbucks Coffee Phnom Pe")
        self.assertEqual(out["emptyName"], "MERCHANT")
        self.assertTrue(out["isValid"])

    def test_cambodian_tin_validation_js(self):
        """Test Cambodian GDT Tax Identification Number (TIN) validation in JS."""
        code = """
        const t1 = u.validateCambodianTin("123456789");
        const t2 = u.validateCambodianTin("K001-987654321");
        const t3 = u.validateCambodianTin("K002-១២៣៤៥៦៧៨៩");
        const t4 = u.validateCambodianTin("L-123456789");
        const t_inv = u.validateCambodianTin("12345");
        console.log(JSON.stringify({ t1, t2, t3, t4, t_inv }));
        """
        out = json.loads(run_node_eval(code))
        self.assertTrue(out["t1"]["is_valid_syntax"])
        self.assertEqual(out["t1"]["tin_type"], "standard_tin")
        self.assertTrue(out["t2"]["is_valid_syntax"])
        self.assertEqual(out["t2"]["entity_type"], "corporate")
        self.assertEqual(out["t2"]["branch_code"], "001")
        self.assertTrue(out["t3"]["is_valid_syntax"])
        self.assertEqual(out["t3"]["digits"], "123456789")
        self.assertTrue(out["t4"]["is_valid_syntax"])
        self.assertEqual(out["t4"]["entity_type"], "sole_proprietorship")
        self.assertFalse(out["t_inv"]["is_valid_syntax"])

    def test_lunar_zodiac_and_sak_js(self):
        """Test Khmer Lunar Zodiac and Sak era calculation parity in JS runtime."""
        code = """
        const z2024 = u.getKhmerLunarZodiac(2024);
        const s2024 = u.getKhmerSakEra(2024);
        const info2026 = u.getKhmerYearEraInfo(2026);
        console.log(JSON.stringify({ z2024, s2024, info2026 }));
        """
        out = json.loads(run_node_eval(code))
        self.assertEqual(out["z2024"]["zodiac_km"], "រោង")
        self.assertEqual(out["z2024"]["zodiac_en"], "Dragon")
        self.assertEqual(out["s2024"]["sak_km"], "ឆស័ក")
        self.assertEqual(out["s2024"]["sak_number"], 6)
        self.assertEqual(out["info2026"]["zodiac_km"], "មមី")
        self.assertEqual(out["info2026"]["sak_km"], "អដ្ឋស័ក")
        self.assertEqual(out["info2026"]["formal_string_km"], "ព.ស. ២៥៦៩ ឆ្នាំមមី អដ្ឋស័ក")


if __name__ == "__main__":
    unittest.main()
