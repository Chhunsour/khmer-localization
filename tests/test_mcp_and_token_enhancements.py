"""
test_mcp_and_token_enhancements.py - Unit Tests for Token-Saving Enhancements & MCP Server

Validates:
1. lookup_ui_term function in Python and Node.js (exact and partial match).
2. lint_khmer_text function in Python and Node.js (Unicode errors, warnings, royal register, decimal KHR).
3. CLI commands: lookup, lint, --help in Python and Node.js.
4. Python MCP server (khmer_mcp_server.py) over JSON-RPC stdio.
5. Node.js MCP server (khmer_mcp_server.js) over JSON-RPC stdio.
"""

import json
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import lint_khmer_text, lookup_ui_term


class TestTokenEnhancementsPython(unittest.TestCase):
    def test_lookup_exact_and_partial(self):
        # Exact match
        res_exact = lookup_ui_term("Settings")
        self.assertTrue(len(res_exact) >= 1)
        self.assertEqual(res_exact[0]["key"], "nav.settings")
        self.assertEqual(res_exact[0]["km"], "ការកំណត់")

        # Key match
        res_key = lookup_ui_term("auth.sign_in")
        self.assertTrue(len(res_key) >= 1)
        self.assertEqual(res_key[0]["km"], "ចូលគណនី")

        # Khmer match
        res_km = lookup_ui_term("រក្សាទុក")
        self.assertTrue(len(res_km) >= 1)
        self.assertEqual(res_km[0]["key"], "action.save")

        # Partial match
        res_partial = lookup_ui_term("pass")
        self.assertTrue(len(res_partial) >= 1)

    def test_lint_clean_text(self):
        res = lint_khmer_text("តម្លៃសរុប 10,000៛ ចូលគណនី")
        self.assertTrue(res["is_clean"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["warnings"]), 0)
        self.assertTrue(res["stats"]["total_khmer"] > 0)

    def test_lint_detects_defects(self):
        # Dotted circle
        res_dc = lint_khmer_text("កា\u25CCរ")
        self.assertFalse(res_dc["is_clean"])
        self.assertTrue(any("dotted circle" in w.lower() for w in res_dc["warnings"]))

        # Trailing Coeng
        res_coeng = lint_khmer_text("សង្កាត់្")
        self.assertFalse(res_coeng["is_clean"])
        self.assertTrue(any("trailing coeng" in w.lower() for w in res_coeng["warnings"]))

        # Inverted word order
        res_order = lint_khmer_text("សូមបង់ប្រាក់ សរុបតម្លៃ")
        self.assertFalse(res_order["is_clean"])
        self.assertTrue(any("inverted word order" in w.lower() for w in res_order["warnings"]))

        # Royal register
        res_royal = lint_khmer_text("សូមយាងចូលក្នុងប្រព័ន្ធ")
        self.assertFalse(res_royal["is_clean"])
        self.assertTrue(any("royal" in w.lower() for w in res_royal["warnings"]))

        # Decimal KHR
        res_khr = lint_khmer_text("តម្លៃ 25.50៛")
        self.assertFalse(res_khr["is_clean"])
        self.assertTrue(any("khr" in w.lower() or "decimal" in w.lower() for w in res_khr["warnings"]))


class TestTokenEnhancementsCli(unittest.TestCase):
    def test_python_cli_lookup_and_lint(self):
        # Python CLI lookup
        proc_lookup = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, "scripts", "khmer_utils.py"), "lookup", "Settings"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc_lookup.stdout)
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]["key"], "nav.settings")

        # Python CLI lint clean
        proc_lint_clean = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, "scripts", "khmer_utils.py"), "lint", "តម្លៃសរុប 10,000៛"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_lint_clean.returncode, 0)

        # Python CLI lint warning returns exit code 1
        proc_lint_warn = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, "scripts", "khmer_utils.py"), "lint", "សរុបតម្លៃ 25.50៛"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_lint_warn.returncode, 1)

    def test_node_cli_help_lookup_lint(self):
        node_script = os.path.join(REPO_ROOT, "scripts", "khmer_utils.js")

        # Node CLI --help exits 0
        proc_help = subprocess.run(["node", node_script, "--help"], capture_output=True, text=True)
        self.assertEqual(proc_help.returncode, 0)
        self.assertIn("khmer-utils (Node.js)", proc_help.stdout)

        # Node CLI lookup
        proc_lookup = subprocess.run(["node", node_script, "lookup", "Save"], capture_output=True, text=True, check=True)
        data = json.loads(proc_lookup.stdout)
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]["key"], "action.save")

        # Node CLI lint clean
        proc_lint = subprocess.run(["node", node_script, "lint", "រក្សាទុក"], capture_output=True, text=True)
        self.assertEqual(proc_lint.returncode, 0)


class TestMcpServers(unittest.TestCase):
    def test_python_mcp_server(self):
        server_py = os.path.join(REPO_ROOT, "scripts", "khmer_mcp_server.py")

        # Initialize
        init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        tools_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        call_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "khmer_spellout_words", "arguments": {"amount": 50000, "currency": "KHR"}},
        })
        input_data = f"{init_req}\n{tools_req}\n{call_req}\n"

        proc = subprocess.run(
            [sys.executable, server_py],
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )

        lines = [json.loads(line) for line in proc.stdout.strip().split("\n") if line.strip()]
        self.assertEqual(len(lines), 3)

        # Verify tools/list
        tools = lines[1]["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("khmer_lookup_term", tool_names)
        self.assertIn("khmer_normalize_phone", tool_names)
        self.assertIn("khmer_format_currency", tool_names)
        self.assertIn("khmer_spellout_words", tool_names)
        self.assertIn("khmer_lint_text", tool_names)

        # Verify tools/call result
        call_res = json.loads(lines[2]["result"]["content"][0]["text"])
        self.assertIn("ប្រាំម៉ឺនរៀលគត់", call_res["words"])

    def test_node_mcp_server(self):
        server_js = os.path.join(REPO_ROOT, "scripts", "khmer_mcp_server.js")

        init_req = json.dumps({"jsonrpc": "2.0", "id": 10, "method": "initialize"})
        call_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "khmer_normalize_phone", "arguments": {"phone": "012 889 977"}},
        })
        input_data = f"{init_req}\n{call_req}\n"

        proc = subprocess.run(
            ["node", server_js],
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )

        lines = [json.loads(line) for line in proc.stdout.strip().split("\n") if line.strip()]
        self.assertEqual(len(lines), 2)
        phone_res = json.loads(lines[1]["result"]["content"][0]["text"])
        self.assertEqual(phone_res["normalized_e164"], "+85512889977")
        self.assertTrue(phone_res["is_valid_syntax"])


if __name__ == "__main__":
    unittest.main()
