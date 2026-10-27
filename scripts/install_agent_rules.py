#!/usr/bin/env python3
"""
install_agent_rules.py - Automated Agent System Prompt & Rule Installer

Installs pre-tuned, token-efficient Khmer localization guardrails and rules directly
into project configuration files for AI coding agents:
- Cursor (.cursorrules or .cursor/rules/khmer-localization.mdc)
- Claude Code (CLAUDE.md)
- Windsurf (.windsurfrules)
- GitHub Copilot (.github/copilot-instructions.md)
- Google Gemini CLI / Antigravity (GEMINI.md)
- Universal Agent Standard (AGENTS.md)

Zero external dependencies. Compatible with Python 3.10+.
"""

import argparse
import os
import sys
from typing import Dict, List, Optional

RULES_BY_TIER: Dict[str, str] = {
    "nano": """### Khmer Localization Guardrails (Nano Tier)
- Word Order: Strict [Noun] + [Adjective] (e.g. 'តម្លៃសរុប' Total Price, never 'សរុបតម្លៃ').
- Currency: Khmer Riel (KHR / ៛) uses whole-riel integers only—never output .00 decimal cents.
- Register: Professional modern digital tone. Never use royal vocabulary (no យាង, សោយ, ព្រះរាជ, និមន្ត).
- Truncation: Never slice raw UTF-16 code units; use Intl.Segmenter(..., { granularity: 'grapheme' }) to avoid orphan subscripts (Coeng).
- Typography: Set CSS line-height >= 1.6 to prevent diacritic and stacked subscript clipping.
""",
    "standard": """### Khmer (ភាសាខ្មែរ) Engineering & Localization Guardrails (Standard Tier)
1. Register & Tone: Standard modern digital Khmer. Avoid royal/monastic register (no យាង, សោយ, ព្រះរាជ, និមន្ត). Use direct natural phrasing (e.g. "Settings" -> "ការកំណត់", "Save" -> "រក្សាទុក", "Search" -> "ស្វែងរក").
2. Word Order: Strictly [Noun] + [Adjective] (e.g. "Active Users" -> "អ្នកប្រើប្រាស់សកម្ម", "New Password" -> "ពាក្យសម្ងាត់ថ្មី").
3. Currency: KHR uses comma thousand separators without decimals (10,000 រៀល). Dual currency displays both USD ($2.50) and KHR (10,000 ៛).
4. Phone Numbers: Cambodian phone format is 8-9 digits NSN (+855 or domestic 0...). Always normalize to E.164 (+855...) for database storage.
5. Unicode Safety: Never split strings between base consonants and subscript signs (Coeng U+17D2). Use grapheme cluster segmentation for UI truncation. Do not remove Zero-Width Space (U+200B).
6. Typography & Layout: Ensure minimum CSS line-height >= 1.6 on all Khmer text elements to prevent vertical clipping of stacked subscripts.
""",
    "enterprise": """### Khmer Fintech & Digital Commerce Guardrails (Enterprise Tier)
- Regulatory Context: National Bank of Cambodia (NBC) and Bakong standards.
- Currency Rules:
  * Khmer Riel (KHR / ៛): Whole integers only. Decimals (tiens/sen) do not exist in circulation. Format: "125,000 ៛" or "125,000 KHR".
  * US Dollar (USD / $): Standard 2 decimal places ($12.50).
  * In formal receipts, provide spelled-out Khmer words (e.g. "មួយម៉ឺនរៀលគត់" for 10,000 KHR).
- KHQR Specifications:
  * QR Code standard: EMVCo merchant-presented QR code with CRC16-CCITT (polynomial 0x1021, initial 0xFFFF).
  * Payload Tag 53 currency codes: "116" for KHR, "840" for USD.
  * Tag 54 amount: KHR must not have decimal fraction; USD must have two decimals.
- Date & Calendar Systems:
  * Civil Standard: Gregorian calendar with Khmer localized solar month names (មករា, កុម្ភៈ, ...).
  * Buddhist Era (ព.ស.): Gregorian Year + 543 (e.g. 2026 CE -> 2569 BE).
- Phrasing & Terminology Standards:
  * "Transfer" -> "ផ្ទេរប្រាក់" | "Account Balance" -> "សមតុល្យគណនី"
  * "Transaction History" -> "ប្រវត្តិប្រតិបត្តិការ"
  * "Successful" -> "ជោគជ័យ" | "Failed" -> "បរាជ័យ"
- Typography & Layout:
  * Enforce CSS line-height >= 1.6 for Khmer text elements to prevent subscript clipping (Coeng U+17D2).
  * Recommended fonts: 'Kantumruy Pro', 'Hanuman', 'Noto Sans Khmer', system-ui.
""",
}

