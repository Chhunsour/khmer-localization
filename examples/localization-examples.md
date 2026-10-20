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

---

## Example 7: Date, Time & Buddhist Era Formatting

### Problem
A banking and legal document portal displayed raw ISO timestamps (`2026-10-19T08:30:00Z`) or US-formatted dates (`10/19/2026`), and failed to support the official Cambodian Buddhist Era (BE) format required on official receipts.

### Before (Raw ISO String or US Format)
```tsx
// Broken: US date formatting and raw UTC timestamps
export function ReceiptHeader({ timestamp }: { timestamp: string }) {
  const date = new Date(timestamp);
  return (
    <div className="receipt-header">
      <p>Date: {date.toLocaleDateString("en-US")}</p> {/* 10/19/2026 */}
      <p>Time: {date.toLocaleTimeString()}</p>
    </div>
  );
}
```

### After (Locale-Aware Gregorian & Buddhist Era Display)
```tsx
// Clean: Localized Cambodian date, time, and optional Buddhist Era
export interface FormattedDateOptions {
  includeBuddhistEra?: boolean;
  numberingSystem?: "latn" | "khmr";
}

export function formatKhmerDate(
  date: Date,
  options: FormattedDateOptions = {}
): string {
  const { includeBuddhistEra = false, numberingSystem = "latn" } = options;

  // Standard Cambodian long date format
  const formatter = new Intl.DateTimeFormat(`km-KH-u-nu-${numberingSystem}`, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const formattedDate = formatter.format(date); // e.g. "19 តុលា 2026"

  if (!includeBuddhistEra) {
    return `ថ្ងៃទី ${formattedDate}`;
  }

  // Buddhist Era (BE) = Christian Era (CE) + 543
  const buddhistYear = date.getFullYear() + 543;
  return `ថ្ងៃទី ${formattedDate} (ព.ស. ${buddhistYear})`;
}

export function ReceiptHeader({ timestamp }: { timestamp: string }) {
  const date = new Date(timestamp);

  return (
    <div className="receipt-header text-sm text-gray-700">
      <p className="font-medium">{formatKhmerDate(date, { includeBuddhistEra: true })}</p>
    </div>
  );
}
```
**Why this is better:**
- Correctly formats month names in Khmer (e.g. `តុលា` for October).
- Follows the Cambodian day-first standard (`DD/MM/YYYY` or `ថ្ងៃទី...`).
- Seamlessly calculates the official Buddhist Era ($2026 + 543 = 2569\text{ BE}$).

---

## Example 8: React Hook Form + Zod Schema for Cambodian Phone Input

### Problem
A user registration form used standard generic string validation or a US phone regex, failing to validate Cambodian phone numbers or confusing syntax validation with account verification.

### Before (Naive String Validation)
```typescript
import { z } from "zod";

// Broken: Rejects Cambodian numbers, no normalization
const signupSchema = z.object({
  fullName: z.string().min(2),
  phone: z.string().regex(/^\d{10}$/, "Invalid phone number"), // US-centric
});
```

### After (Zod Refinement with E.164 Normalization)
```typescript
import { z } from "zod";
import { normalizeCambodianPhone } from "@/utils/cambodiaPhone";

export const cambodianPhoneSchema = z
  .string()
  .min(1, "សូមបំពេញលេខទូរស័ព្ទ")
  .transform((val) => normalizeCambodianPhone(val))
  .refine((res) => res.isValidSyntax, {
    message: "សូមបញ្ចូលលេខទូរស័ព្ទដែលត្រឹមត្រូវ (ឧ. 012 345 678 ឬ +855 12 345 678)",
  });

export const registrationSchema = z.object({
  fullName: z.string().min(2, "សូមបញ្ចូលឈ្មោះពេញរបស់អ្នក"),
  phone: cambodianPhoneSchema,
});

export type RegistrationFormData = z.infer<typeof registrationSchema>;
```
**Why this is better:**
- Integrates seamlessly with `react-hook-form` and standard validation pipelines.
- Normalizes spaces, dashes, brackets, `+855`, and Khmer digits (`០-៩`) automatically.
- Validates both 8-digit and 9-digit NSN mobile structures under TRC / ITU-T E.164.

---

## Example 9: Next.js + Tailwind CSS Localization & Typography Setup

### Problem
An AI coding agent set up a new Next.js project with Tailwind CSS, but omitted Khmer font definitions and line-height tokens, resulting in distorted fallback typography and clipped diacritics.

