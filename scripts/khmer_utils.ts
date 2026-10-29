/**
 * khmer_utils.ts - Type-Safe Zero-Dependency Isomorphic Khmer Localization Utility
 *
 * Production-ready algorithms for TypeScript and modern JavaScript environments:
 * - Cambodian phone normalization (E.164, 8 & 9-digit NSN TRC standard, fixed-line + mobile).
 * - Dual currency formatting and financial precision math (KHR whole-riel integer vs USD 2-decimal).
 * - Cambodian calendar, date formatting, and Buddhist Era (BE = CE + 543).
 * - Grapheme-cluster-aware safe text truncation (prevents broken Coeng & dotted circles).
 * - Number-to-words conversion in Khmer for invoices and tax compliance (GDT).
 * - Bakong KHQR EMVCo CRC16 checksum calculation, verification, and full TLV parser.
 * - Khmer alphabetical collation per Chuon Nath dictionary order.
 *
 * Compatible with TypeScript 4.5+, Next.js, React, React Native, Node.js, Deno, Bun.
 */

export interface CambodianPhoneResult {
  raw: string;
  nsn: string | null;
  normalized_e164: string | null;
  normalized_domestic: string | null;
  is_valid_syntax: boolean;
  length_category: "8_digits" | "9_digits" | "short_code" | "invalid";
  line_type: "mobile" | "fixed_line" | "short_code" | "unknown";
  area_name: string | null;
  requires_otp_verification: boolean;
  is_active_sim: boolean;
  error: string | null;
}

export interface KhmerDateOptions {
  includeBE?: boolean;
  useKhmerDigits?: boolean;
}

export interface KhqrVerifyResult {
  isValid: boolean;
  error: string | null;
}

export interface KhqrParsedResult {
  raw: string;
  is_valid_format: boolean;
  is_valid_crc: boolean;
  crc_expected: string | null;
  crc_actual: string | null;
  currency_code: string | null;
  currency_name: string | null;
  amount: number | null;
  merchant_name: string | null;
  merchant_city: string | null;
  country_code: string | null;
  bakong_account_id: string | null;
  tags: Record<string, any>;
  error: string | null;
}

export interface MoneyItem {
  price: number;
  quantity?: number;
}

export interface MoneyTotalResult {
  currency: string;
  subtotal_minor: number;
  tax_minor: number;
  total_minor: number;
  subtotal: number;
  tax: number;
  total: number;
  subtotal_formatted: string;
  tax_formatted: string;
  total_formatted: string;
  rounding_mode: string;
}

export interface KhmerCharacterStats {
  totalKhmer: number;
  consonants: number;
  independentVowels: number;
  dependentVowels: number;
  coengSubscripts: number;
  diacritics: number;
  digits: number;
  symbols: number;
  isKhmer?: boolean;
}

// --- 1. Cambodian Phone Number Normalization ---

export const CAMBODIA_GEOGRAPHIC_PREFIXES: Record<string, string> = {
  "23": "Phnom Penh / Kandal",
  "24": "Kandal",
  "25": "Kampong Speu",
  "26": "Kampong Chhnang",
  "32": "Takeo",
  "33": "Kampot / Kep",
  "34": "Preah Sihanouk",
  "35": "Koh Kong",
  "42": "Kampong Cham / Tboung Khmum",
  "43": "Prey Veng",
  "44": "Svay Rieng",
  "52": "Pursat",
  "53": "Battambang / Pailin",
  "54": "Banteay Meanchey",
  "62": "Kampong Thom",
  "63": "Siem Reap",
  "64": "Preah Vihear",
  "72": "Kratie",
  "73": "Stung Treng",
  "74": "Mondulkiri",
  "75": "Ratanakiri",
};

export const CAMBODIA_SHORT_CODES: Record<string, string> = {
  "117": "Police Emergency",
  "118": "Fire Emergency",
  "119": "Ambulance Emergency",
  "115": "CDC Disease Surveillance",
  "1288": "Anti-Corruption Unit",
  "1299": "National Disaster Management",
};

/**
 * Normalizes a Cambodian phone number into E.164 and domestic format.
 * TRC compliant: verifies 8 or 9 digit NSN without carrier lock-in.
 * Supports mobile, fixed line geographic areas, and emergency short codes.
 */