TARGET_FILES: Dict[str, str] = {
    "cursor": ".cursorrules",
    "cursor-mdc": ".cursor/rules/khmer-localization.mdc",
    "claude": "CLAUDE.md",
    "windsurf": ".windsurfrules",
    "copilot": ".github/copilot-instructions.md",
    "gemini": "GEMINI.md",
    "agents": "AGENTS.md",
}


def install_rules(
    target: str = "cursor",
    tier: str = "standard",
    dest_dir: str = ".",
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, str]:
    """
    Install rules for the specified target and tier into dest_dir.
    Returns a dict mapping relative file path to status ("created", "appended", "skipped").
    """
    if tier not in RULES_BY_TIER:
        raise ValueError(f"Unknown tier: {tier}. Choices: {list(RULES_BY_TIER.keys())}")

    rule_content = RULES_BY_TIER[tier]
    results: Dict[str, str] = {}

    targets_to_run = list(TARGET_FILES.keys()) if target == "all" else [target]

    for t in targets_to_run:
        if t not in TARGET_FILES:
            continue
        rel_path = TARGET_FILES[t]
        full_path = os.path.join(dest_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True) if os.path.dirname(full_path) else None

        if t == "cursor-mdc":
            mdc_header = "---\ndescription: Production Khmer localization guardrails\nglobs: [\"**/*.{ts,tsx,js,jsx,json,vue,svelte,py}\"]\n---\n\n"
            content_to_write = mdc_header + rule_content
        else:
            content_to_write = rule_content

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                existing_text = f.read()

            if ("Khmer" in existing_text and "Localization" in existing_text) and not force:
                results[rel_path] = "skipped (already present)"
                continue

            if not dry_run:
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write("\n\n" + content_to_write)
            results[rel_path] = "appended"
        else:
            if not dry_run:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content_to_write)
            results[rel_path] = "created"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="install_agent_rules.py",
        description="Install token-efficient Khmer localization guardrails into AI coding agent configs.",
    )
    parser.add_argument(
        "--target",
        default="cursor",
        choices=["cursor", "cursor-mdc", "claude", "windsurf", "copilot", "gemini", "agents", "all"],
        help="Target AI agent configuration to install (default: cursor)",
    )
    parser.add_argument(
        "--tier",
        default="standard",
        choices=["nano", "standard", "enterprise"],
        help="Token optimization tier: nano (45t), standard (120t), enterprise (250t) (default: standard)",
    )
    parser.add_argument(
        "--dest",
        default=".",
        help="Destination directory for configuration files (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite or re-append even if Khmer rules already exist in target file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate installation without writing files to disk",
    )

    args = parser.parse_args()
    results = install_rules(
        target=args.target,
        tier=args.tier,
        dest_dir=args.dest,
        force=args.force,
        dry_run=args.dry_run,
    )

    print("Khmer Localization Agent Rules Installation Report:")
    for path, status in results.items():
        prefix = "[DRY-RUN] " if args.dry_run else ""
        print(f"  {prefix}{path}: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
