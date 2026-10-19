"""
test_date_and_formatting.py - Tests for Khmer Date, Time, Calendar, Buddhist Era,
and Safe Text Truncation / Word Segmentation.

Verifies:
1. Solar calendar month names and day names in Khmer.
2. Buddhist Era (BE = CE + 543) conversion.
3. Relative time formatting in Khmer.
4. Grapheme-aware text truncation preserving Coeng sequences without dotted circles.
5. Live Node.js Intl.DateTimeFormat and Intl.Segmenter runtime behavior.
"""

import datetime
import json
import shutil
import subprocess
import unicodedata
import unittest
from typing import Optional


# --- Python Reference Implementation of Helpers ---

KHMER_MONTHS = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ"
]

KHMER_DAYS = [
    "ច័ន្ទ", "អង្គារ", "ពុធ", "ព្រហស្បតិ៍", "សុក្រ", "សៅរ៍", "អាទិត្យ"
]


def to_buddhist_era(year_ce: int) -> int:
    """Calculate Buddhist Era from Christian Era (BE = CE + 543)."""
    return year_ce + 543


def format_khmer_date(
    d: datetime.date,
    include_be: bool = False,
    use_khmer_digits: bool = False
) -> str:
    """Format a date using Cambodian calendar conventions."""
    month_name = KHMER_MONTHS[d.month - 1]
    day_str = str(d.day)
    year_str = str(d.year)

    if use_khmer_digits:
        table = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
        day_str = day_str.translate(table)
        year_str = year_str.translate(table)

    formatted = f"ថ្ងៃទី {day_str} ខែ{month_name} ឆ្នាំ {year_str}"
    if include_be:
        be_year = to_buddhist_era(d.year)
        be_str = str(be_year)
        if use_khmer_digits:
            be_str = be_str.translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))
        formatted += f" (ព.ស. {be_str})"

    return formatted


def format_khmer_relative_time(diff_seconds: int) -> str:
    """Format elapsed seconds as natural Khmer relative time."""
    if diff_seconds < 60:
        return "មុននេះបន្តិច"
    mins = diff_seconds // 60
    if mins < 60:
        return f"{mins} នាទីមុន"
    hours = mins // 60
    if hours < 24:
        return f"{hours} ម៉ោងមុន"
    days = hours // 24
    if days == 1:
        return "ម្សិលមិញ"
    if days < 7:
        return f"{days} ថ្ងៃមុន"
    return f"{days // 7} សប្តាហ៍មុន"


def safe_truncate_khmer(text: str, max_chars: int) -> str:
    """
    Truncate text without splitting Khmer combining marks or Coeng sequences.
    Ensures cut index does not land on or immediately after Coeng (U+17D2).
    """
    if len(text) <= max_chars:
        return text

    cut_idx = max_chars
    # Walk backward if cut point is a combining mark or immediately after Coeng (U+17D2)
    while cut_idx > 0:
        char = text[cut_idx:cut_idx+1]
        prev_char = text[cut_idx-1:cut_idx] if cut_idx > 0 else ""

        # If current char is a combining mark, step back
        if unicodedata.combining(char):
            cut_idx -= 1
            continue

        # If previous char was Coeng (U+17D2), we cannot cut right after Coeng
        if prev_char == "\u17D2":
            cut_idx -= 1
            continue

        break

    return text[:cut_idx] + "…"


# --- Test Suite ---

class TestKhmerDateAndCalendar(unittest.TestCase):
    def test_buddhist_era_calculation(self):
        """Buddhist Era is exactly CE + 543."""
        self.assertEqual(to_buddhist_era(2026), 2569)
        self.assertEqual(to_buddhist_era(2024), 2567)
        self.assertEqual(to_buddhist_era(1993), 2536)  # Year of Kingdom restoration

    def test_khmer_month_names(self):
        """All 12 solar month names match Cambodian standard."""
        self.assertEqual(len(KHMER_MONTHS), 12)
        self.assertEqual(KHMER_MONTHS[0], "មករា")   # January
        self.assertEqual(KHMER_MONTHS[9], "តុលា")   # October
        self.assertEqual(KHMER_MONTHS[11], "ធ្នូ")   # December

    def test_format_khmer_date_standard(self):
        """Standard date formatting with Khmer month and Latin numerals."""
        d = datetime.date(2026, 10, 19)
        result = format_khmer_date(d)
        self.assertEqual(result, "ថ្ងៃទី 19 ខែតុលា ឆ្នាំ 2026")

    def test_format_khmer_date_with_be(self):
        """Date formatting with Buddhist Era."""
        d = datetime.date(2026, 10, 19)
        result = format_khmer_date(d, include_be=True)
        self.assertEqual(result, "ថ្ងៃទី 19 ខែតុលា ឆ្នាំ 2026 (ព.ស. 2569)")

    def test_format_khmer_date_khmer_numerals(self):
        """Date formatting using traditional Khmer numerals."""
        d = datetime.date(2026, 10, 19)
        result = format_khmer_date(d, include_be=True, use_khmer_digits=True)
        self.assertEqual(result, "ថ្ងៃទី ១៩ ខែតុលា ឆ្នាំ ២០២៦ (ព.ស. ២៥៦៩)")


