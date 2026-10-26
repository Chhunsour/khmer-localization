# AI Agent Token-Saver Cheat Sheet (Khmer Localization)

This reference provides dense, token-optimized code patterns and immediate answers for AI coding agents. Read this file when you need immediate implementation code without spending context tokens on background explanations.

---

## 1. Instant Drop-In Code Snippets (Copy & Paste)

### 1.1 KHR Whole-Riel Currency Formatting
**The Bug:** Default `Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` outputs 2 decimal places (`25,000.00៛`). Cambodia has no fractional physical riel in circulation.
**The Fix:**
```typescript
// TypeScript / JavaScript
export function formatKHR(amount: number): string {
  return new Intl.NumberFormat('km-KH', {
    style: 'currency',
    currency: 'KHR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Math.round(amount));
}
// formatKHR(25000) => "25,000 ៛"
```

```python
# Python
def format_khr(amount: float) -> str:
    rounded = int(round(amount))
    return f"{rounded:,} ៛"
```

---

### 1.2 Safe Text Truncation (Preserving Syllables & Coeng Subscripts)
**The Bug:** Naive `.slice(0, n)` cuts after Coeng (`\u17D2`), creating an orphaned subscript marker that displays as a broken dotted circle (`U+25CC`).
**The Fix:**
```typescript
// TypeScript / JavaScript
export function safeTruncateKhmer(text: string, maxGraphemes: number, suffix = '…'): string {
  const segmenter = new Intl.Segmenter('km', { granularity: 'grapheme' });
  const segments = Array.from(segmenter.segment(text), s => s.segment);
  if (segments.length <= maxGraphemes) return text;
  return segments.slice(0, maxGraphemes).join('') + suffix;
}
```

```python
# Python
import unicodedata

def safe_truncate_khmer(text: str, max_len: int, suffix: str = "...") -> str:
    if len(text) <= max_len:
        return text
    idx = max_len
    # Never truncate immediately after Coeng (U+17D2)
    if idx > 0 and text[idx - 1] == '\u17D2':
        idx -= 1
    # Strip any trailing combining marks
    while idx > 0 and unicodedata.combining(text[idx - 1]) != 0:
        idx -= 1
    return text[:idx] + suffix
```

---

### 1.3 Zero-Width Word Break Injection (Preventing Container Overflow)
**The Bug:** Khmer has no visible spaces between words. Browsers without dictionary breakers either overflow or break words mid-syllable.
**The Fix:**
```typescript
// TypeScript / JavaScript
export function insertKhmerWordBreaks(text: string): string {
  if (typeof Intl === 'undefined' || !(Intl as any).Segmenter) return text;
  const segmenter = new (Intl as any).Segmenter('km', { granularity: 'word' });
  return Array.from(segmenter.segment(text), (s: any) => s.segment).join('\u200B');
}
```

---

### 1.4 Cambodian Phone Number Normalization (+855)
**The Trap:** 8-digit vs. 9-digit NSN. E.g. `012 345 678` (8 digits NSN) vs `096 123 4567` (9 digits NSN). Both are valid.
```typescript
// TypeScript / JavaScript
export function normalizeCambodianPhone(raw: string) {
  let digits = raw.replace(/[^\d+]/g, '');
  if (digits.startsWith('+855')) digits = digits.slice(4);
  else if (digits.startsWith('00855')) digits = digits.slice(5);
  else if (digits.startsWith('855')) digits = digits.slice(3);
  else if (digits.startsWith('0')) digits = digits.slice(1);

  const isValidLength = digits.length === 8 || digits.length === 9;
  return {
    e164: isValidLength ? `+855${digits}` : '',
    domestic: isValidLength ? `0${digits}` : '',
    nsn: digits,
    isValid: isValidLength,
    note: "Syntax valid only; requires SMS OTP verification to prove active status."
  };
}
```

---

### 1.5 Bakong KHQR EMVCo CRC16 Checksum
**The Trap:** Do not use CRC-16/IBM or MODBUS. NBC Bakong requires **CRC16-CCITT-FALSE** (Polynomial `0x1021`, Initial `0xFFFF`, no reflection) over the entire string including `6304`.
```typescript
// TypeScript / JavaScript
export function calculateKhqrCrc16(payloadWithoutCrc: string): string {
  // Ensure payload ends with tag 6304
  const data = payloadWithoutCrc.endsWith('6304') ? payloadWithoutCrc : `${payloadWithoutCrc}6304`;
  let crc = 0xFFFF;
  for (let i = 0; i < data.length; i++) {
    crc ^= data.charCodeAt(i) << 8;
    for (let j = 0; j < 8; j++) {
      if ((crc & 0x8000) !== 0) crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
      else crc = (crc << 1) & 0xFFFF;
    }
  }
  return crc.toString(16).toUpperCase().padStart(4, '0');
}
```

---

### 1.6 Buddhist Era (BE) Conversion
$$\text{Year (BE)} = \text{Year (CE)} + 543 \quad (2026\text{ CE} + 543 = 2569\text{ BE})$$
```typescript
export const toBuddhistEra = (ceYear: number) => ceYear + 543;
```

