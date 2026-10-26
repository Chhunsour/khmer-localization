---
name: khmer-localization
description: >-
  Production-grade localization engineering for Khmer language (Cambodia).
  Use this skill when developing, translating, auditing, or reviewing software
  for Cambodian users. Covers Khmer Unicode integrity, Coeng subscripts, ZWSP
  preservation, Chuon Nath collation, +855 phone normalization, minor-unit
  dual currency (USD/KHR), recursive number-to-words spellouts, Bakong KHQR
  EMVCo TLV parsing & CRC16 calculation, 4-tier administrative addresses,
  Buddhist Era dates, mobile line-height clipping prevention, and bilingual
  React, Next.js, React Native, Node.js, and Python application architectures.
---

# Khmer Localization Engineering Skill (Cambodia)

This skill guides AI coding agents (Claude, Codex, ChatGPT, Gemini, Antigravity) in designing, translating, configuring, auditing, and verifying production-quality software for Khmer-speaking users and the Cambodian market.

It provides actionable procedures, battle-tested code patterns, automated audit tooling (`scripts/audit_khmer_i18n.py`), and a strict Unicode verification engine (`scripts/check_khmer_unicode.py`) with zero runtime dependencies.

---

## 9-Step AI Agent Operational Workflow

When assigned any localization, translation, or feature task in a repository with Khmer content, you **MUST** follow this structured 9-step workflow:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      9-STEP AGENT WORKFLOW                             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Detect Stack ──────> 2. Map Flows ───────> 3. Inspect Tests         │
│         │                      │                       │               │
│ 4. Minimal Plan ──────> 5. Apply Changes ───> 6. Add Regressions       │
│         │                      │                       │               │
│ 7. Run Checks ────────> 8. Inspect UI ──────> 9. Honest Report         │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Detect Project Stack & Existing Architecture
Never assume every project uses Next.js or `react-i18next`. Autodetect the actual technology stack before touching code:
- **Next.js / React Web:** Look for `next-intl`, `next-i18next`, `react-intl`, or custom locale providers. Check `next.config.js`, `app/[locale]`, or `pages/_app.tsx`.
- **React Native / Expo:** Look for `i18n-js`, `react-i18next`, or custom JSON dictionaries. Check `includeFontPadding: false` on Android and mobile text styles.
- **Vue / Nuxt:** Look for `vue-i18n` or `@nuxtjs/i18n`.
- **Node.js / Express / NestJS:** Check backend locale middleware, request headers (`Accept-Language`), and database schema.
- **Python (Django / Flask / FastAPI):** Check `django.utils.translation`, `Babel`, `Flask-Babel`, or custom helper modules.
- **No Framework Found:** Do **NOT** force a heavy external library for a small task. Recommend a minimal typed dictionary or use the lightweight built-in helpers in `scripts/khmer_utils.js` or `scripts/khmer_utils.py`.

### Step 2: Identify Localization Requirements & Affected Flows
Trace the entire user flow affected by the change:
- **User Facing Copy:** Navigation, headers, buttons, form placeholders, validation errors, and empty states.
- **Financial Calculations:** Pricing displays, cart calculations, VAT/tax, invoice totals, and currency switches (KHR vs USD).
- **Communication & Auth:** Cambodian phone number input (+855, mobile vs fixed-line, SMS OTP expectations).
- **Payments & QR:** Bakong KHQR payloads, merchant IDs, EMVCo TLV tags, and CRC16 checksums.
- **Delivery & Addresses:** 4-tier hierarchy (Province, District/Khan, Commune/Sangkat, Village).

### Step 3: Inspect Existing Code & Run Baseline Checks
Before making any edits:
1. Run existing tests to ensure the working tree is clean.
2. Run the Khmer localization audit tool to find existing defects:
   ```bash
   python3 scripts/audit_khmer_i18n.py --locales <path-to-locales> --src <path-to-src>
   ```
3. Run the strict Unicode integrity checker:
   ```bash
   python3 scripts/check_khmer_unicode.py --strict --json .
   ```

