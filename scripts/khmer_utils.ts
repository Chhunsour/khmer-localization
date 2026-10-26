/**
 * khmer_utils.ts - Type-Safe Zero-Dependency Isomorphic Khmer Localization Utility
 *
 * Production-ready algorithms for TypeScript and modern JavaScript environments:
 * - Cambodian phone normalization (E.164, 8 & 9-digit NSN TRC standard).
 * - Dual currency formatting (KHR whole-riel integer vs USD 2-decimal).
 * - Cambodian calendar, date formatting, and Buddhist Era (BE = CE + 543).
 * - Grapheme-cluster-aware safe text truncation (prevents broken Coeng & dotted circles).
 * - Number-to-words conversion in Khmer for invoices and tax compliance (GDT).
 * - Bakong KHQR EMVCo CRC16 checksum calculation and verification.
 *
 * Compatible with TypeScript 4.5+, Next.js, React, React Native, Node.js, Deno, Bun.
 */

export interface CambodianPhoneResult {
  raw: string;
  nsn: string | null;
  normalized_e164: string | null;
  normalized_domestic: string | null;
  is_valid_syntax: boolean;
  length_category: "8_digits" | "9_digits" | "invalid";
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

/**
 * Normalizes a Cambodian phone number into E.164 and domestic format.
 * TRC compliant: verifies 8 or 9 digit NSN without carrier lock-in.
 */
export function normalizeCambodianPhone(inputStr: string): CambodianPhoneResult {
  const result: CambodianPhoneResult = {
    raw: inputStr,
    nsn: null,
    normalized_e164: null,
    normalized_domestic: null,
    is_valid_syntax: false,
    length_category: "invalid",
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

  // 3. Strip international prefixes (+855, 00855, 855) or trunk zero (0)
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

  // 4. Validate digits only
  if (!/^\d+$/.test(nationalNumber)) {
    result.error = "Phone number contains non-numeric characters.";
    return result;
  }

  // 5. NSN length: 8 digits (standard mobile) or 9 digits (extended mobile)
  if (nationalNumber.length === 8) {
    result.length_category = "8_digits";
  } else if (nationalNumber.length === 9) {
    result.length_category = "9_digits";
  } else {
    result.error = `Invalid NSN length: ${nationalNumber.length} digits (expected 8 or 9 digits).`;
    return result;
  }

  result.nsn = nationalNumber;
  result.normalized_e164 = `+855${nationalNumber}`;
  result.normalized_domestic = `0${nationalNumber}`;
  result.is_valid_syntax = true;
  return result;
}

// --- 2. Dual-Currency Formatting (USD & KHR) ---

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
 */
export function integerToKhmerWords(num: number): string {
  const nInt = Math.floor(num);
  if (nInt === 0) return "សូន្យ";
  if (nInt < 0) return `ដក${integerToKhmerWords(Math.abs(nInt))}`;

  let n = nInt;
  let words = "";

  // Millions (លាន)
  if (n >= 1000000) {
    const millions = Math.floor(n / 1000000);
    words += `${_threeDigitsToKhmer(millions)}លាន`;
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
  return `${words}ដុល្លារអាមេរិក និង${centsWords}សេន`;
}

// --- 6. Bakong KHQR EMVCo CRC16 Checksum ---

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

// --- 7. Character and Text Utilities ---

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
