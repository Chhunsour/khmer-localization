# Khmer Fintech & Bakong KHQR Payment Engineering

This reference provides technical specifications, EMVCo tag mappings, CRC16 algorithms, and code implementations for integrating Cambodia's national mobile payment standard: **Bakong KHQR**, regulated by the **National Bank of Cambodia (NBC)**.

---

## 1. Overview of Bakong & The KHQR Standard

**Bakong** is the core retail payment and mobile settlement switch operated by the National Bank of Cambodia (NBC). **KHQR** is the standardized Quick Response (QR) code specification built on the **EMVCo Merchant-Presented Mode (MPM)** specification.

KHQR serves as a universal payment rail across all licensed commercial banks, microfinance deposit-taking institutions (MDIs), and Payment Service Providers (PSPs) in Cambodia, including:
- ABA Bank, ACLEDA Bank, Canadia Bank, Sathapana Bank
- Wing Bank, TrueMoney, Chip Mong Bank, Prince Bank

### Key Architectural Characteristics:
1. **Single QR for Interoperability:** A customer using any Cambodian banking app can scan any merchant's KHQR code.
2. **Dual-Currency Isolation:** A single dynamic invoice QR is issued in either **KHR (Currency code `116`)** or **USD (Currency code `840`)**.
3. **P2P vs. Corporate Routing:** KHQR specifies whether the recipient is an individual account (Tag 29) or a registered corporate merchant (Tag 30).
4. **Mandatory CRC16 Checksum:** Every KHQR payload ends with a 4-character uppercase hexadecimal cyclic redundancy check (Tag 63).

---

## 2. Complete KHQR EMVCo Tag Mapping

A KHQR payload is composed of serialized **TLV (Tag-Length-Value)** blocks:

| Tag | Name | Format | Required | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **`00`** | Payload Format Indicator | String (2) | Yes | Always `"01"` (EMVCo specification version). |
| **`01`** | Point of Initiation Method | String (2) | Yes | `"11"` = Static QR (reusable); `"12"` = Dynamic QR (single transaction with amount). |
| **`29`** | Individual Account Info | Template | Cond. | Used for P2P / individual accounts. Contains sub-tag `00` (Bakong Account ID). |
| **`30`** | Merchant Account Info | Template | Cond. | Used for corporate businesses. Contains sub-tag `00` (Bakong ID) and `01` (Merchant ID). |
| **`52`** | Merchant Category Code (MCC) | String (4) | Yes | ISO 18245 MCC (e.g. `"5411"` Grocery, `"5812"` Restaurant, `"0000"` General). |
| **`53`** | Transaction Currency | String (3) | Yes | ISO 4217 Numeric: `"116"` for KHR, `"840"` for USD. |
| **`54`** | Transaction Amount | String (var) | Cond. | Mandatory for Dynamic QR (`01=12`). **KHR: Whole riel (`25000`)**; **USD: 2 decimals (`12.50`)**. |
| **`58`** | Country Code | String (2) | Yes | ISO 3166-1 alpha-2: Always `"KH"`. |
| **`59`** | Merchant Name | String (var) | Yes | Registered business or account name (max 25 chars). |
| **`60`** | Merchant City | String (var) | Yes | City name (e.g. `"Phnom Penh"`, `"Siem Reap"`). |
| **`62`** | Additional Data Field | Template | No | Sub-tags for Bill Number (`01`), Mobile Number (`02`), Terminal Label (`07`). |
| **`63`** | CRC16 Checksum | String (4) | Yes | 4-hex checksum over all preceding characters including `"6304"`. |

---

## 3. CRC16-CCITT-FALSE Checksum Calculation

KHQR mandates the **CRC16-CCITT-FALSE** algorithm:
- **Polynomial:** `0x1021` ($x^{16} + x^{12} + x^5 + 1$)
- **Initial Value:** `0xFFFF`
- **Input Reflection:** False
- **Result Reflection:** False
- **Final XOR:** `0x0000`
- **Output:** 4 uppercase hexadecimal characters (padded with leading zeros if needed).

The checksum is computed over the entire string up to and including the characters `6304`.

---

## 4. Production TypeScript Implementation: KHQR Generator & Validator