### Step 4: Create a Targeted, Minimal Implementation Plan
Formulate a minimal plan consistent with the project's architecture:
- Preserve working functionality; do not rewrite undamaged modules.
- Choose natural terminology from `data/ui_terms.json`.
- Preserve Zero-Width Spaces (`\u200B`) and combining marks.
- Follow the project's formatting, naming, and style conventions.

### Step 5: Apply Changes Consistent with Architecture
Implement the modifications:
- For web/mobile forms, ensure minimum CSS `line-height: 1.6`–`1.8` to prevent vertical clipping of Khmer stacked vowels (e.g. U+17B8, U+17BA) and Coeng subscripts (U+17D2).
- Use `Intl.Segmenter` or `safeTruncateKhmer` for text truncation (never cut after Coeng `U+17D2` or slice raw UTF-16 code units).
- Use integer minor units for monetary totals (`calculate_money_total`) to prevent floating-point drift.
- Ensure Cambodian Riel (`KHR`) displays as whole numbers without `.00` decimals in consumer UI.

### Step 6: Add or Update Regression Tests
Never ship changes without test coverage:
- Add table-driven unit tests for new utility functions or edge cases.
- Test telephone normalization with domestic `0...`, international `+855...`, landline `023...`, and short codes (`117`, `119`).
- Test large numbers in `integer_to_khmer_words` (millions, billions, trillions, negative values).
- Test KHQR CRC16 calculation and TLV tag extraction.

### Step 7: Run Checks, Linter, and Test Suites
Execute the test runner and verify zero errors:
```bash
# Python test suite
python3 -m unittest discover -s tests -p "test_*.py" -v

# Strict Unicode check across all files
python3 scripts/check_khmer_unicode.py --strict --json .

# I18n audit scanner
python3 scripts/audit_khmer_i18n.py --locales <path> --src <path>
```

### Step 8: Inspect Visual Rendering & Layout Stability
When browser or device inspection is available:
- Verify layout on 320px–390px viewports (iPhone SE / Android standard).
- Check that multi-line buttons do not overflow containers.
- Confirm there are no broken **dotted circles (`U+25CC`)** caused by unattached combining vowels or orphan Coeng markers.

### Step 9: Report Honestly & Transparently
In your final report to the user, you **MUST** explicitly state:
1. **What was changed:** Precise list of files modified or created.
2. **Commands executed & output:** Exact test commands and verification tool outputs.
3. **What could NOT be automatically verified:** E.g., visual rendering on physical Android devices, actual SMS OTP delivery, or live Bakong bank settlement.
4. **Assumptions requiring human confirmation:** E.g., brand-specific tone of voice, legal contract wording, or custom merchant credentials.

---

## 4-Layer Quality & Audit Governance

