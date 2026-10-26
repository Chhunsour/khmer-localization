# Top 10 Khmer AI Hallucinations & Architectural Guardrails

Large Language Models (LLMs) such as Claude, GPT-4, Codex, and Gemini frequently stumble over Khmer language and Cambodian market conventions due to training data imbalances. This guide outlines the top 10 failure modes, why they occur, and how to programmatically guard against them.

---

## 1. The Royal & Monk Vocabulary Trap (*Reachasap* / *Sanghasap*)

### Why LLMs Fail
Historic, religious, and royal texts are disproportionately represented in digital Khmer corpora. When prompted for "formal" or "polite" translations, general LLMs often default to royal language (*Reachasap* / រាជសព្ទ) or Buddhist monk language (*Sanghasap* / សង្ឃសព្ទ).

### Hallucination Examples
- **Login:** Model generates `យាងចូល` (reserved for royalty walking into a palace).
- **Submit / Send:** Model generates `ថ្វាយ` (making an offering to a king/god).
- **Confirm:** Model generates `យល់ព្រមតាមព្រះរាជតម្រាស់` (agreeing to a royal decree).
- **Eat / Dine:** Model generates `សោយ` (royal dining) or `ឆាន់` (monk eating).

### Guardrail
Always specify: **"Use standard contemporary digital tech register (អក្សរផ្លូវការទូទៅ). Strictly forbid Reachasap and Sanghasap."**
- Login $\rightarrow$ `ចូលគណនី`
- Submit $\rightarrow$ `ដាក់ស្នើ`
- Confirm $\rightarrow$ `បញ្ជាក់`

---

## 2. Inverted Word Order (`[Adjective] [Noun]` vs `[Noun] [Adjective]`)

### Why LLMs Fail
English places adjectives before nouns ("Active Users", "Total Amount", "Khmer Language"). Khmer strictly places descriptive adjectives **after** the noun. LLMs frequently produce word-for-word transliterations that invert Khmer grammar.

### Hallucination Examples
| English Concept | Inverted Hallucination (WRONG) | Natural Khmer (CORRECT) |
| :--- | :--- | :--- |
| **Khmer Language** | `ខ្មែរភាសា` | `ភាសាខ្មែរ` |
| **Total Price** | `សរុបតម្លៃ` | `តម្លៃសរុប` |
| **Active User** | `សកម្មអ្នកប្រើប្រាស់` | `អ្នកប្រើប្រាស់សកម្ម` |
| **Current Location** | `បច្ចុប្បន្នទីតាំង` | `ទីតាំងបច្ចុប្បន្ន` |
| **New Message** | `ថ្មីសារ` | `សារថ្មី` |

### Guardrail
Instruct the agent: **"Verify all noun-modifier pairs. In Khmer, the head noun must precede the adjective."**

---

## 3. The ICU / ECMAScript Fractional Riel Trap

### Why LLMs Fail
Under ISO 4217, the Cambodian Riel (`KHR`) is formally registered with minor unit 2. Consequently, standard ECMAScript / ICU implementations of `Intl.NumberFormat('km-KH', { style: 'currency', currency: 'KHR' })` render amounts with two decimal places (`25,000.00៛`).
In Cambodian domestic commerce, however, physical fractional riels do not circulate. Displaying `.00៛` on receipts, invoices, or checkout screens looks amateurish and un-localized.

### Guardrail
Never use `Intl.NumberFormat` with default fraction digits for KHR. Always explicitly enforce whole riels:
```typescript
const khrFormatter = new Intl.NumberFormat('km-KH', {
  style: 'currency',
  currency: 'KHR',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});
```

---

## 4. The 8-Digit vs. 9-Digit Phone NSN Trap

### Why LLMs Fail
Many international phone validation libraries and LLMs assume national phone numbers have a single fixed length. In Cambodia:
- Standard mobile numbers have an **8-digit National Significant Number (NSN)** (9 digits domestic with leading zero, e.g., `012 345 678` $\rightarrow$ `+855 12 345 678`).
- Extended mobile blocks (such as Smart `096`) have a **9-digit NSN** (10 digits domestic, e.g., `096 123 4567` $\rightarrow$ `+855 96 123 4567`).

LLMs often generate regexes like `/^\+855\d{9}$/` that reject all 8-digit NSN numbers, immediately locking out more than half of Cambodian mobile users.

### Guardrail
Use length-agnostic NSN validation:
$$\text{NSN Length} \in \{8, 9\} \quad (\text{E.164 total length: 11 or 12 digits including }+855)$$

---

