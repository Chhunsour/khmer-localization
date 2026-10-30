#!/usr/bin/env python3
"""
check_khmer_unicode.py - Khmer Unicode & Encoding Integrity Checker

A static analysis tool designed for internationalization (i18n) and localization (l10n)
workflows. Inspects source and translation files for UTF-8 integrity, corrupted
characters (e.g. U+FFFD), suspicious control characters, orphaned combining marks,
and reports Khmer typography statistics.

Standard Library only: Compatible with Python 3.9+.
Does NOT modify or overwrite files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Supported text file extensions by default
DEFAULT_EXTENSIONS: Set[str] = {
    ".json",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".htm",
    ".css",
    ".po",
    ".pot",
    ".properties",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".vue",
    ".svelte",
    ".xml",
    ".arb",
    ".strings",
    ".stringsdict",
    ".resw",
    ".resx",
}

# Unicode code points & ranges
REPLACEMENT_CHAR = "\uFFFD"  # Unicode Replacement Character (corrupted decoding)
DOTTED_CIRCLE = "\u25CC"     # Dotted circle (shaping engine artifact or broken sequence)

# Khmer Unicode Block: U+1780 - U+17FF
KHMER_START = 0x1780
KHMER_END = 0x17FF

# Khmer Symbols Block: U+19E0 - U+19FF
KHMER_SYMBOLS_START = 0x19E0
KHMER_SYMBOLS_END = 0x19FF

# Khmer Consonants: U+1780 - U+17A2
KHMER_CONSONANTS_START = 0x1780
KHMER_CONSONANTS_END = 0x17A2

# Deprecated Khmer Consonants: U+17A3, U+17A4 (deprecated in Unicode 4.0; use U+17A2 instead)
DEPRECATED_KHMER_CONSONANTS = {"\u17A3", "\u17A4"}

# Independent Vowels: U+17A5 - U+17B3
KHMER_INDEP_VOWELS_START = 0x17A5
KHMER_INDEP_VOWELS_END = 0x17B3

# Dependent Vowel Signs: U+17B6 - U+17C5
KHMER_DEP_VOWELS_START = 0x17B6
KHMER_DEP_VOWELS_END = 0x17C5

# Khmer Diacritics and Signs: U+17C6 - U+17D1, U+17D3
KHMER_SIGNS_START = 0x17C6
KHMER_SIGNS_END = 0x17D3

# Subscript consonant marker (Coeng): U+17D2
KHMER_COENG = "\u17D2"

# Khmer Currency Symbol (Riel): U+17DB (៛)
KHMER_RIEL = "\u17DB"

# Khmer Digits: U+17E0 - U+17E9 (០ - ៩)
KHMER_DIGITS_START = 0x17E0
KHMER_DIGITS_END = 0x17E9

# Legitimate Invisible Typography Characters
ZWSP = "\u200B"   # Zero-Width Space: standard in Khmer for word boundaries
ZWNJ = "\u200C"   # Zero-Width Non-Joiner: prevents ligatures
ZWJ = "\u200D"    # Zero-Width Joiner: contextual ligatures

# Bidirectional overrides (suspicious if unmanaged in localization files)
BIDI_OVERRIDES = {
    "\u202A": "LRE (Left-to-Right Embedding)",
    "\u202B": "RLE (Right-to-Left Embedding)",
    "\u202C": "PDF (Pop Directional Format)",
    "\u202D": "LRO (Left-to-Right Override)",
    "\u202E": "RLO (Right-to-Left Override)",
    "\u2066": "LRI (Left-to-Right Isolate)",
    "\u2067": "RLI (Right-to-Left Isolate)",
    "\u2068": "FSI (First Strong Isolate)",
    "\u2069": "PDI (Pop Directional Isolate)",
}


def is_khmer_char(char: str) -> bool:
    """Check if a character falls within the Khmer or Khmer Symbols Unicode blocks."""
    code = ord(char)
    return (KHMER_START <= code <= KHMER_END) or (KHMER_SYMBOLS_START <= code <= KHMER_SYMBOLS_END)


def is_khmer_combining_mark(char: str) -> bool:
    """Check if a character is a Khmer combining mark (dependent vowel, coeng, diacritic)."""
    code = ord(char)
    if code == 0x17D2:  # Coeng
        return True
    if KHMER_DEP_VOWELS_START <= code <= KHMER_DEP_VOWELS_END:
        return True
    if KHMER_SIGNS_START <= code <= KHMER_SIGNS_END and code != 0x17D2:
        return True
    return False


def is_khmer_base(char: str) -> bool:
    """Check if a character is a valid Khmer base consonant or independent vowel."""
    code = ord(char)
    return (KHMER_CONSONANTS_START <= code <= KHMER_CONSONANTS_END) or (
        KHMER_INDEP_VOWELS_START <= code <= KHMER_INDEP_VOWELS_END
    )


def is_suspicious_control_char(char: str) -> bool:
    """
    Check if a character is a suspicious control character.
    Excludes standard whitespace: horizontal tab (\\t), line feed (\\n), carriage return (\\r).
    """
    code = ord(char)
    # C0 control characters (0x00 to 0x1F, 0x7F) except \t (0x09), \n (0x0A), \r (0x0D)
    if code < 0x20 and code not in (0x09, 0x0A, 0x0D):
        return True
    if code == 0x7F:
        return True
    # C1 control characters (0x80 to 0x9F)
    if 0x80 <= code <= 0x9F:
        return True
    return False


@dataclass
class Issue:
    level: str       # "ERROR" or "WARNING"
    category: str    # "BYTE_ENCODING", "DATA_CORRUPTION", "SUSPICIOUS_CONTROL", "VISUAL_RENDERING", "DEPRECATED_CHAR", "BIDI_OVERRIDE"
    line_number: int
    column_number: int
    message: str
    code_point: Optional[str] = None
    character_name: Optional[str] = None
    line_snippet: Optional[str] = None


@dataclass
class KhmerStats:
    total_khmer_chars: int = 0
    consonants: int = 0
    independent_vowels: int = 0
    dependent_vowels: int = 0
    coeng_subscripts: int = 0
    diacritics: int = 0
    digits: int = 0
    symbols_and_punct: int = 0
    riel_symbols: int = 0
    zero_width_spaces: int = 0
    zero_width_joiners: int = 0


@dataclass
class FileResult:
    path: Path
    has_khmer: bool = False
    stats: KhmerStats = field(default_factory=KhmerStats)
    issues: List[Issue] = field(default_factory=list)
    encoding_error: Optional[str] = None

    @property
    def error_count(self) -> int:
        base = 1 if self.encoding_error else 0
        return base + sum(1 for issue in self.issues if issue.level == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == "WARNING")


class KhmerUnicodeChecker:
    def __init__(
        self,
        extensions: Optional[Set[str]] = None,
        check_trailing_coeng: bool = True,
        check_bidi_overrides: bool = True,
        check_deprecated_chars: bool = True,
        check_orphaned_marks: bool = True,
    ):
        self.extensions = extensions if extensions is not None else DEFAULT_EXTENSIONS
        self.check_trailing_coeng = check_trailing_coeng
        self.check_bidi_overrides = check_bidi_overrides
        self.check_deprecated_chars = check_deprecated_chars
        self.check_orphaned_marks = check_orphaned_marks

    def check_file(self, file_path: Path) -> FileResult:
        result = FileResult(path=file_path)

        # 1. Read binary bytes and attempt UTF-8 decode
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
        except OSError as e:
            result.encoding_error = f"Cannot read file: {e}"
            return result

        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            result.encoding_error = (
                f"Invalid UTF-8 byte sequence at byte {e.start}: {e.reason}. "
                "Ensure the file is saved as UTF-8 without lossy conversions."
            )
            return result

        lines = content.splitlines(keepends=True)
        for line_idx, line in enumerate(lines, start=1):
            self._check_line(line, line_idx, result)

        return result

    def _check_line(self, line: str, line_number: int, result: FileResult) -> None:
        stripped_line = line.rstrip("\r\n")
        line_len = len(line)

        for col_idx, char in enumerate(line, start=1):
            code = ord(char)
            code_hex = f"U+{code:04X}"
            char_name = unicodedata.name(char, "UNKNOWN CHARACTER")

            # Check 1: Replacement character (U+FFFD) - ALWAYS AN ERROR (DATA_CORRUPTION)
            if char == REPLACEMENT_CHAR:
                result.issues.append(
                    Issue(
                        level="ERROR",
                        category="DATA_CORRUPTION",
                        line_number=line_number,
                        column_number=col_idx,
                        message=(
                            "Unicode Replacement Character detected (U+FFFD). "
                            "This indicates corrupted text or lossy character encoding conversion."
                        ),
                        code_point=code_hex,
                        character_name=char_name,
                        line_snippet=stripped_line,
                    )
                )

            # Check 2: Suspicious control characters - ALWAYS AN ERROR (SUSPICIOUS_CONTROL)
            elif is_suspicious_control_char(char):
                result.issues.append(
                    Issue(
                        level="ERROR",
                        category="SUSPICIOUS_CONTROL",
                        line_number=line_number,
                        column_number=col_idx,
                        message=(
                            f"Suspicious control character detected ({code_hex}). "
                            "Raw control codes should not appear in localized text."
                        ),
                        code_point=code_hex,
                        character_name=char_name,
                        line_snippet=stripped_line,
                    )
                )

            # Check 3: Literal Dotted Circle (U+25CC) - WARNING (VISUAL_RENDERING)
            # In UI translations, it often indicates a broken sequence was copy-pasted.
            # In documentation or font tests, it may be used intentionally.
            elif char == DOTTED_CIRCLE:
                result.issues.append(
                    Issue(
                        level="WARNING",
                        category="VISUAL_RENDERING",
                        line_number=line_number,
                        column_number=col_idx,
                        message=(
                            "Literal Dotted Circle detected (U+25CC). "
                            "In localized UI copy, this often occurs when a broken glyph sequence "
                            "with missing base consonant was copy-pasted. Verify whether this is intentional."
                        ),
                        code_point=code_hex,
                        character_name=char_name,
                        line_snippet=stripped_line,
                    )
                )

            # Check 4: Orphaned Combining Marks - WARNING (VISUAL_RENDERING)
            # In Khmer, combining marks (dependent vowels, coeng, diacritics) must attach to a valid
            # base consonant or independent vowel, or follow another legally attached combining mark.
            # If preceded by whitespace, ZWSP (\u200B), punctuation, digits, or start of line, it is orphaned.
            elif self.check_orphaned_marks and is_khmer_combining_mark(char):
                prev_char = line[col_idx - 2] if col_idx > 1 else None
                is_orphaned = False
                if prev_char is None:
                    is_orphaned = True
                elif prev_char == ZWSP:
                    # Combining mark cannot cross a Zero-Width Space word boundary
                    is_orphaned = True
                elif not (is_khmer_base(prev_char) or is_khmer_combining_mark(prev_char)):
                    is_orphaned = True

                if is_orphaned:
                    result.issues.append(
                        Issue(
                            level="WARNING",
                            category="VISUAL_RENDERING",
                            line_number=line_number,
                            column_number=col_idx,
                            message=(
                                f"Orphaned Khmer combining mark detected: {char_name} ({code_hex}). "
                                "Combining marks must attach to a Khmer base consonant or vowel; "
                                "rendering engines will display a broken dotted circle (U+25CC)."
                            ),
                            code_point=code_hex,
                            character_name=char_name,
                            line_snippet=stripped_line,
                        )
                    )

            # Check 5: Trailing Coeng or Double Coeng - WARNING/ERROR (VISUAL_RENDERING)
            # U+17D2 (Coeng) must be immediately followed by a subscript consonant or sign.
            if self.check_trailing_coeng and char == KHMER_COENG:
                next_char = line[col_idx] if col_idx < line_len else None
                if next_char == KHMER_COENG:
                    result.issues.append(
                        Issue(
                            level="ERROR",
                            category="VISUAL_RENDERING",
                            line_number=line_number,
                            column_number=col_idx,
                            message=(
                                "Illegal double Coeng sequence (U+17D2 U+17D2) detected. "
                                "Khmer script cannot contain consecutive subscript markers; "
                                "this causes broken rendering or crash in OpenType font engines."
                            ),
                            code_point=code_hex,
                            character_name=char_name,
                            line_snippet=stripped_line,
                        )
                    )
                elif next_char is None or next_char in (" ", "\t", "\n", "\r", '"', "'", ",", ".", ";", ":", ZWSP):
                    result.issues.append(
                        Issue(
                            level="WARNING",
                            category="VISUAL_RENDERING",
                            line_number=line_number,
                            column_number=col_idx,
                            message=(
                                "Trailing Khmer Coeng (subscript marker U+17D2) detected without "
                                "a following subscript consonant. This results in incomplete syllable shaping."
                            ),
                            code_point=code_hex,
                            character_name=char_name,
                            line_snippet=stripped_line,
                        )
                    )

            # Check 6: Suspicious Bidirectional Overrides - WARNING (BIDI_OVERRIDE)
            elif self.check_bidi_overrides and char in BIDI_OVERRIDES:
                desc = BIDI_OVERRIDES[char]
                result.issues.append(
                    Issue(
                        level="WARNING",
                        category="BIDI_OVERRIDE",
                        line_number=line_number,
                        column_number=col_idx,
                        message=(
                            f"Bidirectional override character detected: {desc} ({code_hex}). "
                            "Verify that bidirectional embedding is intentional and properly paired."
                        ),
                        code_point=code_hex,
                        character_name=char_name,
                        line_snippet=stripped_line,
                    )
                )

            # Check 7: Deprecated Khmer characters - WARNING (DEPRECATED_CHAR)
            elif self.check_deprecated_chars and char in DEPRECATED_KHMER_CONSONANTS:
                result.issues.append(
                    Issue(
                        level="WARNING",
                        category="DEPRECATED_CHAR",
                        line_number=line_number,
                        column_number=col_idx,
                        message=(
                            f"Deprecated Khmer character detected: {char_name} ({code_hex}). "
                            "Deprecated in Unicode 4.0; use U+17A2 (Khmer Letter QA) instead."
                        ),
                        code_point=code_hex,
                        character_name=char_name,
                        line_snippet=stripped_line,
                    )
                )

            # Statistics & Khmer tracking
            if is_khmer_char(char):
                result.has_khmer = True
                stats = result.stats
                stats.total_khmer_chars += 1

                if KHMER_CONSONANTS_START <= code <= KHMER_CONSONANTS_END:
                    stats.consonants += 1
                elif KHMER_INDEP_VOWELS_START <= code <= KHMER_INDEP_VOWELS_END:
                    stats.independent_vowels += 1
                elif KHMER_DEP_VOWELS_START <= code <= KHMER_DEP_VOWELS_END:
                    stats.dependent_vowels += 1
                elif code == 0x17D2:
                    stats.coeng_subscripts += 1
                elif KHMER_SIGNS_START <= code <= KHMER_SIGNS_END:
                    stats.diacritics += 1
                elif KHMER_DIGITS_START <= code <= KHMER_DIGITS_END:
                    stats.digits += 1
                elif char == KHMER_RIEL:
                    stats.symbols_and_punct += 1
                    stats.riel_symbols += 1
                else:
                    stats.symbols_and_punct += 1

            # Legitimate invisible typography characters
            if char == ZWSP:
                result.stats.zero_width_spaces += 1
            elif char in (ZWJ, ZWNJ):
                result.stats.zero_width_joiners += 1

    def scan_path(self, target: Path) -> List[FileResult]:
        """Scan a file or recursively scan a directory for supported text files."""
        results: List[FileResult] = []

        if target.is_file():
            results.append(self.check_file(target))
        elif target.is_dir():
            for root, dirs, files in os.walk(target):
                # Skip hidden directories like .git, node_modules, .venv, __pycache__
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith(".") and d not in ("node_modules", "vendor", "__pycache__", "build", "dist")
                ]
                for filename in sorted(files):
                    file_path = Path(root) / filename
                    if file_path.suffix.lower() in self.extensions:
                        results.append(self.check_file(file_path))

        return results


def format_text_report(results: List[FileResult], verbose: bool = False, show_stats: bool = True) -> Tuple[str, int, int]:
    """Format file results into human-readable text report."""
    output: List[str] = []
    total_files = len(results)
    files_with_khmer = sum(1 for r in results if r.has_khmer)
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    total_khmer_chars = sum(r.stats.total_khmer_chars for r in results)
    total_zwsps = sum(r.stats.zero_width_spaces for r in results)

    output.append("=" * 72)
    output.append(" KHMER UNICODE & ENCODING INTEGRITY REPORT")
    output.append("=" * 72)

    has_reported_file = False

    for r in results:
        if r.encoding_error:
            has_reported_file = True
            output.append(f"\n[FAIL] {r.path}")
            output.append(f"  ERROR [BYTE_ENCODING]: {r.encoding_error}")
        elif r.issues:
            has_reported_file = True
            status = "FAIL" if r.error_count > 0 else "WARN"
            output.append(f"\n[{status}] {r.path}")
            for issue in r.issues:
                prefix = f"  ERROR [{issue.category}]" if issue.level == "ERROR" else f"  WARNING [{issue.category}]"
                cp_info = f" [{issue.code_point}]" if issue.code_point else ""
                output.append(f"{prefix} (line {issue.line_number}, col {issue.column_number}){cp_info}: {issue.message}")
                if issue.line_snippet:
                    output.append(f"    Snippet: {issue.line_snippet[:100]}")
        elif verbose and r.has_khmer:
            output.append(f"\n[PASS] {r.path} (Khmer text verified, {r.stats.total_khmer_chars} chars)")

    if not has_reported_file:
        output.append("\nNo encoding errors or Unicode sequence issues detected.")

    if show_stats:
        output.append("\n" + "-" * 72)
        output.append(" SUMMARY STATISTICS")
        output.append("-" * 72)
        output.append(f"Files scanned             : {total_files}")
        output.append(f"Files containing Khmer    : {files_with_khmer}")
        output.append(f"Total Khmer characters    : {total_khmer_chars}")
        output.append(f"Zero-Width Spaces (ZWSP)  : {total_zwsps} (legitimate typography word separators)")
        output.append(f"Total Errors              : {total_errors}")
        output.append(f"Total Warnings            : {total_warnings}")
        output.append("-" * 72)
        output.append("Categories: [BYTE_ENCODING] [DATA_CORRUPTION] [SUSPICIOUS_CONTROL] [VISUAL_RENDERING]")
        output.append("Note: This tool verifies UTF-8 integrity and character-level Unicode")
        output.append("validity. It does not evaluate grammar, spelling, or font rendering.")
        output.append("=" * 72)

    return "\n".join(output), total_errors, total_warnings


def format_json_report(
    results: List[FileResult],
    strict: bool = False,
) -> Tuple[str, int, int]:
    """Format check results as structured JSON for CI and AI agent consumption."""
    total_files = len(results)
    files_with_khmer = sum(1 for r in results if r.has_khmer)
    total_khmer_chars = sum(r.stats.total_khmer_chars for r in results)
    total_zwsps = sum(r.stats.zero_width_spaces for r in results)
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)

    if total_errors > 0 or (strict and total_warnings > 0):
        status = "FAIL"
    elif total_warnings > 0:
        status = "WARN"
    else:
        status = "PASS"

    data = {
        "summary": {
            "status": status,
            "total_files": total_files,
            "files_with_khmer": files_with_khmer,
            "total_khmer_chars": total_khmer_chars,
            "zero_width_spaces": total_zwsps,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
        },
        "files": [],
    }

    for r in results:
        file_status = "FAIL" if r.error_count > 0 else ("WARN" if r.warning_count > 0 else "PASS")
        file_entry = {
            "path": str(r.path),
            "status": file_status,
            "has_khmer": r.has_khmer,
            "encoding_error": r.encoding_error,
            "total_errors": r.error_count,
            "total_warnings": r.warning_count,
            "stats": {
                "total_khmer_chars": r.stats.total_khmer_chars,
                "consonants": r.stats.consonants,
                "independent_vowels": r.stats.independent_vowels,
                "dependent_vowels": r.stats.dependent_vowels,
                "coeng_subscripts": r.stats.coeng_subscripts,
                "diacritics": r.stats.diacritics,
                "digits": r.stats.digits,
                "symbols_and_punct": r.stats.symbols_and_punct,
                "riel_symbols": r.stats.riel_symbols,
                "zero_width_spaces": r.stats.zero_width_spaces,
            },
            "issues": [
                {
                    "level": issue.level,
                    "category": issue.category,
                    "line_number": issue.line_number,
                    "column_number": issue.column_number,
                    "code_point": issue.code_point,
                    "character_name": issue.character_name,
                    "message": issue.message,
                    "line_snippet": issue.line_snippet,
                }
                for issue in r.issues
            ],
        }
        data["files"].append(file_entry)

    return json.dumps(data, indent=2, ensure_ascii=False), total_errors, total_warnings


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_khmer_unicode.py",
        description=(
            "Khmer Unicode & UTF-8 Integrity Checker.\n"
            "Scans source and translation files for corrupted characters (U+FFFD),\n"
            "suspicious control codes, orphaned combining marks, and reports Khmer typography statistics.\n\n"
            "NOTE: This tool detects encoding and sequence-level defects. It does not evaluate\n"
            "linguistic correctness, grammar, or device font rendering."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        help="One or more files or directories to scan.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit status 1 on warnings).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON results for CI pipelines and automated agents.",
    )
    parser.add_argument(
        "--ext",
        dest="extensions",
        help="Comma-separated list of file extensions to scan (e.g. '.json,.ts,.tsx').",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show clean files in the report output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress informational output; only print errors and warnings.",
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Omit the summary statistics section in text output.",
    )
    return parser


def main() -> int:
    parser = build_cli_parser()
    args = parser.parse_args()

    extensions: Optional[Set[str]] = None
    if args.extensions:
        extensions = {
            f".{ext.strip().lstrip('.')}"
            for ext in args.extensions.split(",")
            if ext.strip()
        }

    checker = KhmerUnicodeChecker(extensions=extensions)
    all_results: List[FileResult] = []

    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Error: Target path does not exist: {path}", file=sys.stderr)
            return 2
        all_results.extend(checker.scan_path(path))

    if args.json:
        report, total_errors, total_warnings = format_json_report(
            all_results,
            strict=args.strict,
        )
        print(report)
    else:
        report, total_errors, total_warnings = format_text_report(
            all_results,
            verbose=args.verbose,
            show_stats=not args.no_stats and not args.quiet,
        )
        if not args.quiet or total_errors > 0 or (args.strict and total_warnings > 0):
            print(report)

    if total_errors > 0:
        return 1
    if args.strict and total_warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