The localization auditor (`scripts/audit_khmer_i18n.py`) classifies findings into 4 distinct governance layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                       4 GOVERNANCE LAYERS                              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. [AUTOMATED_ERROR / WARNING] Deterministic static defects            │
│    - Missing / orphaned keys, placeholder mismatches, decimal KHR      │
│    - Royal/monastic register words, destructive regexes                │
│                                                                        │
│ 2. [HUMAN_REVIEW_REQUIRED] Linguistic & contextual tone               │
│    - Tone appropriateness, natural phrasing, cultural sensitivity       │
│                                                                        │
│ 3. [VISUAL_INSPECTION_REQUIRED] Device viewport rendering              │
│    - Subscript clipping on 320px screens, button wrap, font fallback  │
│                                                                        │
│ 4. [EXTERNAL_VERIFICATION_REQUIRED] Third-party provider checks        │
│    - Live Bakong KHQR settlement, active SIM carrier OTP delivery      │
└────────────────────────────────────────────────────────────────────────┘
```

Never claim static analysis alone guarantees that a translation is natural or that a mobile layout renders perfectly on all hardware.

---

## Machine-Readable Data Catalogs (`data/`) & Metadata Registry

Consult `data/METADATA.json` for verified source authorities, update procedures, and licensing for all 21 catalogs:

| Catalog File | Records | Authority / Source | Primary Usage |
| :--- | :--- | :--- | :--- |
| `data/ui_terms.json` | 100+ | Industry Standard / Tech Lexicon | Clean UI translations; prohibits hallucinations |
| `data/provinces.json` | 25 | National Institute of Statistics / ISO 3166-2:KH | Province & capital dropdowns |
| `data/banknotes.json` | 11 | National Bank of Cambodia (NBC) | Currency cash handling & cash register UI |
| `data/telecom_operators.json` | 10 | Telecommunication Regulator of Cambodia (TRC) | Carrier detection & MCC-MNC codes |
| `data/public_holidays.json` | 22 | Royal Government Sub-Decree (Anukret) | Payroll, working days, and calendar UI |
| `data/bakong_members.json` | 14 | NBC Bakong Payment System | Bank selection & KHQR acquiring bank routing |
| `data/khqr_mcc_codes.json` | 10 | ISO 18245 / NBC KHQR Standard | Merchant Category Codes for KHQR Tag 52 |
| `data/khmer_symbols.json` | 8 | Unicode Standard / Chuon Nath | Typography symbols (Khan, Bariyoosan, Lek Too) |
| `data/khmer_keyboard.json` | 18 | NiDA Standard Keyboard Mapping | Virtual keyboard layouts & key mappings |
| `data/phnom_penh_districts.json`| 14 | Ministry of Interior (MoI) | All 14 Khans of Phnom Penh capital |
| `data/siem_reap_districts.json` | 12 | Ministry of Interior (MoI) | All 12 districts of Siem Reap province |
| `data/battambang_districts.json`| 14 | Ministry of Interior (MoI) | All 14 districts of Battambang province |
| `data/kandal_districts.json`    | 11 | Ministry of Interior (MoI) | All 11 districts of Kandal province |
| `data/kampong_cham_districts.json`| 10 | Ministry of Interior (MoI) | All 10 districts of Kampong Cham province |
| `data/kampot_districts.json`    | 9  | Ministry of Interior (MoI) | All 9 districts of Kampot province |
| `data/preah_sihanouk_districts.json`| 5 | Ministry of Interior (MoI) | All 5 coastal districts of Preah Sihanouk |
| `data/khmer_consonants.json`   | 33 | Chuon Nath Dictionary / MoEYS | 33 consonants with series 1/2 and phonology |
| `data/khmer_independent_vowels.json`| 14| Unicode Standard / MoEYS | 14 non-deprecated independent vowels |
| `data/cambodia_postal_codes.json`| 12| Cambodia Post / MPTC | 6-digit postal codes (optional for delivery) |
| `data/cambodia_logistics.json` | 10 | Cambodian Logistics Association | Express couriers & delivery integrations |
| `data/cambodia_ministries.json`| 5  | Royal Government of Cambodia | Regulatory ministries & government portals |

---

## Agent Quick-Routing Matrix

| User Task / Problem | Immediate Agent Action | Primary Reference |
| :--- | :--- | :--- |
| **Token-efficient agent cheat sheet** | Copy-paste zero-shot snippets for KHR, BE, ZWSP, phone, CRC16, and UI lookups. | [Agent Fast Path](./references/agent-fast-path.md) |
| **System prompts for Cursor / Claude** | Inject pre-tuned 45t, 120t, or 250t prompts into `.cursorrules` or `CLAUDE.md`. | [Agent System Prompts](./prompts/agent-system-prompts.md) |
| **Audit repository for i18n bugs** | Run `python3 scripts/audit_khmer_i18n.py --locales <path> --src <path>`. | [Audit Script](./scripts/audit_khmer_i18n.py) |
| **Prevent AI hallucinations** | Audit top 10 LLM failure modes (royal words, inverted word order, Coeng slicing). | [Khmer AI Guardrails](./references/khmer-ai-guardrails.md) |
| **Standard UI dictionary (100+ terms)** | Check natural UI copy vs avoid hallucinated machine translation in `data/ui_terms.json`. | [UI Terms Catalog](./data/ui_terms.json) |
| **Cambodian phone input (+855)** | Use `normalizeCambodianPhone` (8/9-digit NSN, landline `023`, emergency `117/119`). | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Currency formatting (KHR / USD)** | Whole-riel integers (`25,000៛`, no `.00`); minor-unit `calculateMoneyTotal`. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **QR Payments / Fintech (KHQR)** | Generate & parse EMVCo TLV payloads, validate CRC16, extract Bakong account. | [Khmer Fintech & KHQR](./references/khmer-fintech-and-khqr.md) |
| **Addresses & delivery forms** | Model 4-tier hierarchy: Province (`រាជធានី/ខេត្ត`) $\rightarrow$ District $\rightarrow$ Sangkat $\rightarrow$ Village. | [Administrative Divisions](./references/cambodia-administrative-divisions.md) |
| **Number to Khmer words (Invoices)** | Convert amounts to formal Khmer currency words (`ពីរម៉ឺនប្រាំពាន់រៀលគត់`) for GDT. | [Collation & Number Words](./references/khmer-collation-and-number-words.md) |
| **Khmer alphabetical sorting** | Use `sortKhmerWords` per Chuon Nath dictionary order (pure Python & JS `Intl.Collator`). | [Collation & Number Words](./references/khmer-collation-and-number-words.md) |
| **Dates, Calendars & Buddhist Era** | Use solar months (មករា..ធ្នូ), day-first format `DD/MM/YYYY`, $\text{BE} = \text{CE} + 543$. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Clipping diacritics / layout** | Apply `line-height: 1.6`–`1.8`, `min-h-[44px]`, `includeFontPadding: false` (Android). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **String truncation & dotted circles** | Truncate grapheme clusters using `Intl.Segmenter` (never slice after Coeng `U+17D2`). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Runnable E-Commerce Example** | Check Python and JS runnable checkout flows with KHQR and spelled-out invoices. | [E-Commerce Checkout Example](./examples/ecommerce_checkout.py) |
| **Runnable HR / Payroll Example** | Check Python and JS payroll flows with Chuon Nath collation and payslip generation. | [HR Payroll Example](./examples/hr_payroll.py) |
| **Bilingual React Form Component** | Production-ready React/Next.js bilingual component with dynamic `lang="km"`. | [React Khmer Form](./examples/react_khmer_form.tsx) |
| **Verify repository / CI check** | Run `python3 scripts/check_khmer_unicode.py --strict --json <path>`. | [Checker Script](./scripts/check_khmer_unicode.py) |

---

## 5 Fatal AI Agent Pitfalls to Avoid

1. **The Social Register Trap:** Never output royal (*Reachasap* / រាជសព្ទ) or monk (*Sanghasap* / សង្ឃសព្ទ) vocabulary (e.g., `យាង`, `សោយ`, `និមន្ត`). Standard modern consumer software uses neutral, respectful tech terminology.
2. **The Code-Unit Slicing Trap:** Never truncate Khmer strings with naive `.slice(0, n)` or `.substring()`. Cutting after Coeng (`\u17D2`) or between a base consonant and a combining vowel generates an illegal sequence and renders a broken **dotted circle (`U+25CC`)**. Always use grapheme-aware segmenters (`Intl.Segmenter` or `safeTruncateKhmer`).
3. **The Intl Currency Default Trap:** Never assume `Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` formats whole riel by default. In ECMAScript/ICU runtimes, it defaults to **2 decimal places (`25,000.00៛`)** due to ISO 4217 minor units. You **MUST** explicitly configure `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`.
4. **The Whitespace Stripping Trap:** Never run generic regexes like `replace(/\s+/g, '')` that strip Zero-Width Spaces (`\u200B` / ZWSP). Khmer relies on ZWSP for word breaking; stripping it causes text to overflow containers or break across consonants.
5. **The Carrier Prefix & Liveness Trap:** Never reject phone numbers because their 2- or 3-digit prefix is unlisted (prefixes change under TRC regulatory updates). Never claim a number is "active" or "verified" without an SMS OTP check.
