"""
test_check_khmer_unicode.py - Automated tests for Khmer Unicode and UTF-8 integrity checker.

Tests verify:
- Valid Khmer text with standard combining marks
- Legitimate typography characters (ZWSP, punctuation, riel symbol)
- English-only text
- Mixed Khmer and English text
- Replacement character (U+FFFD) detection (ERROR [DATA_CORRUPTION])
- Suspicious control characters (ERROR [SUSPICIOUS_CONTROL])
- Invalid UTF-8 bytes (ERROR [BYTE_ENCODING])
- Literal dotted circle (U+25CC) detection (WARNING [VISUAL_RENDERING])
- Orphaned combining marks (WARNING [VISUAL_RENDERING])
- Orphaned combining marks after ZWSP and Latin characters
- Trailing coeng warning (WARNING [VISUAL_RENDERING])
- Multi-file scanning & CLI exit codes
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path so we can import directly
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_khmer_unicode import KhmerUnicodeChecker, format_text_report  # noqa: E402


class TestKhmerUnicodeChecker(unittest.TestCase):
    def setUp(self):
        self.checker = KhmerUnicodeChecker()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_file(self, filename: str, content: str, encoding: str = "utf-8") -> Path:
        file_path = self.test_dir / filename
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return file_path

    def _create_binary_file(self, filename: str, raw_bytes: bytes) -> Path:
        file_path = self.test_dir / filename
        with open(file_path, "wb") as f:
            f.write(raw_bytes)
        return file_path

    def test_valid_khmer_text(self):
        """Valid Khmer words with combining marks and Coeng subscripts should pass without issues."""
        # កម្ពុជា (Kampuchea) contains Coeng Mo (\u17D2\u1798)
        # ភាសាខ្មែរ (Khmer language) contains Coeng Kha (\u17D2\u1781) and vowel \u17C2
        # សួស្តី (Hello) contains Coeng Sa (\u17D2\u179F) and Coeng Da (\u17D2\u178A)
        content = (
            '{\n'
            '  "app_title": "កម្ពុជា",\n'
            '  "language": "ភាសាខ្មែរ",\n'
            '  "greeting": "សួស្តី"\n'
            '}\n'
        )
        file_path = self._create_file("valid_khmer.json", content)
        result = self.checker.check_file(file_path)

        self.assertTrue(result.has_khmer)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)
        self.assertGreater(result.stats.total_khmer_chars, 10)
        self.assertGreater(result.stats.coeng_subscripts, 0)
        self.assertGreater(result.stats.dependent_vowels, 0)

    def test_legitimate_typography_characters_not_rejected(self):
        """ZWSP (\u200B), Khmer Riel (\u17DB), Khan punctuation (\u17D4), Colon (\u17D6) must pass."""
        # Using ZWSP for word breaking: "សូម\u200Bស្វាគមន៍"
        content = (
            "welcome: 'សូម\u200Bស្វាគមន៍'\n"
            "price: '10,000 ៛'\n"
            "sentence: 'សូមអរគុណ។'\n"
            "definition: 'អត្ថន័យ៖ សេចក្តីលម្អិត'\n"
            "repeated: 'ញឹកញាប់ៗ'\n"
        )
        file_path = self._create_file("legitimate_typography.yml", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)
        self.assertGreater(result.stats.zero_width_spaces, 0)
        self.assertEqual(result.stats.riel_symbols, 1)

    def test_english_only_text(self):
        """Standard English text should produce 0 errors, 0 warnings, and 0 Khmer characters."""
        content = (
            '{\n'
            '  "title": "Welcome to the Dashboard",\n'
            '  "button": "Submit",\n'
            '  "status": "Active"\n'
            '}\n'
        )
        file_path = self._create_file("en.json", content)
        result = self.checker.check_file(file_path)

        self.assertFalse(result.has_khmer)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)
        self.assertEqual(result.stats.total_khmer_chars, 0)

    def test_mixed_khmer_and_english_text(self):
        """Mixed Khmer and English text (bilingual UI keys) should pass cleanly."""
        content = (
            'export const currencies = [\n'
            '  { code: "USD", symbol: "$", label: "ដុល្លារអាមេរិក (USD)" },\n'
            '  { code: "KHR", symbol: "៛", label: "រៀលកម្ពុជា (KHR)" }\n'
            '];\n'
        )
        file_path = self._create_file("currencies.ts", content)
        result = self.checker.check_file(file_path)

        self.assertTrue(result.has_khmer)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)
        self.assertEqual(result.stats.riel_symbols, 1)

    def test_replacement_character_detected(self):
        """Unicode Replacement Character U+FFFD must be detected as an ERROR under DATA_CORRUPTION."""
        content = 'greeting = "សួស្តី \uFFFD"'
        file_path = self._create_file("corrupted.py", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 1)
        self.assertTrue(any("Replacement Character" in i.message for i in result.issues))
        self.assertEqual(result.issues[0].level, "ERROR")
        self.assertEqual(result.issues[0].category, "DATA_CORRUPTION")

    def test_suspicious_control_characters_detected(self):
        """Raw control characters like NULL byte or C0 codes must be detected as ERRORs under SUSPICIOUS_CONTROL."""
        content = 'key = "កម្ពុជា\x00\x07"'
        file_path = self._create_file("control_chars.txt", content)
        result = self.checker.check_file(file_path)

        self.assertGreaterEqual(result.error_count, 2)
        errors = [i for i in result.issues if i.level == "ERROR"]
        self.assertTrue(all(err.category == "SUSPICIOUS_CONTROL" for err in errors))
        self.assertTrue(any("control character" in err.message.lower() for err in errors))

    def test_literal_dotted_circle_detected(self):
        """Literal dotted circle U+25CC should trigger a WARNING under VISUAL_RENDERING."""
        content = 'label: "អត្ថបទ\u25CC"'
        file_path = self._create_file("dotted_circle.yaml", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 1)
        warnings = [i for i in result.issues if i.level == "WARNING"]
        self.assertEqual(warnings[0].category, "VISUAL_RENDERING")
        self.assertTrue(any("Dotted Circle" in w.message for w in warnings))

    def test_orphaned_combining_mark_detected(self):
        """A Khmer combining mark without a preceding base consonant triggers a WARNING."""
        content = 'label = " ា"'
        file_path = self._create_file("orphaned_vowel.txt", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertGreaterEqual(result.warning_count, 1)
        warnings = [i for i in result.issues if i.level == "WARNING"]
        self.assertEqual(warnings[0].category, "VISUAL_RENDERING")
        self.assertTrue(any("Orphaned" in w.message for w in warnings))

    def test_orphaned_combining_mark_after_zwsp(self):
        """A combining mark cannot follow a ZWSP word boundary; it must trigger an orphaned mark warning."""
        # \u200B followed by vowel \u17B6
        content = 'label = "សូម\u200B\u17B6"'
        file_path = self._create_file("vowel_after_zwsp.txt", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertGreaterEqual(result.warning_count, 1)
        warnings = [i for i in result.issues if i.level == "WARNING"]
        self.assertTrue(any("Orphaned" in w.message for w in warnings))

    def test_orphaned_combining_mark_after_latin_char(self):
        """A Khmer combining mark cannot attach to an ASCII/Latin character."""
        content = 'label = "hello\u17B6"'
        file_path = self._create_file("vowel_after_latin.txt", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertGreaterEqual(result.warning_count, 1)
        warnings = [i for i in result.issues if i.level == "WARNING"]
        self.assertTrue(any("Orphaned" in w.message for w in warnings))

    def test_trailing_coeng_warning(self):
        """A trailing Coeng marker (\u17D2) at end of string should trigger a WARNING."""
        content = 'label = "ក្ "'
        file_path = self._create_file("trailing_coeng.txt", content)
        result = self.checker.check_file(file_path)

        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 1)
        warnings = [i for i in result.issues if i.level == "WARNING"]
        self.assertEqual(warnings[0].category, "VISUAL_RENDERING")
        self.assertTrue(any("Trailing Khmer Coeng" in w.message for w in warnings))

    def test_invalid_utf8_binary_bytes(self):
        """A file with invalid UTF-8 byte sequences must report an encoding ERROR."""
        # 0x80 is an invalid stand-alone byte in UTF-8
        file_path = self._create_binary_file("invalid_utf8.txt", b"\x80\x81\xFF")
        result = self.checker.check_file(file_path)

        self.assertIsNotNone(result.encoding_error)
        self.assertEqual(result.error_count, 1)
        self.assertIn("Invalid UTF-8 byte sequence", result.encoding_error)

    def test_multi_file_directory_scan(self):
        """Scanning a directory should process multiple files and aggregate statistics."""
        self._create_file("file1.json", '{"name": "កម្ពុជា"}')
        self._create_file("file2.ts", 'const str = "ភាសាខ្មែរ";')
        self._create_file("file3.md", '# English Documentation\n\nOnly English here.')

        results = self.checker.scan_path(self.test_dir)
        self.assertEqual(len(results), 3)

        report, total_errors, total_warnings = format_text_report(results, show_stats=True)
        self.assertEqual(total_errors, 0)
        self.assertEqual(total_warnings, 0)
        self.assertIn("Files scanned             : 3", report)
        self.assertIn("Files containing Khmer    : 2", report)


class TestCommandLineInterface(unittest.TestCase):
    def setUp(self):
        self.script_path = str(SCRIPTS_DIR / "check_khmer_unicode.py")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_cli(self, args: list) -> subprocess.CompletedProcess:
        cmd = [sys.executable, self.script_path] + args
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_cli_help(self):
        """CLI --help should exit with status 0 and show usage."""
        proc = self._run_cli(["--help"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Khmer Unicode & UTF-8 Integrity Checker", proc.stdout)

    def test_cli_clean_file_exit_zero(self):
        """CLI with clean files should exit with status 0."""
        file_path = self.test_dir / "clean.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"hello": "សួស្តី"}')

        proc = self._run_cli([str(file_path)])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("No encoding errors", proc.stdout)

    def test_cli_error_file_exit_one(self):
        """CLI with errors should exit with status 1."""
        file_path = self.test_dir / "bad.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"corrupt": "កម្ពុជា \uFFFD"}')

        proc = self._run_cli([str(file_path)])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Unicode Replacement Character", proc.stdout)

    def test_cli_strict_mode_exit_one_on_warning(self):
        """CLI in --strict mode should exit with status 1 when warnings are detected."""
        file_path = self.test_dir / "warn.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"trailing": "ក្ "}')

        # Normal mode: returns 0 on warning
        proc_normal = self._run_cli([str(file_path)])
        self.assertEqual(proc_normal.returncode, 0)

        # Strict mode: returns 1 on warning
        proc_strict = self._run_cli(["--strict", str(file_path)])
        self.assertEqual(proc_strict.returncode, 1)

    def test_cli_nonexistent_path_exit_two(self):
        """CLI with nonexistent path should exit with status 2."""
        proc = self._run_cli(["/nonexistent/path/to/nothing.json"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Target path does not exist", proc.stderr)

    def test_cli_json_output(self):
        """CLI with --json should return structured JSON parseable by automated agents."""
        file_path = self.test_dir / "data.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"title": "កម្ពុជា"}')

        proc = self._run_cli(["--json", str(file_path)])
        self.assertEqual(proc.returncode, 0)
        import json
        data = json.loads(proc.stdout)
        self.assertEqual(data["summary"]["status"], "PASS")
        self.assertEqual(data["summary"]["total_files"], 1)
        self.assertEqual(data["summary"]["files_with_khmer"], 1)
        self.assertEqual(data["files"][0]["status"], "PASS")
        self.assertEqual(data["files"][0]["total_errors"], 0)
        self.assertGreater(data["files"][0]["stats"]["total_khmer_chars"], 0)

    def test_cli_json_output_with_errors(self):
        """CLI with --json and errors should output valid JSON with error details and exit status 1."""
        file_path = self.test_dir / "corrupt.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"text": "កម្ពុជា \uFFFD"}')

        proc = self._run_cli(["--json", str(file_path)])
        self.assertEqual(proc.returncode, 1)
        import json
        data = json.loads(proc.stdout)
        self.assertEqual(data["summary"]["status"], "FAIL")
        self.assertEqual(data["summary"]["total_errors"], 1)
        self.assertEqual(data["files"][0]["status"], "FAIL")
        self.assertEqual(len(data["files"][0]["issues"]), 1)
        self.assertEqual(data["files"][0]["issues"][0]["category"], "DATA_CORRUPTION")


if __name__ == "__main__":
    unittest.main()