export function normalizeCambodianPhone(inputStr: string): CambodianPhoneResult {
  const result: CambodianPhoneResult = {
    raw: inputStr,
    nsn: null,
    normalized_e164: null,
    normalized_domestic: null,
    is_valid_syntax: false,
    length_category: "invalid",
    line_type: "unknown",
    area_name: null,
    requires_otp_verification: true,
    is_active_sim: false,
    error: null,
  };

  if (!inputStr || typeof inputStr !== "string") {
    result.error = "Input is empty or invalid.";
    return result;
  }

  // 1. Remove whitespace, hyphens, brackets, dots
  let cleaned = inputStr.replace(/[\s\-\(\)\.]+/g, "");

  // 2. Convert Khmer numerals (U+17E0 - U+17E9) to ASCII digits
  cleaned = cleaned.replace(/[\u17E0-\u17E9]/g, (ch) =>
    String(ch.charCodeAt(0) - 0x17e0)
  );

  // 3. Handle emergency short codes
  if (CAMBODIA_SHORT_CODES[cleaned]) {
    result.nsn = cleaned;
    result.normalized_domestic = cleaned;
    result.normalized_e164 = cleaned;
    result.is_valid_syntax = true;
    result.length_category = "short_code";
    result.line_type = "short_code";
    result.area_name = CAMBODIA_SHORT_CODES[cleaned];
    result.requires_otp_verification = false;
    return result;
  }

  // 4. Strip international prefixes (+855, 00855, 855) or trunk zero (0)
  let nationalNumber = cleaned;
  if (nationalNumber.startsWith("+855")) {
    nationalNumber = nationalNumber.slice(4);
  } else if (nationalNumber.startsWith("00855")) {
    nationalNumber = nationalNumber.slice(5);
  } else if (nationalNumber.startsWith("855")) {
    nationalNumber = nationalNumber.slice(3);
  } else if (nationalNumber.startsWith("0")) {
    nationalNumber = nationalNumber.slice(1);
  }

  // Strip redundant trunk zero after international prefix (e.g. +855012 -> 12)
  if (nationalNumber.startsWith("0")) {
    nationalNumber = nationalNumber.slice(1);
  }

  // 5. Validate digits only
  if (!/^\d+$/.test(nationalNumber)) {
    result.error = "Phone number contains non-numeric characters.";
    return result;
  }

  // 6. NSN length: 8 digits (standard mobile / fixed) or 9 digits (extended mobile)
  if (nationalNumber.length === 8) {
    result.length_category = "8_digits";
  } else if (nationalNumber.length === 9) {
    result.length_category = "9_digits";
  } else {
    result.error = `Invalid NSN length: ${nationalNumber.length} digits (expected 8 or 9 digits).`;
    return result;
  }

  // 7. Determine line type and geographic area
  const prefix2 = nationalNumber.slice(0, 2);
  if (CAMBODIA_GEOGRAPHIC_PREFIXES[prefix2]) {
    result.line_type = "fixed_line";
    result.area_name = CAMBODIA_GEOGRAPHIC_PREFIXES[prefix2];
  } else {
    result.line_type = "mobile";
  }

  result.nsn = nationalNumber;
  result.normalized_e164 = `+855${nationalNumber}`;
  result.normalized_domestic = `0${nationalNumber}`;
  result.is_valid_syntax = true;
  return result;
}

// --- 2. Dual-Currency Formatting & Financial Precision Engine ---

/**
 * Format Cambodian Riel (KHR).
 * Default to integer whole-riel (no cents or .00) per NBC consumer standard.
 */
