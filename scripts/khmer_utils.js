/**
 * khmer_utils.js - Zero-Dependency Isomorphic Khmer Localization Utility
 *
 * Production-ready algorithms for JavaScript and Node.js environments:
 * - Cambodian phone normalization (E.164, 8 & 9-digit NSN TRC standard).
 * - Dual currency formatting (KHR whole-riel integer vs USD 2-decimal).
 * - Cambodian calendar, date formatting, and Buddhist Era (BE = CE + 543).
 * - Grapheme-cluster-aware safe text truncation (prevents broken Coeng & dotted circles).
 * - Number-to-words conversion in Khmer for invoices and tax compliance (GDT).
 * - Bakong KHQR EMVCo CRC16 checksum calculation and verification.
 *
 * Environment: Node.js 16+, Browsers, Cloudflare Workers, Bun, Deno.
 */

"use strict";

// --- 1. Cambodian Phone Number Normalization ---

/**
 * Normalizes a Cambodian phone number into E.164 and domestic format.
 * TRC compliant: verifies 8 or 9 digit NSN without carrier lock-in.
 *
 * @param {string} inputStr
 * @returns {object}
 */
function normalizeCambodianPhone(inputStr) {
  const result = {
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
 *
 * @param {number} amount
 * @param {boolean} [wholeRiel=true]
 * @param {boolean} [useKhmerDigits=false]
 * @returns {string}
 */
function formatKHR(amount, wholeRiel = true, useKhmerDigits = false) {
  let formattedNum;
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
    const digitMap = {
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
 *
 * @param {number} amount
 * @returns {string}
 */
function formatUSD(amount) {
  const formattedNum = amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `$${formattedNum}`;
}

// --- 3. Calendar, Dates & Buddhist Era ---

const KHMER_MONTHS = [
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

const KHMER_DAYS = [
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
 *
 * @param {number} yearCE
 * @returns {number}
 */
function toBuddhistEra(yearCE) {
  return yearCE + 543;
}

/**
 * Convert an ASCII string of digits to Khmer numeral characters.
 *
 * @param {string|number} value
 * @returns {string}
 */
function toKhmerDigits(value) {
  const digitMap = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"];
  return String(value).replace(/[0-9]/g, (d) => digitMap[Number(d)]);
}

/**
 * Format a Date object in Cambodian style (day-first).
 *
 * @param {Date} date
 * @param {object} [options]
 * @param {boolean} [options.includeBE=false]
 * @param {boolean} [options.useKhmerDigits=false]
 * @returns {string}
 */
function formatKhmerDate(date, options = {}) {
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
    let beYear = toBuddhistEra(yearCE);
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
 *
 * @param {number} diffSeconds
 * @returns {string}
 */
function formatKhmerRelativeTime(diffSeconds) {
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
 *
 * @param {string} text
 * @param {number} maxGraphemes
 * @returns {string}
 */
function safeTruncateKhmer(text, maxGraphemes) {
  if (!text) return "";

  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const segmenter = new Intl.Segmenter("km", { granularity: "grapheme" });
    const segments = Array.from(segmenter.segment(text));

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

const _KHMER_ONES = [
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

const _KHMER_TENS = [
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

function _twoDigitsToKhmer(n) {
  if (n <= 0) return "";
  if (n < 10) return _KHMER_ONES[n];
  const tens = Math.floor(n / 10);
  const ones = n % 10;
  return `${_KHMER_TENS[tens]}${_KHMER_ONES[ones]}`;
}

function _threeDigitsToKhmer(n) {
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
 *
 * @param {number} num
 * @returns {string}
 */
function integerToKhmerWords(num) {
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
 *
 * @param {number} amount
 * @param {string} [currency="KHR"]
 * @returns {string}
 */
function formatCurrencyKhmerWords(amount, currency = "KHR") {
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
 *
 * @param {string} payloadUpTo6304
 * @returns {string}
 */
function calculateKhqrCrc16(payloadUpTo6304) {
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
 *
 * @param {string} khqrString
 * @returns {{ isValid: boolean, error: string | null }}
 */
function verifyKhqr(khqrString) {
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
 *
 * @param {string} text
 * @returns {boolean}
 */
function isKhmerText(text) {
  if (!text) return false;
  return /[\u1780-\u17FF\u19E0-\u19FF]/.test(text);
}

/**
 * Analyze text and return counts of Khmer script structural components.
 *
 * @param {string} text
 * @returns {object}
 */
function getKhmerCharacterStats(text) {
  const stats = {
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

// --- Module Exports & CLI Handling ---

const khmerUtils = {
  normalizeCambodianPhone,
  formatKHR,
  formatUSD,
  toBuddhistEra,
  toKhmerDigits,
  formatKhmerDate,
  formatKhmerRelativeTime,
  safeTruncateKhmer,
  integerToKhmerWords,
  formatCurrencyKhmerWords,
  calculateKhqrCrc16,
  verifyKhqr,
  isKhmerText,
  getKhmerCharacterStats,
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = khmerUtils;
}

// CLI Execution Support
if (typeof require !== "undefined" && require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (!cmd) {
    console.log("Usage: node khmer_utils.js <phone|currency|words|date|khqr-crc|stats> [args...]");
    process.exit(0);
  }

  switch (cmd) {
    case "phone": {
      const num = args[1] || "";
      const res = normalizeCambodianPhone(num);
      console.log(JSON.stringify(res, null, 2));
      process.exit(res.is_valid_syntax ? 0 : 1);
    }
    case "currency": {
      const amount = parseFloat(args[1] || "0");
      const curr = (args[2] || "KHR").toUpperCase();
      if (curr === "KHR") {
        console.log(formatKHR(amount));
      } else {
        console.log(formatUSD(amount));
      }
      break;
    }
    case "words": {
      const amount = parseFloat(args[1] || "0");
      const curr = (args[2] || "KHR").toUpperCase();
      if (curr === "NONE") {
        console.log(integerToKhmerWords(Math.floor(amount)));
      } else {
        console.log(formatCurrencyKhmerWords(amount, curr));
      }
      break;
    }
    case "date": {
      const iso = args[1] || new Date().toISOString().slice(0, 10);
      const d = new Date(iso);
      const includeBE = args.includes("--be");
      console.log(formatKhmerDate(d, { includeBE }));
      break;
    }
    case "khqr-crc": {
      const payload = args[1] || "";
      const crc = calculateKhqrCrc16(payload);
      console.log(`Computed CRC16: ${crc}`);
      console.log(`Full KHQR: ${payload}${crc}`);
      break;
    }
    case "stats": {
      const str = args[1] || "";
      const stats = getKhmerCharacterStats(str);
      stats.isKhmer = isKhmerText(str);
      console.log(JSON.stringify(stats, null, 2));
      break;
    }
    default:
      console.error(`Unknown command: ${cmd}`);
      process.exit(1);
  }
}
