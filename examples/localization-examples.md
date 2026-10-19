# Khmer Localization Examples: Before & After

This guide presents realistic before-and-after code and UI examples showing how an AI coding agent should transform an application for Cambodian and Khmer-speaking users.

---

## Example 1: Natural UI Copy vs. Awkward Literal Translation

### Problem
An AI agent or machine translation tool produced word-for-word literal translations. Words like "Sign In" were translated as "sign a signature", "Submit" was translated as "dispatch", and validation messages sounded robotic and unnatural.

### Before (Awkward Machine Translation)
```json
{
  "auth": {
    "login_title": "ចុះហត្ថលេខាលើគណនី",
    "login_button": "ចុះហត្ថលេខាលើ",
    "signup_prompt": "មិនមានគណនី? ចុះបញ្ជីឈ្មោះនៅទីនេះ",
    "forgot_password": "តើអ្នកបានបាត់បង់ពាក្យសម្ងាត់របស់អ្នក?",
    "submit": "បញ្ជូនទៅកាន់ម៉ាស៊ីនបម្រើ",
    "error_required": "វាលនេះត្រូវបានទាមទារដោយប្រព័ន្ធ",
    "error_phone": "លេខទូរស័ព្ទគឺខុស",
    "empty_state": "គ្មានធាតុណាមួយត្រូវបានរកឃើញនៅក្នុងមូលដ្ឋានទិន្នន័យ"
  }
}
```

### After (Natural, Production-Quality Khmer UI Copy)
```json
{
  "auth": {
    "login_title": "ចូលគណនី",
    "login_button": "ចូល",
    "signup_prompt": "មិនទាន់មានគណនីមែនទេ? ចុះឈ្មោះ",
    "forgot_password": "ភ្លេចពាក្យសម្ងាត់?",
    "submit": "ដាក់ស្នើ",
    "error_required": "សូមបំពេញព័ត៌មាននេះ",
    "error_phone": "សូមបញ្ចូលលេខទូរស័ព្ទដែលត្រឹមត្រូវ",
    "empty_state": "មិនមានទិន្នន័យទេ"
  }
}
```
**Why this is better:**
- Direct, active verbs (`ចូល` for Log In, `ចុះឈ្មោះ` for Register).
- Respectful but concise validation copy (`សូមបំពេញព័ត៌មាននេះ`).
- Follows the vocabulary conventions of standard Cambodian digital products.

---

## Example 2: Bilingual (Khmer / English) i18n Architecture

### Problem
The application had hardcoded strings scattered across JSX components and inline ternary conditionals (`isKhmer ? "..." : "..."`). Pluralization logic erroneously added `-s` suffixes to Khmer words.

### Before (Scattered Hardcoded Conditionals)
```tsx
// Broken: Hardcoded conditionals and invalid pluralization
export function CartSummary({ count, isKhmer }: { count: number; isKhmer: boolean }) {
  return (
    <div className="cart-summary">
      <h3>{isKhmer ? "សេចក្តីសង្ខេបកន្ត្រក" : "Cart Summary"}</h3>
      <p>
        {isKhmer 
          ? `អ្នកមាន ${count} មុខទំនិញs នៅក្នុងកន្ត្រក` // Broken: Appends English 's' to Khmer word
          : `You have ${count} ${count === 1 ? "item" : "items"} in your cart`}
      </p>
      <button>{isKhmer ? "បង់ប្រាក់" : "Checkout"}</button>
    </div>
  );
}
```

### After (Clean Translation Keys & Proper Pluralization)
```tsx
// Clean, maintainable i18n implementation using standard translation hook
import { useTranslation } from "react-i18next";

export function CartSummary({ count }: { count: number }) {
  const { t } = useTranslation();

  return (
    <div className="cart-summary">
      <h3 className="font-semibold text-lg">{t("cart.summary_title")}</h3>
      <p className="text-gray-600">
        {t("cart.item_count", { count })}
      </p>
      <button className="px-4 py-2 bg-blue-600 text-white rounded">
        {t("cart.checkout_button")}
      </button>
    </div>
  );
}
```

**Translation Dictionaries:**