## 5. The Destructive Regex Whitespace Cleaner

### Why LLMs Fail
Many backend cleanup routines execute `text.replace(/\s+/g, ' ')` or `text.replace(/[\u200B-\u200D\uFEFF]/g, '')`.
In Khmer, Zero-Width Space (`\u200B` / ZWSP) is not unwanted whitespace; it is an essential line-breaking delimiter. Stripping ZWSP destroys browser text flow, causing long phrases to overflow mobile cards or clip out of dialog boxes.

### Guardrail
Never strip `\u200B` from Khmer text during normalization. Strip only ASCII whitespace (`[ \t\r\n]+`).

---

## 6. Illegal Combining Mark Sequences & Dotted Circles (U+25CC)

### Why LLMs Fail
In the Khmer Unicode specification, combining characters must strictly follow their base consonant:
$$\text{Base Consonant} \rightarrow [\text{Coeng (U+17D2)} + \text{Subscript Consonant}] \rightarrow [\text{Dependent Vowel}] \rightarrow [\text{Diacritic}]$$

When LLMs manipulate strings by characters or tokens, they frequently swap vowel signs before subscript Coeng marks. When an OpenType font encounters an orphaned or out-of-order combining mark, the shaping engine inserts a fallback **Dotted Circle (`U+25CC`)**.

### Guardrail
Run `scripts/check_khmer_unicode.py --strict` in CI. Always perform text slicing using grapheme-cluster-aware APIs (`Intl.Segmenter`).

---

## 7. Inventing Arbitrary Currency Conversion Rates

### Why LLMs Fail
Cambodia is a dual-currency economy (USD and KHR circulate simultaneously). LLMs asked to "display price in both currencies" frequently hallucinate a static exchange rate (e.g., `1 USD = 4,000 KHR` or `1 USD = 4,100 KHR`).
In real-world applications, exchange rates fluctuate daily per the National Bank of Cambodia (NBC) market rate. Silently hardcoding an exchange rate causes legal, accounting, and financial discrepancies.

### Guardrail
Keep USD and KHR amounts isolated. Never perform automatic conversion unless an explicit, authenticated exchange rate is passed into the function.

---

## 8. The Mandatory Postal Code Form Blocker

### Why LLMs Fail
Standard e-commerce checkout templates (Shopify, WooCommerce, Magento) require a 5- or 6-digit postal code.
In Cambodia, postal codes are not part of daily residential or commercial delivery. Local delivery drivers (via PassApp, GrabExpress, or motorbike couriers) locate customers using phone calls and **landmarks / directions** (`ទីតាំងសម្គាល់`).
Making postal code mandatory causes 60%+ form abandonment in Cambodian checkout flows.

### Guardrail
- Make Postal Code optional.
- Make **Recipient Phone Number** and **Landmark / Delivery Directions** mandatory.

---

## 9. Hallucinated KHQR CRC Algorithms

### Why LLMs Fail
When generating Bakong KHQR EMVCo strings, LLMs know a CRC16 is required at Tag 63, but frequently guess the wrong algorithm:
- CRC-16/IBM (Polynomial `0x8005`) $\rightarrow$ INVALID
- CRC-16/MODBUS $\rightarrow$ INVALID
- CRC-16/XMODEM $\rightarrow$ INVALID

### Guardrail
NBC Bakong strictly mandates **CRC16-CCITT-FALSE**:
- Polynomial: `0x1021` ($x^{16} + x^{12} + x^5 + 1$)
- Initial value: `0xFFFF`
- Input reflected: `False`
- Output reflected: `False`
- Final XOR: `0x0000`
- Calculation scope: The entire payload including the prefix `6304`.

---

## 10. Number-to-Words Scale Mismatch for GDT Tax Invoices

### Why LLMs Fail
Western number-to-words algorithms group digits in thousands ($10^3, 10^6, 10^9$).
Khmer traditional and tax scales group numbers in intermediate powers of 10:
- $10^4$ (10,000) $\rightarrow$ **ម៉ឺន** (*Meun*)
- $10^5$ (100,000) $\rightarrow$ **សែន** (*Saen*)
- $10^6$ (1,000,000) $\rightarrow$ **លាន** (*Lean*)

LLMs that directly translate "one hundred thousand riel" output `មួយរយពាន់រៀល`, which is grammatically invalid on Cambodian General Department of Taxation (GDT) invoices. The official legal phrase is `មួយសែនរៀលគត់`.

### Guardrail
Use the verified scale converter in `scripts/khmer_utils.py` or `scripts/khmer_utils.js`.
