#!/usr/bin/env python3
"""
audit_khmer_i18n.py - Automated Khmer Localization Quality & Audit Engine

Inspects codebases and translation files for:
1. Missing, orphaned, and untranslated i18n keys.
2. Placeholder & interpolation mismatches ({name}, {{user}}, %s).
3. Prohibited royal/monastic register terms (Reachasap) in UI copy.
4. Inverted grammatical word order (e.g. [Adj] + [Noun] hallucinations).
5. Currency formatting bugs (fractional KHR riel .00 decimals).
6. Hardcoded Khmer strings outside translation functions in source code.
7. Unsafe string slicing and destructive whitespace regexes.
8. Visual text overflow risks on narrow viewports.

Categorizes findings across 4 governance layers:
- [AUTOMATED_ERROR / WARNING]: Deterministically verified software defects.
- [HUMAN_REVIEW_REQUIRED]: Stylistic, cultural, or domain-specific nuances.
- [VISUAL_INSPECTION_REQUIRED]: Layout clearance, line-height, and clipping risks.
- [EXTERNAL_VERIFICATION_REQUIRED]: Live banking, KHQR, and regulatory merchant auth.

Zero external dependencies. Compatible with Python 3.10+.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


# Prohibited royal/monastic words in modern digital tech UI
PROHIBITED_ROYAL_TERMS = ["យាង", "សោយ", "ព្រះរាជ", "ទ្រង់", "សោយទិវង្គត", "និមន្ត", "ឆាន់"]

# Inverted word order red-flag pairs (Common LLM hallucination patterns)
INVERTED_WORD_PATTERNS = [
    (r"សរុបតម្លៃ", "តម្លៃសរុប (Total Price: Noun + Adjective)"),
    (r"ថ្មីពាក្យសម្ងាត់", "ពាក្យសម្ងាត់ថ្មី (New Password: Noun + Adjective)"),
    (r"ចាស់ពាក្យសម្ងាត់", "ពាក្យសម្ងាត់ចាស់ (Old Password: Noun + Adjective)"),
    (r"សកម្មអ្នកប្រើប្រាស់", "អ្នកប្រើប្រាស់សកម្ម (Active Users: Noun + Adjective)"),
]


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, str]:
    """Flatten a nested dictionary into a single-level dictionary with dot notation."""
    items: List[Tuple[str, str]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, (str, int, float, bool)):
            items.append((new_key, str(v)))
    return dict(items)


def extract_placeholders(text: str) -> Set[str]:
    """Extract placeholders like {name}, {{user}}, %s, {0}, :count."""
    patterns = [
        r"\{\{([a-zA-Z0-9_]+)\}\}",   # {{user}}
        r"\{([a-zA-Z0-9_]+)\}",       # {name}
        r":([a-zA-Z0-9_]+)",          # :count
        r"%(?:[0-9]+\$)?[sdif]",       # %s, %d, %1$s
    ]
    found = set()
    for p in patterns:
        for m in re.finditer(p, text):
            found.add(m.group(0))
    return found


def audit_locale_files(
    locales_dir: str,
    base_locale: str = "en",
    target_locale: str = "km",
) -> List[Dict[str, Any]]:
    """Audit translation JSON files for missing keys, placeholders, royal register, and decimals."""
    findings: List[Dict[str, Any]] = []

    if not os.path.isdir(locales_dir):
        return findings

    base_file = None
    target_file = None

    # Search for base and target locale files
    for fname in os.listdir(locales_dir):
        lower = fname.lower()
        if lower in (f"{base_locale}.json", f"{base_locale}-us.json", f"{base_locale}-gb.json"):
            base_file = os.path.join(locales_dir, fname)
        elif lower in (f"{target_locale}.json", f"{target_locale}-kh.json"):
            target_file = os.path.join(locales_dir, fname)

    if not base_file or not target_file:
        return findings

    try:
        with open(base_file, "r", encoding="utf-8") as f:
            base_data = flatten_dict(json.load(f))
    except Exception as e:
        findings.append({
            "layer": "AUTOMATED_ERROR",
            "file": base_file,
            "key": None,
            "rule": "BASE_LOCALE_PARSE_ERROR",
            "message": f"Failed to parse base locale file: {str(e)}",
        })
        return findings

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            target_data = flatten_dict(json.load(f))
    except Exception as e:
        findings.append({
            "layer": "AUTOMATED_ERROR",
            "file": target_file,
            "key": None,
            "rule": "TARGET_LOCALE_PARSE_ERROR",
            "message": f"Failed to parse target locale file: {str(e)}",
        })
        return findings

    base_keys = set(base_data.keys())
    target_keys = set(target_data.keys())

    # 1. Missing keys in target locale
    for missing_k in sorted(base_keys - target_keys):
        findings.append({
            "layer": "AUTOMATED_ERROR",
            "file": target_file,
            "key": missing_k,
            "rule": "MISSING_TRANSLATION_KEY",
            "message": f"Translation key '{missing_k}' is present in {os.path.basename(base_file)} but missing in {os.path.basename(target_file)}.",
        })

    # 2. Orphaned keys in target locale
    for orphan_k in sorted(target_keys - base_keys):
        findings.append({
            "layer": "AUTOMATED_WARNING",
            "file": target_file,
            "key": orphan_k,
            "rule": "ORPHANED_TRANSLATION_KEY",
            "message": f"Translation key '{orphan_k}' exists in {os.path.basename(target_file)} but is absent in {os.path.basename(base_file)}.",
        })

    # 3. Analyze shared keys
    for common_k in sorted(base_keys & target_keys):
        en_val = base_data[common_k].strip()
        km_val = target_data[common_k].strip()

        # Untranslated English copy in target file
        if km_val == en_val and len(en_val) > 3 and re.search(r"[a-zA-Z]{3,}", en_val):
            findings.append({
                "layer": "AUTOMATED_WARNING",
                "file": target_file,
                "key": common_k,
                "rule": "UNTRANSLATED_STRING",
                "message": f"Key '{common_k}' has identical English text in {os.path.basename(target_file)}: '{km_val}'",
            })

        # Placeholder mismatches
        en_ph = extract_placeholders(en_val)
        km_ph = extract_placeholders(km_val)
        if en_ph != km_ph:
            missing_ph = en_ph - km_ph
            extra_ph = km_ph - en_ph
            findings.append({
                "layer": "AUTOMATED_ERROR",
                "file": target_file,
                "key": common_k,
                "rule": "PLACEHOLDER_MISMATCH",
                "message": f"Key '{common_k}' placeholder mismatch. English: {list(en_ph)}, Khmer: {list(km_ph)}. Missing: {list(missing_ph)}, Extra: {list(extra_ph)}",
            })

        # Royal / Monastic register words
        for royal in PROHIBITED_ROYAL_TERMS:
            if royal in km_val:
                findings.append({
                    "layer": "AUTOMATED_ERROR",
                    "file": target_file,
                    "key": common_k,
                    "rule": "ROYAL_REGISTER_DETECTED",
                    "message": f"Key '{common_k}' contains royal/monastic term '{royal}'. Standard digital UI requires neutral tech terms.",
                })

        # Inverted word order patterns
        for pattern, recommendation in INVERTED_WORD_PATTERNS:
            if re.search(pattern, km_val):
                findings.append({
                    "layer": "AUTOMATED_WARNING",
                    "file": target_file,
                    "key": common_k,
                    "rule": "INVERTED_WORD_ORDER",
                    "message": f"Key '{common_k}' contains likely inverted word order '{re.search(pattern, km_val).group(0)}'. Recommended: {recommendation}",
                })

        # Fractional Riel decimal check (.00 on riel amounts)
        if re.search(r"\d+\.\d{2}\s*៛|\d+\.\d{2}\s*KHR", km_val, re.IGNORECASE):
            findings.append({
                "layer": "AUTOMATED_ERROR",
                "file": target_file,
                "key": common_k,
                "rule": "DECIMAL_RIEL_DETECTED",
                "message": f"Key '{common_k}' contains KHR with decimal places ('{km_val}'). Cambodian Riel does not use cents/decimals.",
            })

        # Trailing Coeng or orphaned combining mark in translation string
        if km_val.endswith("\u17D2"):
            findings.append({
                "layer": "AUTOMATED_ERROR",
                "file": target_file,
                "key": common_k,
                "rule": "TRAILING_COENG_DETECTED",
                "message": f"Key '{common_k}' ends with trailing Coeng U+17D2, which triggers a broken dotted circle defect.",
            })

    return findings


def audit_source_code(src_dir: str) -> List[Dict[str, Any]]:
    """Audit application source files (.ts, .tsx, .js, .jsx, .vue, .py, .html) for hardcoded UI text and traps."""
    findings: List[Dict[str, Any]] = []

    if not os.path.isdir(src_dir):
        return findings

    valid_exts = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".html", ".py"}
    ignored_dirs = {"node_modules", ".git", "dist", "build", ".next", "venv", "__pycache__"}

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in valid_exts:
                continue

            filepath = os.path.join(root, f)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except Exception:
                continue

            for line_no, line in enumerate(lines, start=1):
                # 1. Hardcoded Khmer string in JSX / HTML / code outside translation calls
                # Detect lines with Khmer characters (U+1780 to U+17FF)
                khmer_chars = [c for c in line if 0x1780 <= ord(c) <= 0x17FF]
                if khmer_chars:
                    # Check if line calls translation helper (t('...'), i18n, Trans, etc.)
                    is_translated_call = bool(re.search(r"\b(t|translate|\$t|formatMessage|i18n\.t)\s*\(", line))
                    is_comment = line.strip().startswith("//") or line.strip().startswith("#") or line.strip().startswith("/*")
                    if not is_translated_call and not is_comment:
                        findings.append({
                            "layer": "AUTOMATED_WARNING",
                            "file": filepath,
                            "line": line_no,
                            "rule": "HARDCODED_KHMER_STRING",
                            "message": f"Hardcoded Khmer text found outside translation function: '{line.strip()[:60]}...'",
                        })

                # 2. Hardcoded currency string concatenation: e.g. amount + "៛" or "$" + amount
                if re.search(r"(\+\s*['\"]\s*៛['\"]|\+\s*['\"]\s*KHR['\"]|['\"]\$\s*['\"]\s*\+)", line):
                    findings.append({
                        "layer": "AUTOMATED_WARNING",
                        "file": filepath,
                        "line": line_no,
                        "rule": "HARDCODED_CURRENCY_CONCAT",
                        "message": f"Manual currency symbol concatenation detected: '{line.strip()[:60]}...'. Use Intl.NumberFormat or formatKHR/formatUSD.",
                    })

                # 3. Destructive whitespace regex that deletes ZWSP \u200B
                if re.search(r"\.replace\(\s*/\\s\+/g\s*,\s*['\"]['\"]\s*\)", line):
                    findings.append({
                        "layer": "AUTOMATED_WARNING",
                        "file": filepath,
                        "line": line_no,
                        "rule": "DESTRUCTIVE_WHITESPACE_REGEX",
                        "message": f"Regex `replace(/\\s+/g, '')` strips Zero-Width Spaces (\\u200B). Preserve ZWSP for Khmer typography.",
                    })

                # 4. Naive string slicing on variables likely holding localized strings
                if re.search(r"\.(slice|substring)\(\s*0\s*,\s*\d+\s*\)", line) and ("khmer" in line.lower() or "text" in line.lower() or "title" in line.lower()):
                    findings.append({
                        "layer": "AUTOMATED_WARNING",
                        "file": filepath,
                        "line": line_no,
                        "rule": "UNSAFE_STRING_SLICING",
                        "message": f"Naive string slicing detected on text variable: '{line.strip()[:60]}...'. Use safeTruncateKhmer or Intl.Segmenter.",
                    })

                # 5. Mobile Visual Text Overflow Risk: Hardcoded button width with Khmer
                if re.search(r"(w-\[|width:\s*\d+px).*?(Button|<button)", line, re.IGNORECASE) and khmer_chars:
                    findings.append({
                        "layer": "VISUAL_INSPECTION_REQUIRED",
                        "file": filepath,
                        "line": line_no,
                        "rule": "FIXED_WIDTH_BUTTON_OVERFLOW",
                        "message": f"Fixed-width button element containing Khmer script may clip or wrap awkwardly on mobile viewports.",
                    })

    return findings


def run_full_audit(
    root_dir: str,
    locales_dir: Optional[str] = None,
    src_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute complete multi-layer audit over an application codebase."""
    # Autodetect locales directory if not specified
    if not locales_dir:
        candidates = [
            os.path.join(root_dir, "locales"),
            os.path.join(root_dir, "src", "locales"),
            os.path.join(root_dir, "public", "locales"),
            os.path.join(root_dir, "lang"),
            os.path.join(root_dir, "i18n"),
        ]
        for c in candidates:
            if os.path.isdir(c):
                locales_dir = c
                break

    # Autodetect src directory if not specified
    if not src_dir:
        candidates = [
            os.path.join(root_dir, "src"),
            os.path.join(root_dir, "app"),
            os.path.join(root_dir, "components"),
            root_dir,
        ]
        for c in candidates:
            if os.path.isdir(c) and c != root_dir:
                src_dir = c
                break
        if not src_dir:
            src_dir = root_dir

    findings: List[Dict[str, Any]] = []

    if locales_dir and os.path.isdir(locales_dir):
        findings.extend(audit_locale_files(locales_dir))

    if src_dir and os.path.isdir(src_dir):
        findings.extend(audit_source_code(src_dir))

    # Add standard external and human review requirements
    findings.append({
        "layer": "HUMAN_REVIEW_REQUIRED",
        "file": locales_dir or root_dir,
        "rule": "NATIVE_SPEAKER_TONE_REVIEW",
        "message": "Verify tone of voice matches brand expectations (conversational vs formal). Confirm technical translations with a native speaker.",
    })
    findings.append({
        "layer": "VISUAL_INSPECTION_REQUIRED",
        "file": src_dir or root_dir,
        "rule": "MOBILE_VIEWPORT_CLIPPING_CHECK",
        "message": "Verify rendering on 320px–390px viewports (iPhone SE / Android) for stacked vowel clipping and multi-line button wraps.",
    })
    findings.append({
        "layer": "EXTERNAL_VERIFICATION_REQUIRED",
        "file": root_dir,
        "rule": "PAYMENT_GATEWAY_CREDENTIAL_CHECK",
        "message": "Verifying KHQR payloads locally does NOT confirm merchant account validity or payment settlement. Test with Bakong sandbox/production APIs.",
    })

    # Tally counts by layer
    errors_count = sum(1 for f in findings if f["layer"] == "AUTOMATED_ERROR")
    warnings_count = sum(1 for f in findings if f["layer"] == "AUTOMATED_WARNING")
    human_count = sum(1 for f in findings if f["layer"] == "HUMAN_REVIEW_REQUIRED")
    visual_count = sum(1 for f in findings if f["layer"] == "VISUAL_INSPECTION_REQUIRED")
    external_count = sum(1 for f in findings if f["layer"] == "EXTERNAL_VERIFICATION_REQUIRED")

    status = "PASS" if errors_count == 0 else "FAIL"

    return {
        "status": status,
        "locales_dir": locales_dir,
        "src_dir": src_dir,
        "summary": {
            "automated_errors": errors_count,
            "automated_warnings": warnings_count,
            "human_review_required": human_count,
            "visual_inspection_required": visual_count,
            "external_verification_required": external_count,
            "total_findings": len(findings),
        },
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="audit_khmer_i18n.py",
        description="Automated Khmer Localization Quality & Audit Engine",
    )
    parser.add_argument("path", nargs="?", default=".", help="Root path of the application to audit")
    parser.add_argument("--locales", dest="locales_dir", default=None, help="Path to translation JSON locales directory")
    parser.add_argument("--src", dest="src_dir", default=None, help="Path to application source code directory")
    parser.add_argument("--strict", action="store_true", help="Exit code 1 on errors or warnings")
    parser.add_argument("--json", action="store_true", help="Output audit report as structured JSON")

    args = parser.parse_args()

    report = run_full_audit(args.path, locales_dir=args.locales_dir, src_dir=args.src_dir)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 80)
        print(" KHMER LOCALIZATION QUALITY & AUDIT REPORT")
        print("=" * 80)
        print(f"Target Project   : {os.path.abspath(args.path)}")
        print(f"Locales Directory: {report['locales_dir'] or 'Not detected'}")
        print(f"Source Directory : {report['src_dir'] or 'Not detected'}")
        print(f"Overall Status   : {report['status']}")
        print("-" * 80)
        print(f"Automated Errors               : {report['summary']['automated_errors']}")
        print(f"Automated Warnings             : {report['summary']['automated_warnings']}")
        print(f"Human Review Needed            : {report['summary']['human_review_required']}")
        print(f"Visual Device Inspection Needed: {report['summary']['visual_inspection_required']}")
        print(f"External Provider Checks Needed: {report['summary']['external_verification_required']}")
        print("-" * 80)

        for item in report["findings"]:
            prefix = f"[{item['layer']}]"
            loc = f"{os.path.basename(item.get('file', ''))}"
            if "line" in item:
                loc += f":{item['line']}"
            if "key" in item and item["key"]:
                loc += f" ({item['key']})"
            print(f"{prefix:<32} {loc:<30} {item['rule']}")
            print(f"  -> {item['message']}")

        print("=" * 80)

    if args.strict and (report["summary"]["automated_errors"] > 0 or report["summary"]["automated_warnings"] > 0):
        return 1

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
