"""
test_agent_rules_installer.py - Unit tests for install_agent_rules.py

Verifies:
1. Rule installation across all supported agent targets (Cursor, Claude, Copilot, Windsurf, Gemini, AGENTS).
2. Tiers (nano, standard, enterprise).
3. Append vs Create vs Skip behavior.
4. Dry-run mode without modifying filesystem.
"""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.install_agent_rules import RULES_BY_TIER, TARGET_FILES, install_rules


class TestAgentRulesInstaller(unittest.TestCase):
    def test_tier_contents(self):
        self.assertIn("nano", RULES_BY_TIER)
        self.assertIn("standard", RULES_BY_TIER)
        self.assertIn("enterprise", RULES_BY_TIER)
        self.assertIn("Noun", RULES_BY_TIER["nano"])
        self.assertIn("Adjective", RULES_BY_TIER["standard"])
        self.assertIn("Bakong", RULES_BY_TIER["enterprise"])

    def test_dry_run_creates_no_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = install_rules(target="all", tier="standard", dest_dir=tmpdir, dry_run=True)
            self.assertEqual(len(res), len(TARGET_FILES))
            for path_key in res:
                self.assertFalse(os.path.exists(os.path.join(tmpdir, path_key)))

    def test_install_single_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = install_rules(target="cursor", tier="nano", dest_dir=tmpdir)
            cursorrules_path = os.path.join(tmpdir, ".cursorrules")
            self.assertTrue(os.path.exists(cursorrules_path))
            with open(cursorrules_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Khmer Localization Guardrails (Nano Tier)", content)
            self.assertEqual(res[".cursorrules"], "created")

    def test_install_idempotent_skip_without_force(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # First install
            install_rules(target="claude", tier="standard", dest_dir=tmpdir)
            # Second install should skip
            res2 = install_rules(target="claude", tier="standard", dest_dir=tmpdir, force=False)
            self.assertEqual(res2["CLAUDE.md"], "skipped (already present)")

    def test_install_cursor_mdc_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            install_rules(target="cursor-mdc", tier="standard", dest_dir=tmpdir)
            mdc_path = os.path.join(tmpdir, ".cursor", "rules", "khmer-localization.mdc")
            self.assertTrue(os.path.exists(mdc_path))
            with open(mdc_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("---", content)
            self.assertIn("globs:", content)
            self.assertIn("Standard Tier", content)


if __name__ == "__main__":
    unittest.main()
