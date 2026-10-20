#!/usr/bin/env python3
"""
khmer_utils.py - Production Khmer Localization Utility Library

A zero-dependency Python 3.10+ reference module providing core algorithms for:
- Cambodian phone number normalization (ITU-T E.164 & TRC standards).
- Dual-currency formatting (KHR whole-riel vs USD 2-decimal).
- Cambodian calendar, dates, and Buddhist Era (BE = CE + 543) conversion.
- Grapheme-cluster-aware safe text truncation (dotted-circle prevention).
- Number-to-words spellout in Khmer for invoices and tax compliance (GDT).
- Bakong KHQR EMVCo CRC16 checksum calculation and verification.

Standard Library only. Compatible with Python 3.10+.
"""

import argparse
import datetime
import json
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


# --- 1. Cambodian Phone Number Normalization ---

def normalize_cambodian_phone(input_str: str) -> Dict[str, Any]:
    """
    Normalizes a Cambodian phone number into E.164 and domestic format.
    Decoupled from carrier prefix tables; verifies 8 or 9 digit NSN length per TRC.
    """
    result: Dict[str, Any] = {
        "raw": input_str,
        "nsn": None,
        "normalized_e164": None,
        "normalized_domestic": None,
        "is_valid_syntax": False,
        "length_category": "invalid",
        "requires_otp_verification": True,
        "is_active_sim": False,
        "error": None,
    }

    if not input_str or not isinstance(input_str, str):
        result["error"] = "Input is empty or invalid."
        return result

    # 1. Clean whitespace, hyphens, brackets, and periods
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", input_str)

    # 2. Convert Khmer digits (០-៩) to ASCII digits (0-9)
    cleaned = re.sub(
        r"[\u17E0-\u17E9]",
        lambda m: str(ord(m.group(0)) - 0x17E0),
        cleaned,
    )

    # 3. Strip international prefixes (+855, 00855, 855) or domestic trunk (0)
    national_number = cleaned
    if national_number.startswith("+855"):
        national_number = national_number[4:]
    elif national_number.startswith("00855"):
        national_number = national_number[5:]
    elif national_number.startswith("855"):
        national_number = national_number[3:]
    elif national_number.startswith("0"):
        national_number = national_number[1:]

    # Remove redundant domestic zero after country code (e.g. +855012...)
    if national_number.startswith("0"):
        national_number = national_number[1:]

    # 4. Check digits
    if not national_number.isdigit():
        result["error"] = "Phone number contains non-numeric characters."
        return result

    # 5. Length verification: 8 digits (standard mobile) or 9 digits (extended mobile)
    if len(national_number) == 8:
        result["length_category"] = "8_digits"
    elif len(national_number) == 9:
        result["length_category"] = "9_digits"
    else:
        result["error"] = f"Invalid NSN length: {len(national_number)} digits (expected 8 or 9 digits)."
        return result

    result["nsn"] = national_number
    result["normalized_e164"] = f"+855{national_number}"
    result["normalized_domestic"] = f"0{national_number}"
    result["is_valid_syntax"] = True
    return result


# --- 2. Dual-Currency Formatting (USD & KHR) ---

def format_khr(
    amount: float | int,
    whole_riel: bool = True,
    use_khmer_digits: bool = False,
) -> str:
    """
    Format Cambodian Riel (KHR).
    Defaults to whole-riel prices without .00 (consumer commercial standard).
    """
    if whole_riel:
        rounded_val = int(round(amount))
        formatted_num = f"{rounded_val:,}"
    else:
        formatted_num = f"{amount:,.2f}"

    if use_khmer_digits:
        # Convert ASCII digits to Khmer numerals
        trans = str.maketrans("0123456789,", "០១២៣៤៥៦៧៨៩.")
        formatted_num = formatted_num.translate(trans)

    return f"{formatted_num}៛"


def format_usd(amount: float | int) -> str:
    """Format US Dollar (USD) with standard 2 decimal places."""
    return f"${amount:,.2f}"


# --- 3. Calendar, Dates & Buddhist Era ---

KHMER_MONTHS = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ"
]

KHMER_DAYS = [
    "ច័ន្ទ", "អង្គារ", "ពុធ", "ព្រហស្បតិ៍", "សុក្រ", "សៅរ៍", "អាទិត្យ"
]


def to_buddhist_era(year_ce: int) -> int:
    """Calculate Buddhist Era (BE) from Christian Era (CE): BE = CE + 543."""
    return year_ce + 543