```typescript
/**
 * Calculate CRC16-CCITT-FALSE for EMVCo / KHQR payload.
 */
export function calculateKhqrCrc16(data: string): string {
  let crc = 0xffff;
  for (let i = 0; i < data.length; i++) {
    crc ^= data.charCodeAt(i) << 8;
    for (let j = 0; j < 8; j++) {
      if ((crc & 0x8000) !== 0) {
        crc = ((crc << 1) ^ 0x1021) & 0xffff;
      } else {
        crc = (crc << 1) & 0xffff;
      }
    }
  }
  return crc.toString(16).toUpperCase().padStart(4, "0");
}

/**
 * Format a single EMVCo Tag-Length-Value block.
 */
export function formatTlv(tag: string, value: string): string {
  const length = value.length.toString().padStart(2, "0");
  return `${tag}${length}${value}`;
}

export interface KhqrOptions {
  bakongAccountId: string; // e.g. "sokha_chhorn@acleda" or "merchant@devb"
  merchantName: string;     // e.g. "Angkor Coffee"
  merchantCity?: string;    // e.g. "Phnom Penh"
  currency: "KHR" | "USD";  // KHR (116) or USD (840)
  amount?: number;          // Optional for dynamic QR
  billNumber?: string;      // Optional invoice ID
}

/**
 * Generate a validated Bakong KHQR string.
 */
export function generateKhqr(options: KhqrOptions): string {
  const isDynamic = typeof options.amount === "number" && options.amount > 0;
  let payload = "";

  // Tag 00: Version
  payload += formatTlv("00", "01");

  // Tag 01: Initiation Method (11 = Static, 12 = Dynamic)
  payload += formatTlv("01", isDynamic ? "12" : "11");

  // Tag 29: Individual Bakong Account Information
  const subTag00 = formatTlv("00", options.bakongAccountId);
  payload += formatTlv("29", subTag00);

  // Tag 52: MCC
  payload += formatTlv("52", "5411");

  // Tag 53: Currency (116 = KHR, 840 = USD)
  const currencyCode = options.currency === "KHR" ? "116" : "840";
  payload += formatTlv("53", currencyCode);

  // Tag 54: Amount (if dynamic)
  if (isDynamic && options.amount !== undefined) {
    // KHR MUST be integer whole riel; USD has 2 decimals
    const formattedAmount =
      options.currency === "KHR"
        ? Math.round(options.amount).toString()
        : options.amount.toFixed(2);
    payload += formatTlv("54", formattedAmount);
  }

  // Tag 58: Country Code
  payload += formatTlv("58", "KH");

  // Tag 59: Merchant Name
  payload += formatTlv("59", options.merchantName.slice(0, 25));

  // Tag 60: Merchant City
  payload += formatTlv("60", options.merchantCity || "Phnom Penh");

  // Tag 62: Additional Data (Bill Number)
  if (options.billNumber) {
    const billSubTlv = formatTlv("01", options.billNumber);
    payload += formatTlv("62", billSubTlv);
  }

  // Tag 63: CRC16 Checksum
  payload += "6304";
  const checksum = calculateKhqrCrc16(payload);
  return payload + checksum;
}

/**
 * Verify integrity and parse basic details of a KHQR string.
 */
export function verifyKhqr(khqrString: string): { isValid: boolean; error?: string } {
  if (!khqrString || khqrString.length < 20) {
    return { isValid: false, error: "KHQR string is too short or empty." };
  }

  const crcIndex = khqrString.indexOf("6304");
  if (crcIndex === -1 || crcIndex + 8 !== khqrString.length) {
    return { isValid: false, error: "Missing or malformed CRC Tag 6304." };
  }

  const payloadUpToCrc = khqrString.slice(0, crcIndex + 4);
  const expectedCrc = khqrString.slice(crcIndex + 4);
  const actualCrc = calculateKhqrCrc16(payloadUpToCrc);

  if (expectedCrc.toUpperCase() !== actualCrc) {
    return {
      isValid: false,
      error: `CRC mismatch: expected ${expectedCrc}, computed ${actualCrc}.`,
    };
  }

  return { isValid: true };
}
```

---

## 5. UI Guidelines for KHQR Displays

When rendering a KHQR code on an e-commerce checkout page or physical payment terminal:
1. **Prominent Currency Symbol:** Display `៛` (KHR) or `$` (USD) in bold text above or below the QR code. Never force the user to guess the payment currency.
2. **Merchant Name Verification:** Show the exact registered Merchant Name (Tag 59) so the customer can verify they are paying the correct beneficiary inside their banking app.
3. **Transaction Expiration Countdown:** Dynamic KHQR codes should display an expiration timer (typically 3 to 15 minutes).
4. **Bilingual Status Feedback:**
   - Pending: `រង់ចាំការទូទាត់...` (Awaiting payment...)
   - Success: `ការទូទាត់ទទួលបានជោគជ័យ!` (Payment successful!)
   - Expired: `កូដ QR បានផុតកំណត់` (QR code has expired)


> [!TIP]
> A structured registry of key Bakong participant financial institutions is available at [`data/bakong_members.json`](../data/bakong_members.json).
