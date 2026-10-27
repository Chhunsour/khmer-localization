# Extended 9-Step AI Agent Workflow & Governance

This reference details the full 9-step operational lifecycle and 4-layer quality governance model for software engineering in Cambodian Khmer localization tasks.

---

## 9-Step AI Agent Operational Workflow

When assigned any localization, translation, or feature task in a repository with Khmer content, AI agents should follow this structured workflow:

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
- Choose natural terminology using `khmer-utils lookup "<term>"` or `data/ui_terms.json`.
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
In your final report to the user, explicitly state:
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
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

Never claim static analysis alone guarantees that a translation is natural or that a mobile layout renders perfectly on all hardware.