`locales/en/translation.json`:
```json
{
  "cart": {
    "summary_title": "Cart Summary",
    "item_count_one": "You have {{count}} item in your cart",
    "item_count_other": "You have {{count}} items in your cart",
    "checkout_button": "Checkout"
  }
}
```

`locales/km/translation.json`:
```json
{
  "cart": {
    "summary_title": "សេចក្តីសង្ខេបកន្ត្រក",
    "item_count": "អ្នកមាន {{count}} មុខទំនិញនៅក្នុងកន្ត្រក",
    "checkout_button": "បន្តទៅការទូទាត់"
  }
}
```
**Why this is better:**
- No brittle inline ternaries.
- Respects the linguistic rule that Khmer nouns do not inflect for plurals.
- Easy to audit and translate in isolation.

---

## Example 3: Cambodian Phone Number Input & Validation

### Problem
A signup form used a rigid US phone regex (`/^\d{10}$/`) that rejected all Cambodian phone numbers, coupled validation to a brittle hardcoded carrier prefix list, or falsely claimed the number was "verified" without sending an SMS OTP.

### Before (US-Centric Regex, Brittle Prefixes, & False Claims)
```typescript
// Broken: Rejects Cambodian numbers, couples to fixed prefixes, and makes false liveness claims
function validatePhone(input: string) {
  // Brittle: hardcoded 3-prefix list fails on valid 9-digit NSNs like 096
  const hardcodedPrefixRegex = /^0(12|15|88)\d{6}$/;
  if (hardcodedPrefixRegex.test(input)) {
    return { valid: true, message: "Phone number is active and verified!" }; // False claim!
  }
  return { valid: false, message: "Invalid phone number" };
}
```

### After (Decoupled E.164 Normalization & Explicit OTP Boundary)
```typescript
import { normalizeCambodianPhone, PhoneNormalizationResult } from "@/utils/cambodiaPhone";

export function handlePhoneInput(rawInput: string): PhoneNormalizationResult {
  // Normalization handles 8-digit and 9-digit NSNs, +855, and Khmer numerals (០-៩)
  const result = normalizeCambodianPhone(rawInput);

  if (!result.isValidSyntax) {
    return {
      ...result,
      error: "សូមបញ្ចូលលេខទូរស័ព្ទដែលត្រឹមត្រូវ (ឧ. 012 345 678 ឬ +855 12 345 678)",
    };
  }

  // Pass normalized E.164 (+855...) to backend SMS OTP service.
  // Note: result.isActiveSim remains false until OTP verification succeeds.
  return result;
}
```
**Why this is better:**
- Decouples normalization from volatile operator prefix lists.
- Supports both standard 8-digit NSNs (`012 345 678`) and extended 9-digit NSNs (`096 123 4567`).
- Normalizes international (`+855`), domestic (`0`), and Khmer numerals (`០-៩`).
- Never claims the number is active based on syntax alone; explicitly preserves the OTP verification boundary.

---

## Example 4: Dual Currency Formatting (USD and KHR)

### Problem
A developer called `new Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` expecting whole-riel prices, but the browser formatted whole numbers with two decimal zeros (`1,000.00៛`) due to ISO 4217 minor units. Another component silently converted USD to KHR assuming a fixed 4,000 rate.

### Before (Runtime Default Decimal Pitfall & Silent Conversion)
```typescript
// Broken: Intl defaults KHR to 2 decimals (1000.00៛); silently assumes fixed exchange rate
function formatPrice(amount: number, currency: "USD" | "KHR") {
  if (currency === "USD") {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);
  } else {
    // Pitfall: In Node/V8/Chromium, Intl.NumberFormat defaults KHR to 2 fraction digits!
    // Yields "25,000.00៛", which is contrary to consumer whole-riel display.
    return new Intl.NumberFormat("km-KH", { style: "currency", currency: "KHR" }).format(amount);
  }
}
```

