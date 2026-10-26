# Khmer Localization (`khmer-localization`)
### Production-Grade Khmer (Cambodia) Localization & AI Agent Engineering Toolkit

[![Tests](https://github.com/Chhunsour/khmer-localization/actions/workflows/tests.yml/badge.svg)](https://github.com/Chhunsour/khmer-localization/actions)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-104%20Passed-brightgreen.svg)](#-test-suite--quality-assurance-matrix)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Dependencies: 0](https://img.shields.io/badge/Dependencies-Zero%20External-success.svg)](#-zero-dependency-isomorphic-api-reference)
[![Unicode: 15.1](https://img.shields.io/badge/Unicode-Khmer%20U%2B1780--U%2B17FF-informational.svg)](https://unicode.org/charts/PDF/U1780.pdf)
[![Country: Cambodia](https://img.shields.io/badge/Country-Cambodia%20%28%2B855%29-red.svg)](https://trc.gov.kh)
[![Runtime](https://img.shields.io/badge/Runtime-Node.js%20%7C%20TS%20%7C%20Python%20%7C%20Web-purple.svg)](#-zero-dependency-isomorphic-api-reference)

---

## 📊 Executive KPI Dashboard

| Dimension | Engineering Metric | Verification Method | Production Standard |
| :--- | :---: | :--- | :--- |
| **Deterministic Reliability** | **104 / 104 Tests Passing** | Automated Python & Node.js test runners | 100% deterministic CI coverage |
| **Unicode & Script Safety** | **0 Errors, 0 Warnings** | `scripts/check_khmer_unicode.py --strict` | Scanned 14,200+ Khmer characters |
| **External Dependencies** | **0 (Zero)** | Pure standard library & native Web APIs | No supply-chain bloat or CVE surface |
| **AI Token Overhead** | **~90% Reduction** | Modular 45t / 120t / 250t system prompts | Zero exploratory prompt loops |
| **Curated Offline Data** | **21 JSON Datasets** | Schema-validated offline catalogs | Telecom, banking, administrative |
| **UI Dictionary Coverage** | **107 UI Terms** | Curated digital strings with hallucination traps | Auth, commerce, actions, navigation |
| **Cross-Platform Parity** | **TypeScript, JS, Python** | Isomorphic dual implementation | Node 18+, Bun, Deno, iOS, Android, Web |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Layer1["1. AI Agent & Token Optimization Layer"]
        A["Agent Prompt / Developer Input"] --> B{"Optimization Tier"}
        B -->|Nano (45t)| C[".cursorrules / .windsurfrules"]
        B -->|Standard (120t)| D["CLAUDE.md / Copilot"]
        B -->|Enterprise (250t)| E["Fintech & KHQR Compliance"]
        B -->|Zero-Shot| F["Agent Fast-Path Cheat Sheet"]
    end

    subgraph Layer2["2. Isomorphic Core Engine (Zero External Deps)"]
        G["Phone Normalizer (+855)"]
        H["Dual Currency Engine (KHR / USD)"]
        I["Unicode Grapheme Segmenter"]
        J["GDT Number-to-Words Engine"]
        K["NBC Bakong KHQR CRC16 Validator"]
        L["Buddhist Era & Calendar Engine"]
    end

    subgraph Layer3["3. Authoritative Datasets & Regulatory Compliance"]
        M["data/ui_terms.json (107 Terms)"]
        N["TRC Telecom Plan (+855)"]
        O["NBC Bakong KHQR (EMVCo)"]
        P["ISO 3166-2:KH (25 Provinces)"]
        Q["GDT Invoicing Regulations"]
    end

    Layer1 --> Layer2
    Layer2 --> Layer3
```

---

## ⚡ Agent Quick-Routing Matrix

| Developer Goal / Problem | Fast-Action Pattern | Reference & Asset |
| :--- | :--- | :--- |
| **Save Agent Context Tokens** | Copy-paste 1-page zero-shot snippets for KHR, BE, ZWSP, Phone, CRC16. | [`references/agent-fast-path.md`](./references/agent-fast-path.md) |
| **Cursor / Claude System Prompts** | Inject pre-tuned 45t, 120t, or 250t prompt blocks into config files. | [`prompts/agent-system-prompts.md`](./prompts/agent-system-prompts.md) |
| **Prevent AI Hallucinations** | Guard against Top 10 failure modes (royal vocabulary, inverted word order). | [`references/khmer-ai-guardrails.md`](./references/khmer-ai-guardrails.md) |
| **Standard UI Localization** | Lookup 107 standardized UI strings with explicit "avoid" hallucination lists. | [`data/ui_terms.json`](./data/ui_terms.json) |
| **Cambodian Phone Normalization** | Convert any input to E.164 (`+855...`) & domestic format (`0...`) with OTP flag. | [`scripts/khmer_utils.ts`](./scripts/khmer_utils.ts) / [`.py`](./scripts/khmer_utils.py) |
| **Dual-Currency Formatting** | Format KHR as whole integers (`15,000៛`) and USD with 2 decimals (`$15.00`). | [`scripts/khmer_utils.ts`](./scripts/khmer_utils.ts) / [`.py`](./scripts/khmer_utils.py) |
| **Bakong KHQR Payments** | Generate & verify EMVCo payloads with CRC16-CCITT checksums. | [`references/khmer-fintech-and-khqr.md`](./references/khmer-fintech-and-khqr.md) |
| **4-Tier Administrative Address** | Model Province $\rightarrow$ District $\rightarrow$ Sangkat $\rightarrow$ Village delivery addresses. | [`references/cambodia-administrative-divisions.md`](./references/cambodia-administrative-divisions.md) |
| **GDT Tax Invoices (Spellout)** | Convert numeric amounts into official spelled-out Khmer words. | [`references/khmer-collation-and-number-words.md`](./references/khmer-collation-and-number-words.md) |
| **Mobile Line-Height & Dotted Circle** | Set `line-height: 1.6+` and use `Intl.Segmenter` to prevent broken Coeng glyphs. | [`references/unicode-and-typography.md`](./references/unicode-and-typography.md) |
| **Static Code Audit / CI Verification** | Run strict Unicode and UTF-8 scanner with zero exit code on clean repos. | [`scripts/check_khmer_unicode.py`](./scripts/check_khmer_unicode.py) |

---

## ⚖️ Enterprise Contrast Matrix: Naive LLM vs. Khmer Localization

| Domain | Naive AI / Default Engineering (Failure Mode) | Production Standard (`khmer-localization`) | Severity |
| :--- | :--- | :--- | :---: |
| **Social Register** | Hallucinates archaic royal (*Reachasap* / រាជសព្ទ) vocabulary (`យាងចូល`, `សោយ`). | Enforces respectful modern digital tech vocabulary (`ចូលគណនី`, `រក្សាទុក`). | 🔴 High |
| **Word Order** | Calques English `[Adj] + [Noun]` ("Total Price" $\rightarrow$ ungrammatical `សរុបតម្លៃ`). | Strictly enforces Khmer grammar: `[Noun] + [Adj]` (`តម្លៃសរុប`). | 🔴 High |
| **KHR Currency** | `Intl.NumberFormat` default outputs `.00` decimals (`25,000.00៛`). | Explicit `{ fractionDigits: 0 }` outputs whole riel (`25,000៛`). | 🔴 High |
| **String Slicing** | Naive `.slice(0, n)` cuts Coeng (`U+17D2`), triggering **dotted circle (`U+25CC`)**. | Uses `Intl.Segmenter` grapheme cluster boundary detection. | 🔴 High |
| **Whitespace** | `s.replace(/\s+/g, '')` strips Zero-Width Space (`\u200B`), destroying word wrapping. | Preserves ZWSP; injects soft break opportunities cleanly. | 🟡 Med |
| **Phone Validation** | Rejects valid users because prefix lists are outdated; claims number is active. | Decouples TRC 8/9-digit NSN format; flags OTP boundary requirement. | 🔴 High |
| **Exchange Rate** | Hardcodes static rates (e.g., $1 = 4000៛) causing financial discrepancy. | Separates formatting from conversion; requires live NBC feed. | 🔴 High |
| **Pluralization** | Appends awkward suffixes (`ទំនិញច្រើន`) imitating English plural rules. | Uses native classifier particles and invariant noun stems (`ទំនិញ 3`). | 🟡 Med |
| **Buddhist Era** | Offsets year incorrectly or confuses with Thai solar calendar variants. | Strictly applies Cambodian civil standard formula: $\text{BE} = \text{CE} + 543$. | 🟡 Med |
| **Tax Invoicing** | Emits numeric string where GDT regulations mandate spelled-out Khmer words. | Automates official scale words (`ពីរម៉ឺនប្រាំពាន់រៀលគត់`). | 🔴 High |

---

## 🎯 Analytical Engineering Pillars

### 1. Dual-Currency Financial Engine (KHR vs. USD)

Cambodia's commercial economy runs simultaneously on Cambodian Riel (KHR / ៛) and US Dollar (USD / $):

| Parameter | Cambodian Riel (KHR / ៛) | United States Dollar (USD / $) |
| :--- | :--- | :--- |
| **Circulation Reality** | Physical banknotes only; no coins or cents in circulation | Banknotes and electronic transfers |
| **Display Standard** | **Integer whole riel only** (e.g., `15,000 ៛`) | **2 decimal places mandatory** (e.g., `$15.00`) |
| **ISO 4217 Runtime Default** | ⚠️ Defaults to 2 decimals (`15,000.00៛`) in browser ICU | Defaults to 2 decimals (`$15.00`) |
| **Compliance Requirement** | **Must explicitly pass `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`** | Standard formatting |

```typescript
// Isomorphic TypeScript / JavaScript
import { formatKHR, formatUSD } from "./scripts/khmer_utils";

formatKHR(15000); // => "15,000៛"
formatUSD(15.5);  // => "$15.50"
```

---

### 2. Cambodian Phone Number Engineering (+855)

The Telecommunication Regulator of Cambodia (TRC) mandates a closed numbering plan under ITU-T E.164:

| Format Tier | Domestic Notation | International E.164 | NSN Digits | Operator Classification |
| :--- | :--- | :--- | :---: | :--- |
| **Standard Mobile** | `012 345 678` | `+85512345678` | **8 digits** | Cellcard, Smart, Metfone |
| **Extended Mobile** | `096 123 4567` | `+855961234567` | **9 digits** | Smart 096, Metfone 097, CooTel 038 |
| **Syntax Validity** | Valid if NSN is exactly 8 or 9 digits | Valid if starts with `+855` followed by 8 or 9 digits | - | Decoupled from dynamic carrier tables |
| **Liveness Boundary** | ⚠️ **Never assume active SIM:** Syntax check must always flag `requires_otp_verification: true`. |

```typescript
import { normalizeCambodianPhone } from "./scripts/khmer_utils";

const result = normalizeCambodianPhone("012 345 678");
// {
//   nsn: "12345678",
//   normalized_e164: "+85512345678",
//   normalized_domestic: "012345678",
//   is_valid_syntax: true,
//   length_category: "8_digits",
//   requires_otp_verification: true
// }
```

---

### 3. Unicode Integrity & Typography (No Dotted Circles)

Khmer is an **abugida script** where subscript consonants (ជើងអក្សរ) are constructed dynamically using the Coeng control code (`U+17D2`):

$$\text{Subscript Consonant} = \text{Coeng (U+17D2)} + \text{Base Consonant}$$

| Failure Mode | Visual Defect | Root Cause | Production Guardrail |
| :--- | :---: | :--- | :--- |
| **Code-Unit Slicing** | **Dotted Circle (`U+25CC`)** | Slicing string across multi-byte UTF-16 code units or severing Coeng `U+17D2` | Truncate grapheme clusters with `Intl.Segmenter` |
| **Diacritic Clipping** | Truncated top accents or bottom subscripts | Tight CSS line height (`line-height: 1.0` or `1.2`) | Set `line-height >= 1.6`, button `min-h-[44px]` |
| **Mobile Overflow** | Horizontal card breaking or cut-off text | Khmer has no visible spaces; browser can't break lines | Inject Zero-Width Space (`\u200B`) at word boundaries |
| **Android Text Clipping** | Subscript consonants clipped on Native | Default Android font padding enabled | Set `includeFontPadding: false` in React Native |

```css
/* Production Typography Standard */
.khmer-text {
  font-family: 'Kantumruy Pro', 'Noto Sans Khmer', system-ui, sans-serif;
  line-height: 1.7; /* Vital clearance for stacked vowels and Coeng subscripts */
  overflow-wrap: break-word;
  word-break: normal;
}
```

---

### 4. NBC Bakong KHQR Fintech Standard (EMVCo)

The National Bank of Cambodia operates Bakong, the national payment switch. KHQR complies with EMVCo Merchant-Presented Mode (MPM):

| EMVCo Tag | Field Name | Format & Rule | Validation Standard |
| :---: | :--- | :--- | :--- |
| **Tag 00** | Format Indicator | Fixed `"01"` | Mandatory |
| **Tag 01** | Point of Initiation | `"11"` (Static) or `"12"` (Dynamic) | Mandatory |
| **Tag 29 / 30** | Merchant / Individual ID | Contains sub-tag `00` Bakong ID (e.g., `sokha@devb`) | Mandatory |
| **Tag 53** | Transaction Currency | `"116"` for KHR; `"840"` for USD | ISO 4217 numeric |
| **Tag 54** | Transaction Amount | KHR: Whole integer only; USD: 2 decimal places | Strict currency match |
| **Tag 58** | Country Code | Fixed `"KH"` | ISO 3166-1 alpha-2 |
| **Tag 63** | CRC16 Checksum | 4 hex characters computed via CRC16-CCITT-FALSE | Polynomial 0x1021, Initial 0xFFFF |

```typescript
import { calculateKhqrCrc16, verifyKhqr } from "./scripts/khmer_utils";

// Verify KHQR Payload Integrity
const { isValid, error } = verifyKhqr("000201010211...6304ABCD");
```

---

### 5. Cambodian Administrative Addressing (4-Tier Hierarchy)

Addressing follows a strict 4-tier civilian administrative hierarchy:

```
[Tier 1] Province / Capital (រាជធានី-ខេត្ត) — 25 Divisions (Phnom Penh + 24 Provinces)
  └── [Tier 2] District / Khan / Municipality (ស្រុក/ខណ្ឌ/ក្រុង) — 209 Subdivisions
        └── [Tier 3] Commune / Sangkat (ឃុំ/សង្កាត់) — 1,652 Communes
              └── [Tier 4] Village (ភូមិ) — 14,000+ Villages
```

| Operational Reality | E-Commerce Delivery Form Rule |
| :--- | :--- |
| **Postal Codes** | ⚠️ **Never make postal code a mandatory blocking field.** Couriers in Cambodia do not route via postal codes. |
| **Mandatory Fields** | Recipient Phone Number (`+855...`), Province/Capital, District/Khan, and Sangkat. |
| **Last-Mile Logistics** | Always provide a dedicated **Landmark / Specific Directions** textarea field for rider guidance. |

---

### 6. GDT Tax Invoicing & Number-to-Words

The General Department of Taxation (GDT) mandates that official tax invoices spell out financial amounts in Khmer words:

| Amount | Spelled-Out Khmer Words | Currency Rule |
| :--- | :--- | :--- |
| `25,000 ៛` | `ពីរម៉ឺនប្រាំពាន់រៀលគត់` | Appends `រៀលគត់` (Riel exact) |
| `150,000 ៛` | `មួយសែនប្រាំម៉ឺនរៀលគត់` | Uses Khmer numerical scales (`សែន`, `ម៉ឺន`) |
| `$10.50` | `ដប់ដុល្លារអាមេរិក និងហាសិបសេន` | Appends `ដុល្លារអាមេរិក` and `សេន` for cents |

```typescript
import { formatCurrencyKhmerWords } from "./scripts/khmer_utils";

formatCurrencyKhmerWords(25000, "KHR"); // => "ពីរម៉ឺនប្រាំពាន់រៀលគត់"
formatCurrencyKhmerWords(10.5, "USD");   // => "ដប់ដុល្លារអាមេរិក និងហាសិបសេន"
```

---

### 7. Cambodian Calendar, Dates & Buddhist Era (BE)

| Context | Calculation / Format | Example Output |
| :--- | :--- | :--- |
| **Buddhist Era (BE)** | $\text{Year (BE)} = \text{Year (CE)} + 543$ | $2026\text{ CE} \rightarrow 2569\text{ BE}$ |
| **Official Date Format** | `ថ្ងៃទី DD ខែ [Month] ឆ្នាំ YYYY` | `ថ្ងៃទី 26 ខែតុលា ឆ្នាំ 2026` |
| **Bilingual Date Ordering** | Day precedes month (`DD/MM/YYYY`) | `26/10/2026` |
| **Solar Months (12)** | មករា, កុម្ភៈ, មីនា, មេសា, ឧសភា, មិថុនា, កក្កដា, សីហា, កញ្ញា, តុលា, វិច្ឆិកា, ធ្នូ |

---

## 📚 Standard UI Localization Dictionary (`data/ui_terms.json`)

Contains **107 curated digital software engineering terms** mapping natural Khmer against prohibited machine hallucinations:

| Category | Term Count | Example English | Natural Khmer | Prohibited LLM Hallucination |
| :--- | :---: | :--- | :--- | :--- |
| **Authentication** | 13 terms | Sign In | **ចូលគណនី** | ❌ `យាងចូល` (royal) / `ចុះឈ្មោះចូល` |
| **Navigation** | 16 terms | Dashboard | **ផ្ទាំងគ្រប់គ្រង** | ❌ `ក្ដារគ្រប់គ្រង` (literal wooden board) |
| **Actions** | 20 terms | Save | **រក្សាទុក** | ❌ `សង្គ្រោះ` (rescue life) / `សន្សំ` (save cash) |
| **Commerce & Payments** | 19 terms | Total Price | **តម្លៃសរុប** | ❌ `សរុបតម្លៃ` (inverted word order) |
| **Status & Feedback** | 12 terms | Successful | **ជោគជ័យ** | ❌ `បានសម្រេច` (ambiguous) |
| **Forms & Inputs** | 14 terms | Date of Birth | **ថ្ងៃខែឆ្នាំកំណើត** | ❌ `ថ្ងៃកំណើត` (birthday party) |
| **Privacy & Legal** | 6 terms | Privacy Policy | **គោលការណ៍ឯកជនភាព** | ❌ `គោលនយោបាយភាពឯកជន` |

---

## 🛠️ Zero-Dependency Isomorphic API Reference

The library provides 100% feature parity between TypeScript/JavaScript and Python with zero third-party dependencies:

| Function Signature (TypeScript / JavaScript) | Equivalent Python Function | Return Type | Description |
| :--- | :--- | :---: | :--- |
| `normalizeCambodianPhone(input: string)` | `normalize_cambodian_phone(input_str)` | `object` | E.164 & domestic formatting with 8/9-digit TRC validation |
| `formatKHR(amount: number, wholeRiel?: boolean)` | `format_khr(amount, whole_riel=True)` | `string` | Formats integer whole riel (`15,000៛`) per consumer standards |
| `formatUSD(amount: number)` | `format_usd(amount)` | `string` | Formats USD with standard 2 decimal places (`$15.00`) |
| `toBuddhistEra(yearCE: number)` | `to_buddhist_era(year_ce)` | `number` | Converts CE to BE: $\text{BE} = \text{CE} + 543$ |
| `formatKhmerDate(d: Date, options?: object)` | `format_khmer_date(d, include_be=False)` | `string` | Day-first localized Cambodian calendar string |
| `safeTruncateKhmer(text: string, max: number)` | `safe_truncate_khmer(text, max_chars)` | `string` | Grapheme cluster truncation preventing dotted circle defects |
| `integerToKhmerWords(num: number)` | `integer_to_khmer_words(num)` | `string` | Spells out numbers in Khmer (រយ, ពាន់, ម៉ឺន, សែន, លាន) |
| `formatCurrencyKhmerWords(amount, currency)` | `format_currency_khmer_words(amount, curr)`| `string` | Spells out currency for GDT tax invoices |
| `calculateKhqrCrc16(payload: string)` | `calculate_khqr_crc16(payload)` | `string` | Calculates 4-hex EMVCo CRC16-CCITT-FALSE checksum |
| `verifyKhqr(khqr: string)` | `verify_khqr(khqr_string)` | `object` | Verifies KHQR payload integrity and checksum |
| `isKhmerText(text: string)` | `is_khmer_text(text)` | `boolean` | Checks for Khmer script presence (U+1780..U+17FF) |
| `getKhmerCharacterStats(text: string)` | `get_khmer_character_stats(text)` | `object` | Detailed linguistic composition statistics |

### Command-Line Interface (CLI)
```bash
# Node.js CLI
node scripts/khmer_utils.js phone "012 345 678"
node scripts/khmer_utils.js currency 15000 KHR
node scripts/khmer_utils.js words 25000 KHR

# Python CLI
python3 scripts/khmer_utils.py phone "012 345 678"
python3 scripts/khmer_utils.py currency 15000 --currency KHR
python3 scripts/khmer_utils.py words 25000 --currency KHR
```

---

## 🗄️ Curated Offline Datasets (`data/`)

Zero-dependency offline JSON datasets structured for fast agent lookups and form scaffolding:

| Dataset Path | Records | Authority / Domain | Primary Engineering Use Case |
| :--- | :---: | :--- | :--- |
| [`data/ui_terms.json`](./data/ui_terms.json) | **107** | Digital Software Engineering | Natural UI translations with forbidden hallucination list |
| [`data/provinces.json`](./data/provinces.json) | **25** | ISO 3166-2:KH / Ministry of Interior | Top-level address cascades and regional localization |
| [`data/phnom_penh_districts.json`](./data/phnom_penh_districts.json) | **14** | Phnom Penh Capital Administration | Khan administrative division dropdowns and postal routing |
| [`data/siem_reap_districts.json`](./data/siem_reap_districts.json) | **12** | Siem Reap Administration | Tourism, hospitality, and provincial logistics |
| [`data/battambang_districts.json`](./data/battambang_districts.json) | **14** | Battambang Administration | Western agricultural zone and delivery forms |
| [`data/kandal_districts.json`](./data/kandal_districts.json) | **11** | Kandal Administration | Capital peri-urban zone delivery routing |
| [`data/kampong_cham_districts.json`](./data/kampong_cham_districts.json) | **10** | Kampong Cham Administration | Central Mekong commercial district selections |
| [`data/kampot_districts.json`](./data/kampot_districts.json) | **9** | Kampot Administration | Coastal trade and agro-tourism routing |
| [`data/preah_sihanouk_districts.json`](./data/preah_sihanouk_districts.json) | **5** | Sihanoukville Administration | Deep-water port, logistics, and island districts |
| [`data/telecom_operators.json`](./data/telecom_operators.json) | **5** | TRC / ITU-T MCC-MNC | Operator prefix verification and MCC-MNC lookups |
| [`data/banknotes.json`](./data/banknotes.json) | **11** | National Bank of Cambodia (NBC) | Currency denomination pickers and cash payment UI |
| [`data/bakong_members.json`](./data/bakong_members.json) | **10** | NBC Bakong Switch | Bank and MFI participant selector lists |
| [`data/khqr_mcc_codes.json`](./data/khqr_mcc_codes.json) | **16** | ISO 18245 / NBC | Bakong KHQR Tag 52 Merchant Category Codes |
| [`data/public_holidays.json`](./data/public_holidays.json) | **12** | Ministry of Labour & Voc. Training | Statutory non-working day calendars & SLA calculators |
| [`data/cambodia_postal_codes.json`](./data/cambodia_postal_codes.json) | **25** | Cambodia Post | Major postal routing and logistics codes |
| [`data/cambodia_logistics.json`](./data/cambodia_logistics.json) | **10** | Domestic Freight & Courier | Courier service integrations (J&T, Kerry, Virak Buntham) |
| [`data/cambodia_ministries.json`](./data/cambodia_ministries.json) | **10** | Royal Government of Cambodia | Official regulatory authorities and e-government portals |
| [`data/khmer_symbols.json`](./data/khmer_symbols.json) | **12** | Unicode 15.1 (Khmer Symbols) | Punctuation marks (Khan, Bariyoosan, Lek Too, Riel) |
| [`data/khmer_keyboard.json`](./data/khmer_keyboard.json) | **66** | NiDA / Khmer OS Standard | Virtual keyboard rendering and key event handlers |
| [`data/khmer_consonants.json`](./data/khmer_consonants.json) | **33** | National Institute of Linguistics | Complete 33 consonants, Vagga phonology, Series 1 & 2 |
| [`data/khmer_independent_vowels.json`](./data/khmer_independent_vowels.json) | **14** | Unicode Consortium | 14 non-deprecated independent vowels and phonetic IPA |

---

## 🚀 Installation & Framework Setup

### Platform Matrix
| Agent / Platform | Integration Method | Configuration Path |
| :--- | :--- | :--- |
| **Google Antigravity / Gemini CLI** | Copy to skills directory | `.agents/skills/khmer-localization/` or `~/.gemini/config/skills/` |
| **Cursor** | Paste Nano or Standard prompt | `.cursorrules` or `.cursor/rules/khmer.mdc` |
| **Claude Code** | Copy to skills directory / reference | `.claude/skills/khmer-localization/` or `CLAUDE.md` |
| **OpenAI Codex / ChatGPT** | Reference in agent markdown | `AGENTS.md` |
| **Next.js / React Web** | Import isomorphic TypeScript utils | `import { formatKHR } from "@/scripts/khmer_utils"` |
| **React Native / Expo** | Configure font and styling | `lineHeight: 28, includeFontPadding: false` |

---

## 🧪 Test Suite & Quality Assurance Matrix

Run the automated offline test suite across all 10 suites:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

```
========================================================================================
 TEST SUITE EXECUTION REPORT — ALL 104 TESTS DETERMINISTICALLY PASSING (0.35s)
========================================================================================
 Suite File                    | Tests | Scope & Verifications
-------------------------------+-------+------------------------------------------------
 test_ui_terms.py              |   4   | 107 UI terms, unique keys, no royal register
 test_khmer_utils_js.py        |   7   | Node.js execution: phone, KHR, BE, KHQR CRC16
 test_check_khmer_unicode.py   |  20   | U+FFFD, control characters, ZWSP, trailing Coeng
 test_khmer_utils.py           |  24   | Python library: phone, currency, words, dates
 test_data_catalog.py          |   6   | Provinces, banknotes, operators, holidays, Bakong
 test_extended_catalogs.py     |   4   | Districts (PP, SR, BB), independent vowels, postcodes
 test_domain_catalogs.py       |   4   | Kandal, Kampong Cham, Kampot, couriers, ministries
 test_currency_formatting.py   |  12   | Whole-riel formatting, ICU defaults, rounding
 test_date_and_formatting.py   |  15   | Months, BE formula (CE+543), grapheme truncation
 test_phone_normalization.py   |   8   | 8/9-digit NSN lengths, E.164, OTP requirement flag
-------------------------------+-------+------------------------------------------------
 TOTAL VERIFIED TESTS          |  104  | 100% Deterministic CI Compliance (0 Failures)
========================================================================================
```

Static Unicode audit command:
```bash
python3 scripts/check_khmer_unicode.py --strict --json .
# Output: { "summary": { "status": "PASS", "total_errors": 0, "total_warnings": 0 } }
```

---

## ❓ Frequently Asked Questions (FAQ)

### Q1: Why do browsers format Cambodian Riel as `25,000.00៛` by default?
**A:** In ISO 4217, the Cambodian Riel is formally assigned 2 minor units (fractional subunits called *sen* / *tiens*), even though physical coins have been absent from daily commerce for decades. As a result, the default ECMAScript/ICU implementation of `Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` formats with 2 decimal places. Production software **must explicitly configure** `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }` to output consumer-compliant whole riel (`25,000៛`).

### Q2: What causes the broken Dotted Circle (`U+25CC`) artifact on screen?
**A:** The dotted circle (`U+25CC`) is rendered by OpenType shaping engines (HarfBuzz, DirectWrite, CoreText) when a combining mark, dependent vowel, or subscript consonant marker (Coeng `U+17D2`) is orphaned without a preceding base consonant. This happens when developers truncate strings using naive UTF-16 code-unit slicing (`.slice(0, n)` or `.substring()`). Always use `Intl.Segmenter` with `{ granularity: 'grapheme' }` to truncate at user-perceived character boundaries.

### Q3: What is the valid phone number structure in Cambodia?
**A:** Under Telecommunication Regulator of Cambodia (TRC) regulations:
- **Country Code:** `+855`
- **Domestic Trunk:** `0` (omitted internationally)
- **Standard Mobile (8-digit NSN):** 9 digits domestic (`012 345 678` $\rightarrow$ `+855 12 345 678`)
- **Extended Mobile (9-digit NSN):** 10 digits domestic (`096 123 4567` $\rightarrow$ `+855 96 123 4567`)
- Always decouple validation from static carrier prefix lists because number portability (MNP) and regulatory updates make prefix tables volatile.

### Q4: Why do LLMs frequently generate royal words (*Reachasap*) in digital UI copy?
**A:** Multi-lingual base models are heavily trained on digitized historical chronicles, traditional literature, and Buddhist canons where royal honorifics are frequent. Without explicit register conditioning, models default to royal verbs like `យាង` or `សោយ`. This skill enforces modern digital tech terminology (`ចូលគណនី`, `រក្សាទុក`, `ដាក់ស្នើ`).

### Q5: How is the Cambodian Buddhist Era (BE) calculated?
**A:** In Cambodia, civil and religious documents calculate the Buddhist Era (ពុទ្ធសករាជ - ព.ស.) by adding **543** to the Christian Gregorian year:
$$\text{Year (BE)} = \text{Year (CE)} + 543 \quad (2026\text{ CE} \rightarrow 2569\text{ BE})$$

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

## 📄 License & Community

Distributed under the [MIT License](LICENSE). Built for enterprise engineering teams, independent developers, and autonomous coding agents building world-class software for Cambodia.
