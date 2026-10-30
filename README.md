# Khmer Localization (`khmer-localization`)
### Production-Grade Khmer (Cambodia) Localization & AI Agent Engineering Toolkit

<p align="center">
  <sub>Developed by <strong>Seng Chhunsour</strong></sub>
</p>

[![Author: Seng Chhunsour](https://img.shields.io/badge/Author-Seng%20Chhunsour-FF5A1F?style=flat-square&logo=github&logoColor=white)](https://github.com/Chhunsour)
[![Tests](https://github.com/Chhunsour/khmer-localization/actions/workflows/tests.yml/badge.svg)](https://github.com/Chhunsour/khmer-localization/actions)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-143%20Passed-brightgreen.svg)](#-test-suite--quality-assurance-matrix)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Dependencies: 0](https://img.shields.io/badge/Dependencies-Zero%20External-success.svg)](#-zero-dependency-isomorphic-api-reference)
[![Unicode: 15.1](https://img.shields.io/badge/Unicode-Khmer%20U%2B1780--U%2B17FF-informational.svg)](https://unicode.org/charts/PDF/U1780.pdf)
[![Country: Cambodia](https://img.shields.io/badge/Country-Cambodia%20%28%2B855%29-red.svg)](https://trc.gov.kh)
[![Runtime](https://img.shields.io/badge/Runtime-Node.js%20%7C%20TS%20%7C%20Python%20%7C%20Bun%20%7C%20Web-purple.svg)](#-zero-dependency-isomorphic-api-reference)

---

## 📊 Executive KPI Dashboard

| Strategic Dimension | Engineering Metric | Verification Methodology | Production Benchmark Standard |
| :--- | :---: | :--- | :--- |
| **Deterministic Reliability** | **143 / 143 Passing** | 13 test suites in Python & Node.js/Bun | 100% deterministic CI coverage |
| **Unicode & Script Safety** | **0 Errors, 0 Warnings** | `scripts/check_khmer_unicode.py --strict` | Scanned 19,700+ Khmer characters across 66 files |
| **Localization Quality Engine** | **4 Governance Layers** | `scripts/audit_khmer_i18n.py` CLI scanner | Automated, Human, Visual, External |
| **Supply-Chain Security** | **0 (Zero External Deps)** | Pure standard library & native Web APIs | Zero CVE surface, zero npm install lag |
| **AI Token Optimization** | **Up to 99.0% Reduction** | Modular 45t / 120t / 250t system prompts | Eradicates exploratory prompt loops |
| **Curated Offline Data** | **40 JSON Catalogs** | Verified via `data/METADATA.json` | Official authorities, sources & licenses |
| **UI Dictionary Coverage** | **160 Standard Terms** | Curated digital strings with hallucination traps | Auth, commerce, actions, navigation, cloud, security |
| **Cross-Platform Parity** | **TypeScript, JS, Python** | Isomorphic triple implementation | Node 18+, Bun, Deno, iOS, Android, Web |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Layer1["1. Developer & AI Assistant Layer"]
        IDE["Developer IDE / Coding Agent<br>(Cursor, Claude Code, Antigravity, Copilot)"]
        PROMPT["Pre-Tuned System Prompts<br>(Nano 45t / Standard 120t / Enterprise 250t)"]
        FASTPATH["Agent Fast-Path Cheat Sheet<br>(Zero-shot copy-paste snippets)"]
        EXAMPLES["Executable Examples<br>(E-Commerce, HR Payroll, React Form)"]
    end

    subgraph Layer2["2. Zero-Dependency Isomorphic Engine"]
        PHONE["Phone Normalizer (+855)<br>8/9-digit TRC NSN + Landlines & 117/119"]
        CURR["Dual-Currency Minor Units<br>KHR integer riels vs. USD cents (half-up)"]
        UNICODE["Unicode & Grapheme Segmenter<br>Intl.Segmenter dotted-circle prevention"]
        WORDS["Recursive Number-to-Words<br>Scale words for billions/trillions (រៀលគត់)"]
        KHQR["Bakong KHQR Engine<br>EMVCo TLV Generator + CRC16 Parser"]
        CALENDAR["Calendar & Buddhist Era<br>Solar months: BE = CE + 543"]
        COLLATION["Khmer Collation Engine<br>Chuon Nath alphabetical sorting"]
    end

    subgraph Layer3["3. Quality, Audit & Compliance Layer"]
        AUDIT["I18n Audit Scanner<br>(scripts/audit_khmer_i18n.py)"]
        UNICODE_CHECK["Strict Unicode Checker<br>(scripts/check_khmer_unicode.py)"]
        METADATA["Metadata Registry<br>(data/METADATA.json)"]
        UI_TERMS["160 UI Terms Catalog<br>(data/ui_terms.json)"]
        TRC_DATA["TRC Telecom Plan<br>(data/telecom_operators.json)"]
        NBC_DATA["Bakong Banks & KHQR MCC<br>(data/bakong_members.json)"]
        ADMIN_DATA["ISO 3166-2:KH 25 Provinces<br>(data/provinces.json + 25 district catalogs)"]
    end

    IDE --> PROMPT
    IDE --> FASTPATH
    IDE --> EXAMPLES
    PROMPT --> Layer2
    FASTPATH --> Layer2
    EXAMPLES --> Layer2
    Layer2 --> Layer3
```

---

## ⚡ Agent Quick-Routing Matrix

| Developer Goal / Problem | Fast-Action Pattern | Reference & Asset |
| :--- | :--- | :--- |
| **Audit Repository for I18n Bugs** | Scan codebase for missing keys, placeholder bugs, royal registers, decimal KHR. | [`scripts/audit_khmer_i18n.py`](./scripts/audit_khmer_i18n.py) |
| **Save Agent Context Tokens** | Copy-paste 1-page zero-shot snippets for KHR, BE, ZWSP, Phone, CRC16. | [`references/agent-fast-path.md`](./references/agent-fast-path.md) |
| **Cursor / Claude System Prompts** | Inject pre-tuned 45t, 120t, or 250t prompt blocks into config files. | [`prompts/agent-system-prompts.md`](./prompts/agent-system-prompts.md) |
| **Prevent AI Hallucinations** | Guard against Top 10 failure modes (royal vocabulary, inverted word order). | [`references/khmer-ai-guardrails.md`](./references/khmer-ai-guardrails.md) |
| **Standard UI Localization** | Lookup 160 standardized UI strings with explicit "avoid" hallucination lists. | [`data/ui_terms.json`](./data/ui_terms.json) |
| **Cambodian Phone Normalization** | Convert any input to E.164 (`+855...`) & domestic format (`0...`) with OTP flag. | [`scripts/khmer_utils.ts`](./scripts/khmer_utils.ts) / [`.py`](./scripts/khmer_utils.py) |
| **Dual-Currency Minor-Unit Engine** | Format KHR as whole integers (`15,000៛`); calculate totals with zero float drift. | [`scripts/khmer_utils.ts`](./scripts/khmer_utils.ts) / [`.py`](./scripts/khmer_utils.py) |
| **Bakong KHQR Payments** | Generate & parse EMVCo payloads with CRC16-CCITT checksums and sub-tags. | [`references/khmer-fintech-and-khqr.md`](./references/khmer-fintech-and-khqr.md) |
| **Cambodian TIN & E-Invoicing** | Validate 9-digit / branch TIN, generate GDT VAT invoice, in-words KHR (គត់). | [`references/cambodia-tax-and-invoicing.md`](./references/cambodia-tax-and-invoicing.md) |
| **Khmer Lunar Zodiac & Sak Era** | Calculate Lunar Animal (Chhnam) and Sak (1st to 10th) from CE year. | [`references/khmer-lunar-calendar.md`](./references/khmer-lunar-calendar.md) |
| **4-Tier Administrative Address** | Model Province $\rightarrow$ District $\rightarrow$ Sangkat $\rightarrow$ Village delivery across all 25 provinces. | [`references/cambodia-administrative-divisions.md`](./references/cambodia-administrative-divisions.md) |
| **GDT Tax Invoices (Spellout)** | Convert numeric amounts into official spelled-out Khmer words (up to trillions). | [`references/khmer-collation-and-number-words.md`](./references/khmer-collation-and-number-words.md) |
| **Alphabetical Sorting (Collation)** | Sort words per Chuon Nath dictionary order in pure Python & JS `Intl.Collator`. | [`references/khmer-collation-and-number-words.md`](./references/khmer-collation-and-number-words.md) |
| **Mobile Line-Height & Dotted Circle** | Set `line-height: 1.6+` and use `Intl.Segmenter` to prevent broken Coeng glyphs. | [`references/unicode-and-typography.md`](./references/unicode-and-typography.md) |
| **Static Code Audit / CI Verification** | Run strict Unicode and UTF-8 scanner with zero exit code on clean repos. | [`scripts/check_khmer_unicode.py`](./scripts/check_khmer_unicode.py) |
| **Runnable E-Commerce Example** | Complete checkout flow with KHR/USD taxes, phone validation, and KHQR. | [`examples/ecommerce_checkout.py`](./examples/ecommerce_checkout.py) / [`.js`](./examples/ecommerce_checkout.js) |
| **Runnable HR Payroll Example** | Monthly payroll with Chuon Nath collation, NSSF, ToS, and formal payslips. | [`examples/hr_payroll.py`](./examples/hr_payroll.py) / [`.js`](./examples/hr_payroll.js) |
| **Runnable GDT Tax Invoice** | Full bilingual VAT Tax Invoice in Python and Node.js with TIN, KHR words, KHQR. | [`examples/cambodia_tax_invoice.py`](./examples/cambodia_tax_invoice.py) / [`.js`](./examples/cambodia_tax_invoice.js) |
| **Bilingual React Form Component** | Production-grade React/Next.js checkout form with dynamic `lang="km"`. | [`examples/react_khmer_form.tsx`](./examples/react_khmer_form.tsx) |

---

## 🔍 Khmer Localization Quality & Audit Engine (`scripts/audit_khmer_i18n.py`)

The toolkit includes an automated i18n quality and static analysis engine that inspects translation dictionaries and application source code for common Cambodian localization defects:

```bash
python3 scripts/audit_khmer_i18n.py --locales path/to/locales --src path/to/src
```

### 4 Distinct Governance Layers
When auditing an application, `scripts/audit_khmer_i18n.py` enforces separation of concerns across 4 distinct layers:

1. **`[AUTOMATED_ERROR / AUTOMATED_WARNING]` (Deterministic Code Defects):**
   - **Missing Translation Keys:** Translation key in base locale (`en.json`) missing from `km.json`.
   - **Untranslated English Strings:** Identical English strings copied into Khmer translation files.
   - **Placeholder & Interpolation Mismatch:** Incompatible variables between languages (e.g. `{name}` in English missing in Khmer).
   - **Social Register Violations:** Inappropriate royal (*Reachasap*) or monk (*Sanghasap*) vocabulary (e.g. `យាង`, `សោយ`, `និមន្ត`).
   - **Decimal Riel Violations:** Prices displaying fractional KHR cents (e.g. `25.00 KHR`).
   - **Inverted Word Order:** English grammatical calques (e.g. `សរុបតម្លៃ` instead of `តម្លៃសរុប`).
   - **Hardcoded Strings in UI:** Khmer literals outside i18n translation functions.
   - **Manual Currency Concatenation:** Concatenating symbols like `amount + "៛"` instead of localized formatting.
   - **Destructive Regexes:** Whitespace strippers (`replace(/\s+/g, '')`) that delete Zero-Width Spaces (`\u200B`).

2. **`[HUMAN_REVIEW_REQUIRED]` (Linguistic & Cultural Review):**
   - Tone appropriateness, naturalness, brand register, and domain terminology that cannot be determined by static analysis.

3. **`[VISUAL_INSPECTION_REQUIRED]` (Device Viewport Rendering):**
   - Mobile viewport testing on 320px–390px screens for line-height clipping, button wrap stability, and missing font fallbacks.

4. **`[EXTERNAL_VERIFICATION_REQUIRED]` (Third-Party Provider Verification):**
   - Validating that KHQR payload syntax does not imply bank account validity or successful payment settlement; checking that phone syntax does not imply active SIM ownership without SMS OTP.

---

## 💻 Executable Production Examples (`examples/`)

Runnable, standalone production examples with zero external dependencies:

### 1. E-Commerce Checkout & Fiscal Invoice
- **Python:** `python3 examples/ecommerce_checkout.py`
- **Node.js:** `node examples/ecommerce_checkout.js`
- **Features:** Validates Cambodian customer phone (`012 889 977` $\rightarrow$ `+855 12 889 977`), calculates 10% VAT using integer minor units, generates EMVCo KHQR with CRC16-CCITT, parses the QR payload, and spells out the total invoice amount in formal Khmer words (`មួយសែនប្រាំពីរម៉ឺនបីពាន់ប្រាំបីរយរៀលគត់`).

### 2. HR Payroll & Formal Payslip System
- **Python:** `python3 examples/hr_payroll.py`
- **Node.js:** `node examples/hr_payroll.js`
- **Features:** Collates employee roster using Chuon Nath dictionary order (`sort_khmer_words`), formats pay period in Khmer solar months and Buddhist Era ($\text{BE} = \text{CE} + 543$), computes Cambodian Tax on Salary (ToS) progressive brackets, deducts NSSF pension, and generates a formal bilingual payslip (ប័ណ្ណបើកប្រាក់បៀវត្ស).

### 3. Bilingual React / Next.js Payment Form
- **Component:** [`examples/react_khmer_form.tsx`](./examples/react_khmer_form.tsx)
- **Features:** Production React component with dynamic `lang="km"` and `dir="ltr"`, guaranteed CSS `line-height: 1.75` (preventing stacked vowel clipping), live Cambodian phone normalization with line type badge, dual-currency selector, live in-words calculation, and grapheme-safe notes preview.

### 4. GDT VAT Tax Invoice (វិក្កយបត្រអាករ) & E-Invoicing
- **Python:** `python3 examples/cambodia_tax_invoice.py`
- **Node.js:** `node examples/cambodia_tax_invoice.js`
- **Features:** Full enterprise VAT Tax Invoice compliant with General Department of Taxation (GDT) regulations. Validates 9-digit enterprise and branch TINs, dual-currency line items, 10% VAT calculation with integer minor units, NBC exchange rate conversion, formal spelled-out Khmer words ending in `គត់`, traditional Khmer lunar calendar (Animal Zodiac & Sak era), and Bakong dynamic KHQR payload generation.

---

## 📉 AI Context Token Optimization Benchmarks

Localizing into low-resource scripts like Khmer frequently wastes thousands of context tokens due to multi-turn debugging. `khmer-localization` eliminates this overhead with pre-tuned prompt tiers:

| Optimization Strategy | Context Tokens | Overhead Reduction | Visual Token Footprint | Primary Engineering Fit |
| :--- | :---: | :---: | :--- | :--- |
| **Raw Multi-File Documentation** | ~4,500 | 0% (Baseline) | `████████████████████` 100% | Full manual documentation review |
| **Enterprise / Fintech Tier** | ~250 | **94.4%** | `█░░░░░░░░░░░░░░░░░░░` 5.6% | Payment gateways, KHQR, GDT invoices |
| **Standard UI Tier** | ~120 | **97.3%** | `▌░░░░░░░░░░░░░░░░░░░` 2.7% | Web & mobile frontend apps |
| **Nano Tier** | ~45 | **99.0%** | `▎░░░░░░░░░░░░░░░░░░░` 1.0% | `.cursorrules`, `.windsurfrules` |

> [!NOTE]
> **Token Benchmark Methodology:** Token counts were measured using the standard OpenAI/Anthropic `cl100k_base` BPE tokenizer on the modular prompt templates in [`prompts/agent-system-prompts.md`](./prompts/agent-system-prompts.md) compared against reading raw multi-file reference directories (~4,500 tokens).

---

## ⚖️ Enterprise Contrast Matrix: Naive LLM vs. Khmer Localization

| Domain | Naive AI / Default Engineering (Failure Mode) | Production Standard (`khmer-localization`) | Severity |
| :--- | :--- | :--- | :---: |
| **Social Register** | Hallucinates archaic royal (*Reachasap* / រាជសព្ទ) vocabulary (`យាងចូល`, `សោយ`). | Enforces respectful modern digital tech vocabulary (`ចូលគណនី`, `រក្សាទុក`). | 🔴 High |
| **Word Order** | Calques English `[Adj] + [Noun]` ("Total Price" $\rightarrow$ ungrammatical `សរុបតម្លៃ`). | Strictly enforces Khmer grammar: `[Noun] + [Adj]` (`តម្លៃសរុប`). | 🔴 High |
| **KHR Currency** | `Intl.NumberFormat` default outputs `.00` decimals (`25,000.00៛`). | Explicit `{ fractionDigits: 0 }` outputs whole riel (`25,000៛`). | 🔴 High |
| **Financial Math** | Floating point calculations cause precision drift in riel subtotals. | Integer minor units with configurable rounding (`half_up` / `half_even`). | 🔴 High |
| **String Slicing** | Naive `.slice(0, n)` cuts Coeng (`U+17D2`), triggering **dotted circle (`U+25CC`)**. | Uses `Intl.Segmenter` grapheme cluster boundary detection. | 🔴 High |
| **Whitespace** | `s.replace(/\s+/g, '')` strips Zero-Width Space (`\u200B`), destroying word wrapping. | Preserves ZWSP; injects soft break opportunities cleanly. | 🟡 Med |
| **Phone Validation** | Rejects landlines or emergency short codes; claims number is active without OTP. | Recognizes mobile, geographic landlines (023, 063), short codes (117, 119). | 🔴 High |
| **Alphabetical Sort** | Sorts by raw Unicode code points, violating Khmer dictionary rules. | Implements Chuon Nath dictionary order collation in Python and JS. | 🔴 High |
| **Large Numbers** | Hardcoded scale fails at millions, billions, or negative values. | Recursive grouping converts unlimited numbers into formal Khmer words. | 🟡 Med |
| **KHQR Payments** | Incomplete CRC check or assumes QR validity guarantees payment settlement. | Full EMVCo TLV parser with CRC16-CCITT; decouples syntax from settlement. | 🔴 High |
| **Exchange Rate** | Hardcodes static rates (e.g., $1 = 4000៛) causing financial discrepancy. | Separates formatting from conversion; requires live NBC feed. | 🔴 High |
| **Buddhist Era** | Offsets year incorrectly or confuses with Thai solar calendar variants. | Strictly applies Cambodian civil standard formula: $\text{BE} = \text{CE} + 543$. | 🟡 Med |

---

## 🗄️ Curated Offline Datasets (`data/`) & Metadata Registry

All 40 offline JSON catalogs are cataloged in [`data/METADATA.json`](./data/METADATA.json) with documented authorities, verification dates, schemas, and licenses:

| Dataset Path | Records | Authority / Domain | Primary Engineering Use Case |
| :--- | :---: | :--- | :--- |
| [`data/ui_terms.json`](./data/ui_terms.json) | **160** | Digital Software Engineering | Natural UI translations with forbidden hallucination list |
| [`data/provinces.json`](./data/provinces.json) | **25** | ISO 3166-2:KH / Ministry of Interior | Top-level address cascades and regional localization |
| [`data/phnom_penh_districts.json`](./data/phnom_penh_districts.json) | **14** | Phnom Penh Capital Administration | Khan administrative division dropdowns and postal routing |
| [`data/siem_reap_districts.json`](./data/siem_reap_districts.json) | **12** | Siem Reap Administration | Tourism, hospitality, and provincial logistics |
| [`data/battambang_districts.json`](./data/battambang_districts.json) | **14** | Battambang Administration | Western agricultural zone and delivery forms |
| [`data/kandal_districts.json`](./data/kandal_districts.json) | **11** | Kandal Administration | Capital peri-urban zone delivery routing |
| [`data/kampong_cham_districts.json`](./data/kampong_cham_districts.json) | **10** | Kampong Cham Administration | Central Mekong commercial district selections |
| [`data/kampot_districts.json`](./data/kampot_districts.json) | **9** | Kampot Administration | Coastal trade and agro-tourism routing |
| [`data/preah_sihanouk_districts.json`](./data/preah_sihanouk_districts.json) | **5** | Sihanoukville Administration | Deep-water port, logistics, and island districts |
| [`data/koh_kong_districts.json`](./data/koh_kong_districts.json) | **7** | Koh Kong Administration | Coastal corridor and eco-tourism routing |
| [`data/pursat_districts.json`](./data/pursat_districts.json) | **7** | Pursat Administration | Tonle Sap basin agricultural delivery routing |
| [`data/takeo_districts.json`](./data/takeo_districts.json) | **10** | Takeo Administration | Southern economic corridor and heritage routing |
| [`data/prey_veng_districts.json`](./data/prey_veng_districts.json) | **13** | Prey Veng Administration | Eastern lowland rice basket logistics |
| [`data/kampong_speu_districts.json`](./data/kampong_speu_districts.json) | **9** | Kampong Speu Administration | Industrial corridor and National Road 4 freight |
| [`data/kampong_thom_districts.json`](./data/kampong_thom_districts.json) | **9** | Kampong Thom Administration | Central junction and Sambor Prei Kuk logistics |
| [`data/svay_rieng_districts.json`](./data/svay_rieng_districts.json) | **8** | Svay Rieng Administration | Bavet Special Economic Zone & border trade |
| [`data/banteay_meanchey_districts.json`](./data/banteay_meanchey_districts.json) | **9** | Banteay Meanchey Administration | Poipet border gateway and cross-border trade |
| [`data/kratie_districts.json`](./data/kratie_districts.json) | **6** | Kratie Administration | North-eastern Mekong eco-tourism and river ports |
| [`data/kampong_chhnang_districts.json`](./data/kampong_chhnang_districts.json) | **8** | Kampong Chhnang Administration | Central riverine trade and pottery manufacturing |
| [`data/tbong_khmum_districts.json`](./data/tbong_khmum_districts.json) | **7** | Tbong Khmum Administration | Rubber plantation zone and border trade |
| [`data/preah_vihear_districts.json`](./data/preah_vihear_districts.json) | **8** | Preah Vihear Administration | Northern temple heritage and agricultural logistics |
| [`data/oddar_meanchey_districts.json`](./data/oddar_meanchey_districts.json) | **5** | Oddar Meanchey Administration | Northern border passes (O Smach) and logistics |
| [`data/kep_districts.json`](./data/kep_districts.json) | **2** | Kep Administration | Coastal tourism and seafood commerce |
| [`data/pailin_districts.json`](./data/pailin_districts.json) | **2** | Pailin Administration | Cardamom western border zone and mining commerce |
| [`data/stung_treng_districts.json`](./data/stung_treng_districts.json) | **6** | Stung Treng Administration | Upper Mekong confluence and Laos border trade |
| [`data/ratanakiri_districts.json`](./data/ratanakiri_districts.json) | **9** | Ratanakiri Administration | Highland agro-industry, mining, and eco-tourism |
| [`data/mondulkiri_districts.json`](./data/mondulkiri_districts.json) | **5** | Mondulkiri Administration | Highland eco-tourism and coffee/pepper agriculture |
| [`data/telecom_operators.json`](./data/telecom_operators.json) | **10** | TRC / ITU-T MCC-MNC | Operator prefix verification and MCC-MNC lookups |
| [`data/banknotes.json`](./data/banknotes.json) | **11** | National Bank of Cambodia (NBC) | Currency denomination pickers and cash payment UI |
| [`data/bakong_members.json`](./data/bakong_members.json) | **10** | NBC Bakong Switch | Bank and MFI participant selector lists |
| [`data/khqr_mcc_codes.json`](./data/khqr_mcc_codes.json) | **10** | ISO 18245 / NBC | Bakong KHQR Tag 52 Merchant Category Codes |
| [`data/public_holidays.json`](./data/public_holidays.json) | **12** | Royal Government Sub-Decree | Statutory non-working day calendars & SLA calculators |
| [`data/cambodia_postal_codes.json`](./data/cambodia_postal_codes.json) | **12** | Cambodia Post | Major postal routing and logistics codes |
| [`data/cambodia_logistics.json`](./data/cambodia_logistics.json) | **10** | Domestic Freight & Courier | Courier service integrations (J&T, Kerry, Virak Buntham) |
| [`data/cambodia_ministries.json`](./data/cambodia_ministries.json) | **5** | Royal Government of Cambodia | Official regulatory authorities and e-government portals |
| [`data/khmer_symbols.json`](./data/khmer_symbols.json) | **8** | Unicode 15.1 (Khmer Symbols) | Punctuation marks (Khan, Bariyoosan, Lek Too, Riel) |
| [`data/khmer_keyboard.json`](./data/khmer_keyboard.json) | **18** | NiDA / Khmer OS Standard | Virtual keyboard rendering and key event handlers |
| [`data/khmer_consonants.json`](./data/khmer_consonants.json) | **33** | National Institute of Linguistics | Complete 33 consonants, Vagga phonology, Series 1 & 2 |
| [`data/khmer_independent_vowels.json`](./data/khmer_independent_vowels.json) | **14** | Unicode Consortium | 14 non-deprecated independent vowels and phonetic IPA |
| [`data/khmer_diacritics.json`](./data/khmer_diacritics.json) | **14** | Unicode Consortium & RAC | Khmer signs, diacritics, and subscript markers catalog |

---

## 🧪 Test Suite & Quality Assurance Matrix

The test suite runs offline with zero external dependencies across both Python and Node.js runtimes:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

```
========================================================================================
 TEST SUITE EXECUTION REPORT — ALL 143 TESTS DETERMINISTICALLY PASSING
========================================================================================
 Suite File                       | Tests | Scope & Verifications
----------------------------------+-------+---------------------------------------------
 test_audit_khmer_i18n.py         |   8   | Missing keys, royal register, font stacks, line-height, HTML attributes, TIN, unlocalized dates
 test_check_khmer_unicode.py      |  21   | U+FFFD, control characters, ZWSP, trailing Coeng, double Coeng, CLI strict mode
 test_currency_formatting.py      |  12   | Whole-riel formatting, ICU defaults, rounding, minor units
 test_data_catalog.py             |   7   | Provinces, banknotes, operators, holidays, Bakong, diacritics
 test_data_metadata.py            |   3   | Complete data/METADATA.json verification of all 40 catalogs
 test_date_and_formatting.py      |  16   | Months, BE formula (CE+543), grapheme truncation, Lunar Zodiac & Sak era
 test_domain_catalogs.py          |   4   | Kandal, Kampong Cham, Kampot, couriers, ministries
 test_extended_catalogs.py        |   7   | Complete 25 provincial district catalogs, independent vowels, postal codes
 test_khmer_utils.py              |  26   | Core phone, currency, dates, words, KHQR builder, TIN, zodiac
 test_khmer_utils_extended.py     |   8   | Landlines, minor unit math, National ID, plates, deep KHQR tag 62, collation
 test_khmer_utils_js.py           |  16   | Isomorphic JS/Node/Bun runtime parity validation, TIN, Zodiac/Sak, KHQR
 test_phone_normalization.py      |   8   | 8/9-digit NSN lengths, E.164, OTP requirement flag, TRC lookup
 test_ui_terms.py                 |   7   | 160 UI terms schema, naming rules, anti-hallucination, fintech/cloud coverage
----------------------------------+-------+---------------------------------------------
 TOTAL VERIFIED TESTS             |  143  | 100% Deterministic CI Compliance (0 Failures)
========================================================================================
```

Static Unicode audit command:
```bash
python3 scripts/check_khmer_unicode.py --strict --json .
# Output: { "summary": { "status": "PASS", "total_errors": 0, "total_warnings": 0 } }
```

---

## 🔒 Security & Vulnerability Reporting Policy

We take software security and integrity seriously. Because `khmer-localization` handles financial formatting, KHQR payload generation, and telephone normalization:
- **Zero Runtime Dependencies:** The codebase contains 0 third-party runtime dependencies, preventing supply chain attacks and arbitrary code execution vulnerabilities.
- **Reporting Vulnerabilities:** If you discover a security vulnerability or precision defect, please report it via [GitHub Security Advisories](https://github.com/Chhunsour/khmer-localization/security/advisories) or open a private issue.
- **Decoupled Verification:** Always remember that syntax validation of phone numbers and KHQR payloads does not verify SIM activity, ownership, or banking settlement.

---

## 📜 Regulatory Citations & Standards

- **Telecommunication Regulator of Cambodia (TRC):** [https://trc.gov.kh](https://trc.gov.kh) — *National Numbering Plan & Mobile Allocations* (verified October 2026).
- **National Bank of Cambodia (NBC):** [https://www.nbc.gov.kh](https://www.nbc.gov.kh) — *Bakong Payment System & KHQR EMVCo Specifications*.
- **General Department of Taxation (GDT):** [https://www.tax.gov.kh](https://www.tax.gov.kh) — *E-Invoicing and Khmer Word Currency Requirements*.
- **International Telecommunication Union (ITU):** [ITU-T Recommendation E.164](https://www.itu.int/rec/T-REC-E.164) — *The International Public Telecommunication Numbering Plan (Cambodia +855)*.
- **The Unicode Consortium:** [Khmer Unicode Block Charts (U+1780..U+17FF)](https://unicode.org/charts/PDF/U1780.pdf).
- **ISO 4217 Currency Standard:** Maintenance Agency for Currency Codes (`KHR` numeric 116, minor unit 2).
- **ISO 3166-2:KH:** International standard for Cambodia's 25 primary administrative subdivisions.

---

## 👤 Author & Developer

**Developed by Seng Chhunsour**
- **GitHub:** [@Chhunsour](https://github.com/Chhunsour)
- **Project:** [Khmer Localization](https://github.com/Chhunsour/khmer-localization)

---

## 📄 License & Community

Distributed under the [MIT License](LICENSE). Built for enterprise engineering teams, independent developers, and autonomous coding agents building world-class software for Cambodia.