---

## 2. Immediate UI Phrasing Lookup (50 High-Frequency Terms)

When translating UI microcopy, use this exact table to avoid hallucinating archaic or royal words:

| UI Key | Natural Modern Khmer (Use This) | Avoid / AI Hallucination Trap |
| :--- | :--- | :--- |
| **Login / Sign In** | `ចូលគណនី` | `ចុះហត្ថលេខាលើ`, `យាងចូល` |
| **Sign Up / Register** | `ចុះឈ្មោះ` | `បង្កើតអត្តសញ្ញាណ` |
| **Log Out / Sign Out** | `ចាកចេញ` | `ដកថយ`, `យាងចេញ` |
| **Submit** | `ដាក់ស្នើ` | `បញ្ជូនទៅកាន់ម៉ាស៊ីនបម្រើ` |
| **Confirm** | `បញ្ជាក់` | `យល់ព្រមតាមព្រះរាជតម្រាស់` |
| **Cancel** | `បោះបង់` | `លុបចោលទាំងស្រុង` |
| **Save** | `រក្សាទុក` | `សន្សំសំចៃ` |
| **Delete** | `លុប` | `សម្លាប់` |
| **Edit** | `កែសម្រួល` | `ផ្លាស់ប្តូររូបរាង` |
| **Search** | `ស្វែងរក` | `រុករក` (navigation), `តាមរក` |
| **Settings** | `ការកំណត់` | `បរិស្ថានម៉ាស៊ីន` |
| **Cart / Basket** | `កន្ត្រកទំនិញ` | `រទេះរុញ` |
| **Checkout** | `ទូទាត់ប្រាក់` | `ពិនិត្យចេញ` |
| **Total Amount** | `ចំនួនទឹកប្រាក់សរុប` | `សរុបចំនួន` (inverted order) |
| **Subtotal** | `ចំនួនរង` / `ទឹកប្រាក់មិនទាន់គិតពន្ធ` | `ផ្នែករង` |
| **Discount** | `ការបញ្ចុះតម្លៃ` | `កាត់បន្ថយ` |
| **Shipping Address** | `អាសយដ្ឋានដឹកជញ្ជូន` | `កន្លែងផ្ញើ` |
| **Phone Number** | `លេខទូរស័ព្ទ` | `ទូរស័ព្ទលេខ` |
| **Email Address** | `អាសយដ្ឋានអ៊ីមែល` | `សារអេឡិចត្រូនិច` |
| **Password** | `ពាក្យសម្ងាត់` | `លេខកូដសម្ងាត់` |
| **Notifications** | `ការជូនដំណឹង` | `សេចក្តីប្រកាស` |
| **Profile** | `ព័ត៌មានគណនី` | `រូបភាពផ្ទាល់ខ្លួន` |
| **Order History** | `ប្រវត្តិការបញ្ជាទិញ` | `បញ្ជីចាស់` |
| **Pending** | `កំពុងរង់ចាំ` | `នៅសល់` |
| **Completed** | `បានជោគជ័យ` / `បានបញ្ចប់` | `សម្រេចបានល្អឥតខ្ចោះ` |
| **Failed** | `មិនជោគជ័យ` | `បរាជ័យធ្ងន់ធ្ងរ` |
| **Retry** | `ព្យាយាមម្តងទៀត` | `សាកល្បងសារជាថ្មីម្តងទៀត` |
| **Loading...** | `កំពុងដំណើរការ...` | `កំពុងផ្ទុកទំនិញ...` |
| **Required Field** | `ចាំបាច់ត្រូវបំពេញ` | `តម្រូវការដាច់ខាត` |
| **Landmark / Directions** | `ទីតាំងសម្គាល់ / ទិសដៅ` | `ស្លាកសញ្ញាដី` |

---

## 3. Top 3 Grammar & Syntax Rules for AI Agents

1. **Noun First, Adjective Second:**
   - English: `[Adjective] + [Noun]` ("Khmer Language", "Active Users", "Total Price")
   - Khmer: `[Noun] + [Adjective]` (`ភាសាខ្មែរ`, `អ្នកប្រើប្រាស់សកម្ម`, `តម្លៃសរុប`)
   - *Never generate:* `ខ្មែរភាសា`, `សរុបតម្លៃ`.

2. **Spacing Around Punctuation:**
   - **Khan (`។`):** NO space before; ONE space after (`...របស់អ្នក។ បន្ទាប់មក...`).
   - **Camnuc Pii Kuuh / Colon (`៖`):** NO space before; ONE space after (`ព័ត៌មាន៖ ឈ្មោះ...`).
   - **Lek Too (`ៗ`):** Space before and space after (`រាល់ ៗ ថ្ងៃ`).

3. **Form Modeling for Cambodia:**
   - **Never make Postal Code mandatory** in Cambodian checkout forms (postal codes are not used by domestic motorbike couriers).
   - **Always collect Recipient Phone Number** and a dedicated **Landmark / Delivery Directions** field (`ទីតាំងសម្គាល់`).
