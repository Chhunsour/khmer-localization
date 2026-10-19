---
name: khmer-localization
description: >-
  Practical localization engineering for Khmer language (Cambodia).
  Use this skill when developing, translating, or reviewing software for
  Khmer-speaking users, handling Khmer Unicode and typography, configuring
  Cambodian phone number validation (+855), formatting USD and KHR currencies,
  setting up Bakong / KHQR payment displays, formatting Cambodian dates and
  Buddhist Era calendars, preventing mobile line-height clipping, inserting
  zero-width word breaks (\u200B), or testing bilingual (Khmer/English)
  responsive web and mobile interfaces.
---

# Khmer Localization Engineering Skill

This skill guides AI coding agents (Claude, Codex, ChatGPT, Gemini, and Antigravity) in designing, translating, configuring, and verifying production-quality software for Khmer-speaking users and the Cambodian market.

It provides actionable procedures, battle-tested code patterns, and automated verification for natural UI copy, Unicode integrity, bilingual internationalization, Cambodian phone inputs, dual-currency formatting, date/calendar conventions, and mobile typography.

---

## Agent Quick-Routing Matrix

When a user prompt involves Cambodian localization, consult this direct lookup table:

| User Task / Problem | Immediate Agent Action | Primary Reference |
| :--- | :--- | :--- |
| **Translate / review UI copy** | Use natural tech verbs (`ចូល`, `ដាក់ស្នើ`); avoid royal/monk vocabulary. | [Khmer Writing Guide](./references/khmer-writing-guide.md) |
| **Cambodian phone input (+855)** | Use `normalizeCambodianPhone` (8/9-digit NSN; decouple prefixes; require OTP). | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Currency formatting (KHR / USD)** | Configure `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }` for whole KHR. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **QR Payments / Banking (KHQR)** | Specify currency (KHR vs USD), recipient name, amount in whole riel or USD cents. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Dates, Calendars & Buddhist Era** | Use solar months (មករា..ធ្នូ), day-first format `DD/MM/YYYY`, $\text{BE} = \text{CE} + 543$. | [Cambodia Formatting Guide](./references/cambodia-formatting.md) |
| **Clipping diacritics / layout** | Apply `line-height: 1.6`–`1.8`, `min-h-[44px]`, `includeFontPadding: false` (Android). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Word breaking / container overflow** | Use `insertKhmerWordBreaks` with `Intl.Segmenter` + CSS `overflow-wrap: break-word`. | [Unicode & Typography](./references/unicode-and-typography.md) |
| **String truncation & dotted circles** | Truncate grapheme clusters using `Intl.Segmenter` (never slice after Coeng `U+17D2`). | [Unicode & Typography](./references/unicode-and-typography.md) |
| **Verify repository / CI check** | Run `python3 scripts/check_khmer_unicode.py --strict --json <path>` | [Checker Script](./scripts/check_khmer_unicode.py) |

---

## 5 Fatal AI Agent Pitfalls to Avoid

1. **The Social Register Trap:** Never output royal (*Reachasap* / រាជសព្ទ) or monk (*Sanghasap* / សង្ឃសព្ទ) vocabulary (e.g., `យាង`, `សោយ`, `និមន្ត`). Standard modern consumer software uses neutral, respectful tech terminology.
2. **The Code-Unit Slicing Trap:** Never truncate Khmer strings with naive `.slice(0, n)` or `.substring()`. Cutting after Coeng (`\u17D2`) or between a base consonant and a combining vowel generates an illegal sequence and renders a broken **dotted circle (`U+25CC`)**. Always use grapheme-aware segmenters (`Intl.Segmenter`).
3. **The Intl Currency Default Trap:** Never assume `Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` formats whole riel by default. In ECMAScript/ICU runtimes, it defaults to **2 decimal places (`25,000.00៛`)** due to ISO 4217 minor units. You **MUST** explicitly configure `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`.
4. **The Whitespace Stripping Trap:** Never run generic regexes like `replace(/\s+/g, '')` that strip Zero-Width Spaces (`\u200B` / ZWSP). Khmer relies on ZWSP for word breaking; stripping it causes text to overflow containers or break across consonants.
5. **The Carrier Prefix & Liveness Trap:** Never reject phone numbers because their 2- or 3-digit prefix is unlisted (prefixes change under TRC regulatory updates). Never claim a number is "active" or "verified" without an SMS OTP check.

---

## Workflow Procedures

