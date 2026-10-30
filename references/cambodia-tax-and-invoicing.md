# Cambodia Tax, E-Invoicing & Fiscal Localization Standards

### Regulatory Framework: General Department of Taxation (GDT / អគ្គនាយកដ្ឋានពន្ធដារ)

This guide provides software engineering specifications for generating, validating, and displaying tax invoices, receipts, and fiscal documents in compliance with Kingdom of Cambodia taxation laws and Prakas regulations.

---

## 1. Invoice Classifications & Bilingual Terminology

The General Department of Taxation recognizes two primary categories of invoices:

| Invoice Type | Khmer Statutory Title | English Equivalent | Applicable Business Category |
| :--- | :--- | :--- | :--- |
| **Tax Invoice** | **វិក្កយបត្រអាករ** | Tax Invoice | Real Regime taxpayers registered for Value Added Tax (VAT). |
| **Commercial Invoice** | **វិក្កយបត្រធម្មតា** | Commercial Invoice / Receipt | Small taxpayers, non-VAT businesses, or non-taxable sales. |

> [!IMPORTANT]
> **Strict Title Matching:** Do not use informal terms like `វិក្កយបត្រលក់` (Sales Bill) or `បង្កាន់ដៃ` (Hand Receipt) for official fiscal invoices. The header must explicitly read **វិក្កយបត្រអាករ** for VAT-registered transactions.

---

## 2. Tax Identification Number (TIN / VATTIN) Format

Every registered taxpayer in Cambodia is assigned a 9-digit Tax Identification Number (TIN).

### Canonical Structural Formats
1. **Standard 9-Digit TIN:** `123456789` or `000123456`
2. **Branch Entity TIN:** `K001-123456789` (Enterprise branch 1) or `B002-123456789` (Bank branch 2)
3. **Sole Proprietorship:** `L-123456789` or `L001-123456789`

### Entity Code Prefixes
- `K`: Corporate Enterprise / Private Limited Company (សហគ្រាសឯកជន / ក្រុមហ៊ុនទទួលខុសត្រូវមានកម្រិត)
- `B`: Commercial Bank or Financial Institution Branch (សាខាធនាគារពាណិជ្ជ)
- `L`: Sole Proprietorship (សហគ្រាសឯកបុគ្គល)
- `E`: State Institution or Autonomous Public Establishment

### Validation Function
Use `validate_cambodian_tin(tin_str)` from `scripts/khmer_utils.py` or `validateCambodianTin(tinStr)` in JavaScript/TypeScript.

---

## 3. Mandatory Statutory Invoice Elements

Under GDT Prakas No. 724 and subsequent e-invoicing instructions, an official Tax Invoice **MUST** contain:

1. **Header:** Title **វិក្កយបត្រអាករ** (Tax Invoice) prominently centered in larger font.
2. **Seller Information:**
   - Legal company name in Khmer (must match GDT patent certificate) and Latin script.
   - Registered Tax Identification Number (TIN / លេខអត្តសញ្ញាណកម្មសារពើពន្ធ).
   - Registered business address in Cambodia and contact telephone.
3. **Buyer Information:**
   - Buyer name in Khmer / Latin.
   - Buyer TIN (if registered taxpayer, essential for input VAT deduction).
   - Buyer address.
4. **Document Controls:**
   - Unique sequential invoice number (`លេខវិក្កយបត្រ`, e.g., `INV-2026-00452`).
   - Date of issuance (`កាលបរិច្ឆេទ`, formatted as `DD/MM/YYYY` or `ថ្ងៃទី DD ខែ... ឆ្នាំ YYYY`).
5. **Itemization Grid:**
   - Description of goods or services (`បរិយាយទំនិញ/សេវា`).
   - Quantity (`បរិមាណ`), Unit price (`ថ្លៃឯកតា`), and Subtotal (`សរុប`).
6. **Financial Summary:**
   - Subtotal excluding VAT (`សរុបមិនរួមបញ្ចូលអាករ`).
   - Value Added Tax 10% (`អាករលើតម្លៃបន្ថែម ១០%`).
   - Total payable amount (`ចំនួនទឹកប្រាក់សរុបត្រូវទូទាត់`).
7. **Spelled-Out Amount in Khmer Words:**
   - Total amount spelled out in full formal Khmer words ending with `គត់` (e.g., `មួយសែនពីរម៉ឺនប្រាំពាន់រៀលគត់`).
   - Required by GDT to prevent post-issuance tampering.
8. **Signatures:**
   - Signature/stamp of seller (`ហត្ថលេខា និងឈ្មោះអ្នកលក់`).
   - Signature/stamp of buyer (`ហត្ថលេខា និងឈ្មោះអ្នកទិញ`).

---

## 4. Dual-Currency Conventions (USD vs. KHR)

Cambodia operates a dollarized dual-currency economy. For taxation:
- **Statutory Accounting Currency:** Cambodian Riel (KHR).
- **Invoices Quoted in USD:** If an invoice is issued in United States Dollars (USD), it **MUST** display:
  1. The transaction subtotal, VAT 10%, and total in **USD**.
  2. The official National Bank of Cambodia (NBC) daily exchange rate (`អត្រាប្តូរប្រាក់ផ្លូវការ`).
  3. The grand total equivalent converted into **KHR**.
  4. The in-words text spelled out in **Khmer Riels** (`រៀលគត់`).

### Example Dual Currency Summary Block
```
Subtotal / សរុបមិនរួមអាករ:              $100.00
VAT 10% / អាករលើតម្លៃបន្ថែម ១០%:           $10.00
Grand Total / សរុបរួម:                   $110.00
Exchange Rate / អត្រាប្តូរប្រាក់ (NBC):       4,100 KHR/USD
Grand Total (KHR) / សរុបជារៀល:           451,000 ៛
In Words / ជាអក្សរ: បួនសែនប្រាំម៉ឺនមួយពាន់រៀលគត់
```

---

## 5. Tax Rates Reference Table

| Tax Identifier | Khmer Regulatory Term | Standard Rate | Applicable Scope |
| :--- | :--- | :---: | :--- |
| **VAT** | អាករលើតម្លៃបន្ថែម (អតប) | **10%** | Standard domestic supply of goods and services. |
| **VAT (Export)** | អាករលើតម្លៃបន្ថែម (ការនាំចេញ) | **0%** | Export of goods and services outside Cambodia. |
| **PLT** | អាករសម្រាប់បំភ្លឺសាធារណៈ | **3%** | Alcoholic beverages and tobacco products. |
| **Specific Tax** | អាករពិសេសលើទំនិញ និងសេវាមួយចំនួន | **3% – 35%** | Entertainment, telecommunications, luxury vehicles. |
| **Accommodation** | អាករលើការស្នាក់នៅ | **2%** | Hotel and tourist lodging accommodation services. |
