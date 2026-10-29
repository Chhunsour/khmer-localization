"""
test_currency_formatting.py - Tests for KHR and USD currency formatting, rounding, and large values.

Verifies:
1. ISO 4217 & Intl.NumberFormat runtime behavior:
   - Demonstrates that ECMAScript/ICU runtimes default to 2 decimal places for KHR (1,000.00៛),
     which is why explicit configuration { minimumFractionDigits: 0, maximumFractionDigits: 0 }
     is MANDATORY for standard whole-riel consumer prices.
2. Explicit Whole-Riel formatting:
   - Zero, negative amounts, large amounts (billions), and rounding of fractional riel.
3. USD formatting:
   - Standard 2 decimal places, zero, negative amounts, large amounts, and half-up rounding.
4. Khmer numeral (-u-nu-khmr) vs Latin numeral (-u-nu-latn) formatting.
5. Cross-runtime parity (Node.js Intl.NumberFormat tested when node is available).
"""

import json
import math
import os
import shutil
import subprocess
import sys
import unittest


def format_khr_python(
    amount: float,
    whole_riel: bool = True,
    use_khmer_digits: bool = False,
    symbol: str = "៛"
) -> str:
    """
    Reference Python implementation for formatting Cambodian Riel (KHR).
    Demonstrates explicit handling of whole-riel display vs fractional rounding.
    """
    if whole_riel:
        # Standard commercial display convention: round to nearest whole riel
        # Use standard round-half-up
        sign = "-" if amount < 0 else ""
        abs_val = abs(amount)
        rounded = int(math.floor(abs_val + 0.5))
        # Format integer with commas
        formatted_num = f"{rounded:,}"
        if use_khmer_digits:
            # In Khmer locale, grouping with Khmer digits conventionally uses period '.'
            formatted_num = formatted_num.replace(",", ".")
            khmer_digits = "០១២៣៤៥៦៧៨៩"
            formatted_num = "".join(khmer_digits[int(c)] if c.isdigit() else c for c in formatted_num)
        return f"{sign}{formatted_num} {symbol}"
    else:
        # Accounting / ISO 4217 minor unit representation (2 decimal places)
        sign = "-" if amount < 0 else ""
        abs_val = abs(amount)
        formatted_num = f"{abs_val:,.2f}"
        if use_khmer_digits:
            khmer_digits = "០១២៣៤៥៦៧៨៩"
            formatted_num = "".join(khmer_digits[int(c)] if c.isdigit() else c for c in formatted_num)
        return f"{sign}{formatted_num} {symbol}"


def format_usd_python(amount: float) -> str:
    """
    Reference Python implementation for formatting US Dollars (USD).
    Standard 2 decimal places with half-up rounding.
    """
    sign = "-" if amount < 0 else ""
    abs_val = abs(amount)
    # Round half-up to 2 decimals
    rounded = math.floor(abs_val * 100 + 0.5) / 100.0
    formatted_num = f"{rounded:,.2f}"
    return f"{sign}${formatted_num}"


class TestCurrencyFormattingPython(unittest.TestCase):
    def test_khr_whole_riel_standard(self):
        """KHR whole-riel formatting with Latin numerals."""
        self.assertEqual(format_khr_python(1000), "1,000 ៛")
        self.assertEqual(format_khr_python(25000), "25,000 ៛")
        self.assertEqual(format_khr_python(500), "500 ៛")

    def test_khr_zero_and_negative(self):
        """KHR handles zero and negative values cleanly."""
        self.assertEqual(format_khr_python(0), "0 ៛")
        self.assertEqual(format_khr_python(-25000), "-25,000 ៛")
        self.assertEqual(format_khr_python(-100000), "-100,000 ៛")

    def test_khr_rounding(self):
        """Fractional riel amounts round to nearest integer under whole-riel convention."""
        self.assertEqual(format_khr_python(25000.4), "25,000 ៛")
        self.assertEqual(format_khr_python(25000.5), "25,001 ៛")
        self.assertEqual(format_khr_python(25000.75), "25,001 ៛")

    def test_khr_large_values(self):
        """KHR handles multi-million and multi-billion amounts with standard separators."""
        self.assertEqual(format_khr_python(100_000_000), "100,000,000 ៛")
        self.assertEqual(format_khr_python(1_234_567_890), "1,234,567,890 ៛")

    def test_khr_khmer_numerals(self):
        """KHR formatting using Khmer digits (០-៩)."""
        # 25,000 -> ២៥.០០០ ៛
        self.assertEqual(format_khr_python(25000, use_khmer_digits=True), "២៥.០០០ ៛")
        self.assertEqual(format_khr_python(1000, use_khmer_digits=True), "១.០០០ ៛")

    def test_usd_standard(self):
        """USD formats with standard 2 decimal places."""
        self.assertEqual(format_usd_python(12.5), "$12.50")
        self.assertEqual(format_usd_python(100), "$100.00")
        self.assertEqual(format_usd_python(0), "$0.00")

    def test_usd_negative(self):
        """USD negative values formatted correctly."""
        self.assertEqual(format_usd_python(-15.99), "-$15.99")
        self.assertEqual(format_usd_python(-0.5), "-$0.50")

    def test_usd_rounding(self):
        """USD rounds fractional cents half-up."""
        self.assertEqual(format_usd_python(12.345), "$12.35")
        self.assertEqual(format_usd_python(12.344), "$12.34")

    def test_usd_large_values(self):
        """USD handles large numbers with thousand separators."""
        self.assertEqual(format_usd_python(1_000_000), "$1,000,000.00")
        self.assertEqual(format_usd_python(987_654_321.1), "$987,654,321.10")