def format_khmer_date(
    d: datetime.date,
    include_be: bool = False,
    use_khmer_digits: bool = False,
) -> str:
    """Format a date using Cambodian calendar conventions (day-first)."""
    month_name = KHMER_MONTHS[d.month - 1]
    day_str = str(d.day)
    year_str = str(d.year)

    if use_khmer_digits:
        table = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
        day_str = day_str.translate(table)
        year_str = year_str.translate(table)

    formatted = f"ថ្ងៃទី {day_str} ខែ{month_name} ឆ្នាំ {year_str}"
    if include_be:
        be_year = to_buddhist_era(d.year)
        be_str = str(be_year)
        if use_khmer_digits:
            be_str = be_str.translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))
        formatted += f" (ព.ស. {be_str})"

    return formatted


def format_khmer_relative_time(diff_seconds: int) -> str:
    """Format elapsed seconds as natural Khmer relative microcopy."""
    if diff_seconds < 60:
        return "មុននេះបន្តិច"
    mins = diff_seconds // 60
    if mins < 60:
        return f"{mins} នាទីមុន"
    hours = mins // 60
    if hours < 24:
        return f"{hours} ម៉ោងមុន"
    days = hours // 24
    if days == 1:
        return "ម្សិលមិញ"
    if days < 7:
        return f"{days} ថ្ងៃមុន"
    return f"{days // 7} សប្តាហ៍មុន"


# --- 4. Unicode Grapheme Truncation & Word Breaking ---

def safe_truncate_khmer(text: str, max_chars: int) -> str:
    """
    Truncate Khmer text without splitting combining marks or Coeng sequences.
    Prevents orphaned subscript signs and dotted circle (U+25CC) defects.
    """
    if len(text) <= max_chars:
        return text

    cut_idx = max_chars
    while cut_idx > 0:
        char = text[cut_idx:cut_idx+1]
        prev_char = text[cut_idx-1:cut_idx] if cut_idx > 0 else ""

        if unicodedata.combining(char):
            cut_idx -= 1
            continue

        if prev_char == "\u17D2":
            cut_idx -= 1
            continue

        break

    return text[:cut_idx] + "…"


# --- 5. Number-to-Words in Khmer (Invoice & Tax Compliance) ---

_KHMER_ONES = ["", "មួយ", "ពីរ", "បី", "បួន", "ប្រាំ", "ប្រាំមួយ", "ប្រាំពីរ", "ប្រាំបី", "ប្រាំបួន"]
_KHMER_TENS = ["", "ដប់", "ម្ភៃ", "សាមសិប", "សែសិប", "ហាសិប", "ហុកសិប", "ចិតសិប", "ប៉ែតសិប", "កៅសិប"]


def _two_digits_to_khmer(n: int) -> str:
    if n <= 0:
        return ""
    if n < 10:
        return _KHMER_ONES[n]
    tens = n // 10
    ones = n % 10
    return f"{_KHMER_TENS[tens]}{_KHMER_ONES[ones]}"


def _three_digits_to_khmer(n: int) -> str:
    if n <= 0:
        return ""
    hundreds = n // 100
    rem = n % 100
    result = ""
    if hundreds > 0:
        result += f"{_KHMER_ONES[hundreds]}រយ"
    if rem > 0:
        result += _two_digits_to_khmer(rem)
    return result


def integer_to_khmer_words(num: int) -> str:
    """Convert an integer to spelled-out Khmer words."""
    if num == 0:
        return "សូន្យ"
    if num < 0:
        return f"ដក{integer_to_khmer_words(abs(num))}"

    n = num
    words = ""

    # Millions (លាន)
    if n >= 1_000_000:
        millions = n // 1_000_000
        words += f"{_three_digits_to_khmer(millions)}លាន"
        n %= 1_000_000

    # Hundred Thousands (សែន)
    if n >= 100_000:
        hundred_thousands = n // 100_000
        words += f"{_KHMER_ONES[hundred_thousands]}សែន"
        n %= 100_000

    # Ten Thousands (ម៉ឺន)
    if n >= 10_000:
        ten_thousands = n // 10_000
        words += f"{_KHMER_ONES[ten_thousands]}ម៉ឺន"
        n %= 10_000

    # Thousands (ពាន់)
    if n >= 1_000:
        thousands = n // 1_000
        words += f"{_KHMER_ONES[thousands]}ពាន់"
        n %= 1_000

    # Hundreds, Tens, and Ones (0-999)
    if n > 0:
        words += _three_digits_to_khmer(n)

    return words


