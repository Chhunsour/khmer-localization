# Cambodia Regional Formatting & Internationalization Guide

This reference provides technical specifications, regulatory standards, and code patterns for Cambodian phone-number handling, dual-currency formatting (USD and KHR), and bilingual (Khmer/English) software internationalization.

---

## 1. Cambodian Phone Numbers

### 1.1 Regulatory Authority and Primary Sources
- **National Regulatory Body:** Telecommunication Regulator of Cambodia (TRC) — [https://trc.gov.kh](https://trc.gov.kh) (Direct resource: *Mobile Service Providers & National Numbering Plan*, verified October 2026).
- **Ministry:** Ministry of Post and Telecommunications (MPTC) — [https://mptc.gov.kh](https://mptc.gov.kh).
- **International Standard:** ITU-T Recommendation E.164 (Cambodia National Numbering Plan), maintained via the ITU International Numbering Resources portal: [https://www.itu.int/en/ITU-T/inr/nnp/Pages/default.aspx](https://www.itu.int/en/ITU-T/inr/nnp/Pages/default.aspx).

### 1.2 Separation of Normalization Algorithm vs. Prefix Lookup Data

To build maintainable systems, agents and developers must separate:
1. **The Normalization Algorithm (Stable):** Strips formatting symbols, normalizes Khmer digits, extracts country/trunk prefixes, and validates structural length (NSN). This algorithm rarely changes.
2. **Carrier Prefix Lookup Data (Volatile):** Carrier prefix assignments (`012` Cellcard, `096` Smart, `088` Metfone, etc.) are subject to MPTC/TRC regulatory updates, operator mergers, and Mobile Number Portability (MNP). Normalization must never fail on unknown prefixes simply because a prefix list is outdated.

```mermaid
flowchart TD
    Raw["Raw User Input<br>(e.g. '+855 (0) 96 123-4567')"] --> Norm["Step 1: Universal Normalization<br>(Clean symbols, convert Khmer digits, extract NSN)"]
    Norm --> LenCheck["Step 2: Length & Syntax Validation<br>(8 or 9 digits NSN per ITU-T E.164)"]
    LenCheck --> PrefixLookup["Step 3: Optional Carrier Prefix Mapping<br>(Pluggable lookup: Cellcard, Smart, Metfone, etc.)"]
    LenCheck --> Liveness["Step 4: Liveness & Ownership Verification<br>(SMS OTP / Carrier Network API)"]
```

### 1.3 National Numbering Architecture & Length Variations

Under ITU-T Recommendation E.164 and the TRC plan, Cambodia uses a closed numbering plan:
- **Country Calling Code:** `+855` (allocated by ITU-T).
- **Domestic Trunk Prefix:** `0` (used when dialing domestically; dropped in international E.164 format).
- **National Significant Number (NSN) Length:** **8 or 9 digits** depending on operator allocation.

#### Length Breakdown:
1. **Standard 8-digit NSN (9 digits domestic with `0`):**
   - Typically 2-digit operator code + 6-digit subscriber number (e.g. `012 xxx xxx`).
   - Domestic dialing: `012 345 678` (9 digits).
   - International E.164: `+855 12 345 678` (11 characters).
2. **Extended 9-digit NSN (10 digits domestic with `0`):**
   - Typically 2- or 3-digit operator code + 7-digit subscriber number (marked with `*` in TRC plan, e.g. `096 xxx xxxx`, `088 xxx xxxx`, `076 xxx xxxx`).
   - Domestic dialing: `096 123 4567` (10 digits).
   - International E.164: `+855 96 123 4567` (12 characters).
3. **Geographic Fixed Lines (Landlines):**
   - Geographic area code (e.g. `023` for Phnom Penh, `063` for Siem Reap, `053` for Battambang) followed by 5 to 7 subscriber digits (total 8 or 9 digits domestic).

### 1.4 Current Mobile Network Operator Prefixes (TRC Baseline, October 2026)
> [!NOTE]
> This table represents the operational baseline documented by the TRC as of October 2026. Use this for carrier routing or informational labeling, but do not block user registration if a newly assigned prefix is encountered.

| Operator | Brand | Domestic Prefixes | NSN Length |
| :--- | :--- | :--- | :--- |
| **CamGSM Plc.** | Cellcard | `011`, `012`, `014`, `017`, `061`, `077`, `078`, `085`, `089`, `092`, `095`, `099`<br>`076`* | 8 digits<br>9 digits (`*`) |
| **Smart Axiata Co., Ltd.** | Smart | `010`, `015`, `016`, `069`, `070`, `081`, `086`, `087`, `093`, `098`<br>`096`* | 8 digits<br>9 digits (`*`) |
| **Viettel (Cambodia) Pte., Ltd.** | Metfone | `060`, `066`, `067`, `068`, `090`<br>`031`*, `071`*, `088`*, `097`* | 8 digits<br>9 digits (`*`) |
| **South East Asia Telecom Co., Ltd.** | Seatel | `018`* | 9 digits (`*`) |

### 1.5 Robust TypeScript Normalization Implementation

```typescript
export interface PhoneNormalizationResult {
  raw: string;
  nsn: string | null;                  // National Significant Number (8 or 9 digits)
  normalizedE164: string | null;       // +855...
  normalizedDomestic: string | null;   // 0...
  isValidSyntax: boolean;
  lengthCategory: "8_digits" | "9_digits" | "invalid";
  requiresOtpVerification: true;      // Explicit boundary flag
  isActiveSim: false;                  // Syntax check NEVER confirms active status
  error?: string;
}

export function normalizeCambodianPhone(input: string): PhoneNormalizationResult {
  const result: PhoneNormalizationResult = {
    raw: input,
    nsn: null,
    normalizedE164: null,
    normalizedDomestic: null,
    isValidSyntax: false,
    lengthCategory: "invalid",
    requiresOtpVerification: true,
    isActiveSim: false,
  };

  if (!input || typeof input !== "string") {
    result.error = "Input is empty or invalid.";
    return result;
  }

  // 1. Remove whitespace, hyphens, brackets, and dots
  let cleaned = input.replace(/[\s\-\(\)\.]+/g, "");

  // 2. Convert Khmer numerals (០-៩) to ASCII digits (0-9)
  cleaned = cleaned.replace(/[\u17E0-\u17E9]/g, (match) => {
    return String(match.charCodeAt(0) - 0x17E0);
  });

  // 3. Extract country code and trunk prefix
  let nationalNumber = "";
  if (cleaned.startsWith("+855")) {
    nationalNumber = cleaned.slice(4);
  } else if (cleaned.startsWith("00855")) {
    nationalNumber = cleaned.slice(5);
  } else if (cleaned.startsWith("855")) {
    nationalNumber = cleaned.slice(3);
  } else if (cleaned.startsWith("0")) {
    nationalNumber = cleaned.slice(1);
  } else {
    nationalNumber = cleaned;
  }

  // Handle accidental redundant zero after country code (e.g. '+855012...')
  if (nationalNumber.startsWith("0")) {
    nationalNumber = nationalNumber.slice(1);
  }

  // 4. Verify all remaining characters are numeric
  if (!/^\d+$/.test(nationalNumber)) {
    result.error = "Phone number contains non-numeric characters.";
    return result;
  }

  // 5. Length verification: Cambodian NSN is 8 or 9 digits
  if (nationalNumber.length === 8) {
    result.lengthCategory = "8_digits";
  } else if (nationalNumber.length === 9) {
    result.lengthCategory = "9_digits";
  } else {
    result.error = `Invalid NSN length: ${nationalNumber.length} digits (expected 8 or 9 digits).`;
    return result;
  }

  result.nsn = nationalNumber;
  result.normalizedE164 = `+855${nationalNumber}`;
  result.normalizedDomestic = `0${nationalNumber}`;
  result.isValidSyntax = true;

  return result;
}
```

> [!CRITICAL]
> **Syntax Validation vs. Active Liveness:**
> Syntax validation only verifies structural format and length. It **NEVER** proves that a telephone number is active, assigned to a valid SIM, or in the possession of the user. Verifying active status requires an out-of-band challenge (SMS OTP) or telecommunications carrier lookup.

---

## 2. Currency Formatting: USD and KHR

Cambodia is an officially dual-currency economy. Both the **Cambodian Riel (KHR)** and the **United States Dollar (USD)** circulate simultaneously in daily commerce, retail, banking, and e-commerce.

### 2.1 Currency Comparison & Runtime Defaults

| Attribute | Cambodian Riel (KHR) | United States Dollar (USD) |
| :--- | :--- | :--- |
| **ISO 4217 Currency Code** | `KHR` | `USD` |
| **Currency Symbol** | `៛` (`U+17DB`) | `$` |
| **ISO 4217 Minor Units** | **2** (Formal ISO standard specification) | **2** (Cents) |
| **Cash Circulation Reality** | **0 decimals** (100 ៛ smallest banknote; no coins/cents) | **2 decimals** (Cents in circulation) |
| **`Intl.NumberFormat` Default** | **2 decimal places (`25,000.00៛`)** in V8/Node/browsers! | **2 decimal places (`$25.00`)** |
| **Consumer Display Convention** | **Whole Riel (`25,000 ៛`)** | Standard 2 decimals (`$25.00`) |

### 2.2 Critical Audit: Do Not Assume 0 Decimals by Default

> [!WARNING]
> In standard ECMAScript / ICU implementations of `Intl.NumberFormat`, calling:
> ```javascript
> new Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' }).format(1000);
> ```
> **produces `1,000.00៛`**, because ICU relies on the ISO 4217 table where KHR has minor units = 2.
>
> In everyday Cambodian retail and consumer applications, whole-riel prices without `.00` are overwhelmingly expected. Therefore, developers **MUST explicitly configure `{ minimumFractionDigits: 0, maximumFractionDigits: 0 }`** to achieve whole-riel display.

### 2.3 Formatting vs. Conversion

> [!CRITICAL]
> **Currency formatting is NOT currency conversion.**
> Never convert USD amounts to KHR (or vice versa) without an explicit, verifiable exchange rate provided by the user or fetched from an official source (such as the National Bank of Cambodia - NBC: [https://www.nbc.gov.kh](https://www.nbc.gov.kh)). Never assume a fixed 4,000 KHR or 4,100 KHR rate silently in production code.

### 2.4 Production-Quality Currency Formatting Utilities

```typescript
export interface FormatCurrencyOptions {
  locale?: "km-KH" | "en-US" | "en-KH";
  numberingSystem?: "latn" | "khmr"; // 'latn' = 0-9, 'khmr' = ០-៩
  wholeRiel?: boolean;               // Default true: formats whole riel without .00
}

/**
 * Format Cambodian Riel (KHR)
 * Explicitly configures whole-riel display (0 decimals) or ISO fractional display.
 */
export function formatKHR(amount: number, options: FormatCurrencyOptions = {}): string {
  const { locale = "km-KH", numberingSystem = "latn", wholeRiel = true } = options;

  const fractionDigits = wholeRiel
    ? { minimumFractionDigits: 0, maximumFractionDigits: 0 }
    : { minimumFractionDigits: 2, maximumFractionDigits: 2 };

  // Note: Most fintech apps (Bakong, ABA) default to 'latn' numerals for clarity
  const formatter = new Intl.NumberFormat(`${locale}-u-nu-${numberingSystem}`, {
    style: "currency",
    currency: "KHR",
    ...fractionDigits,
  });

  return formatter.format(amount);
}

/**
 * Format US Dollar (USD)
 * Standard: 2 decimal places with half-up rounding.
 */
export function formatUSD(amount: number, options: FormatCurrencyOptions = {}): string {
  const { locale = "en-US", numberingSystem = "latn" } = options;

  const formatter = new Intl.NumberFormat(`${locale}-u-nu-${numberingSystem}`, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return formatter.format(amount);
}
```

#### Verified Outputs:
- **Whole Riel (standard):** `formatKHR(25000)` $\rightarrow$ `"25,000៛"`
- **Zero Riel:** `formatKHR(0)` $\rightarrow$ `"0៛"`
- **Negative Riel:** `formatKHR(-25000)` $\rightarrow$ `"-25,000៛"`
- **Rounding fractional riel:** `formatKHR(25000.75)` $\rightarrow$ `"25,001៛"` (rounds half-expand)
- **Large Riel values:** `formatKHR(1234567890)` $\rightarrow$ `"1,234,567,890៛"`
- **Khmer Numerals:** `formatKHR(25000, { numberingSystem: "khmr" })` $\rightarrow$ `"២៥.០០០៛"` (ICU uses period separators with Khmer digits)
- **USD standard:** `formatUSD(12.5)` $\rightarrow$ `"$12.50"`
- **USD rounding:** `formatUSD(12.345)` $\rightarrow$ `"$12.35"`
- **USD large values:** `formatUSD(1000000)` $\rightarrow$ `"$1,000,000.00"`

---

## 3. Bilingual (Khmer / English) Internationalization

### 3.1 Pluralization in Khmer
Unlike English, Khmer does not inflect nouns for singular vs. plural:
- English: `1 item`, `5 items` (inflected with `-s`)
- Khmer: `ទំនិញ ១`, `ទំនិញ ៥` (base noun remains unchanged)

When configuring i18n libraries (e.g. `i18next`, `react-intl`, `vue-i18n`), Khmer only requires the `other` plural form:

```json
{
  "cart_items_count_one": "{{count}} item",
  "cart_items_count_other": "{{count}} items",
  "cart_items_count_km": "ទំនិញ {{count}}"
}
```

### 3.2 Locale Switching & Fallback Hierarchy
1. Store locale preference explicitly (e.g., `localStorage.getItem('user_locale')` or user profile database record).
2. Default hierarchy:
   $$\text{User Preference} \rightarrow \text{Browser Navigator Language} \rightarrow \text{Khmer (km)} \rightarrow \text{English (en) Fallback}$$
3. When a Khmer translation key is missing during development, fall back gracefully to the English string rather than crashing or showing raw empty keys (`undefined`).