class TestKhmerRelativeTime(unittest.TestCase):
    def test_just_now(self):
        self.assertEqual(format_khmer_relative_time(30), "មុននេះបន្តិច")

    def test_minutes_ago(self):
        self.assertEqual(format_khmer_relative_time(300), "5 នាទីមុន")

    def test_hours_ago(self):
        self.assertEqual(format_khmer_relative_time(7200), "2 ម៉ោងមុន")

    def test_yesterday(self):
        self.assertEqual(format_khmer_relative_time(86400), "ម្សិលមិញ")

    def test_days_ago(self):
        self.assertEqual(format_khmer_relative_time(86400 * 3), "3 ថ្ងៃមុន")


class TestSafeTextTruncation(unittest.TestCase):
    def test_truncation_preserves_coeng_subscript(self):
        """Truncating 'កម្ពុជា' must never split Coeng (U+17D2) from subscript consonant."""
        text = "កម្ពុជា"  # ក (U+1780) + ម (U+1798) + ្ (U+17D2) + ព (U+1796) + ុ (U+17BB) + ជ (U+1787) + ា (U+17B6)
        # Length in code points is 7. If max_chars is 3, naive slice lands on U+17D2
        truncated = safe_truncate_khmer(text, 3)
        # Should back up to index 2 (before Coeng) rather than slicing after U+17D2
        self.assertNotIn("\u17D2…", truncated)
        self.assertTrue(truncated.endswith("…"))

    def test_short_string_not_truncated(self):
        text = "សួស្តី"
        self.assertEqual(safe_truncate_khmer(text, 10), "សួស្តី")


class TestNodeIntlDateTimeFormatRuntime(unittest.TestCase):
    """Verifies live Node.js Intl.DateTimeFormat and Intl.Segmenter."""

    @classmethod
    def setUpClass(cls):
        cls.node_available = shutil.which("node") is not None

    def _run_node_script(self, js_code: str) -> dict:
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)

    def test_intl_datetimeformat_km_kh(self):
        if not self.node_available:
            self.skipTest("Node.js is not installed in the environment.")

        js_code = """
        const d = new Date(Date.UTC(2026, 9, 19)); // Month 9 is October (0-indexed)
        const formatter = new Intl.DateTimeFormat('km-KH', {
          month: 'long',
          timeZone: 'UTC'
        });
        const monthName = formatter.format(d);
        console.log(JSON.stringify({ monthName }));
        """
        output = self._run_node_script(js_code)
        # October in km-KH is តុលា
        self.assertIn("តុលា", output["monthName"])

    def test_intl_segmenter_graphemes(self):
        if not self.node_available:
            self.skipTest("Node.js is not installed in the environment.")

        js_code = """
        const text = "កម្ពុជា";
        const segmenter = new Intl.Segmenter('km', { granularity: 'grapheme' });
        const segments = Array.from(segmenter.segment(text)).map(s => s.segment);
        console.log(JSON.stringify({ segments, count: segments.length }));
        """
        output = self._run_node_script(js_code)
        # Intl.Segmenter groups Coeng and vowels into grapheme clusters, avoiding dotted circles
        self.assertGreater(output["count"], 0)
        self.assertLess(output["count"], len("កម្ពុជា"))  # Far fewer graphemes than 7 UTF-16 code units

    def test_intl_segmenter_word_breaks(self):
        if not self.node_available:
            self.skipTest("Node.js is not installed in the environment.")

        js_code = """
        const text = "សួស្តីកម្ពុជា"; // Hello Cambodia (no spaces)
        const segmenter = new Intl.Segmenter('km', { granularity: 'word' });
        const words = Array.from(segmenter.segment(text)).map(s => s.segment);
        console.log(JSON.stringify({ words, count: words.length }));
        """
        output = self._run_node_script(js_code)
        # ICU dictionary segments into words: ["សួស្តី", "កម្ពុជា"]
        self.assertIn("សួស្តី", output["words"])
        self.assertIn("កម្ពុជា", output["words"])


if __name__ == "__main__":
    unittest.main()
