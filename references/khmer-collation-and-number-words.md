# Khmer Alphabetical Collation & Number-to-Words Conversion

This reference provides technical specifications, linguistic ordering standards, and code implementations for:
1. **Khmer Alphabetical Collation (Sorting):** Ordering customer lists, dictionaries, tables, and directories per the authoritative Samdech Chuon Nath standard.
2. **Number-to-Words Spellout (បម្លែងលេខជាពាក្យ):** Generating spelled-out legal currency text for invoices, VAT compliance (General Department of Taxation - GDT), bank checks, and receipts.

---

## 1. Khmer Alphabetical Collation (Dictionary Order)

In standard database systems and JavaScript runtimes, calling `.sort()` on strings performs code-point comparison (`U+1780 < U+1781...`), which fails to sort complex Khmer syllables correctly because:
- Subscript consonants (Coeng `U+17D2` + consonant) must sort under the base consonant hierarchy.
- Dependent vowels have a distinct linguistic precedence from independent vowels.
- Diacritics have secondary collation weights.

### 1.1 The Official Chuon Nath Ordering Hierarchy

The National Institute of Language (Royal Academy of Cambodia) and the classic Chuon Nath Khmer Dictionary define the following sequence:

#### 1. Consonants (ព្យញ្ជនៈទាំង ៣៣ តួ):
```text
ក, ខ, គ, ឃ, ង,
ច, ឆ, ជ, ឈ, ញ,
ដ, ឋ, ឌ, ឍ, ណ,
ត, ថ, ទ, ធ, ន,
ប, ផ, ព, ភ, ម,
យ, រ, ល, វ, ស,
ហ, ឡ, អ
```

#### 2. Independent Vowels (ស្រៈពេញតួ):
```text
ឥ, ឦ, ឧ, ឩ, ឪ, ឫ, ឬ, ឭ, ឮ, ឯ, ឰ, ឲ, ឳ
```

#### 3. Dependent Vowel Signs (ស្រៈនិស្ស័យ - illustrated with base consonant ក):
```text
កា, កិ, កី, កឹ, កឺ, កុ, កូ, កួ, កើ, កឿ, កៀ, កេ, កែ, កៃ, កោ, កៅ
```

#### 4. Diacritics & Signs:
```text
កំ (U+17C6), កះ (U+17C7), កៈ (U+17C8), ប៉ (U+17C9), ប៊ (U+17CA),
ក់ (U+17CB), ករ៍ (U+17CC), ក៍ (U+17CD), ក៎ (U+17CE), ក៏ (U+17CF), ក័ (U+17D0)
```

---

### 1.2 ECMAScript / Node.js Collation with `Intl.Collator`

Modern browsers and Node.js implement the Unicode Collation Algorithm (UCA) with Khmer tailoring in ICU:

```typescript
/**
 * Sort an array of Khmer strings according to standard Khmer alphabetical order.
 */
export function sortKhmerStrings(items: string[]): string[] {
  const collator = new Intl.Collator("km-KH", {
    sensitivity: "base",
    numeric: true, // Naturally sort numbers inside text (e.g. "ជំពូក 2" before "ជំពូក 10")
  });

  return [...items].sort((a, b) => collator.compare(a, b));
}
```

---

## 2. Number-to-Words Conversion (Khmer Spellout)

In Cambodia, official tax invoices (General Department of Taxation - GDT), loan agreements, and bank checks legally require billing amounts to be spelled out in Khmer words.

### 2.1 The Khmer Numerical Scale System

Unlike English (which groups by thousands: thousands, millions, billions), traditional Khmer counting includes unique intermediate bases:
- **ដប់ (*Dap*):** Ten ($10^1$)
- **រយ (*Roy*):** Hundred ($10^2$)
- **ពាន់ (*Pwoan*):** Thousand ($10^3$)
- **ម៉ឺន (*Meun*):** Ten Thousand ($10^4$) — *Distinct base!*
- **សែន (*Saen*):** Hundred Thousand ($10^5$) — *Distinct base!*
- **លាន (*Lean*):** Million ($10^6$)
- **កោដិ (*Kaot*):** Ten Million ($10^7$)

### 2.2 Digits and Tens Vocabulary

| Digit | Khmer Word | Tens Number | Khmer Word |
| :--- | :--- | :--- | :--- |
| **0** | សូន្យ (*Soun*) | **10** | ដប់ (*Dap*) |
| **1** | មួយ (*Muoy*) | **20** | ម្ភៃ (*Mphei*) |
| **2** | ពីរ (*Pii*) | **30** | សាមសិប (*Samsip*) |
| **3** | បី (*Bei*) | **40** | សែសិប (*Saesip*) |
| **4** | បួន (*Boun*) | **50** | ហាសិប (*Hasip*) |
| **5** | ប្រាំ (*Pram*) | **60** | ហុកសិប (*Hoksip*) |
| **6** | ប្រាំមួយ (*Pram-muoy*) | **70** | ចិតសិប (*Chetsip*) |
| **7** | ប្រាំពីរ (*Pram-pii*) | **80** | ប៉ែតសិប (*Paetsip*) |
| **8** | ប្រាំបី (*Pram-bei*) | **90** | កៅសិប (*Kaosip*) |
| **9** | ប្រាំបួន (*Pram-boun*) | | |