### Step 1 — Inspect the Project
Before proposing changes or generating code:
1. **Detect Existing Architecture:** Identify the project's i18n framework (e.g., `i18next`, `next-intl`, `vue-i18n`, `flutter_localizations`, or Android/iOS resource files). Reuse existing conventions and translation key structures rather than rewriting working systems.
2. **Inspect Typography & Fonts:** Check if web fonts or system fonts include Khmer script support (e.g., `Kantumruy Pro`, `Noto Sans Khmer`, `Khmer Sangam MN`, `Leelawadee UI`). Check global CSS for `line-height` rules.
3. **Audit Data Flow:** Inspect how phone numbers, currency amounts, and dates are stored, transmitted, and formatted.
4. **Locate Test Suites:** Check existing test runners (Jest, Vitest, Pytest, Playwright, Cypress) to add regression tests for Khmer localization.

---

### Step 2 — Understand Language Registers and UI Phrasing
When creating or reviewing Khmer UI content:
1. **Prioritize Natural Modern Phrasing over Literal Translation:**
   - Avoid wooden machine translation (e.g. use `ចូលគណនី` for "Sign In", not `ចុះហត្ថលេខាលើ`; use `ដាក់ស្នើ` for "Submit", not `បញ្ជូនទៅកាន់ម៉ាស៊ីនបម្រើ`).
   - Consult the [Khmer Writing Guide](./references/khmer-writing-guide.md) for standard UI labels, buttons, form errors, empty states, and onboarding copy.
2. **Keep Mobile UI Copy Concise:** Khmer script is visually intricate. Long sentences on narrow viewports wrap excessively and push primary actions off-screen.
3. **Maintain Consistency:** Standardize key terminology (e.g., choose either `គណនី` or `ប្រវត្តិរូប` for Profile, and use it consistently across navigation, headings, and settings).
4. **Flag Ambiguities & Recommend Review:** If legal terms, industry jargon, or domain-specific phrases are ambiguous, highlight them explicitly to the user and recommend native Khmer speaker review.

---

### Step 3 — Protect Khmer Unicode & Grapheme Integrity
Khmer syllables rely on base consonants, subscript consonants (generated via Coeng `U+17D2`), dependent vowel signs, and diacritics:
1. **Never Strip Combining Marks:** Do not use aggressive regex replacements that strip non-ASCII characters or assume combining marks are rogue accents.
2. **Preserve Zero-Width Spaces (`U+200B`):** Khmer text does not use visible spaces between words. The Zero-Width Space (ZWSP) is standard in digital layouts for line-breaking. Never strip `\u200B` as unwanted whitespace.
3. **Prevent Syllable Slicing:** Avoid naive `.substring()` or `.slice()` calls that cut through combining marks or after `U+17D2`, which triggers the broken **dotted circle (`U+25CC`)**. Use grapheme-aware segmenters (`Intl.Segmenter` in JS/TS).
4. **Run Static Verification:** Run the provided Unicode verification script across translation files and source code:
   ```bash
   python3 scripts/check_khmer_unicode.py --strict path/to/locales/
   ```
5. Consult the [Unicode & Typography Reference](./references/unicode-and-typography.md) for deep-dive technical guidance on font fallbacks, OpenType shaping, and encoding safety.

---

### Step 4 — Implement Bilingual Internationalization
1. **Use Structured Translation Keys:** Avoid hardcoding language conditionals (`isKhmer ? "..." : "..."`) in component templates. Use namespaced keys in locale JSON or PO files.
2. **Handle Non-Inflected Plurals:** Khmer does not conjugate nouns for pluralization (`1 item` vs `5 items` both use the base noun `ទំនិញ`). Configure i18n plural rules to avoid appending artificial plural suffixes.
3. **Provide Predictable Fallbacks:** Ensure the fallback hierarchy defaults to Khmer (`km`) or English (`en`) gracefully if a translation key is missing.
4. **Preserve User Locale Selection:** Store the user's selected language in local storage, cookies, or user profile settings across navigation and browser restarts.
5. Refer to [Localization Examples](./examples/localization-examples.md) for before-and-after component architectures.

---

### Step 5 — Handle Cambodian Phone Numbers (+855)
1. **Three-Stage Pipeline:**
   - **Normalization (Stable Algorithm):** Strip spaces, hyphens, brackets, and dots; convert Khmer numerals (`០-៩`) to ASCII digits (`0-9`); normalize `+855`, `00855`, `855`, or domestic trunk `0`; and extract the National Significant Number (NSN).
   - **Syntax & Length Validation:** Verify NSN length under ITU-T Recommendation E.164 and Telecommunication Regulator of Cambodia (TRC) standards:
     - **8 digits NSN:** Standard mobile numbers (9 digits domestic with `0`, e.g. `012 345 678` -> `+855 12 345 678`).
     - **9 digits NSN:** Extended mobile numbers marked with `*` in the TRC plan (10 digits domestic with `0`, e.g. `096 123 4567` -> `+855 96 123 4567`).
   - **Verification Boundary (Liveness/Ownership):** Format validation checks structure and length only. Never claim a phone number is "active" or "verified" without an SMS OTP or carrier network check.
