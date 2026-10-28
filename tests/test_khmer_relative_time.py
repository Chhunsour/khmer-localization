"""
test_khmer_relative_time.py - Unit tests for Khmer relative time formatting.

Validates:
1. "អម្បាញ់មិញ" for immediate past (< 10 seconds).
2. Seconds, minutes, hours ago ("X នាទីមុន", "X ម៉ោងមុន").
3. "ម្សិលមិញ" for yesterday.
4. Days, weeks, months, years ago ("X ថ្ងៃមុន", "X សប្តាហ៍មុន", "X ខែមុន", "X ឆ្នាំមុន").
5. Future relative times ("ថ្ងៃស្អែក", "ក្នុងរយៈពេល X នាទីទៀត").
6. Optional Khmer digits (០-៩).
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import format_khmer_relative_time


class TestKhmerRelativeTime(unittest.TestCase):
    def test_just_now(self):
        self.assertEqual(format_khmer_relative_time(0), "អម្បាញ់មិញ")
        self.assertEqual(format_khmer_relative_time(-5), "អម្បាញ់មិញ")
        self.assertEqual(format_khmer_relative_time(5), "អម្បាញ់មិញ")

    def test_minutes_and_hours_ago(self):
        # 30 seconds ago
        self.assertEqual(format_khmer_relative_time(-30), "មុននេះបន្តិច")
        # 5 minutes ago
        self.assertEqual(format_khmer_relative_time(-300), "5 នាទីមុន")
        # 2 hours ago
        self.assertEqual(format_khmer_relative_time(-7200), "2 ម៉ោងមុន")

    def test_yesterday_and_days_ago(self):
        # 1 day ago (86400s) -> ម្សិលមិញ
        self.assertEqual(format_khmer_relative_time(-86400), "ម្សិលមិញ")
        # 3 days ago
        self.assertEqual(format_khmer_relative_time(-86400 * 3), "3 ថ្ងៃមុន")

    def test_weeks_months_years_ago(self):
        # 2 weeks ago
        self.assertEqual(format_khmer_relative_time(-86400 * 14), "2 សប្តាហ៍មុន")
        # 2 months ago (60 days)
        self.assertEqual(format_khmer_relative_time(-86400 * 60), "2 ខែមុន")
        # 2 years ago (730 days)
        self.assertEqual(format_khmer_relative_time(-86400 * 730), "2 ឆ្នាំមុន")

    def test_future_times(self):
        # In 10 minutes
        self.assertEqual(format_khmer_relative_time(600, future=True), "ក្នុងរយៈពេល 10 នាទីទៀត")
        # Tomorrow (86400s)
        self.assertEqual(format_khmer_relative_time(86400, future=True), "ថ្ងៃស្អែក")
        # In 3 days
        self.assertEqual(format_khmer_relative_time(86400 * 3, future=True), "ក្នុងរយៈពេល 3 ថ្ងៃទៀត")

    def test_khmer_numerals(self):
        res = format_khmer_relative_time(-300, use_khmer_digits=True)
        self.assertEqual(res, "៥ នាទីមុន")


if __name__ == "__main__":
    unittest.main()
