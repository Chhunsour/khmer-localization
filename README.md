# Khmer Localization (`khmer-localization`)

[![Tests](https://github.com/Chhunsour/khmer-localization/actions/workflows/tests.yml/badge.svg)](https://github.com/Chhunsour/khmer-localization/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Agent Skills Standard](https://img.shields.io/badge/Standard-Agent%20Skills-purple.svg)](https://agentskills.org)

An open-source, production-ready **Agent Skill** for AI coding assistants (**Claude Code**, **OpenAI Codex / ChatGPT**, **Google Antigravity / Gemini**). It equips AI coding agents with deep, verified domain knowledge to build, localize, and verify software for Khmer-speaking users and the Cambodian market.

> [!NOTE]
> This repository packages a **reusable AI coding skill**, not a monolithic runtime framework or web app. Installing this skill teaches your AI coding assistant how to write, inspect, format, and verify Khmer localization across your own applications and codebases.

---

## Agent Quick-Routing Matrix

| Problem / Prompt | What the Agent Does | Reference Document |
| :--- | :--- | :--- |
| **Translate / review UI copy** | Uses natural, modern tech verbs; avoids royal (*Reachasap*) and monk (*Sanghasap*) registers. | [Khmer Writing Guide](./references/khmer-writing-guide.md) |
| **Cambodian phone input (+855)** | Uses `normalizeCambodianPhone` (8/9-digit NSN; decouples prefixes; preserves OTP boundary). | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Currency formatting (KHR / USD)** | Configures `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }` for whole-riel prices. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **QR Payments (Bakong / KHQR)** | Displays merchant name, dual currency (KHR vs USD), and whole riel amounts without decimals. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Dates, Calendars & Buddhist Era** | Formats solar months (មករា..ធ្នូ), day-first format `DD/MM/YYYY`, and converts $\text{BE} = \text{CE} + 543$. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Diacritic clipping in buttons/cards** | Sets CSS `line-height: 1.6`–`1.8`, `min-h-[44px]`, and `includeFontPadding: false` (Android). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Word breaking & mobile text overflow** | Inserts Zero-Width Spaces (`\u200B`) via `Intl.Segmenter` + CSS `overflow-wrap: break-word`. | [Unicode & Typography](./references/unicode-and-typography.md) |
| **String truncation & dotted circles** | Truncates grapheme clusters using `Intl.Segmenter` (never slices after Coeng `U+17D2`). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Verify repository / CI check** | Runs `python3 scripts/check_khmer_unicode.py --strict --json <path>` | [Checker Script](./scripts/check_khmer_unicode.py) |

---

## Capabilities

1. **Natural Khmer UI Phrasing & Anti-Hallucination Guardrails:**
   - Action-oriented vocabulary (`ចូលគណនី` for Sign In, `ដាក់ស្នើ` for Submit, `ចុះឈ្មោះ` for Register).
   - Explicit guardrails preventing AI agents from hallucinating high-honorific royal vocabulary (*Reachasap*) or Buddhist monk vocabulary (*Sanghasap*).
   - Clear guidelines on when to use Latin digits (`0-9`) vs. traditional Khmer numerals (`០-៩`).
2. **Khmer Unicode & Grapheme Cluster Integrity:**
   - Preservation of base consonants, subscript consonants (generated via Coeng `U+17D2`), dependent vowels, and diacritics.
   - Grapheme-cluster-aware text truncation (`Intl.Segmenter`) preventing broken **dotted circle artifacts (`U+25CC`)**.
   - Zero-Width Space (`\u200B` / ZWSP) preservation and safe automatic word boundary insertion.
3. **Bilingual Internationalization (KM/EN):**
   - Architectural patterns for structured translation keys in `i18next`, `next-intl`, and `vue-i18n`.
   - Native handling of non-inflected Khmer nouns in pluralization rules (`cart_item_km: "ទំនិញ {{count}}"`).
   - Resilient fallback hierarchies and persistent user locale state.
4. **Cambodian Phone Input Handling (+855):**
   - Three-stage normalization pipeline decoupling stable E.164 normalization from volatile carrier prefix tables.
   - Support for both standard 8-digit NSNs (`+855 12 xxx xxx`) and extended 9-digit NSNs (`+855 96 xxx xxxx`) per Telecommunication Regulator of Cambodia (TRC) standards.
   - Conversion of Khmer numerals (`០-៩`) to ASCII digits, preserving the OTP verification boundary.
5. **Dual Currency Formatting (USD and KHR):**
   - Explicit whole-riel configuration (`{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`), avoiding the common ICU ISO 4217 minor-unit trap where KHR erroneously formats with `.00`.
   - Standard 2-decimal USD formatting (`minimumFractionDigits: 2`).
   - Strict separation between formatting and conversion (preventing fabricated exchange rates).
6. **National Payment Standards (Bakong & KHQR):**
   - Display guidelines for Cambodia's ubiquitous national QR payment standard (KHQR), ensuring currency, merchant name, and amount legibility.
7. **Cambodian Dates, Times & Buddhist Era (BE):**
   - Standard solar month names (មករា..ធ្នូ) and day-first date formatting (`DD/MM/YYYY` or `ថ្ងៃទីDD ខែMM ឆ្នាំYYYY`).
   - Buddhist Era conversion formula ($\text{BE} = \text{CE} + 543$).
   - 12-hour period qualifiers (ព្រឹក, រសៀល, ល្ងាច, យប់) and relative time microcopy.
8. **Modern Frontend Framework Recipes:**
   - Production-tested configurations for **Next.js** (Google Fonts `Kantumruy_Pro`), **Tailwind CSS** (`tailwind.config.ts` font families & line-height tokens), **React Native / Expo** (`includeFontPadding: false`), and **Zod** schema validation.
9. **Automated Static Unicode & UTF-8 Checker:**
   - Zero-dependency Python 3.10+ CLI tool (`check_khmer_unicode.py`) supporting `--strict` CI enforcement and `--json` machine-readable output.

---

## Repository Structure

```text
khmer-localization/
├── SKILL.md                          # Core Agent Skills entrypoint, routing matrix, and workflow
├── README.md                         # Documentation, quick reference, and installation guide
├── LICENSE                           # MIT License
├── CONTRIBUTING.md                   # Contribution guidelines and testing instructions
├── references/
│   ├── khmer-writing-guide.md        # UI vocabulary, registers, AI anti-hallucination guardrails
│   ├── unicode-and-typography.md     # Unicode, Coeng, fonts, line-breaking, and framework recipes
│   └── cambodia-formatting.md        # Phone numbers (+855), KHR/USD, Bakong KHQR, and calendar/BE
├── examples/
│   └── localization-examples.md      # 10 before-and-after implementation code examples
├── scripts/
│   └── check_khmer_unicode.py        # Static Unicode, UTF-8, and typography integrity audit script
├── tests/
│   ├── test_check_khmer_unicode.py   # Unit tests for Unicode checker & JSON CLI (20 tests)
│   ├── test_currency_formatting.py   # Unit tests for KHR & USD formatting and rounding (12 tests)
│   ├── test_date_and_formatting.py   # Unit tests for dates, BE calendar, truncation (15 tests)
│   └── test_phone_normalization.py   # Unit tests for Cambodian phone normalization (8 tests)
└── .github/
    └── workflows/
        └── tests.yml                 # Automated CI test matrix (Python 3.10 - 3.13)
```

---

## Installation & Setup

Install this skill into your preferred AI coding environment using its documented discovery path:

### 1. Google Antigravity / Gemini

**Project-Specific (Recommended):**
```bash
mkdir -p .agents/skills
cp -r /path/to/khmer-localization .agents/skills/khmer-localization
```

**Global (User-Wide):**
```bash
mkdir -p ~/.gemini/config/skills
cp -r /path/to/khmer-localization ~/.gemini/config/skills/khmer-localization
```
*Note: Antigravity also maintains legacy compatibility with `~/.gemini/antigravity/skills/khmer-localization/`.*

---

### 2. OpenAI Codex / ChatGPT / `AGENTS.md`

**Project-Specific Installation:**
```bash
mkdir -p .agents/skills
cp -r /path/to/khmer-localization .agents/skills/khmer-localization
```

Reference the skill in your project root `AGENTS.md`:
```markdown
## Localization Skills
- [Khmer Localization](.agents/skills/khmer-localization/SKILL.md): Complete engineering guide for Khmer UI, phone numbers (+855), dual currencies (USD/KHR), KHQR, and Unicode safety.
```

---

### 3. Claude Code

**Project-Specific:**
```bash
mkdir -p .claude/skills
cp -r /path/to/khmer-localization .claude/skills/khmer-localization
```

**Global (User-Wide):**
```bash
mkdir -p ~/.claude/skills
cp -r /path/to/khmer-localization ~/.claude/skills/khmer-localization
```

---

## Using the Unicode Verification Script

The bundled `check_khmer_unicode.py` script scans codebases and translation files for corrupted characters, suspicious control codes, and orphaned combining marks.

Uses Python's standard library only (zero third-party dependencies, compatible with Python 3.10+):

```bash
# Scan a directory
python3 scripts/check_khmer_unicode.py path/to/locales/

# Strict mode: exit with code 1 on warnings (ideal for CI pipelines)
python3 scripts/check_khmer_unicode.py --strict src/locales/

# JSON output for automated agents and CI reporting
python3 scripts/check_khmer_unicode.py --json --strict src/

# Filter by file extension
python3 scripts/check_khmer_unicode.py --ext .json,.ts,.tsx src/
```

### JSON Output Sample (for AI Agents & CI)
```json
{
  "summary": {
    "status": "PASS",
    "total_files": 14,
    "files_with_khmer": 6,
    "total_khmer_chars": 3444,
    "zero_width_spaces": 0,
    "total_errors": 0,
    "total_warnings": 0
  },
  "files": [ ... ]
}
```

---

## Running Automated Tests

Run the complete test suite using Python's built-in `unittest` runner:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

All **55 unit tests** run deterministically offline in under a second:
- `test_check_khmer_unicode.py` (20 tests): Unicode replacement character detection (`U+FFFD`), control codes, ZWSP preservation, orphaned marks, trailing Coeng, and JSON CLI output.
- `test_currency_formatting.py` (12 tests): KHR explicit whole-riel formatting, ISO 4217 runtime defaults, rounding of fractional amounts, multi-billion values, and live Node.js `Intl.NumberFormat` tests.
- `test_date_and_formatting.py` (15 tests): Khmer month names, Buddhist Era calculation ($\text{BE} = \text{CE} + 543$), relative time formatting, grapheme cluster text truncation, and live Node.js `Intl.DateTimeFormat` / `Intl.Segmenter` tests.
- `test_phone_normalization.py` (8 tests): E.164 normalization, 8-digit vs. 9-digit NSN lengths, Khmer numeral conversion, decoupling from carrier tables, and OTP verification boundary.

---

## Known Limitations

1. **Linguistic & Domain Context:** The skill and tooling detect encoding defects and provide battle-tested terminology, but cannot substitute for native speaker editorial review on high-stakes marketing, legal, or political copy.
2. **Font Shaper Dependency:** Character-level Unicode validity is verified by the script, but visual OpenType glyph rendering depends on system font shapers (HarfBuzz, CoreText, DirectWrite). Visual smoke testing on target mobile devices remains essential.
3. **Carrier Prefix Dynamic Updates:** Operator prefixes in Cambodia are periodically updated by the Telecommunication Regulator of Cambodia (TRC). Always decouple core E.164 normalization logic from dynamic prefix lookup tables.

---

## Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting improvements and running tests.

---

## License

This project is licensed under the [MIT License](LICENSE).
