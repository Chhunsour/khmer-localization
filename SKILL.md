---
name: khmer-localization
description: >-
  Practical localization engineering for Khmer language (Cambodia).
  Use this skill when developing, translating, or reviewing software for
  Khmer-speaking users, handling Khmer Unicode and typography, configuring
  Cambodian phone number validation (+855), formatting USD and KHR currencies,
  or testing bilingual (Khmer/English) responsive web and mobile interfaces.
---

# Khmer Localization Engineering Skill

This skill guides AI coding agents in designing, translating, configuring, and verifying production-quality software for Khmer-speaking users and the Cambodian market.

It provides actionable procedures and checklists for natural UI copy, Unicode integrity, bilingual internationalization, Cambodian phone inputs, dual-currency formatting, and mobile typography.

---

## Workflow Procedures

### Step 1 — Inspect the Project
Before proposing changes or generating translations:
1. **Detect Existing Architecture:** Identify the project's i18n framework (e.g., `i18next`, `next-intl`, `vue-i18n`, `flutter_localizations`, or Android/iOS resource files). Reuse existing conventions and translation key naming structures rather than rewriting working systems.
2. **Inspect Typography & Fonts:** Check if web fonts or system fonts include Khmer script support (e.g., `Kantumruy Pro`, `Noto Sans Khmer`, `Khmer Sangam MN`, `Leelawadee UI`). Check global CSS for `line-height` rules.
3. **Audit Data Flow:** Inspect how phone numbers, currency amounts, and dates are stored, transmitted, and formatted.
4. **Locate Test Suites:** Check existing test runners (Jest, Vitest, Pytest, Playwright, Cypress) to add regression tests for Khmer localization.

---

### Step 2 — Understand the Language and Audience
When creating or reviewing Khmer UI content:
1. **Prioritize Natural Phrasing over Literal Translation:**
   - Avoid wooden machine translation (e.g. use `ចូលគណនី` for "Sign In", not `ចុះហត្ថលេខាលើ`; use `ដាក់ស្នើ` for "Submit", not `បញ្ជូនទៅកាន់ម៉ាស៊ីនបម្រើ`).
   - Consult the [Khmer Writing Guide](./references/khmer-writing-guide.md) for standard UI labels, buttons, form errors, empty states, and onboarding copy.
2. **Keep Mobile UI Copy Concise:** Khmer script is visually intricate. Long sentences on narrow viewports wrap excessively and push primary actions off-screen.
3. **Maintain Consistency:** Standardize key terminology (e.g., choose either `គណនី` or `ប្រវត្តិរូប` for Profile, and use it consistently across navigation, headings, and settings).
4. **Flag Ambiguities & Recommend Review:** If legal terms, industry jargon, or domain-specific phrases are ambiguous, highlight them explicitly to the user and recommend native Khmer speaker review.

---

### Step 3 — Protect Khmer Unicode Integrity
Khmer syllables rely on base consonants, subscript consonants (generated via Coeng `U+17D2`), dependent vowel signs, and diacritics:
1. **Never Strip Combining Marks:** Do not use aggressive regex replacements that strip non-ASCII characters or assume combining marks are rogue accents.
2. **Preserve Zero-Width Spaces (`U+200B`):** Khmer text does not use visible spaces between words. The Zero-Width Space (ZWSP) is standard in digital layouts for line-breaking. Never strip `\u200B` as unwanted whitespace.
3. **Prevent Syllable Slicing:** Avoid naive `.substring()` or `.slice()` calls that cut through combining marks or after `U+17D2`, which triggers the broken **dotted circle (`U+25CC`)**. Use grapheme-aware segmenters (`Intl.Segmenter` in JS/TS).
4. **Run Static Verification:** Run the provided Unicode verification script across translation files and source code:
   ```bash
   python3 scripts/check_khmer_unicode.py path/to/locales/
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

### Step 5 — Handle Cambodian Phone Numbers
1. **Three-Stage Pipeline:**
   - **Normalization:** Strip spaces, hyphens, brackets; convert Khmer numerals (`០-៩`) to ASCII digits; normalize `+855`, `00855`, or domestic trunk `0`.
   - **Syntax Validation:** Verify National Significant Number (NSN) length (8 or 9 digits after country code `+855`, or 9 to 10 digits domestically including leading `0`).
   - **Verification:** Understand that regex validation only checks syntax. Never claim a phone number is "active" or "verified" without an SMS OTP or carrier API check.
2. **Prefix Mutability:** Mobile prefixes (e.g. `012`, `096`, `088`) are regulated by the Telecommunication Regulator of Cambodia (TRC) and are subject to regulatory updates. Do not hardcode brittle single-carrier assumptions.
3. Consult the [Cambodia Regional Formatting Reference](./references/cambodia-formatting.md) for implementation utilities and official TRC prefix allocations.

---

### Step 6 — Format USD and KHR Currencies
Cambodia operates a dual-currency system:
1. **Use Platform-Native Formatting:** Format with `Intl.NumberFormat` rather than manual string concatenation.
2. **Respect Currency Rules:**
   - **Cambodian Riel (KHR / `៛`):** Format with **0 decimal places** (`25,000 ៛` or `KHR 25,000`). Riel has no sub-units/cents in circulation.
   - **United States Dollar (USD / `$`):** Format with **2 decimal places** (`$25.00`).
3. **Default to Latin Numerals in Commercial UI:** While Khmer numerals (`០-៩`) are culturally valuable, standard Cambodian digital banking and retail apps default to Latin numerals (`0-9`) for numeric amounts to ensure legibility and avoid financial input errors.
4. **Never Confuse Formatting with Conversion:** Never perform silent, hardcoded currency conversions (e.g. multiplying by 4000). Conversion must always require an explicit, verified exchange rate from an official source (such as the National Bank of Cambodia).

---

### Step 7 — Test the Actual User Experience
Run a systematic audit of the user interface:
1. **Mobile Viewport Testing:** Test on narrow mobile screens (320px–430px). Verify that longer Khmer translations do not break layouts, wrap off-screen, or overlap adjacent buttons.
2. **Vertical Clearance (Clipping):** Verify that CSS `line-height` is set to at least `1.6`–`1.8` and buttons have adequate vertical padding (`py-2` to `py-3`) so top vowel signs and bottom subscript consonants are not clipped.
3. **Dotted Circle Check:** Inspect rendered screens for dotted circles (`U+25CC`), which indicate broken character sequences or missing font glyphs.
4. **Empty and Loading States:** Verify that empty state messages and loading skeletons display natural Khmer placeholders.
5. **Report Outcomes:** After completing changes, summarize:
   - What localization changes were implemented.
   - Verification tests executed.
   - Remaining limitations and items requiring native speaker review.
