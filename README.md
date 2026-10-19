# Khmer Localization (`khmer-localization`)

[![Tests](https://github.com/Chhunsour/khmer-localization/actions/workflows/tests.yml/badge.svg)](https://github.com/Chhunsour/khmer-localization/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

An open-source, production-ready **Agent Skill** for AI coding assistants (Google Antigravity, Claude Code, OpenAI Codex). It teaches coding agents to engineer high-quality software for Khmer-speaking users and the Cambodian market.

> [!NOTE]
> This repository packages a **reusable AI coding skill**, not a runtime application framework or SaaS product. Installing this skill teaches your AI coding assistant how to write, inspect, format, and verify Khmer localization across your own projects and codebases.

---

## Capabilities

1. **Natural Khmer UI Copy:** Practical vocabulary, phrasing conventions, and microcopy guidance for modern web and mobile apps (avoiding stiff, literal machine translations).
2. **Khmer Unicode & Typography Safety:** Rules for preserving combining marks, subscript consonants (Coeng `U+17D2`), Zero-Width Spaces (`U+200B`), and preventing visual defects like the dotted circle (`U+25CC`).
3. **Bilingual Internationalization (KM/EN):** Architecture patterns for structured translation keys, non-inflected Khmer pluralization, and persistent locale switching.
4. **Cambodian Phone Input Handling:** Practical three-stage normalization and validation pipeline for standard 8-digit and extended 9-digit NSN formats (`+855` / `0xx`) based on Telecommunication Regulator of Cambodia (TRC) standards, decoupling normalization from volatile prefix tables and preserving the OTP verification boundary.
5. **Dual Currency Formatting (USD and KHR):** Correct locale-aware formatting for Cambodian Riel (explaining why `Intl.NumberFormat` defaults to 2 decimals under ISO 4217, and demonstrating explicit configuration for whole-riel prices) and US Dollars (2 decimal digits), strictly avoiding unverified currency conversion.
6. **Mobile-First Responsive UX Testing:** Checklists for narrow mobile screens (320px–430px), CSS line-height clearance (preventing ascender/descender clipping), and layout audits.
7. **Automated Unicode & UTF-8 Integrity Checker:** A zero-dependency Python script (`check_khmer_unicode.py`) to statically audit source code and translation files for corrupted characters (`U+FFFD`), suspicious control codes, and broken sequences.

---

## Repository Structure

```text
khmer-localization/
├── SKILL.md                          # Core Agent Skills entrypoint and workflow
├── README.md                         # Documentation, setup, and installation guide
├── LICENSE                           # MIT License
├── CONTRIBUTING.md                   # Contribution guidelines and testing instructions
├── references/
│   ├── khmer-writing-guide.md        # UI vocabulary, tone, navigation, and validation copy
│   ├── unicode-and-typography.md     # Unicode structure, OpenType shaping, fonts, and CSS
│   └── cambodia-formatting.md        # Phone numbers (+855), dual currencies, and i18n
├── examples/
│   └── localization-examples.md      # Before-and-after implementation code samples
├── scripts/
│   └── check_khmer_unicode.py        # Static Unicode and UTF-8 integrity audit script
├── tests/
│   ├── test_check_khmer_unicode.py   # Unit test suite for Unicode checker (18 tests)
│   ├── test_currency_formatting.py   # Unit tests for KHR & USD formatting and rounding (12 tests)
│   └── test_phone_normalization.py   # Unit tests for Cambodian phone normalization (8 tests)
└── .github/
    └── workflows/
        └── tests.yml                 # Automated CI test matrix (Python 3.10 - 3.13)
```

---

## When This Skill Activates

AI coding assistants activate this skill when encountering tasks such as:
- Translating or localizing UI components into Khmer.
- Reviewing Khmer copy for natural digital tone and proper vocabulary.
- Setting up or refactoring bilingual (Khmer/English) internationalization in web, mobile, or backend apps.
- Implementing phone number input fields for Cambodian users (`+855` / `0xx`).
- Formatting prices and financial transactions in Cambodian Riel (`KHR` / `៛`) and US Dollars (`USD` / `$`).
- Debugging character encoding issues (mojibake, `U+FFFD`, or dotted circle artifacts `U+25CC`).
- Optimizing mobile layouts for Khmer font rendering and line heights.

---

## Installation & Setup

You can install this skill for your preferred AI coding assistant using its documented skill-discovery path:

### 1. Google Antigravity / Gemini

**Project-Specific (Recommended):**
Clone or copy this repository into your project's `.agents/skills/` directory:
```bash
mkdir -p .agents/skills
cp -r /path/to/khmer-localization .agents/skills/khmer-localization
```

**Global (Recommended):**
Install into your global Antigravity configuration directory:
```bash
mkdir -p ~/.gemini/config/skills
cp -r /path/to/khmer-localization ~/.gemini/config/skills/khmer-localization
```

*Legacy Path Compatibility:* Antigravity also continues to recognize skills placed in `~/.gemini/antigravity/skills/khmer-localization/` or `~/.gemini/skills/khmer-localization/`.

---

### 2. OpenAI Codex & `AGENTS.md` Workspaces

**Repository-Local Installation:**
Place the skill into `.agents/skills/khmer-localization/` (or `skills/khmer-localization/`):
```bash
mkdir -p .agents/skills
cp -r /path/to/khmer-localization .agents/skills/khmer-localization
```

Reference the skill in your project's `AGENTS.md`:
```markdown
## Localization Skills
- [Khmer Localization](.agents/skills/khmer-localization/SKILL.md): Procedures for Khmer language, Cambodian phone numbers, USD/KHR formatting, and Unicode integrity.
```

---

### 3. Claude Code

**Project-Specific:**
Place the skill inside the `.claude/skills/` folder at your project root:
```bash
mkdir -p .claude/skills
cp -r /path/to/khmer-localization .claude/skills/khmer-localization
```

**Global (User-Wide):**
Install into Claude Code's user configuration directory:
```bash
mkdir -p ~/.claude/skills
cp -r /path/to/khmer-localization ~/.claude/skills/khmer-localization
```

---

## Using the Unicode Verification Script

The bundled `check_khmer_unicode.py` tool statically scans localization files and source code for corrupted Unicode characters, suspicious control codes, and orphaned combining marks.

It uses Python's standard library only (zero third-party dependencies, compatible with Python 3.10+):

```bash
# Scan a single file or directory
python3 scripts/check_khmer_unicode.py path/to/locales/

# Strict mode: treat warnings as errors (ideal for CI pipelines)
python3 scripts/check_khmer_unicode.py --strict src/locales/

# Filter by specific extensions
python3 scripts/check_khmer_unicode.py --ext .json,.ts,.tsx src/

# View all options
python3 scripts/check_khmer_unicode.py --help
```

### Script Output Sample
```text
========================================================================
 KHMER UNICODE & ENCODING INTEGRITY REPORT
========================================================================

[FAIL] locales/km/broken.json
  ERROR [DATA_CORRUPTION] (line 4, col 18) [U+FFFD]: Unicode Replacement Character detected (U+FFFD).
  WARNING [VISUAL_RENDERING] (line 8, col 12) [U+25CC]: Literal Dotted Circle detected (U+25CC).

------------------------------------------------------------------------
 SUMMARY STATISTICS
------------------------------------------------------------------------
Files scanned             : 14
Files containing Khmer    : 6
Total Khmer characters    : 842
Zero-Width Spaces (ZWSP)  : 34 (legitimate typography word separators)
Total Errors              : 1
Total Warnings            : 1
------------------------------------------------------------------------
Categories: [BYTE_ENCODING] [DATA_CORRUPTION] [SUSPICIOUS_CONTROL] [VISUAL_RENDERING]
Note: This tool verifies UTF-8 integrity and character-level Unicode
validity. It does not evaluate grammar, spelling, or font rendering.
========================================================================
```

---

## Running Automated Tests

Run the complete test suite using Python's built-in `unittest` runner:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

All 38 unit tests run deterministically offline in under a second without network access.
- `test_check_khmer_unicode.py` (18 tests): Unicode replacement character detection, raw control codes, ZWSP preservation, orphaned combining marks, trailing Coeng, and CLI exit codes.
- `test_currency_formatting.py` (12 tests): KHR explicit whole-riel formatting, ISO 4217 runtime defaults, rounding of fractional amounts, multi-billion values, and USD formatting.
- `test_phone_normalization.py` (8 tests): E.164 normalization, 8-digit vs. 9-digit NSN lengths, Khmer numeral conversion, decoupling from carrier tables, and OTP verification boundary.

---

## Known Limitations

1. **Linguistic & Contextual Nuance:** The script and skill detect encoding corruption and character-level defects; they cannot evaluate literary style, grammar, or cultural sensitivity. High-visibility marketing copy and legal terms should always be reviewed by a native Khmer speaker.
2. **Font & Rendering Variability:** OpenType font rendering depends on the operating system's shaping engine (HarfBuzz, CoreText, DirectWrite). The skill provides safe font stacks and line-height guidelines, but visual inspection on target devices remains essential.
3. **Telecommunication Prefix Mutability:** Operator prefixes in Cambodia are regulated by the Telecommunication Regulator of Cambodia (TRC) and are subject to regulatory changes and Mobile Number Portability (MNP). Syntactic validation must not be confused with active subscriber verification (SMS OTP).

---

## Contributing

We welcome contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting improvements, reporting issues, and running tests.

---

## License

This project is licensed under the [MIT License](LICENSE).
