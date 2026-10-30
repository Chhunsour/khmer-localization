"""
test_audit_khmer_i18n.py - Automated Unit Tests for Khmer Localization Audit Engine

Verifies that audit_khmer_i18n.py accurately identifies missing translation keys,
placeholder mismatches, royal vocabulary, inverted word order, decimal riels,
hardcoded strings, and destructive regexes.
"""

import json
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.audit_khmer_i18n import audit_locale_files, audit_source_code, run_full_audit

FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "sample_project")
LOCALES_DIR = os.path.join(FIXTURE_DIR, "locales")
SRC_DIR = os.path.join(FIXTURE_DIR, "src")


class TestKhmerI18nAudit(unittest.TestCase):
    def test_audit_locale_files(self):
        """Test detection of translation defects in locale JSON files."""
        findings = audit_locale_files(LOCALES_DIR, base_locale="en", target_locale="km")
        rules = {f["rule"]: f for f in findings}

        # 1. Missing key
        self.assertIn("MISSING_TRANSLATION_KEY", rules)
        self.assertEqual(rules["MISSING_TRANSLATION_KEY"]["key"], "common.save")

        # 2. Royal register
        self.assertIn("ROYAL_REGISTER_DETECTED", rules)
        self.assertEqual(rules["ROYAL_REGISTER_DETECTED"]["key"], "auth.sign_in")

        # 3. Placeholder mismatch
        placeholder_keys = [f["key"] for f in findings if f["rule"] == "PLACEHOLDER_MISMATCH"]
        self.assertIn("auth.welcome_user", placeholder_keys)
        self.assertIn("commerce.price_tag", placeholder_keys)

        # 4. Untranslated string
        self.assertIn("UNTRANSLATED_STRING", rules)
        self.assertEqual(rules["UNTRANSLATED_STRING"]["key"], "auth.forgot_password")

        # 5. Inverted word order
        self.assertIn("INVERTED_WORD_ORDER", rules)
        self.assertEqual(rules["INVERTED_WORD_ORDER"]["key"], "commerce.total_price")

        # 6. Decimal riel
        self.assertIn("DECIMAL_RIEL_DETECTED", rules)
        self.assertEqual(rules["DECIMAL_RIEL_DETECTED"]["key"], "commerce.price_tag")

    def test_audit_source_code(self):
        """Test detection of hardcoded strings and dangerous patterns in source code."""
        findings = audit_source_code(SRC_DIR)
        rules = {f["rule"]: f for f in findings}

        # 1. Hardcoded Khmer string
        self.assertIn("HARDCODED_KHMER_STRING", rules)

        # 2. Hardcoded currency concatenation
        self.assertIn("HARDCODED_CURRENCY_CONCAT", rules)

        # 3. Destructive whitespace regex
        self.assertIn("DESTRUCTIVE_WHITESPACE_REGEX", rules)

    def test_font_stack_and_line_height_audit(self):
        """Test detection of missing Khmer font fallbacks and restrictive line-heights."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_css = os.path.join(tmpdir, "styles.css")
            with open(bad_css, "w", encoding="utf-8") as f:
                f.write("""
                .khmer-header {
                    font-family: Inter, Roboto, sans-serif;
                    line-height: 1.1;
                }
                """)
            findings = audit_source_code(tmpdir)
            rules = {f["rule"] for f in findings}
            self.assertIn("MISSING_KHMER_FONT_FALLBACK", rules)
            self.assertIn("RESTRICTIVE_LINE_HEIGHT_CLIPPING", rules)

    def test_tin_format_audit(self):
        """Test detection of invalid Cambodian TIN numbers in source files."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = os.path.join(tmpdir, "checkout.ts")
            with open(bad_file, "w", encoding="utf-8") as f:
                f.write('const config = { tin: "12345" };\n')
            findings = audit_source_code(tmpdir)
            rules = {f["rule"] for f in findings}
            self.assertIn("INVALID_TIN_FORMAT", rules)

    def test_html_root_attributes_audit(self):
        """Test detection of invalid dir='rtl' on Khmer HTML elements."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_html = os.path.join(tmpdir, "index.html")
            with open(bad_html, "w", encoding="utf-8") as f:
                f.write('<html lang="km" dir="rtl"><body>សួស្តី</body></html>\n')
            findings = audit_source_code(tmpdir)
            rules = {f["rule"] for f in findings}
            self.assertIn("INVALID_KHMER_TEXT_DIRECTION", rules)

    def test_unlocalized_date_format_detection(self):
        """Test detection of American MM/DD/YYYY date pattern in locale translations."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            en_json = os.path.join(tmpdir, "en.json")
            km_json = os.path.join(tmpdir, "km.json")
            with open(en_json, "w", encoding="utf-8") as f:
                json.dump({"date_hint": "Enter date (MM/DD/YYYY)"}, f)
            with open(km_json, "w", encoding="utf-8") as f:
                json.dump({"date_hint": "បញ្ចូលកាលបរិច្ឆេទ (MM/DD/YYYY)"}, f)
            findings = audit_locale_files(tmpdir, base_locale="en", target_locale="km")
            rules = {f["rule"] for f in findings}
            self.assertIn("UNLOCALIZED_DATE_PATTERN", rules)

    def test_run_full_audit_aggregation(self):
        """Test full audit aggregation and status reporting."""
        report = run_full_audit(FIXTURE_DIR, locales_dir=LOCALES_DIR, src_dir=SRC_DIR)
        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(report["summary"]["automated_errors"], 0)
        self.assertGreater(report["summary"]["automated_warnings"], 0)
        self.assertGreater(report["summary"]["human_review_required"], 0)
        self.assertGreater(report["summary"]["visual_inspection_required"], 0)
        self.assertGreater(report["summary"]["external_verification_required"], 0)

    def test_cli_json_output(self):
        """Test CLI interface returns parseable JSON report."""
        script_path = os.path.join(REPO_ROOT, "scripts", "audit_khmer_i18n.py")
        cmd = [
            sys.executable,
            script_path,
            FIXTURE_DIR,
            "--locales",
            LOCALES_DIR,
            "--src",
            SRC_DIR,
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        # Should exit with code 1 because fixture has errors
        self.assertEqual(proc.returncode, 1)
        data = json.loads(proc.stdout)
        self.assertIn("summary", data)
        self.assertIn("findings", data)
        self.assertEqual(data["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