class TestIntlNumberFormatRuntime(unittest.TestCase):
    """
    Tests verifying real ECMAScript Intl.NumberFormat behavior via Node.js (when available).
    Confirms runtime defaults and explicit fraction-digit overrides.
    """

    @classmethod
    def setUpClass(cls):
        candidates = ["node", "bun", os.path.expanduser("~/.bun/bin/bun")]
        cls.js_binary = None
        for cand in candidates:
            path = shutil.which(cand) if not os.path.isabs(cand) else (cand if os.path.exists(cand) else None)
            if path:
                cls.js_binary = path
                break
        cls.node_available = cls.js_binary is not None

    def _run_node_script(self, js_code: str) -> dict:
        if not self.node_available:
            self.skipTest("Node.js or Bun runtime not installed in environment")
        cmd = [self.js_binary, "-e", js_code]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(proc.returncode, 0, f"JS script failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def test_intl_khr_default_has_two_decimals(self):
        """
        CRITICAL AUDIT TEST:
        Demonstrates that Intl.NumberFormat without fraction options defaults to 2 decimals for KHR.
        This proves that developers CANNOT assume 0 decimals by default.
        """
        js = """
        const fmt = new Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' });
        const res = {
          formatted: fmt.format(1000),
          minFrac: fmt.resolvedOptions().minimumFractionDigits,
          maxFrac: fmt.resolvedOptions().maximumFractionDigits
        };
        console.log(JSON.stringify(res));
        """
        data = self._run_node_script(js)
        # In ECMAScript / ICU, ISO 4217 minor unit for KHR is 2
        self.assertEqual(data["minFrac"], 2)
        self.assertEqual(data["maxFrac"], 2)
        self.assertIn(".00", data["formatted"])

    def test_intl_khr_explicit_whole_riel(self):
        """
        Configuring { minimumFractionDigits: 0, maximumFractionDigits: 0 }
        produces whole-riel formatting without .00.
        """
        js = """
        const fmt = new Intl.NumberFormat('km-KH', {
          style: 'currency',
          currency: 'KHR',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        });
        const res = {
          standard: fmt.format(25000),
          zero: fmt.format(0),
          negative: fmt.format(-25000),
          large: fmt.format(1234567890),
          rounded: fmt.format(25000.75)
        };
        console.log(JSON.stringify(res));
        """
        data = self._run_node_script(js)
        self.assertEqual(data["standard"], "25,000៛")
        self.assertEqual(data["zero"], "0៛")
        self.assertEqual(data["negative"], "-25,000៛")
        self.assertEqual(data["large"], "1,234,567,890៛")
        self.assertEqual(data["rounded"], "25,001៛")

    def test_intl_usd_standard(self):
        """Intl.NumberFormat with USD formats standard 2 decimals, zero, negative, large values."""
        js = """
        const fmt = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
        const res = {
          standard: fmt.format(12.5),
          zero: fmt.format(0),
          negative: fmt.format(-15.99),
          rounded: fmt.format(12.345),
          large: fmt.format(1000000)
        };
        console.log(JSON.stringify(res));
        """
        data = self._run_node_script(js)
        self.assertEqual(data["standard"], "$12.50")
        self.assertEqual(data["zero"], "$0.00")
        self.assertEqual(data["negative"], "-$15.99")
        self.assertEqual(data["rounded"], "$12.35")
        self.assertEqual(data["large"], "$1,000,000.00")


if __name__ == "__main__":
    unittest.main()
