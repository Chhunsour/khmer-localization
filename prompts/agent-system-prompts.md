# Production Agent System Prompts for Khmer Localization

Pre-tuned, token-efficient system prompts for AI coding agents (Claude Code, Cursor, Windsurf, Gemini, OpenAI, GitHub Copilot).

Adding these prompt snippets directly into your project's agent configuration file (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, or system prompt) prevents the most common LLM Khmer hallucinations while consuming minimal token budget.

---

## 1. Nano Tier (45 Tokens) — High Token Savings

Best for: General coding assistants, multi-lingual codebases, tight context budgets (`.cursorrules`, Claude Code brief instructions).

```markdown
### Khmer Localization Rules
- Word Order: Strict [Noun] + [Adjective] (e.g., "Total Price" -> "តម្លៃសរុប", never "សរុបតម្លៃ").
- Currency: Khmer Riel (KHR) has zero decimal places/sub-units (e.g., "15,000 KHR" or "១៥,០០០ រៀល").
- Register: Professional modern digital tone. Never use royal register (e.g., avoid យាង, សោយ, ព្រះ).
- Truncation: Never slice strings by raw byte or code-unit index; use Intl.Segmenter(..., { granularity: 'grapheme' }) to avoid orphan subscripts (Coeng).
```

---

## 2. Standard Tier (120 Tokens) — Web & Mobile Applications

Best for: Frontend / Fullstack web and mobile apps, UI localization, form validations, i18n workflows.

```markdown
### Khmer (ភាសាខ្មែរ) Engineering & Localization Guardrails
1. Register & Tone: Standard modern digital Khmer. Avoid royal/monastic register (no យាង, សោយ, ព្រះ). Use direct natural phrasing (e.g., "Settings" -> "ការកំណត់", "Save" -> "រក្សាទុក", "Search" -> "ស្វែងរក").
2. Word Order: Strictly [Noun] + [Adjective] (e.g., "Active Users" -> "អ្នកប្រើប្រាស់សកម្ម", "New Password" -> "ពាក្យសម្ងាត់ថ្មី").
3. Currency: KHR uses comma thousand separators without decimals (10,000 រៀល). Dual currency displays both USD ($2.50) and KHR (10,000 ៛).
4. Phone Numbers: Cambodian phone format is 9-10 digits starting with 0 or +855 (prefixes: 010-018, 060-099). Always normalize to E.164 (+855...) before database storage.
5. Unicode Safety: Never split strings between base consonants and subscript signs (Coeng U+17D2). Use grapheme cluster segmentation for UI truncation. Do not remove Zero-Width Space (U+200B) where present.
```

---

## 3. Enterprise / Fintech Tier (250 Tokens) — Banking, Payments & Compliance

Best for: Payment gateways, KHQR / Bakong integrations, microfinance, accounting, official documents.

```markdown
### Khmer Fintech & Digital Commerce Guardrails
- Regulatory Context: National Bank of Cambodia (NBC) and Bakong standards.
- Currency Rules:
  * Khmer Riel (KHR / ៛): Integer amounts only. Decimals (tiens/sen) do not exist in circulation. Format: "125,000 ៛" or "125,000 KHR".
  * US Dollar (USD / $): Standard 2 decimal places ($12.50).
  * In formal receipts, provide spelled-out Khmer words (e.g., "មួយម៉ឺនរៀលគត់" for 10,000 KHR).
- KHQR Specifications:
  * QR Code standard: EMVCo merchant-presented QR code with CRC16-CCITT (polynomial 0x1021, initial 0xFFFF).
  * Payload Tag 53 currency codes: "116" for KHR, "840" for USD.
  * Tag 54 amount: KHR must not have decimal fraction; USD must have two decimals.
- Date & Calendar Systems:
  * Civil Standard: Gregorian calendar with Khmer localized month names (មករា, កុម្ភៈ, ...).
  * Buddhist Era (ព.ស.): Gregorian Year + 543 (e.g., 2026 CE -> 2569 BE).
- Phrasing & Terminology Standards:
  * "Transfer" -> "ផ្ទេរប្រាក់"
  * "Account Balance" -> "សមតុល្យគណនី"
  * "Transaction History" -> "ប្រវត្តិប្រតិបត្តិការ"
  * "Successful" -> "ជោគជ័យ" | "Failed" -> "បរាជ័យ"
- Typography & Layout:
  * Enforce CSS line-height >= 1.6 for Khmer text elements to prevent subscript clipping (Coeng U+17D2).
  * Recommended fonts: 'Kantumruy Pro', 'Hanuman', 'Noto Sans Khmer', system-ui.
- Fiscal & Invoicing Standards (GDT Compliance):
  * Official Tax Invoice title must be "វិក្កយបត្រអាករ" (Tax Invoice), never "វិក្កយបត្រលក់".
  * Tax ID (TIN / VATTIN): 9 digits, optionally prefixed by branch (e.g., K001-123456789).
  * Invoices quoted in USD must include NBC daily exchange rate, KHR total, and spelled-out words ending with "រៀលគត់".
```

---

## 4. Copy-Paste Configuration File Templates

### A. Cursor Rules (`.cursorrules` or `.cursor/rules/khmer.mdc`)

```markdown
---
description: Khmer language and Cambodian localization standards
globs: ["**/*.{ts,tsx,js,jsx,json,vue,svelte,py}"]
---

# Khmer Language Rules
- Use modern standard digital Khmer (no royal vocabulary like យាង or សោយ).
- Follow Khmer grammar: [Noun] + [Adjective] (e.g., "តម្លៃសរុប", not "សរុបតម្លៃ").
- KHR currency formatting: Integer amounts only (e.g., 50,000 ៛), never fractional cents.
- String slicing: Always use Intl.Segmenter(locale, { granularity: 'grapheme' }) to prevent corrupting Coeng clusters.
- Phone formatting: Accept local '012 345 678' and convert to E.164 '+85512345678'.
```

### B. Claude Code (`CLAUDE.md`)

```markdown
# Khmer Localization Protocol
When writing, reviewing, or generating code involving Khmer language (km / km-KH):
- Verify translations against data/ui_terms.json in this repository.
- Ensure all text truncation uses scripts/khmer_utils.ts or scripts/khmer_utils.py.
- Check that KHR currency formatting never includes decimal points.
- Verify Unicode integrity using `python3 scripts/check_khmer_unicode.py --strict`.
```

### C. Windsurf (`.windsurfrules`)

```markdown
Khmer Localization:
- Always use professional digital register; do not use royal words.
- Respect Khmer word order (Noun before Adjective).
- Format KHR without decimal points. Format Cambodian phone numbers to E.164.
- Prevent Coeng splitting in UI text by using grapheme cluster segmentation.
```

---

## 5. Token Savings Comparison

| Method | Context Tokens Per Query | Hallucination Risk | Developer Integration Effort |
| :--- | :---: | :---: | :---: |
| Full Documentation in Prompt | ~4,500 tokens | Low | High (slow, burns context window) |
| Enterprise Tier Prompt | ~250 tokens | Very Low | Paste once in `.cursorrules` or `CLAUDE.md` |
| Standard Tier Prompt | ~120 tokens | Low | Paste once in `.cursorrules` or `CLAUDE.md` |
| Nano Tier Prompt | ~45 tokens | Low-Medium | Ultra-lightweight, fits anywhere |
| No System Prompt | 0 tokens | **Very High** (royal words, inverted order, broken Coeng) | None |
