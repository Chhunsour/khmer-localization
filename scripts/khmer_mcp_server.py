#!/usr/bin/env python3
"""
khmer_mcp_server.py - Model Context Protocol (MCP) Server for Khmer Localization

Provides high-efficiency, zero-hallucination MCP tools for AI coding agents
(Claude Code, Cursor, Antigravity, Windsurf, Copilot, etc.) over JSON-RPC stdio.

Tools:
- khmer_lookup_term: Search standardized Khmer UI terminology without reading huge catalogs.
- khmer_normalize_phone: Normalize Cambodian phone numbers (+855 / domestic).
- khmer_format_currency: Format KHR (whole riel) and USD amounts.
- khmer_spellout_words: Convert amounts to official Khmer spelled-out words for invoices.
- khmer_khqr_crc: Compute/verify Bakong KHQR EMVCo CRC16 checksums.
- khmer_lint_text: Fast static text linter for Unicode corruption, dotted circles, and register.
- khmer_sort_words: Sort Khmer words per Chuon Nath dictionary order.

Zero external dependencies. Compatible with Python 3.10+.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import (
    calculate_khqr_crc16,
    format_currency_khmer_words,
    format_khr,
    format_usd,
    integer_to_khmer_words,
    lint_khmer_text,
    lookup_ui_term,
    normalize_cambodian_phone,
    sort_khmer_words,
    verify_khqr,
)

SERVER_NAME = "khmer-localization"
SERVER_VERSION = "2.1.0"

TOOLS = [
    {
        "name": "khmer_lookup_term",
        "description": "Look up standardized Khmer UI terms from the 100+ vetted catalog to avoid hallucinations and inconsistent translations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term in English, Khmer, or key (e.g. 'Settings', 'Save', 'Log Out', 'auth.sign_in')",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "khmer_normalize_phone",
        "description": "Normalize a Cambodian phone number into ITU-T E.164 (+855) and domestic trunk formats with operator/type detection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string",
                    "description": "Raw Cambodian phone string (e.g. '012 345 678', '+855 23 210 022', '0971234567')",
                }
            },
            "required": ["phone"],
        },
    },
    {
        "name": "khmer_format_currency",
        "description": "Format currency amounts following Cambodian banking rules (whole-riel integers for KHR, 2 decimals for USD).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Numeric amount to format"},
                "currency": {"type": "string", "enum": ["KHR", "USD"], "default": "KHR", "description": "Currency code"},
            },
            "required": ["amount"],
        },
    },
    {
        "name": "khmer_spellout_words",
        "description": "Convert an integer or monetary amount into formal Khmer spelled-out words for official receipts, invoices, and GDT tax compliance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount or integer to spell out"},
                "currency": {"type": "string", "enum": ["KHR", "USD", "NONE"], "default": "KHR", "description": "Currency suffix"},
            },
            "required": ["amount"],
        },
    },
    {
        "name": "khmer_khqr_crc",
        "description": "Compute or verify EMVCo CRC16 checksum for NBC Bakong KHQR payment payloads.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "string",
                    "description": "KHQR payload (either ending with '6304' to compute CRC, or full string to verify)",
                }
            },
            "required": ["payload"],
        },
    },
    {
        "name": "khmer_lint_text",
        "description": "Fast static linting of Khmer text for Unicode corruption, dotted circles (U+25CC), trailing Coeng, royal register words, and decimal KHR bugs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Khmer string to lint"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "khmer_sort_words",
        "description": "Sort a list of Khmer words according to the official Chuon Nath dictionary order.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "words": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Khmer words to sort",
                }
            },
            "required": ["words"],
        },
    },
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    if name == "khmer_lookup_term":
        query = arguments.get("query", "")
        return lookup_ui_term(query)

    if name == "khmer_normalize_phone":
        phone = arguments.get("phone", "")
        return normalize_cambodian_phone(phone)

    if name == "khmer_format_currency":
        amount = float(arguments.get("amount", 0))
        currency = arguments.get("currency", "KHR").upper()
        if currency == "KHR":
            return {"formatted": format_khr(amount, whole_riel=True), "currency": "KHR", "amount": amount}
        return {"formatted": format_usd(amount), "currency": "USD", "amount": amount}

    if name == "khmer_spellout_words":
        amount = float(arguments.get("amount", 0))
        currency = arguments.get("currency", "KHR").upper()
        if currency == "NONE":
            return {"words": integer_to_khmer_words(int(amount)), "amount": amount}
        return {"words": format_currency_khmer_words(amount, currency), "currency": currency, "amount": amount}

    if name == "khmer_khqr_crc":
        payload = arguments.get("payload", "")
        if payload.endswith("6304"):
            crc = calculate_khqr_crc16(payload)
            return {"computed_crc": crc, "full_khqr": payload + crc}
        is_valid = verify_khqr(payload)
        return {"is_valid": is_valid, "payload": payload}

    if name == "khmer_lint_text":
        text = arguments.get("text", "")
        return lint_khmer_text(text)

    if name == "khmer_sort_words":
        words = arguments.get("words", [])
        return {"sorted": sort_khmer_words(words)}

    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "capabilities": {"tools": {}},
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS},
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result_data = handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, indent=2, ensure_ascii=False),
                            }
                        ]
                    },
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)},
                }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    main()