---

### 2.3 Production TypeScript Number-to-Words Implementation

```typescript
const ONES = ["", "មួយ", "ពីរ", "បី", "បួន", "ប្រាំ", "ប្រាំមួយ", "ប្រាំពីរ", "ប្រាំបី", "ប្រាំបួន"];
const TENS = ["", "ដប់", "ម្ភៃ", "សាមសិប", "សែសិប", "ហាសិប", "ហុកសិប", "ចិតសិប", "ប៉ែតសិប", "កៅសិប"];

/**
 * Convert a two-digit integer (0-99) to Khmer words.
 */
function twoDigitsToKhmer(n: number): string {
  if (n <= 0) return "";
  if (n < 10) return ONES[n];
  const tensDigit = Math.floor(n / 10);
  const onesDigit = n % 10;
  return `${TENS[tensDigit]}${ONES[onesDigit]}`;
}

/**
 * Convert a three-digit integer (0-999) to Khmer words.
 */
function threeDigitsToKhmer(n: number): string {
  if (n <= 0) return "";
  const hundredDigit = Math.floor(n / 100);
  const remainder = n % 100;
  let result = "";
  if (hundredDigit > 0) {
    result += `${ONES[hundredDigit]}រយ`;
  }
  if (remainder > 0) {
    result += twoDigitsToKhmer(remainder);
  }
  return result;
}

/**
 * Convert any non-negative integer to Khmer words.
 * Handles numbers up to billions using standard Khmer scales (ពាន់, ម៉ឺន, សែន, លាន).
 */
export function integerToKhmerWords(num: number): string {
  if (num === 0) return "សូន្យ";
  if (num < 0) return `ដក${integerToKhmerWords(Math.abs(num))}`;

  let n = Math.floor(num);
  let words = "";

  // Millions (លាន)
  if (n >= 1_000_000) {
    const millions = Math.floor(n / 1_000_000);
    words += `${threeDigitsToKhmer(millions)}លាន`;
    n %= 1_000_000;
  }

  // Hundred Thousands (សែន)
  if (n >= 100_000) {
    const hundredThousands = Math.floor(n / 100_000);
    words += `${ONES[hundredThousands]}សែន`;
    n %= 100_000;
  }

  // Ten Thousands (ម៉ឺន)
  if (n >= 10_000) {
    const tenThousands = Math.floor(n / 10_000);
    words += `${ONES[tenThousands]}ម៉ឺន`;
    n %= 10_000;
  }

  // Thousands (ពាន់)
  if (n >= 1_000) {
    const thousands = Math.floor(n / 1_000);
    words += `${ONES[thousands]}ពាន់`;
    n %= 1_000;
  }

  // Hundreds, Tens, and Ones (0-999)
  if (n > 0) {
    words += threeDigitsToKhmer(n);
  }

  return words;
}

/**
 * Format a financial amount into spelled-out Khmer words for invoices/receipts.
 * E.g. formatCurrencyKhmerWords(25000, "KHR") -> "ពីរម៉ឺនប្រាំពាន់រៀលគត់"
 */
export function formatCurrencyKhmerWords(
  amount: number,
  currency: "KHR" | "USD" = "KHR"
): string {
  const integerPart = Math.floor(amount);
  const words = integerToKhmerWords(integerPart);

  if (currency === "KHR") {
    // Cambodian Riel is whole-unit; suffix with "រៀលគត់" (Riel exact)
    return `${words}រៀលគត់`;
  }

  // USD: Format dollars and optional cents
  const cents = Math.round((amount - integerPart) * 100);
  if (cents === 0) {
    return `${words}ដុល្លារអាមេរិកគត់`;
  }

  const centsWords = integerToKhmerWords(cents);
  return `${words}ដុល្លារអាមេរិក និង${centsWords}សេន`;
}
```

### Verified Examples:
- `25,000 ៛` $\rightarrow$ `ពីរម៉ឺនប្រាំពាន់រៀលគត់`
- `150,000 ៛` $\rightarrow$ `មួយសែនប្រាំម៉ឺនរៀលគត់`
- `1,000,000 ៛` $\rightarrow$ `មួយលានរៀលគត់`
- `$12.50` $\rightarrow$ `ដប់ពីរដុល្លារអាមេរិក និងហាសិបសេន`
- `$100.00` $\rightarrow$ `មួយរយដុល្លារអាមេរិកគត់`