def format_currency_khmer_words(
    amount: float | int,
    currency: str = "KHR",
) -> str:
    """
    Format currency amount into spelled-out Khmer words for invoices/receipts.
    E.g. 25000, "KHR" -> "ពីរម៉ឺនប្រាំពាន់រៀលគត់"
    """
    int_part = int(amount)
    words = integer_to_khmer_words(int_part)

    if currency.upper() == "KHR":
        return f"{words}រៀលគត់"

    cents = int(round((amount - int_part) * 100))
    if cents == 0:
        return f"{words}ដុល្លារអាមេរិកគត់"

    cents_words = integer_to_khmer_words(cents)
    return f"{words}ដុល្លារអាមេរិក និង{cents_words}សេន"


# --- 6. Bakong KHQR EMVCo CRC16 Checksum ---

def calculate_khqr_crc16(payload_up_to_6304: str) -> str:
    """
    Calculate CRC16-CCITT-FALSE for EMVCo / KHQR payload.
    Polynomial: 0x1021, Initial: 0xFFFF, Output: 4 uppercase hex characters.
    """
    crc = 0xFFFF
    for ch in payload_up_to_6304:
        crc ^= ord(ch) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def verify_khqr(khqr_string: str) -> Tuple[bool, Optional[str]]:
    """Verify integrity of a raw KHQR string."""
    if not khqr_string or len(khqr_string) < 20:
        return False, "KHQR string is too short or empty."

    crc_idx = khqr_string.find("6304")
    if crc_idx == -1 or crc_idx + 8 != len(khqr_string):
        return False, "Missing or malformed CRC Tag 6304."

    payload_prefix = khqr_string[: crc_idx + 4]
    expected_crc = khqr_string[crc_idx + 4 :].upper()
    actual_crc = calculate_khqr_crc16(payload_prefix)

    if expected_crc != actual_crc:
        return False, f"CRC mismatch: expected {expected_crc}, computed {actual_crc}."

    return True, None


# --- CLI Interface ---

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="khmer_utils.py",
        description="Khmer Localization Utilities (Phone, Currency, Dates, Words, KHQR)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # phone command
    phone_p = subparsers.add_parser("phone", help="Normalize a Cambodian phone number")
    phone_p.add_argument("number", help="Phone string to normalize (e.g. '012 345 678')")

    # currency command
    curr_p = subparsers.add_parser("currency", help="Format KHR or USD currency")
    curr_p.add_argument("amount", type=float, help="Amount to format")
    curr_p.add_argument("--currency", default="KHR", choices=["KHR", "USD"], help="Currency code")
    curr_p.add_argument("--decimals", action="store_true", help="Include decimal places for KHR")

    # words command
    words_p = subparsers.add_parser("words", help="Spell out a number in Khmer words")
    words_p.add_argument("amount", type=float, help="Number or currency amount")
    words_p.add_argument("--currency", default="KHR", choices=["KHR", "USD", "NONE"], help="Currency suffix")

    # date command
    date_p = subparsers.add_parser("date", help="Format date in Khmer and Buddhist Era")
    date_p.add_argument("iso_date", help="ISO date string (YYYY-MM-DD)")
    date_p.add_argument("--be", action="store_true", help="Include Buddhist Era")

    # khqr-crc command
    crc_p = subparsers.add_parser("khqr-crc", help="Compute CRC16 for a KHQR payload")
    crc_p.add_argument("payload", help="Payload ending with '6304'")

    args = parser.parse_args()

    if args.command == "phone":
        res = normalize_cambodian_phone(args.number)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["is_valid_syntax"] else 1

    if args.command == "currency":
        if args.currency == "KHR":
            print(format_khr(args.amount, whole_riel=not args.decimals))
        else:
            print(format_usd(args.amount))
        return 0

    if args.command == "words":
        if args.currency == "NONE":
            print(integer_to_khmer_words(int(args.amount)))
        else:
            print(format_currency_khmer_words(args.amount, args.currency))
        return 0

    if args.command == "date":
        d = datetime.date.fromisoformat(args.iso_date)
        print(format_khmer_date(d, include_be=args.be))
        return 0

    if args.command == "khqr-crc":
        crc = calculate_khqr_crc16(args.payload)
        print(f"Computed CRC16: {crc}")
        print(f"Full KHQR: {args.payload}{crc}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