### After (Production Next.js & Tailwind Configuration)

`tailwind.config.ts`:
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        khmer: ["var(--font-khmer)", "Kantumruy Pro", "Noto Sans Khmer", "sans-serif"],
      },
      lineHeight: {
        "khmer-tight": "1.5",
        "khmer-normal": "1.7",
        "khmer-relaxed": "1.85",
      },
    },
  },
  plugins: [],
};
export default config;
```

`app/layout.tsx`:
```tsx
import { Kantumruy_Pro } from "next/font/google";
import "./globals.css";

const kantumruyPro = Kantumruy_Pro({
  subsets: ["khmer", "latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-khmer",
  display: "swap",
});

export default function RootLayout({
  children,
  params: { locale = "km" },
}: {
  children: React.ReactNode;
  params: { locale?: string };
}) {
  return (
    <html lang={locale} className={kantumruyPro.variable}>
      <body className="font-khmer leading-khmer-normal text-gray-900 bg-white antialiased">
        {children}
      </body>
    </html>
  );
}
```
**Why this is better:**
- Loads `Kantumruy Pro` with Google Fonts variable optimization.
- Sets global `leading-khmer-normal` (line-height 1.7) to guarantee clearance for ascenders and subscript consonants.
- Exposes responsive Tailwind utility classes (`font-khmer`, `leading-khmer-relaxed`).

---

## Example 10: Automatic Word-Break Insertion for Khmer Web Layouts

### Problem
A blog and news publishing site displayed Khmer articles without zero-width spaces. On mobile screens (375px wide), words failed to wrap or broke arbitrarily across syllables, creating ugly jagged borders.

### After (Safe Word-Break Injection Component)
```tsx
import React, { useMemo } from "react";
import { insertKhmerWordBreaks } from "@/utils/khmerText";

interface KhmerParagraphProps {
  content: string;
  className?: string;
}

export function KhmerParagraph({ content, className = "" }: KhmerParagraphProps) {
  // Memoize word segmentation to maintain high performance
  const formattedText = useMemo(() => {
    return insertKhmerWordBreaks(content);
  }, [content]);

  return (
    <p
      className={`font-khmer leading-khmer-relaxed break-words text-gray-800 ${className}`}
      style={{ overflowWrap: "break-word" }}
    >
      {formattedText}
    </p>
  );
}
```
**Why this is better:**
- Employs `Intl.Segmenter` to insert `\u200B` at natural word boundaries without altering visible text.
- Pairs with CSS `break-words` and `overflowWrap: break-word` for complete layout safety on all mobile viewports.


---

## Example 11: Cascading Cambodian Administrative Address Selector

### Problem
An e-commerce app used a Western address form requiring "State / Postal Code", confusing Cambodian shoppers and leading to high parcel delivery failure rates due to missing Sangkat, Khan, and landmark directions.

### After (Cambodia-Tailored Cascading Address Form)
```tsx
import React, { useState } from "react";

export interface AddressFormData {
  provinceCode: string;   // e.g. "KH-12" (Phnom Penh)
  districtName: string;   // e.g. "ខណ្ឌដូនពេញ" (Khan Daun Penh)
  communeName: string;    // e.g. "សង្កាត់បឹងរាំង" (Sangkat Boeng Reang)
  streetAndHouse: string; // e.g. "ផ្ទះលេខ ១២A, ផ្លូវ ២០០"
  landmarkNotes: string;  // e.g. "ទល់មុខមន្ទីរពេទ្យកាល់ម៉ែត" (Opposite Calmette)
  deliveryPhone: string;  // e.g. "012 345 678" (Courier anchor)
}

export function CambodianAddressForm({
  onSubmit,
}: {
  onSubmit: (data: AddressFormData) => void;
}) {
  const [form, setForm] = useState<AddressFormData>({
    provinceCode: "KH-12",
    districtName: "",
    communeName: "",
    streetAndHouse: "",
    landmarkNotes: "",
    deliveryPhone: "",
  });

  return (
    <form className="space-y-4 font-khmer text-sm" onSubmit={(e) => { e.preventDefault(); onSubmit(form); }}>
      <div>
        <label className="block font-medium mb-1">រាជធានី-ខេត្ត (Province / City) *</label>
        <select
          className="w-full p-2.5 border rounded-lg"
          value={form.provinceCode}
          onChange={(e) => setForm({ ...form, provinceCode: e.target.value })}
        >
          <option value="KH-12">រាជធានីភ្នំពេញ (Phnom Penh)</option>
          <option value="KH-17">ខេត្តសៀមរាប (Siem Reap)</option>
          <option value="KH-2">ខេត្តបាត់ដំបង (Battambang)</option>
          <option value="KH-18">ខេត្តព្រះសីហនុ (Preah Sihanouk)</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block font-medium mb-1">ក្រុង/ស្រុក/ខណ្ឌ (District / Khan) *</label>
          <input
            type="text"
            placeholder="ឧ. ខណ្ឌដូនពេញ"
            className="w-full p-2.5 border rounded-lg"
            value={form.districtName}
            onChange={(e) => setForm({ ...form, districtName: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block font-medium mb-1">ឃុំ/សង្កាត់ (Commune / Sangkat) *</label>
          <input
            type="text"
            placeholder="ឧ. សង្កាត់បឹងរាំង"
            className="w-full p-2.5 border rounded-lg"
            value={form.communeName}
            onChange={(e) => setForm({ ...form, communeName: e.target.value })}
            required
          />
        </div>
      </div>

      <div>
        <label className="block font-medium mb-1">ផ្ទះលេខ និងផ្លូវ (House No. & Street) *</label>
        <input
          type="text"
          placeholder="ឧ. ផ្ទះលេខ ១២A ផ្លូវ ២០០"
          className="w-full p-2.5 border rounded-lg"
          value={form.streetAndHouse}
          onChange={(e) => setForm({ ...form, streetAndHouse: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block font-medium mb-1">ចំណាំទីតាំងសម្គាល់ (Landmark / Directions)</label>
        <input
          type="text"
          placeholder="ឧ. ជិតផ្សារកណ្តាល ឬ ទល់មុខសាលារៀន"
          className="w-full p-2.5 border rounded-lg"
          value={form.landmarkNotes}
          onChange={(e) => setForm({ ...form, landmarkNotes: e.target.value })}
        />
      </div>

      <div>
        <label className="block font-medium mb-1">លេខទូរស័ព្ទអ្នកទទួល (Recipient Phone) *</label>
        <input
          type="tel"
          placeholder="ឧ. 012 345 678"
          className="w-full p-2.5 border rounded-lg"
          value={form.deliveryPhone}
          onChange={(e) => setForm({ ...form, deliveryPhone: e.target.value })}
          required
        />
      </div>

      <button
        type="submit"
        className="w-full min-h-[44px] py-2.5 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
      >
        បញ្ជាក់អាសយដ្ឋានដឹកជញ្ជូន
      </button>
    </form>
  );
}
```
**Why this is better:**
- Matches the authentic Cambodian 4-tier administrative hierarchy.
- Includes a dedicated "Landmark / Directions" input, which is essential for parcel delivery in Cambodia.
- Prioritizes the recipient phone number as the courier anchor.

---

## Example 12: Generating and Verifying a Bakong KHQR String (CRC16)

### Problem
A payment gateway needed to generate merchant-presented dynamic KHQR strings compatible with NBC's Bakong mobile switch, but failed to format the EMVCo TLV blocks or compute the CRC16-CCITT checksum accurately.

### After (Standard KHQR Generator & CRC16 Validator)
```typescript
import { calculateKhqrCrc16, formatTlv, verifyKhqr } from "@/utils/khqr";

export interface InvoiceKhqrParams {
  merchantBakongId: string; // e.g. "merchant@devb"
  merchantName: string;     // e.g. "Coffee Express"
  billNumber: string;       // e.g. "INV-2026-001"
  amount: number;           // e.g. 25000 (KHR) or 6.25 (USD)
  currency: "KHR" | "USD";
}

export function createInvoiceKhqr(params: InvoiceKhqrParams): string {
  let payload = "";

  // 00: EMVCo version 01
  payload += formatTlv("00", "01");

  // 01: Dynamic QR (single invoice with preset amount)
  payload += formatTlv("01", "12");

  // 29: Individual / Merchant Account Info
  const accountSubTag = formatTlv("00", params.merchantBakongId);
  payload += formatTlv("29", accountSubTag);

  // 52: Merchant Category Code (General)
  payload += formatTlv("52", "0000");

  // 53: Transaction Currency (116 = KHR, 840 = USD)
  const currencyCode = params.currency === "KHR" ? "116" : "840";
  payload += formatTlv("53", currencyCode);

  // 54: Transaction Amount (Whole riel for KHR; 2 decimals for USD)
  const formattedAmount =
    params.currency === "KHR"
      ? Math.round(params.amount).toString()
      : params.amount.toFixed(2);
  payload += formatTlv("54", formattedAmount);

  // 58: Country Code (KH)
  payload += formatTlv("58", "KH");

  // 59: Merchant Name
  payload += formatTlv("59", params.merchantName.slice(0, 25));

  // 60: City
  payload += formatTlv("60", "Phnom Penh");

  // 62: Additional Data (Bill Number)
  const billSubTag = formatTlv("01", params.billNumber);
  payload += formatTlv("62", billSubTag);

  // 63: CRC16 Tag
  payload += "6304";
  const checksum = calculateKhqrCrc16(payload);

  const fullQr = payload + checksum;
  const { isValid, error } = verifyKhqr(fullQr);
  if (!isValid) {
    throw new Error(`KHQR self-check failed: ${error}`);
  }

  return fullQr;
}
```
**Why this is better:**
- Follows the official National Bank of Cambodia (NBC) KHQR tag specifications.
- Guarantees KHR amounts are rounded to whole riel integers.
- Appends and self-verifies the CRC16-CCITT-FALSE checksum (`Tag 63`).

---

## Example 13: Spelled-Out Khmer Currency Words on Tax Invoices

### Problem
A SaaS billing system generated VAT tax invoices for Cambodia's General Department of Taxation (GDT) showing only numeric amounts (`150,000 ៛`), which failed compliance audits requiring amounts spelled out in Khmer words.

### After (Automated GDT Spelled-Out Invoice Line)
```tsx
import { formatKHR } from "@/utils/currency";
import { formatCurrencyKhmerWords } from "@/utils/khmerWords";

export function InvoiceTotalRow({ subtotalKHR, vatKHR }: { subtotalKHR: number; vatKHR: number }) {
  const totalKHR = subtotalKHR + vatKHR;
  const numericDisplay = formatKHR(totalKHR); // "165,000៛"
  const spelledWords = formatCurrencyKhmerWords(totalKHR, "KHR"); // "មួយសែនប្រាំមួយម៉ឺនប្រាំពាន់រៀលគត់"

  return (
    <div className="border-t pt-4 font-khmer">
      <div className="flex justify-between text-lg font-bold">
        <span>សរុបរួម (Grand Total):</span>
        <span>{numericDisplay}</span>
      </div>
      <div className="mt-1 text-sm text-gray-600 bg-gray-50 p-2.5 rounded border">
        <span className="font-medium text-gray-700">ចំនួនទឹកប្រាក់ជាអក្សរ (Amount in words): </span>
        <span className="font-semibold text-gray-900">{spelledWords}</span>
      </div>
    </div>
  );
}
```
**Why this is better:**
- Displays both numeric whole riel (`165,000៛`) and spelled-out Khmer words (`មួយសែនប្រាំមួយម៉ឺនប្រាំពាន់រៀលគត់`).
- Follows standard Cambodian GDT invoicing and accounting legal standards.

---

## Example 14: Alphabetical Sorting of Customer Names with `Intl.Collator`

### Problem
A customer management portal sorted Khmer names using standard JavaScript `.sort()`. Names starting with `គ` appeared before `ក`, and subscript vowels scrambled the list order.

### After (Chuon Nath Dictionary Collation)
```typescript
/**
 * Sorts customer records alphabetically using official Khmer dictionary rules.
 */
export interface CustomerRecord {
  id: string;
  fullNameKh: string; // e.g. "ចាន់ សុខា", "កែវ ពិសិដ្ឋ", "ស៊ុន ម៉ាលី"
}

export function sortCustomersAlphabetically(
  customers: CustomerRecord[]
): CustomerRecord[] {
  // Use ICU-tailored Khmer collator
  const collator = new Intl.Collator("km-KH", {
    sensitivity: "base",
    numeric: true,
  });

  return [...customers].sort((a, b) =>
    collator.compare(a.fullNameKh, b.fullNameKh)
  );
}
```
**Why this is better:**
- Applies official Khmer dictionary ordering (`ក` before `ខ` before `គ`...).
- Groups base consonants and subscript clusters in proper linguistic sequence.
