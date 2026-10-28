---
name: khmer-localization
description: Use when developing, translating, auditing, or reviewing software for Cambodian users, including translation auto-fixing, relative time, noun classifiers, 4-tier addresses, Khmer Unicode integrity, zero-decimal KHR currency formatting, +855 phone normalization, Bakong KHQR payments, Chuon Nath alphabetical sorting, Buddhist Era dates, or fixing dotted circle (U+25CC) and diacritic clipping bugs in web or mobile UI.
---

# Khmer Localization Engineering Skill (Cambodia)

Production-grade engineering standards for Khmer language (`km` / `km-KH`) and the Cambodian software ecosystem.

## Non-Negotiable Guardrails (The 6 Golden Rules)

1. **Word Order:** Strictly `[Noun] + [Adjective]` (e.g. `តម្លៃសរុប` "Total Price", never `សរុបតម្លៃ`; `ពាក្យសម្ងាត់ថ្មី` "New Password", never `ថ្មីពាក្យសម្ងាត់`).
2. **Counting Syntax:** Strictly `[Noun] + [Count] + [Classifier]` (e.g. `អ្នកប្រើប្រាស់ 3 នាក់` "3 users", never `*3 អ្នកប្រើប្រាស់`). Consult `data/khmer_classifiers.json` for appropriate classifiers (`នាក់`, `ក្បាល`, `គ្រឿង`, `ច្បាប់`, `សន្លឹក`).
3. **Currency:** Cambodian Riel (`KHR` / `៛`) uses whole-riel integers only—**never output fractional cents (`.00`)**. In ECMAScript, configure `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`.
4. **Register:** Professional modern digital tone. **Prohibit royal (*Reachasap*) and monastic (*Sanghasap*) vocabulary** (avoid `យាង`, `សោយ`, `ព្រះរាជ`, `និមន្ត`).
5. **String Truncation & Coeng:** Never slice raw UTF-16 code units (`.slice(0, n)`). Truncating after Coeng (`\u17D2`) or combining vowels creates an illegal sequence and renders a broken **dotted circle (`U+25CC`)**. Always use grapheme segmenters (`Intl.Segmenter(locale, { granularity: 'grapheme' })`).
6. **Typography & ZWSP:** Set CSS `line-height >= 1.6` on text containers to prevent vertical clipping of stacked subscripts. Preserve Zero-Width Spaces (`\u200B`) for word breaking.

## Zero-Token Executable CLI & MCP Tools

Avoid generating repetitive localization logic or burning context tokens reading catalogs. Execute built-in tools directly:

```bash
# Auto-correct inverted calques, royal registers, decimal riel, & broken Coeng
python3 scripts/khmer_utils.py fix "សរុបតម្លៃ 25.00៛ និងថ្មីពាក្យសម្ងាត់"
# Batch fix translation JSON files directly:
python3 scripts/khmer_utils.py fix --file locales/km.json

# Format natural Cambodian consumer relative time (under 1 min, past, future)
python3 scripts/khmer_utils.py relative-time 300
# or with Khmer digits: python3 scripts/khmer_utils.py relative-time 300 --khmer-digits

# Parse or format 4-tier Cambodian administrative delivery addresses
python3 scripts/khmer_utils.py address "ផ្ទះលេខ 42, ផ្លូវ 310, បឹងកេងកង, ភ្នំពេញ"

# Query UI terms without reading catalogs (saves ~3,500 tokens)
python3 scripts/khmer_utils.py lookup "Settings"
# or Node: ./scripts/khmer_utils.js lookup "Settings"

# Lint string for Unicode corruption, dotted circles, royal words, & decimal KHR
python3 scripts/khmer_utils.py lint "តម្លៃសរុប 10,000៛"

# Normalize Cambodian phone numbers to E.164 (+855) and domestic trunk
python3 scripts/khmer_utils.py phone "012 345 678"

# Format whole-riel KHR or USD
python3 scripts/khmer_utils.py currency 25000 --currency KHR

# Spelled-out Khmer numbers & currency words for invoices (GDT compliance)
python3 scripts/khmer_utils.py words 25000 --currency KHR

# Syllable segmentation & Zero-Width Space (U+200B) injection for web word wrapping
python3 scripts/khmer_utils.py break "ចូលគណនី"

# Calculate or verify Bakong KHQR EMVCo CRC16
python3 scripts/khmer_utils.py khqr-crc "<payload6304>"

# Auto-install agent rules into Cursor, Claude, Windsurf, Copilot, Gemini, or AGENTS
python3 scripts/khmer_utils.py install-rules --target all --tier standard

# Native MCP Server (JSON-RPC stdio) with 11 tools for Claude Code, Cursor, Windsurf
python3 scripts/khmer_mcp_server.py
```

## Streamlined Agent Workflow

1. **Detect Stack:** Identify i18n framework (Next.js `next-intl`, React `react-i18next`, React Native, or Python Babel/Django).
2. **Audit Baseline:** Run audits before editing:
   ```bash
   python3 scripts/audit_khmer_i18n.py --locales <path> --src <path>
   python3 scripts/check_khmer_unicode.py --strict .
   ```
3. **Apply Changes:** Use `lookup` for terminology, format KHR with integer minor units, and set CSS `line-height >= 1.6`.
4. **Verify Regressions:** Run automated test suites:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

## Progressive Disclosure Reference Matrix

When deep domain specifics are required, consult dedicated references:

| Need / Topic | Reference Document |
| :--- | :--- |
| **Instant Drop-In Code Snippets** | [Agent Fast Path](./references/agent-fast-path.md) |
| **Pre-Tuned System Prompts (45t, 120t, 250t)** | [Agent System Prompts](./prompts/agent-system-prompts.md) |
| **Detailed 9-Step Lifecycle & 4 Governance Layers** | [Agent Workflow & Governance](./references/agent-workflow.md) |
| **All 22 Machine-Readable Data Catalogs** | [Data Catalogs Guide](./references/data-catalogs.md) |
| **KHR Currency, Phone (+855), Buddhist Era** | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Bakong KHQR Payments & EMVCo TLV Specs** | [Khmer Fintech & KHQR](./references/khmer-fintech-and-khqr.md) |
| **Fonts, Line-Heights, Coeng Stacking & CSS** | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Top 10 Hallucinations & Countermeasures** | [Khmer AI Guardrails](./references/khmer-ai-guardrails.md) |
| **4-Tier Administrative Divisions (Province..Village)** | [Administrative Divisions](./references/cambodia-administrative-divisions.md) |
| **Chuon Nath Collation & Spelled-Out Numbers** | [Collation & Number Words](./references/khmer-collation-and-number-words.md) |