### After (Explicit Whole-Riel Configuration & Native Formatting)
```typescript
export interface FormatOptions {
  locale?: "km-KH" | "en-US";
  wholeRiel?: boolean; // Default true: explicitly enforces whole riel
}

/**
 * Format USD and KHR using native platform standards.
 * Explicitly configures 0 decimals for whole-riel prices.
 * Never performs silent conversion without a verified exchange rate.
 */
export function formatCurrency(
  amount: number,
  currency: "USD" | "KHR",
  options: FormatOptions = {}
): string {
  const { locale = "km-KH", wholeRiel = true } = options;

  if (currency === "KHR") {
    // MUST configure fraction digits explicitly: KHR defaults to 2 decimals in Intl!
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: "KHR",
      minimumFractionDigits: wholeRiel ? 0 : 2,
      maximumFractionDigits: wholeRiel ? 0 : 2,
    }).format(amount);
  }

  return new Intl.NumberFormat(locale === "km-KH" ? "en-US" : locale, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}
```
**Why this is better:**
- Avoids the ICU ISO 4217 minor-unit pitfall where KHR formats with `.00` by default.
- Formats whole riel cleanly (`25,000៛`), while supporting fractional riel if accounting requires it.
- Correctly formats zero (`0៛`), negative values (`-25,000៛`), and large amounts (`1,234,567,890៛`).
- Zero risk of financial discrepancy caused by fabricated exchange rates.

---

## Example 5: Mobile Layout & Typography Fixes

### Problem
On a 360px mobile viewport, the Khmer button label had top vowels and bottom subscript consonants clipped off by tight CSS line-height and low padding. Long text caused buttons to overflow horizontal margins.

### Before (Clipped Typography & Overflow)
```html
<!-- Broken: Tight line-height clips Khmer diacritics; fixed height causes overflow -->
<button style="height: 36px; line-height: 1.0; font-size: 14px; overflow: hidden; white-space: nowrap;">
  រក្សាទុកការផ្លាស់ប្តូរ និងបន្តដំណើរការ
</button>
```

### After (Mobile-First, Resilient Khmer Layout)
```html
<!-- Fixed: Adequate line-height (1.6+), vertical padding, and flex wrapping -->
<button class="min-h-[44px] py-2.5 px-4 text-sm font-medium leading-relaxed font-khmer rounded-lg bg-blue-600 text-white break-words text-center">
  រក្សាទុកការផ្លាស់ប្តូរ និងបន្តដំណើរការ
</button>
```
**Why this is better:**
- `leading-relaxed` (line-height ~ 1.625) provides vertical clearance for ascenders and subscript coengs.
- `min-h-[44px]` meets mobile touch target standards (Apple HIG / Google Material) while allowing multi-line expansion if needed.
- `break-words` prevents container bursting on narrow screens (320px–390px).

---

## Example 6: Safe Unicode Slicing vs. Broken Splitting

### Problem
A component truncated a long Khmer article title using standard `slice(0, 15)`. The cut landed right after Coeng `\u17D2`, or between a consonant and its dependent vowel, rendering a broken dotted circle (`U+25CC`).

### Before (Naive String Slice)
```typescript
// Broken: Truncates by UTF-16 code units, splitting syllables
function truncateTitle(title: string, maxLength: number = 15) {
  if (title.length <= maxLength) return title;
  return title.slice(0, maxLength) + "...";
  // Slicing "កម្ពុជា" at index 3 lands on Coeng (U+17D2) without its subscript -> broken glyph!
}
```

### After (Grapheme-Cluster-Aware Slicing)
```typescript
// Fixed: Uses Intl.Segmenter to preserve Khmer syllable integrity
export function truncateTitleSafe(title: string, maxGraphemes: number = 15): string {
  if (!title) return "";

  // Segment by visual grapheme clusters (combines base consonant + coeng + vowel)
  const segmenter = new Intl.Segmenter("km", { granularity: "grapheme" });
  const segments = Array.from(segmenter.segment(title));

  if (segments.length <= maxGraphemes) {
    return title;
  }

  const truncated = segments
    .slice(0, maxGraphemes)
    .map((s) => s.segment)
    .join("");

  return truncated + "…";
}
```
**Why this is better:**
- Never cuts a subscript consonant from its Coeng.
- Never orphans dependent vowels or diacritics.
- Completely prevents the dotted circle rendering defect.