export function formatKHR(
  amount: number,
  wholeRiel: boolean = true,
  useKhmerDigits: boolean = false
): string {
  let formattedNum: string;
  if (wholeRiel) {
    const rounded = Math.round(amount);
    formattedNum = rounded.toLocaleString("en-US");
  } else {
    formattedNum = amount.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  if (useKhmerDigits) {
    const digitMap: Record<string, string> = {
      "0": "០",
      "1": "១",
      "2": "២",
      "3": "៣",
      "4": "៤",
      "5": "៥",
      "6": "៦",
      "7": "៧",
      "8": "៨",
      "9": "៩",
      ",": ".",
    };
    formattedNum = formattedNum.replace(/[0-9,]/g, (m) => digitMap[m] || m);
  }

  return `${formattedNum}៛`;
}

/**
 * Format US Dollar (USD) with standard 2 decimal places.
 */
export function formatUSD(amount: number): string {
  const formattedNum = amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `$${formattedNum}`;
}

/**
 * Financial calculation engine using integer minor units (riels for KHR, cents for USD)
 * to prevent IEEE 754 floating-point precision drift.
 */
export function calculateMoneyTotal(
  items: MoneyItem[] | { items: MoneyItem[]; currency?: string; taxRatePercent?: number; roundingMode?: "half_up" | "half_even" },
  currency: string = "KHR",
  taxRatePercent: number = 0.0,
  roundingMode: "half_up" | "half_even" = "half_up"
): MoneyTotalResult {
  let itemList: MoneyItem[] = [];
  if (items && !Array.isArray(items) && Array.isArray((items as any).items)) {
    const opts = items as any;
    itemList = opts.items;
    currency = opts.currency || currency;
    taxRatePercent = opts.taxRatePercent !== undefined ? opts.taxRatePercent : taxRatePercent;
    roundingMode = opts.roundingMode || roundingMode;
  } else if (Array.isArray(items)) {
    itemList = items;
  }
  const isKhr = currency.toUpperCase() === "KHR";
  let subtotalMinor = 0;

  for (const item of itemList) {
    const price = item.price || 0;
    const qty = item.quantity !== undefined ? item.quantity : 1;
    if (isKhr) {
      subtotalMinor += Math.round(price) * qty;
    } else {
      subtotalMinor += Math.round(price * 100) * qty;
    }
  }

  const rawTax = (subtotalMinor * taxRatePercent) / 100.0;
  let taxMinor: number;
  if (roundingMode === "half_even") {
    taxMinor = Math.round(rawTax);
  } else {
    taxMinor = Math.floor(rawTax + 0.5);
  }

  const totalMinor = subtotalMinor + taxMinor;
  let subtotalVal: number, taxVal: number, totalVal: number;
  let subtotalFmt: string, taxFmt: string, totalFmt: string;

  if (isKhr) {
    subtotalVal = subtotalMinor;
    taxVal = taxMinor;
    totalVal = totalMinor;
    subtotalFmt = formatKHR(subtotalVal);
    taxFmt = formatKHR(taxVal);
    totalFmt = formatKHR(totalVal);
  } else {
    subtotalVal = subtotalMinor / 100.0;
    taxVal = taxMinor / 100.0;
    totalVal = totalMinor / 100.0;
    subtotalFmt = formatUSD(subtotalVal);
    taxFmt = formatUSD(taxVal);
    totalFmt = formatUSD(totalVal);
  }

  return {
    currency: currency.toUpperCase(),
    subtotal_minor: subtotalMinor,
    tax_minor: taxMinor,
    total_minor: totalMinor,
    subtotal: subtotalVal,
    tax: taxVal,
    total: totalVal,
    subtotal_formatted: subtotalFmt,
    tax_formatted: taxFmt,
    total_formatted: totalFmt,
    rounding_mode: roundingMode,
  };
}

// --- 3. Calendar, Dates & Buddhist Era ---

export const KHMER_MONTHS: readonly string[] = [
  "មករា",
  "កុម្ភៈ",
  "មីនា",
  "មេសា",
  "ឧសភា",
  "មិថុនា",
  "កក្កដា",
  "សីហា",
  "កញ្ញា",
  "តុលា",
  "វិច្ឆិកា",
  "ធ្នូ",
];

export const KHMER_DAYS: readonly string[] = [
  "ច័ន្ទ",
  "អង្គារ",
  "ពុធ",
  "ព្រហស្បតិ៍",
  "សុក្រ",
  "សៅរ៍",
  "អាទិត្យ",
];

/**
 * Convert Christian Era (CE) year to Buddhist Era (BE) year.
 * BE = CE + 543.
 */
export function toBuddhistEra(yearCE: number): number {
  return yearCE + 543;
}

/**
 * Convert an ASCII string of digits to Khmer numeral characters.
 */
export function toKhmerDigits(value: string | number): string {
  const digitMap = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"];
  return String(value).replace(/[0-9]/g, (d) => digitMap[Number(d)]);
}

/**
 * Format a Date object in Cambodian style (day-first).
 */
export function formatKhmerDate(
  date: Date,
  options: KhmerDateOptions = {}
): string {
  const { includeBE = false, useKhmerDigits = false } = options;
  const day = date.getDate();
  const monthName = KHMER_MONTHS[date.getMonth()];
  const yearCE = date.getFullYear();

  let dayStr = String(day);
  let yearStr = String(yearCE);

  if (useKhmerDigits) {
    dayStr = toKhmerDigits(dayStr);
    yearStr = toKhmerDigits(yearStr);
  }

  let result = `ថ្ងៃទី ${dayStr} ខែ${monthName} ឆ្នាំ ${yearStr}`;

  if (includeBE) {
    const beYear = toBuddhistEra(yearCE);
    let beStr = String(beYear);
    if (useKhmerDigits) {
      beStr = toKhmerDigits(beStr);
    }
    result += ` (ព.ស. ${beStr})`;
  }

  return result;
}

/**
 * Format elapsed seconds as natural Khmer relative microcopy.
 */
export function formatKhmerRelativeTime(diffSeconds: number): string {
  if (diffSeconds < 60) {
    return "មុននេះបន្តិច";
  }
  const mins = Math.floor(diffSeconds / 60);
  if (mins < 60) {
    return `${mins} នាទីមុន`;
  }
  const hours = Math.floor(mins / 60);
  if (hours < 24) {
    return `${hours} ម៉ោងមុន`;
  }
  const days = Math.floor(hours / 24);
  if (days === 1) {
    return "ម្សិលមិញ";
  }
  if (days < 7) {
    return `${days} ថ្ងៃមុន`;
  }
  const weeks = Math.floor(days / 7);
  return `${weeks} សប្តាហ៍មុន`;
}

// --- 4. Unicode Grapheme Truncation & Word Breaking ---

/**
 * Truncate Khmer text safely without splitting combining marks or Coeng clusters.
 * Uses Intl.Segmenter (grapheme granularity) when available, with a resilient fallback.
 */
export function safeTruncateKhmer(text: string, maxGraphemes: number): string {
  if (!text) return "";

  if (typeof Intl !== "undefined" && (Intl as any).Segmenter) {
    const segmenter = new (Intl as any).Segmenter("km", {
      granularity: "grapheme",
    });
    const segments = Array.from(segmenter.segment(text)) as Array<{
      segment: string;
    }>;

    if (segments.length <= maxGraphemes) {
      return text;
    }

    const truncated = segments
      .slice(0, maxGraphemes)
      .map((s) => s.segment)
      .join("");
    return truncated + "…";
  }

  // Resilient fallback for older runtimes
  if (text.length <= maxGraphemes) {
    return text;
  }

  let cutIdx = maxGraphemes;
  while (cutIdx > 0) {
    const codePoint = text.charCodeAt(cutIdx);
    const prevCodePoint = text.charCodeAt(cutIdx - 1);

    // Combining mark range (U+17B6 - U+17D3) or Coeng U+17D2
    if (codePoint >= 0x17b6 && codePoint <= 0x17d3) {
      cutIdx--;
      continue;
    }
    if (prevCodePoint === 0x17d2) {
      cutIdx--;
      continue;
    }
    break;
  }

  return text.slice(0, cutIdx) + "…";
}

// --- 5. Number-to-Words in Khmer (Invoice & Tax Compliance) ---

const _KHMER_ONES: readonly string[] = [
  "",
  "មួយ",
  "ពីរ",
  "បី",
  "បួន",
  "ប្រាំ",
  "ប្រាំមួយ",
  "ប្រាំពីរ",
  "ប្រាំបី",
  "ប្រាំបួន",
];

const _KHMER_TENS: readonly string[] = [
  "",
  "ដប់",
  "ម្ភៃ",
  "សាមសិប",
  "សែសិប",
  "ហាសិប",
  "ហុកសិប",
  "ចិតសិប",
  "ប៉ែតសិប",
  "កៅសិប",
];

function _twoDigitsToKhmer(n: number): string {
  if (n <= 0) return "";
  if (n < 10) return _KHMER_ONES[n];
  const tens = Math.floor(n / 10);
  const ones = n % 10;
  return `${_KHMER_TENS[tens]}${_KHMER_ONES[ones]}`;
}

function _threeDigitsToKhmer(n: number): string {
  if (n <= 0) return "";
  const hundreds = Math.floor(n / 100);
  const rem = n % 100;
  let result = "";
  if (hundreds > 0) {
    result += `${_KHMER_ONES[hundreds]}រយ`;
  }
  if (rem > 0) {
    result += _twoDigitsToKhmer(rem);
  }
  return result;
}

/**
 * Convert an integer to spelled-out Khmer words.
 * Handles millions (លាន), hundred thousands (សែន), ten thousands (ម៉ឺន), thousands (ពាន់).
 * Recursive million grouping supports unlimited values.
 */
export function integerToKhmerWords(num: number): string {
  const nInt = Math.floor(num);
  if (nInt === 0) return "សូន្យ";
  if (nInt < 0) return `ដក${integerToKhmerWords(Math.abs(nInt))}`;

  let n = nInt;
  let words = "";

  // Millions (លាន) - Recursive grouping to support millions, billions, trillions
  if (n >= 1000000) {
    const millions = Math.floor(n / 1000000);
    words += `${integerToKhmerWords(millions)}លាន`;
    n %= 1000000;
  }

  // Hundred Thousands (សែន)
  if (n >= 100000) {
    const hundredThousands = Math.floor(n / 100000);
    words += `${_KHMER_ONES[hundredThousands]}សែន`;
    n %= 100000;
  }

  // Ten Thousands (ម៉ឺន)
  if (n >= 10000) {
    const tenThousands = Math.floor(n / 10000);
    words += `${_KHMER_ONES[tenThousands]}ម៉ឺន`;
    n %= 10000;
  }

  // Thousands (ពាន់)
  if (n >= 1000) {
    const thousands = Math.floor(n / 1000);
    words += `${_KHMER_ONES[thousands]}ពាន់`;
    n %= 1000;
  }

  // Hundreds, Tens, and Ones (0-999)
  if (n > 0) {
    words += _threeDigitsToKhmer(n);
  }

  return words;
}

/**
 * Format currency amount into spelled-out Khmer words for invoices/receipts.
 * E.g., 25000, "KHR" -> "ពីរម៉ឺនប្រាំពាន់រៀលគត់"
 */
export function formatCurrencyKhmerWords(
  amount: number,
  currency: "KHR" | "USD" | string = "KHR"
): string {
  const intPart = Math.floor(amount);
  const words = integerToKhmerWords(intPart);

  if (currency.toUpperCase() === "KHR") {
    return `${words}រៀលគត់`;
  }

  const cents = Math.round((amount - intPart) * 100);
  if (cents === 0) {
    return `${words}ដុល្លារអាមេរិកគត់`;
  }

  const centsWords = integerToKhmerWords(cents);
  if (intPart === 0) {
    return `${centsWords}សេន`;
  }

  return `${words}ដុល្លារអាមេរិក និង${centsWords}សេន`;
}

// --- 6. Bakong KHQR EMVCo CRC16 Checksum & Parser ---

/**
 * Calculate CRC16-CCITT-FALSE for EMVCo / KHQR payload.
 * Polynomial: 0x1021, Initial: 0xFFFF, Output: 4 uppercase hex characters.
 */
export function calculateKhqrCrc16(payloadUpTo6304: string): string {
  let crc = 0xffff;
  for (let i = 0; i < payloadUpTo6304.length; i++) {
    crc ^= payloadUpTo6304.charCodeAt(i) << 8;
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
 * Verify integrity of a raw KHQR string.
 */
export function verifyKhqr(khqrString: string): KhqrVerifyResult {
  if (!khqrString || khqrString.length < 20) {
    return { isValid: false, error: "KHQR string is too short or empty." };
  }

  const crcIdx = khqrString.indexOf("6304");
  if (crcIdx === -1 || crcIdx + 8 !== khqrString.length) {
    return { isValid: false, error: "Missing or malformed CRC Tag 6304." };
  }

  const payloadPrefix = khqrString.slice(0, crcIdx + 4);
  const expectedCrc = khqrString.slice(crcIdx + 4).toUpperCase();
  const actualCrc = calculateKhqrCrc16(payloadPrefix);

  if (expectedCrc !== actualCrc) {
    return {
      isValid: false,
      error: `CRC mismatch: expected ${expectedCrc}, computed ${actualCrc}.`,
    };
  }

  return { isValid: true, error: null };
}

/**
 * Parse a raw EMVCo KHQR string into structured TLV records and payment details.
 */
export function parseKhqr(khqrString: string): KhqrParsedResult {
  const result: KhqrParsedResult = {
    raw: khqrString,
    is_valid_format: false,
    is_valid_crc: false,
    crc_expected: null,
    crc_actual: null,
    currency_code: null,
    currency_name: null,
    amount: null,
    merchant_name: null,
    merchant_city: null,
    country_code: null,
    bakong_account_id: null,
    tags: {},
    error: null,
  };

  if (!khqrString || khqrString.length < 20) {
    result.error = "Payload is empty or shorter than minimum EMVCo length.";
    return result;
  }

  const verifyRes = verifyKhqr(khqrString);
  result.is_valid_crc = verifyRes.isValid;
  if (!verifyRes.isValid) {
    result.error = verifyRes.error;
  }

  let idx = 0;
  const tags: Record<string, any> = {};
  const len = khqrString.length;

  try {
    while (idx < len) {
      if (idx + 4 > len) break;
      const tag = khqrString.slice(idx, idx + 2);
      const tagLen = parseInt(khqrString.slice(idx + 2, idx + 4), 10);
      idx += 4;
      const val = khqrString.slice(idx, idx + tagLen);
      idx += tagLen;

      if ((tag === "29" || tag === "30" || tag === "62") && val.length >= 4) {
        const subTags: Record<string, string> = {};
        let sIdx = 0;
        while (sIdx < val.length) {
          if (sIdx + 4 > val.length) break;
          const sTag = val.slice(sIdx, sIdx + 2);
          const sLen = parseInt(val.slice(sIdx + 2, sIdx + 4), 10);
          sIdx += 4;
          const sVal = val.slice(sIdx, sIdx + sLen);
          sIdx += sLen;
          subTags[sTag] = sVal;
        }
        tags[tag] = { raw: val, sub_tags: subTags };
      } else {
        tags[tag] = val;
      }
    }

    result.tags = tags;
    result.is_valid_format = true;

    if (tags["53"]) {
      result.currency_code = tags["53"];
      if (tags["53"] === "116") result.currency_name = "KHR";
      else if (tags["53"] === "840") result.currency_name = "USD";
      else result.currency_name = "UNKNOWN";
    }

    if (tags["54"]) {
      const parsedAmount = parseFloat(tags["54"]);
      result.amount = isNaN(parsedAmount) ? null : parsedAmount;
    }

    if (tags["59"]) result.merchant_name = tags["59"];
    if (tags["60"]) result.merchant_city = tags["60"];
    if (tags["58"]) result.country_code = tags["58"];

    for (const mTag of ["29", "30"]) {
      if (tags[mTag] && tags[mTag].sub_tags && tags[mTag].sub_tags["00"]) {
        result.bakong_account_id = tags[mTag].sub_tags["00"];
        break;
      }
    }

    if (tags["63"]) {
      result.crc_expected = tags["63"];
    }
  } catch (err: any) {
    result.error = `Failed to parse EMVCo TLV structure: ${err.message}`;
    result.is_valid_format = false;
  }

  return result;
}

export interface GenerateKhqrParams {
  bakongAccountId: string;
  merchantName: string;
  amount: number;
  currency?: string;
  merchantCity?: string;
  billNumber?: string;
  storeLabel?: string;
  terminalLabel?: string;
  mcc?: string;
}

/**
 * Generate an EMVCo compliant Bakong KHQR dynamic payment payload with CRC16 checksum.
 * Decouples payload generation from bank settlement or API authentication.
 */
export function generateKhqr({
  bakongAccountId,
  merchantName,
  amount,
  currency = "KHR",
  merchantCity = "Phnom Penh",
  billNumber = "",
  storeLabel = "",
  terminalLabel = "",
  mcc = "5999",
}: GenerateKhqrParams): string {
  function formatTlv(tag: string, val: string | number): string {
    const s = String(val);
    const len = String(s.length).padStart(2, "0");
    return `${tag}${len}${s}`;
  }

  const parts = [formatTlv("00", "01"), formatTlv("01", "12")];
  const sub29 = formatTlv("00", bakongAccountId);
  parts.push(formatTlv("29", sub29));
  parts.push(formatTlv("52", mcc));

  const currUpper = (currency || "KHR").toUpperCase();
  const currCode = currUpper === "KHR" ? "116" : "840";
  parts.push(formatTlv("53", currCode));

  let amountStr = "";
  if (currCode === "116") {
    amountStr = String(Math.round(amount));
  } else {
    amountStr = Number(amount).toFixed(2);
  }
  parts.push(formatTlv("54", amountStr));

  parts.push(formatTlv("58", "KH"));
  parts.push(formatTlv("59", (merchantName || "").slice(0, 25)));
  parts.push(formatTlv("60", (merchantCity || "Phnom Penh").slice(0, 15)));

  let sub62 = "";
  if (billNumber) sub62 += formatTlv("01", billNumber);
  if (storeLabel) sub62 += formatTlv("07", storeLabel);
  if (terminalLabel) sub62 += formatTlv("08", terminalLabel);
  if (sub62) parts.push(formatTlv("62", sub62));

  const rawWithoutCrc = parts.join("") + "6304";
  const crc = calculateKhqrCrc16(rawWithoutCrc);
  return rawWithoutCrc + crc;
}

export const generateKHQR = generateKhqr;

// --- 7. Character and Collation Utilities ---

/**
 * Sort a list of Khmer words per Chuon Nath dictionary order using Intl.Collator.
 */
export function sortKhmerWords(words: string[]): string[] {
  if (!Array.isArray(words)) return [];
  if (typeof Intl !== "undefined" && (Intl as any).Collator) {
    const collator = new (Intl as any).Collator("km-KH", {
      sensitivity: "base",
      numeric: true,
    });
    return [...words].sort((a, b) => collator.compare(a, b));
  }
  return [...words].sort();
}

/**
 * Check if the string contains any Khmer Unicode characters.
 * Covers the primary Khmer block (U+1780..U+17FF) and Khmer Symbols (U+19E0..U+19FF).
 */
export function isKhmerText(text: string): boolean {
  if (!text) return false;
  return /[\u1780-\u17FF\u19E0-\u19FF]/.test(text);
}

/**
 * Analyze text and return counts of Khmer script structural components.
 */
export function getKhmerCharacterStats(text: string): KhmerCharacterStats {
  const stats: KhmerCharacterStats = {
    totalKhmer: 0,
    consonants: 0,
    independentVowels: 0,
    dependentVowels: 0,
    coengSubscripts: 0,
    diacritics: 0,
    digits: 0,
    symbols: 0,
  };

  for (let i = 0; i < text.length; i++) {
    const cp = text.charCodeAt(i);
    if (cp >= 0x1780 && cp <= 0x17a2) {
      stats.consonants++;
      stats.totalKhmer++;
    } else if (cp >= 0x17a3 && cp <= 0x17b3) {
      stats.independentVowels++;
      stats.totalKhmer++;
    } else if (cp >= 0x17b6 && cp <= 0x17c5) {
      stats.dependentVowels++;
      stats.totalKhmer++;
    } else if (cp === 0x17d2) {
      stats.coengSubscripts++;
      stats.totalKhmer++;
    } else if ((cp >= 0x17c6 && cp <= 0x17d1) || cp === 0x17dd) {
      stats.diacritics++;
      stats.totalKhmer++;
    } else if (cp >= 0x17e0 && cp <= 0x17e9) {
      stats.digits++;
      stats.totalKhmer++;
    } else if ((cp >= 0x17d4 && cp <= 0x17da) || cp === 0x17db) {
      stats.symbols++;
      stats.totalKhmer++;
    }
  }

  return stats;
}

export interface CambodianIdValidationResult {
  raw: string;
  normalized: string;
  khmer_digits: string;
  is_valid: boolean;
  id_type: "smart_id" | "legacy_id" | null;
  province_code: string | null;
  error: string | null;
}

/**
 * Validate and normalize a Cambodian National Identification Card (អត្តសញ្ញាណប័ណ្ណសញ្ជាតិខ្មែរ).
 */
export function validateCambodianId(idVal: string | number): CambodianIdValidationResult {
  if (idVal === null || idVal === undefined) idVal = "";
  const raw = String(idVal);

  const normalized = raw.replace(/[\u17E0-\u17E9]/g, (ch) => String(ch.charCodeAt(0) - 0x17E0));
  const cleanDigits = normalized.replace(/[\s\-\./,]+/g, "");

  if (!/^\d+$/.test(cleanDigits)) {
    return {
      raw,
      normalized: cleanDigits,
      khmer_digits: "",
      is_valid: false,
      id_type: null,
      province_code: null,
      error: "National ID contains non-numeric characters",
    };
  }

  const len = cleanDigits.length;
  if (len !== 9 && len !== 10) {
    return {
      raw,
      normalized: cleanDigits,
      khmer_digits: "",
      is_valid: false,
      id_type: null,
      province_code: null,
      error: `Invalid ID length (${len} digits). Expected 9 or 10 digits.`,
    };
  }

  const idType = len === 10 ? "smart_id" : "legacy_id";
  const provinceCode = cleanDigits.slice(0, 2);
  const khmerDigits = Array.from(cleanDigits).map((c) => String.fromCharCode(0x17E0 + parseInt(c, 10))).join("");

  return {
    raw,
    normalized: cleanDigits,
    khmer_digits: khmerDigits,
    is_valid: true,
    id_type: idType,
    province_code: provinceCode,
    error: null,
  };
}

export interface KhmerLicensePlateResult {
  raw: string;
  normalized: string;
  is_valid_format: boolean;
  plate_type: "civilian_car" | "motorcycle" | "commercial" | "special" | "state" | "police" | "military" | "unknown";
  category: string | null;
  province: string | null;
  series: string | null;
  number: string | null;
  error: string | null;
}

/**
 * Parse and validate Cambodian vehicle license plates (MPWT).
 */
export function parseKhmerLicensePlate(plateStr: string): KhmerLicensePlateResult {
  if (plateStr === null || plateStr === undefined) plateStr = "";
  const raw = String(plateStr).trim();
  const normalized = raw.replace(/[\u17E0-\u17E9]/g, (ch) => String(ch.charCodeAt(0) - 0x17E0));

  const result: KhmerLicensePlateResult = {
    raw,
    normalized,
    is_valid_format: false,
    plate_type: "unknown",
    category: null,
    province: null,
    series: null,
    number: null,
    error: null,
  };

  if (!normalized) {
    result.error = "Empty license plate string";
    return result;
  }

  if (raw.includes("រដ្ឋ") || normalized.toUpperCase().startsWith("STATE")) {
    result.is_valid_format = true;
    result.plate_type = "state";
    result.category = "Government / State Official";
    return result;
  }

  if (raw.includes("ន.ប") || raw.includes("នប")) {
    result.is_valid_format = true;
    result.plate_type = "police";
    result.category = "National Police (នគរបាលជាតិ)";
    return result;
  }

  if (raw.includes("ខ.ម") || raw.includes("ខម")) {
    result.is_valid_format = true;
    result.plate_type = "military";
    result.category = "Royal Cambodian Armed Forces (កងយោធពលខេមរភូមិន្ទ)";
    return result;
  }

  const pattern = /^(?:(.+?)\s+)?([1-9][A-Za-z]{1,3})[\s\-]+(\d{3,5})$/;
  const match = normalized.match(pattern);
  if (match) {
    const prov = match[1];
    const series = match[2].toUpperCase();
    const num = match[3];
    const classDigit = parseInt(series[0], 10);

    result.is_valid_format = true;
    result.province = prov ? prov.trim() : null;
    result.series = series;
    result.number = num;

    if (classDigit === 1) {
      result.plate_type = "motorcycle";
      result.category = "Motorcycle (ទោចក្រយានយន្ត)";
    } else if (classDigit === 2) {
      result.plate_type = "civilian_car";
      result.category = "Automobile / Passenger Vehicle (រថយន្តទេសចរណ៍)";
    } else if (classDigit === 3 || classDigit === 4) {
      result.plate_type = "commercial";
      result.category = "Commercial / Freight Vehicle (រថយន្តដឹកទំនិញ)";
    } else {
      result.plate_type = "special";
      result.category = "Special Heavy Equipment (គ្រឿងចក្រពិសេស)";
    }
    return result;
  }

  result.error = "Unrecognized Cambodian license plate structure";
  return result;
}

/**
 * Sanitize and format EMVCo Tag 59 (Merchant Name) for Bakong KHQR.
 */
export function formatKhqrMerchantName(name: string): string {
  if (!name || typeof name !== "string") {
    return "MERCHANT";
  }
  let sanitized = name.replace(/[\r\n\t]+/g, " ");
  sanitized = sanitized.replace(/[\"';<>\\`]+/g, "");
  sanitized = sanitized.replace(/\s+/g, " ").trim();
  if (!sanitized) {
    return "MERCHANT";
  }
  return sanitized.slice(0, 25);
}