2. **Decouple Normalization from Prefix Lookups:** Carrier prefix allocations (e.g. `012`, `096`, `088`) change with TRC regulatory updates, mergers, and Mobile Number Portability (MNP). Do not reject valid 8- or 9-digit numbers simply because a prefix table is unlisted.
3. Consult the [Cambodia Regional Formatting Reference](./references/cambodia-formatting.md) for direct TRC sources (verified October 2026) and normalization utilities.

---

### Step 6 — Format USD, KHR Currencies & KHQR
Cambodia operates a dual-currency economy:
1. **Use Platform-Native Formatting:** Format with `Intl.NumberFormat` rather than manual string concatenation.
2. **Explicitly Configure Fractional Digits:**
   - **Intl Default Pitfall:** In standard ECMAScript / ICU implementations, KHR defaults to **2 decimal places (`25,000.00៛`)** per ISO 4217 minor units.
   - **Explicit Whole-Riel Display:** For consumer retail and banking, whole-riel prices without `.00` are expected. Developers **MUST explicitly pass `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`** to format whole riel (`25,000៛`).
   - **Fractional Riel & Rounding:** When prorated billing or conversion produces fractional riel, explicitly define rounding rules (half-expand / `Math.round`).
   - **United States Dollar (USD / `$`):** Format with **2 decimal places** (`minimumFractionDigits: 2, maximumFractionDigits: 2`).
3. **Default to Latin Numerals in Commercial UI:** While Khmer numerals (`០-៩`) are culturally valuable, standard Cambodian digital banking and retail apps default to Latin numerals (`0-9`) for numeric amounts to ensure legibility and avoid financial input errors.
4. **Never Confuse Formatting with Conversion:** Never perform silent, hardcoded currency conversions (e.g. multiplying by 4000). Conversion must always require an explicit, verified exchange rate from an official source (such as the National Bank of Cambodia - NBC).
5. **Bakong / KHQR Standards:** Always display the merchant name and exact currency alongside QR codes (`KHR` in whole riel, `USD` in dollars and cents).

---

### Step 7 — Format Dates, Times & Buddhist Era (BE)
1. **Solar Months in Khmer:** Format months with standard names (មករា, កុម្ភៈ, មីនា, មេសា, ឧសភា, មិថុនា, កក្កដា, សីហា, កញ្ញា, តុលា, វិច្ឆិកា, ធ្នូ).
2. **Day-First Conventions:** Display dates in `DD/MM/YYYY` numeric format or `ថ្ងៃទីD ខែ[Month] ឆ្នាំYYYY` localized format.
3. **Buddhist Era Conversion:** For legal, governmental, or traditional contexts:
   $$\text{Year (BE)} = \text{Year (CE)} + 543$$
   *(Example: $2026\text{ CE} + 543 = 2569\text{ BE}$)*
4. **Time & Timezone:** Cambodia is Indochina Time (**ICT — UTC+07:00**). Use 12-hour periods (ព្រឹក `AM`, រសៀល `afternoon`, ល្ងាច `evening`, យប់ `night`) or 24-hour time.

---

### Step 8 — Configure Typography, Line Heights & Word Breaking
1. **Vertical Clearance (Clipping Prevention):** Set CSS `line-height: 1.6`–`1.8` minimum and buttons to `min-h-[44px]` with `py-2.5` to `py-3` padding. On Android React Native, set `includeFontPadding: false`.
2. **Safe Word Breaking:** Khmer does not use spaces between words. To avoid horizontal text overflow on narrow mobile screens (320px–390px), insert Zero-Width Spaces (`\u200B`) at word boundaries using `Intl.Segmenter` and apply CSS `overflow-wrap: break-word`.
3. **Cross-Platform Font Stack:** Use `Kantumruy Pro` (Google Fonts) or system fallbacks (`Khmer Sangam MN`, `Noto Sans Khmer`, `Leelawadee UI`).

---

### Step 9 — Verify with Automated Tooling & Report
1. **Automated Verification:** Run the project's test suite and strict Unicode analysis:
   ```bash
   python3 -m unittest discover -s tests -v
   python3 scripts/check_khmer_unicode.py --strict --json .
   ```
2. **Visual Inspection:** Verify on mobile viewports (320px–430px) for text wrapping, lack of dotted circles (`U+25CC`), and button layout stability.
3. **Report Outcomes:** Summarize changes implemented, verification results, and any items requiring native speaker review.
