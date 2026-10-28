#!/usr/bin/env python3
"""
khmer_utils.py - Production Khmer Localization Utility Library

A zero-dependency Python 3.10+ reference module providing core algorithms for:
- Cambodian phone number normalization (ITU-T E.164 & TRC standards, mobile + fixed-line).
- Dual-currency formatting and financial precision math (KHR whole-riel vs USD 2-decimal).
- Cambodian calendar, dates, and Buddhist Era (BE = CE + 543) conversion.
- Grapheme-cluster-aware safe text truncation (dotted-circle prevention).
- Number-to-words spellout in Khmer for invoices and tax compliance (GDT).
- Bakong KHQR EMVCo CRC16 checksum calculation, verification, and full TLV parsing.
- Deterministic pure-Python Khmer alphabetical collation (Chuon Nath dictionary order).

Standard Library only. Compatible with Python 3.10+.
"""

import argparse
import datetime
import json
import math
import os
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


# --- 1. Cambodian Phone Number Normalization ---

CAMBODIA_GEOGRAPHIC_PREFIXES: Dict[str, str] = {
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
}

CAMBODIA_SHORT_CODES: Dict[str, str] = {
    "117": "Police Emergency",
    "118": "Fire Emergency",
    "119": "Ambulance Emergency",
    "115": "CDC Disease Surveillance",
    "1288": "Anti-Corruption Unit",
    "1299": "National Disaster Management",
}


def normalize_cambodian_phone(input_str: str) -> Dict[str, Any]:
    """
    Normalizes a Cambodian phone number into E.164 and domestic format.
    Supports mobile (8 or 9 digits NSN), geographic fixed-line (8 digits NSN),
    and recognized short emergency codes.
    Decoupled from dynamic carrier tables; validates syntax per TRC standards.
    """
    result: Dict[str, Any] = {
        "raw": input_str,
        "nsn": None,
        "normalized_e164": None,
        "normalized_domestic": None,
        "is_valid_syntax": False,
        "length_category": "invalid",
        "line_type": "unknown",
        "area_name": None,
        "requires_otp_verification": True,
        "is_active_sim": False,
        "error": None,
    }

    if not input_str or not isinstance(input_str, str):
        result["error"] = "Input is empty or invalid."
        return result

    # 1. Clean whitespace, hyphens, brackets, and periods
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", input_str)

    # 2. Convert Khmer digits (U+17E0 - U+17E9) to ASCII digits (0-9)
    cleaned = re.sub(
        r"[\u17E0-\u17E9]",
        lambda m: str(ord(m.group(0)) - 0x17E0),
        cleaned,
    )

    # 3. Handle emergency short codes (3 or 4 digits)
    if cleaned in CAMBODIA_SHORT_CODES:
        result["nsn"] = cleaned
        result["normalized_domestic"] = cleaned
        result["normalized_e164"] = cleaned
        result["is_valid_syntax"] = True
        result["length_category"] = "short_code"
        result["line_type"] = "short_code"
        result["area_name"] = CAMBODIA_SHORT_CODES[cleaned]
        result["requires_otp_verification"] = False
        return result

    # 4. Strip international prefixes (+855, 00855, 855) or domestic trunk (0)
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

    # 5. Check digits
    if not national_number.isdigit():
        result["error"] = "Phone number contains non-numeric characters."
        return result

    # 6. Length verification: 8 digits (standard mobile / fixed) or 9 digits (extended mobile)
    if len(national_number) == 8:
        result["length_category"] = "8_digits"
    elif len(national_number) == 9:
        result["length_category"] = "9_digits"
    else:
        result["error"] = f"Invalid NSN length: {len(national_number)} digits (expected 8 or 9 digits)."
        return result

    # 7. Line type & area identification
    prefix_2 = national_number[:2]
    if prefix_2 in CAMBODIA_GEOGRAPHIC_PREFIXES:
        result["line_type"] = "fixed_line"
        result["area_name"] = CAMBODIA_GEOGRAPHIC_PREFIXES[prefix_2]
    else:
        result["line_type"] = "mobile"

    result["nsn"] = national_number
    result["normalized_e164"] = f"+855{national_number}"
    result["normalized_domestic"] = f"0{national_number}"
    result["is_valid_syntax"] = True
    return result


# --- 2. Dual-Currency Formatting & Financial Precision Engine ---

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


def calculate_money_total(
    items: List[Dict[str, Any]],
    currency: str = "KHR",
    tax_rate_percent: float = 0.0,
    rounding_mode: str = "half_up",
) -> Dict[str, Any]:
    """
    Financial calculation engine using integer minor units (riels for KHR, cents for USD)
    to prevent IEEE 754 floating-point precision drift.

    items: list of dicts with 'price' and 'quantity'.
    currency: 'KHR' or 'USD'.
    rounding_mode: 'half_up' (commercial round 0.5 up) or 'half_even' (banker's).
    """
    is_khr = currency.upper() == "KHR"

    # Calculate subtotal in integer minor units
    subtotal_minor = 0
    for item in items:
        price = item.get("price", 0)
        qty = item.get("quantity", 1)
        if is_khr:
            item_minor = int(round(price)) * qty
        else:
            item_minor = int(round(price * 100)) * qty
        subtotal_minor += item_minor

    # Calculate tax in minor units
    raw_tax = (subtotal_minor * tax_rate_percent) / 100.0
    if rounding_mode == "half_even":
        tax_minor = int(round(raw_tax))
    else:
        # Commercial half-up
        tax_minor = math.floor(raw_tax + 0.5)

    total_minor = subtotal_minor + tax_minor

    if is_khr:
        subtotal_val = subtotal_minor
        tax_val = tax_minor
        total_val = total_minor
        subtotal_fmt = format_khr(subtotal_val)
        tax_fmt = format_khr(tax_val)
        total_fmt = format_khr(total_val)
    else:
        subtotal_val = subtotal_minor / 100.0
        tax_val = tax_minor / 100.0
        total_val = total_minor / 100.0
        subtotal_fmt = format_usd(subtotal_val)
        tax_fmt = format_usd(tax_val)
        total_fmt = format_usd(total_val)

    return {
        "currency": currency.upper(),
        "subtotal_minor": subtotal_minor,
        "tax_minor": tax_minor,
        "total_minor": total_minor,
        "subtotal": subtotal_val,
        "tax": tax_val,
        "total": total_val,
        "subtotal_formatted": subtotal_fmt,
        "tax_formatted": tax_fmt,
        "total_formatted": total_fmt,
        "rounding_mode": rounding_mode,
    }


# --- 3. Calendar, Dates & Buddhist Era ---

KHMER_MONTHS = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ"
]

KHMER_DAYS = [
    "ច័ន្ទ", "អង្គារ", "ពុធ", "ព្រហស្បតិ៍", "សុក្រ", "សៅរ៍", "អាទិត្យ"
]


def to_khmer_digits(value: Any) -> str:
    """Convert ASCII digits (0-9) to Khmer Unicode numerals (០-៩)."""
    digit_map = ["០", "១", "២", "៣", "៤", "៥", "៦", "៧", "៨", "៩"]
    return re.sub(r"[0-9]", lambda m: digit_map[int(m.group(0))], str(value))


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


def format_khmer_relative_time(
    diff_seconds: int,
    use_khmer_digits: bool = False,
    future: bool = False,
) -> str:
    """
    Format time difference in seconds as natural modern Khmer relative microcopy.
    Supports past (elapsed seconds or negative) and future timestamps (future=True).
    """
    def _digits(n: int) -> str:
        s = str(n)
        if use_khmer_digits:
            return s.translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))
        return s

    abs_sec = abs(diff_seconds)

    if abs_sec < 10:
        return "អម្បាញ់មិញ"

    if future:
        if abs_sec < 60:
            return f"ក្នុងរយៈពេល {_digits(abs_sec)} វិនាទីទៀត"
        mins = abs_sec // 60
        if mins < 60:
            return f"ក្នុងរយៈពេល {_digits(mins)} នាទីទៀត"
        hours = mins // 60
        if hours < 24:
            return f"ក្នុងរយៈពេល {_digits(hours)} ម៉ោងទៀត"
        days = hours // 24
        if days == 1:
            return "ថ្ងៃស្អែក"
        if days < 7:
            return f"ក្នុងរយៈពេល {_digits(days)} ថ្ងៃទៀត"
        if days < 30:
            weeks = days // 7
            return f"ក្នុងរយៈពេល {_digits(weeks)} សប្តាហ៍ទៀត"
        if days < 365:
            months = days // 30
            return f"ក្នុងរយៈពេល {_digits(months)} ខែទៀត"
        years = days // 365
        return f"ក្នុងរយៈពេល {_digits(years)} ឆ្នាំទៀត"

    # Past timestamps
    if abs_sec < 60:
        return "មុននេះបន្តិច"
    mins = abs_sec // 60
    if mins < 60:
        return f"{_digits(mins)} នាទីមុន"
    hours = mins // 60
    if hours < 24:
        return f"{_digits(hours)} ម៉ោងមុន"
    days = hours // 24
    if days == 1:
        return "ម្សិលមិញ"
    if days < 7:
        return f"{_digits(days)} ថ្ងៃមុន"
    if days < 30:
        weeks = days // 7
        return f"{_digits(weeks)} សប្តាហ៍មុន"
    if days < 365:
        months = days // 30
        return f"{_digits(months)} ខែមុន"
    years = days // 365
    return f"{_digits(years)} ឆ្នាំមុន"


# --- 4. Unicode Grapheme Truncation & Word Breaking ---

def safe_truncate_khmer(text: str, max_chars: int) -> str:
    """
    Truncate Khmer text without splitting combining marks or Coeng sequences.
    Prevents orphaned subscript signs and dotted circle (U+25CC) defects.
    """
    if not text:
        return ""
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


KHMER_SYLLABLE_PATTERN = re.compile(
    r'(?:'
    r'[\u1780-\u17A2](?:\u17D2[\u1780-\u17A2])?'
    r'|[\u17A3-\u17B3]'
    r'|[\u17E0-\u17E9]+'
    r'|[^\u1780-\u17FF\u19E0-\u19FF\s]+'
    r'|\s+'
    r'|[\u17D4-\u17DA\u17DB]'
    r')'
    r'(?:'
    r'\u17D2[\u1780-\u17A2]'
    r'|[\u17B6-\u17C5]'
    r'|[\u17C6-\u17D3\u17DD]'
    r')*',
    re.UNICODE,
)


def segment_khmer_syllables(text: str) -> List[str]:
    """
    Segment Khmer text into orthographic syllables based on script phonotactics.
    Handles base consonants, independent vowels, Coeng clusters, dependent vowels, and diacritics.
    """
    if not text:
        return []
    return [m.group(0) for m in KHMER_SYLLABLE_PATTERN.finditer(text) if m.group(0)]


def insert_khmer_word_breaks(text: str, break_char: str = "\u200B") -> str:
    """
    Inject Zero-Width Space (U+200B) at syllable boundaries to enable clean browser word wrapping.
    Leaves non-Khmer words, existing whitespace, and punctuation intact without duplicate breaks.
    """
    if not text:
        return ""
    tokens = segment_khmer_syllables(text)
    out: List[str] = []
    khmer_run_re = re.compile(r"[\u1780-\u17FF]")

    for i, tok in enumerate(tokens):
        out.append(tok)
        if i < len(tokens) - 1:
            next_tok = tokens[i + 1]
            if khmer_run_re.search(tok) and khmer_run_re.search(next_tok):
                if not tok.endswith(break_char) and not next_tok.startswith(break_char):
                    out.append(break_char)

    res = "".join(out)
    return re.sub(f"{re.escape(break_char)}+", break_char, res)


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
    """
    Convert an integer to spelled-out Khmer words.
    Handles unlimited values seamlessly via recursive million grouping (លាន),
    hundred thousands (សែន), ten thousands (ម៉ឺន), and thousands (ពាន់).
    """
    if num == 0:
        return "សូន្យ"
    if num < 0:
        return f"ដក{integer_to_khmer_words(abs(num))}"

    n = num
    words = ""

    # Millions (លាន) - Recursive grouping to support millions, billions, trillions
    if n >= 1_000_000:
        millions = n // 1_000_000
        words += f"{integer_to_khmer_words(millions)}លាន"
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
    E.g. 10.50, "USD" -> "ដប់ដុល្លារអាមេរិក និងហាសិបសេន"
    """
    int_part = int(amount)
    words = integer_to_khmer_words(int_part)

    if currency.upper() == "KHR":
        return f"{words}រៀលគត់"

    # USD formatting with cents
    cents = int(round((amount - int_part) * 100))
    if cents == 0:
        return f"{words}ដុល្លារអាមេរិកគត់"

    cents_words = integer_to_khmer_words(cents)
    if int_part == 0:
        return f"{cents_words}សេន"

    return f"{words}ដុល្លារអាមេរិក និង{cents_words}សេន"


# --- 6. Bakong KHQR EMVCo CRC16 Checksum & TLV Parser ---

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


def parse_khqr(khqr_string: str) -> Dict[str, Any]:
    """
    Parse a raw EMVCo KHQR string into structured TLV records and payment details.
    Decouples payload syntax parsing from transaction status or payment execution.
    """
    result: Dict[str, Any] = {
        "raw": khqr_string,
        "is_valid_format": False,
        "is_valid_crc": False,
        "crc_expected": None,
        "crc_actual": None,
        "currency_code": None,
        "currency_name": None,
        "amount": None,
        "merchant_name": None,
        "merchant_city": None,
        "country_code": None,
        "bakong_account_id": None,
        "tags": {},
        "error": None,
    }

    if not khqr_string or len(khqr_string) < 20:
        result["error"] = "Payload is empty or shorter than minimum EMVCo length."
        return result

    # Verify CRC
    is_crc_valid, crc_err = verify_khqr(khqr_string)
    result["is_valid_crc"] = is_crc_valid
    if not is_crc_valid:
        result["error"] = crc_err

    # Parse TLV blocks
    idx = 0
    tags: Dict[str, Any] = {}
    length_str = len(khqr_string)

    try:
        while idx < length_str:
            if idx + 4 > length_str:
                break
            tag = khqr_string[idx : idx + 2]
            length_val = int(khqr_string[idx + 2 : idx + 4])
            idx += 4
            val = khqr_string[idx : idx + length_val]
            idx += length_val

            # Sub-parse nested merchant account info (Tags 29, 30) or additional data (Tag 62)
            if tag in ("29", "30", "62") and len(val) >= 4:
                sub_tags = {}
                sub_idx = 0
                while sub_idx < len(val):
                    if sub_idx + 4 > len(val):
                        break
                    s_tag = val[sub_idx : sub_idx + 2]
                    s_len = int(val[sub_idx + 2 : sub_idx + 4])
                    sub_idx += 4
                    s_val = val[sub_idx : sub_idx + s_len]
                    sub_idx += s_len
                    sub_tags[s_tag] = s_val
                tags[tag] = {"raw": val, "sub_tags": sub_tags}
            else:
                tags[tag] = val

        result["tags"] = tags
        result["is_valid_format"] = True

        # Extract semantic payment fields
        if "53" in tags:
            curr_code = tags["53"]
            result["currency_code"] = curr_code
            if curr_code == "116":
                result["currency_name"] = "KHR"
            elif curr_code == "840":
                result["currency_name"] = "USD"
            else:
                result["currency_name"] = "UNKNOWN"

        if "54" in tags:
            try:
                result["amount"] = float(tags["54"])
            except ValueError:
                result["amount"] = None

        if "59" in tags:
            result["merchant_name"] = tags["59"]

        if "60" in tags:
            result["merchant_city"] = tags["60"]

        if "58" in tags:
            result["country_code"] = tags["58"]

        # Extract Bakong Account ID from Tag 29 or 30 sub-tag 00
        for merchant_tag in ("29", "30"):
            if merchant_tag in tags and isinstance(tags[merchant_tag], dict):
                sub = tags[merchant_tag].get("sub_tags", {})
                if "00" in sub:
                    result["bakong_account_id"] = sub["00"]
                    break

        if "63" in tags:
            result["crc_expected"] = tags["63"]

    except Exception as e:
        result["error"] = f"Failed to parse EMVCo TLV structure: {str(e)}"
        result["is_valid_format"] = False

    return result


def generate_khqr(
    bakong_account_id: str,
    merchant_name: str,
    amount: float | int,
    currency: str = "KHR",
    merchant_city: str = "Phnom Penh",
    bill_number: str = "",
    store_label: str = "",
    terminal_label: str = "",
    mcc: str = "5999",
) -> str:
    """
    Generate an EMVCo compliant Bakong KHQR dynamic payment payload with CRC16 checksum.
    Decouples payload generation from bank settlement or API authentication.
    """
    def _format_tlv(tag: str, value: str) -> str:
        return f"{tag}{len(value):02d}{value}"

    # Tag 00: Payload Format Indicator (01)
    # Tag 01: Point of Initiation Method (12 = Dynamic)
    parts = [_format_tlv("00", "01"), _format_tlv("01", "12")]

    # Tag 29: Merchant Account Information
    sub_29 = _format_tlv("00", bakong_account_id)
    parts.append(_format_tlv("29", sub_29))

    # Tag 52: MCC
    parts.append(_format_tlv("52", mcc))

    # Tag 53: Transaction Currency (116 = KHR, 840 = USD)
    curr_upper = currency.upper()
    curr_code = "116" if curr_upper == "KHR" else "840"
    parts.append(_format_tlv("53", curr_code))

    # Tag 54: Transaction Amount
    if curr_code == "116":
        amount_str = str(int(amount))
    else:
        amount_str = f"{amount:.2f}"
    parts.append(_format_tlv("54", amount_str))

    # Tag 58: Country Code (KH)
    parts.append(_format_tlv("58", "KH"))

    # Tag 59: Merchant Name
    parts.append(_format_tlv("59", merchant_name[:25]))

    # Tag 60: Merchant City
    parts.append(_format_tlv("60", merchant_city[:15]))

    # Tag 62: Additional Data Field Template
    sub_62 = ""
    if bill_number:
        sub_62 += _format_tlv("01", bill_number)
    if store_label:
        sub_62 += _format_tlv("07", store_label)
    if terminal_label:
        sub_62 += _format_tlv("08", terminal_label)
    if sub_62:
        parts.append(_format_tlv("62", sub_62))

    # Tag 63: CRC16 prefix
    raw_without_crc = "".join(parts) + "6304"
    crc = calculate_khqr_crc16(raw_without_crc)
    return raw_without_crc + crc


# --- 7. Pure-Python Khmer Alphabetical Collation (Chuon Nath Order) ---

# Chuon Nath 33 Consonants weight table (1..33)
_KHMER_CONSONANT_WEIGHTS: Dict[str, int] = {
    chr(cp): idx + 1
    for idx, cp in enumerate(range(0x1780, 0x17A3))
}

# Independent vowels weight table (34..47)
_KHMER_INDEP_VOWEL_WEIGHTS: Dict[str, int] = {
    chr(cp): idx + 34
    for idx, cp in enumerate(range(0x17A3, 0x17B4))
}

# Dependent vowels weight table (48..63)
_KHMER_DEP_VOWEL_WEIGHTS: Dict[str, int] = {
    chr(cp): idx + 48
    for idx, cp in enumerate(range(0x17B6, 0x17C6))
}

# Diacritics weight table (64..75)
_KHMER_DIACRITIC_WEIGHTS: Dict[str, int] = {
    chr(cp): idx + 64
    for idx, cp in enumerate(range(0x17C6, 0x17D2))
}


def khmer_sort_key(text: str) -> List[int]:
    """
    Generate a deterministic collation key for sorting Khmer strings
    according to Chuon Nath dictionary order in pure Python standard library.
    Handles base consonants, subscript consonants (Coeng U+17D2), dependent vowels, and diacritics.
    """
    if not text:
        return [0]

    norm_text = unicodedata.normalize("NFC", text)
    key: List[int] = []
    idx = 0
    length = len(norm_text)

    while idx < length:
        ch = norm_text[idx]

        # Check for Coeng Subscript sequence (U+17D2 + Consonant)
        if ch == "\u17D2" and idx + 1 < length:
            sub_consonant = norm_text[idx + 1]
            sub_weight = _KHMER_CONSONANT_WEIGHTS.get(sub_consonant, 100)
            # Subscripts sort after base consonants, flagged with weight + 200
            key.append(200 + sub_weight)
            idx += 2
            continue

        if ch in _KHMER_CONSONANT_WEIGHTS:
            key.append(_KHMER_CONSONANT_WEIGHTS[ch])
        elif ch in _KHMER_INDEP_VOWEL_WEIGHTS:
            key.append(_KHMER_INDEP_VOWEL_WEIGHTS[ch])
        elif ch in _KHMER_DEP_VOWEL_WEIGHTS:
            key.append(_KHMER_DEP_VOWEL_WEIGHTS[ch])
        elif ch in _KHMER_DIACRITIC_WEIGHTS:
            key.append(_KHMER_DIACRITIC_WEIGHTS[ch])
        else:
            # Fallback for Latin / digits / symbols
            key.append(1000 + ord(ch))

        idx += 1

    return key


def sort_khmer_words(words: List[str]) -> List[str]:
    """Sort a list of Khmer words according to Chuon Nath dictionary collation rules."""
    return sorted(words, key=khmer_sort_key)


# --- 8. Character & Text Detection Utilities ---

def is_khmer_text(text: str) -> bool:
    """
    Check if the string contains any Khmer Unicode characters.
    Covers the primary Khmer block (U+1780..U+17FF) and Khmer Symbols (U+19E0..U+19FF).
    """
    if not text:
        return False
    return any(0x1780 <= ord(c) <= 0x17FF or 0x19E0 <= ord(c) <= 0x19FF for c in text)


def get_khmer_character_stats(text: str) -> dict:
    """
    Analyze text and return counts of Khmer script structural components:
    consonants, independent vowels, dependent vowels, Coeng markers, diacritics, digits, and symbols.
    """
    stats = {
        "total_khmer": 0,
        "consonants": 0,
        "independent_vowels": 0,
        "dependent_vowels": 0,
        "coeng_subscripts": 0,
        "diacritics": 0,
        "digits": 0,
        "symbols": 0,
    }
    for ch in text:
        cp = ord(ch)
        if 0x1780 <= cp <= 0x17A2:
            stats["consonants"] += 1
            stats["total_khmer"] += 1
        elif 0x17A3 <= cp <= 0x17B3:
            stats["independent_vowels"] += 1
            stats["total_khmer"] += 1
        elif 0x17B6 <= cp <= 0x17C5:
            stats["dependent_vowels"] += 1
            stats["total_khmer"] += 1
        elif cp == 0x17D2:
            stats["coeng_subscripts"] += 1
            stats["total_khmer"] += 1
        elif (0x17C6 <= cp <= 0x17D1) or cp == 0x17DD:
            stats["diacritics"] += 1
            stats["total_khmer"] += 1
        elif 0x17E0 <= cp <= 0x17E9:
            stats["digits"] += 1
            stats["total_khmer"] += 1
        elif (0x17D4 <= cp <= 0x17DA) or cp == 0x17DB:
            stats["symbols"] += 1
            stats["total_khmer"] += 1
    return stats


# --- 8. UI Terms Catalog Lookup & Fast Text Linter ---

def lookup_ui_term(query: str = "", data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search data/ui_terms.json for matching English or Khmer UI terms.
    Matches against 'key', 'en', and 'km' fields (case-insensitive for English/keys).
    Sorts exact matches before partial matches.
    """
    if data_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(base_dir, "data", "ui_terms.json")
        if os.path.exists(candidate):
            data_path = candidate
        else:
            data_path = os.path.join("data", "ui_terms.json")

    if not os.path.exists(data_path):
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        terms: List[Dict[str, Any]] = json.load(f)

    if not query or not query.strip():
        return terms[:50]

    q_clean = query.strip()
    q_lower = q_clean.lower()
    exact_matches: List[Dict[str, Any]] = []
    partial_matches: List[Dict[str, Any]] = []

    for item in terms:
        key_lower = item.get("key", "").lower()
        en_lower = item.get("en", "").lower()
        km_val = item.get("km", "")

        if q_lower == key_lower or q_lower == en_lower or q_clean == km_val:
            exact_matches.append(item)
        elif q_lower in key_lower or q_lower in en_lower or q_clean in km_val:
            partial_matches.append(item)

    return exact_matches + partial_matches


def lint_khmer_text(text: str) -> Dict[str, Any]:
    """
    Fast linting inspection of an in-memory Khmer string for common defects:
    - Unicode corruption: Replacement char U+FFFD, control characters
    - Broken typography: Literal dotted circle U+25CC
    - Orphaned combining marks: Vowels or diacritics without a preceding base consonant
    - Trailing Coeng: U+17D2 at the end of text
    - Grammatical inversion: Hallucinated [Adj] + [Noun] order
    - Prohibited royal / monastic register words in consumer UI
    - Currency format: Decimal KHR notation (e.g. 10.00៛)
    - Subscript clipping risk: Stacked subscripts without line-height reminder
    """
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

    if not text:
        return {
            "is_clean": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "stats": get_khmer_character_stats(""),
        }

    # 1. Unicode corruption
    if "\uFFFD" in text:
        errors.append("Unicode Replacement Character (U+FFFD) detected: text has suffered encoding corruption.")

    # 2. Literal dotted circle
    if "\u25CC" in text:
        warnings.append("Literal dotted circle (U+25CC) detected: indicates broken glyph rendering or orphan diacritic.")

    # 3. Trailing Coeng
    if text.endswith("\u17D2"):
        warnings.append("Trailing Coeng subscript sign (U+17D2) at end of text without following consonant.")

    # 4. Orphaned combining marks (at index 0, or after space/ZWSP, or after ASCII/Latin)
    combining_ranges = [
        (0x17B6, 0x17C5),  # Dependent vowels
        (0x17C6, 0x17D1),  # Diacritics
        (0x17DD, 0x17DD),  # Thkeam Khmor
    ]
    def is_combining(cp: int) -> bool:
        return any(start <= cp <= end for start, end in combining_ranges)

    for i, ch in enumerate(text):
        cp = ord(ch)
        if is_combining(cp):
            if i == 0:
                warnings.append(f"Orphaned combining mark U+{cp:04X} at start of string with no base consonant.")
            else:
                prev_ch = text[i - 1]
                prev_cp = ord(prev_ch)
                if prev_ch in " \t\r\n\u200B":
                    warnings.append(f"Orphaned combining mark U+{cp:04X} follows whitespace or ZWSP boundary.")
                elif prev_cp < 0x80 and prev_ch.isascii() and prev_ch.isalnum():
                    warnings.append(f"Combining mark U+{cp:04X} follows Latin/ASCII character '{prev_ch}'.")

    # 5. Inverted grammatical word patterns
    inverted_patterns = [
        (r"សរុបតម្លៃ", "Inverted word order: use 'តម្លៃសរុប' (Total Price: [Noun] + [Adjective])"),
        (r"ថ្មីពាក្យសម្ងាត់", "Inverted word order: use 'ពាក្យសម្ងាត់ថ្មី' (New Password: [Noun] + [Adjective])"),
        (r"ចាស់ពាក្យសម្ងាត់", "Inverted word order: use 'ពាក្យសម្ងាត់ចាស់' (Old Password: [Noun] + [Adjective])"),
        (r"សកម្មអ្នកប្រើប្រាស់", "Inverted word order: use 'អ្នកប្រើប្រាស់សកម្ម' (Active Users: [Noun] + [Adjective])"),
    ]
    for pattern, desc in inverted_patterns:
        if re.search(pattern, text):
            warnings.append(desc)

    # 6. Prohibited royal/monastic words
    royal_terms = ["យាង", "សោយ", "ព្រះរាជ", "ទ្រង់", "សោយទិវង្គត", "និមន្ត", "ឆាន់"]
    for term in royal_terms:
        if term in text:
            warnings.append(f"Prohibited royal/monastic register word '{term}' found. Use modern standard digital terminology.")

    # 7. Decimal KHR currency
    if re.search(r"\d+\.\d{1,2}\s*(?:៛|KHR|រៀល)", text):
        warnings.append("Khmer Riel (KHR) formatted with fractional decimal cents. KHR must be formatted as whole-riel integers without decimals.")
        suggestions.append("Format KHR amounts using whole-riel integers (e.g. '25,000 ៛').")

    # 8. Subscript clipping / line-height check
    stats = get_khmer_character_stats(text)
    if stats["coeng_subscripts"] > 0 or stats["dependent_vowels"] > 0:
        suggestions.append("Khmer text contains stacked subscripts/vowels. Ensure CSS 'line-height: >= 1.6' to prevent diacritic clipping.")

    is_clean = len(errors) == 0 and len(warnings) == 0

    return {
        "is_clean": is_clean,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "stats": stats,
    }


# --- 10. Translation & Text Auto-Fixer Engine ---

_FIX_WORD_ORDERS: List[Tuple[str, str, str]] = [
    (r"សរុបតម្លៃ", "តម្លៃសរុប", "Inverted word order: 'សរុបតម្លៃ' -> 'តម្លៃសរុប' (Total Price)"),
    (r"ថ្មីពាក្យសម្ងាត់", "ពាក្យសម្ងាត់ថ្មី", "Inverted word order: 'ថ្មីពាក្យសម្ងាត់' -> 'ពាក្យសម្ងាត់ថ្មី' (New Password)"),
    (r"ចាស់ពាក្យសម្ងាត់", "ពាក្យសម្ងាត់ចាស់", "Inverted word order: 'ចាស់ពាក្យសម្ងាត់' -> 'ពាក្យសម្ងាត់ចាស់' (Old Password)"),
    (r"សកម្មអ្នកប្រើប្រាស់", "អ្នកប្រើប្រាស់សកម្ម", "Inverted word order: 'សកម្មអ្នកប្រើប្រាស់' -> 'អ្នកប្រើប្រាស់សកម្ម' (Active Users)"),
    (r"ថ្មីសារ", "សារថ្មី", "Inverted word order: 'ថ្មីសារ' -> 'សារថ្មី' (New Message)"),
    (r"ចាស់សារ", "សារចាស់", "Inverted word order: 'ចាស់សារ' -> 'សារចាស់' (Old Message)"),
]

_FIX_ROYAL_REGISTER: List[Tuple[str, str, str]] = [
    (r"យាងចូលក្នុង", "ចូលក្នុង", "Royal register: 'យាងចូលក្នុង' -> 'ចូលក្នុង'"),
    (r"យាងចូល", "ចូលគណនី", "Royal register: 'យាងចូល' -> 'ចូលគណនី' (Sign In)"),
    (r"សោយ", "ពិសារ", "Royal register: 'សោយ' -> 'ពិសារ' (Consume/Eat)"),
    (r"ព្រះរាជទ្រព្យ", "ទ្រព្យសម្បត្តិ", "Royal register: 'ព្រះរាជទ្រព្យ' -> 'ទ្រព្យសម្បត្តិ'"),
    (r"និមន្ត", "អញ្ជើញ", "Monastic register: 'និមន្ត' -> 'អញ្ជើញ' (Invite)"),
]


def fix_khmer_text(text: str) -> Dict[str, Any]:
    """
    Auto-correct common Khmer localization mistakes:
    1. Inverted word order calques (e.g. 'សរុបតម្លៃ' -> 'តម្លៃសរុប')
    2. Decimal KHR (.00៛ / .00 KHR -> whole riels)
    3. Trailing or dangling Coeng marks (U+17D2)
    4. Royal / monastic vocabulary in UI (e.g. 'យាងចូល' -> 'ចូលគណនី')
    5. Broken dotted circle replacement glyphs (U+25CC)
    """
    if not text:
        return {"original": "", "fixed": "", "changes": []}

    fixed = text
    changes: List[str] = []

    # 1. Clean dotted circle (U+25CC)
    if "\u25CC" in fixed:
        fixed = fixed.replace("\u25CC", "")
        changes.append("Removed dotted circle glyph (U+25CC)")

    # 2. Fix inverted word orders
    for pattern, replacement, desc in _FIX_WORD_ORDERS:
        if re.search(pattern, fixed):
            fixed = re.sub(pattern, replacement, fixed)
            changes.append(desc)

    # 3. Fix royal registers
    for pattern, replacement, desc in _FIX_ROYAL_REGISTER:
        if re.search(pattern, fixed):
            fixed = re.sub(pattern, replacement, fixed)
            changes.append(desc)

    # 4. Remove decimal cents from KHR (.00 or .XX)
    # Matches: 25,000.00៛ or 25,000.00 KHR or 25,000.00 ៛
    def _repl_khr(match: re.Match) -> str:
        amount_part = match.group(1)
        suffix = match.group(2)
        return f"{amount_part}{suffix}"

    dec_khr_pattern = re.compile(r"(\d+(?:,\d{3})*)\.\d{2}(\s*(?:៛|KHR|រៀល))")
    if dec_khr_pattern.search(fixed):
        fixed = dec_khr_pattern.sub(_repl_khr, fixed)
        changes.append("Removed fractional decimal cents from Khmer Riel (KHR)")

    # 5. Fix dangling or trailing Coeng (U+17D2)
    # Coeng before space, punctuation, or at end of string
    trailing_coeng_pattern = re.compile(r"\u17D2(?=[\s\.,;!?។៖\)\}\]\"\']|\Z)")
    if trailing_coeng_pattern.search(fixed):
        fixed = trailing_coeng_pattern.sub("", fixed)
        changes.append("Removed dangling/trailing Coeng subscript marker (U+17D2)")

    return {
        "original": text,
        "fixed": fixed,
        "changes": changes,
    }


# --- 11. 4-Tier Cambodian Address Formatter & Parser ---

def format_cambodian_address(components: Dict[str, Any], lang: str = "km") -> str:
    """
    Format a 4-tier Cambodian address into a standard comma-separated address string.
    Keys expected: 'street', 'village', 'sangkat' (or 'commune'), 'khan' (or 'district'), 'province' (or 'capital'), 'postal_code'.
    """
    order = ["street", "village", "sangkat", "commune", "khan", "district", "province", "capital", "postal_code"]
    parts: List[str] = []

    for k in order:
        val = components.get(k)
        if val and isinstance(val, str) and val.strip():
            cleaned = val.strip().strip(",")
            if cleaned and cleaned not in parts:
                parts.append(cleaned)

    # Also catch any extra custom keys
    for k, v in components.items():
        if k not in order and isinstance(v, str) and v.strip():
            cleaned = v.strip().strip(",")
            if cleaned and cleaned not in parts:
                parts.append(cleaned)

    return ", ".join(parts)


def parse_cambodian_address(text: str) -> Dict[str, str]:
    """
    Parse a Cambodian address string into standard administrative components:
    street, village, sangkat, khan, province, postal_code.
    """
    if not text:
        return {"street": "", "village": "", "sangkat": "", "khan": "", "province": "", "postal_code": ""}

    cleaned = text.strip()
    result = {
        "street": "",
        "village": "",
        "sangkat": "",
        "khan": "",
        "province": "",
        "postal_code": "",
    }

    # Extract 5 or 6 digit postal code if at the end
    post_match = re.search(r"(?:,\s*|\s+)(\b\d{5,6}\b)\s*$", cleaned)
    if post_match:
        result["postal_code"] = post_match.group(1)
        cleaned = cleaned[:post_match.start()].strip().rstrip(",")

    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    remaining_street_parts: List[str] = []

    for p in parts:
        # Check province / capital
        if any(prov in p for prov in ["រាជធានី", "ខេត្ត", "Phnom Penh", "Province", "Capital"]):
            result["province"] = p
        # Check Khan / District / Krong
        elif any(d in p for d in ["ខណ្ឌ", "ស្រុក", "ក្រុង", "Khan", "District", "Krong"]):
            result["khan"] = p
        # Check Sangkat / Commune
        elif any(s in p for s in ["សង្កាត់", "ឃុំ", "Sangkat", "Commune"]):
            result["sangkat"] = p
        # Check Village
        elif any(v in p for v in ["ភូមិ", "Village"]):
            result["village"] = p
        else:
            remaining_street_parts.append(p)

    result["street"] = ", ".join(remaining_street_parts)
    return result


# --- 12. Khmer Noun Classifier & Counting Word Engine ---

def format_khmer_count(
    noun: str,
    count: int,
    classifier: Optional[str] = None,
    use_khmer_digits: bool = False,
) -> str:
    """
    Format a count with a noun and optional Khmer classifier (សង្ខយាសព្ទ).
    Khmer word order: [Noun] [Count] [Classifier] (e.g. 'អ្នកប្រើប្រាស់ 3 នាក់').
    """
    cnt_str = to_khmer_digits(count) if use_khmer_digits else str(count)
    if classifier and classifier.strip():
        return f"{noun.strip()} {cnt_str} {classifier.strip()}"
    return f"{noun.strip()} {cnt_str}"


# --- CLI Interface ---

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="khmer_utils.py",
        description="Production Khmer Localization Utilities (Phone, Currency, Dates, Words, KHQR, Collation)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # phone command
    phone_p = subparsers.add_parser("phone", help="Normalize a Cambodian phone number")
    phone_p.add_argument("number", help="Phone string to normalize (e.g. '012 345 678' or '023 210 022')")

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

    # relative-time command
    rel_p = subparsers.add_parser("relative-time", help="Format seconds as natural Khmer relative time (e.g. '5 នាទីមុន')")
    rel_p.add_argument("seconds", type=int, help="Elapsed or difference in seconds (e.g. -300 for 5 min ago, 600 for in 10 min)")
    rel_p.add_argument("--khmer-digits", action="store_true", help="Use Khmer numerals (០-៩)")

    # khqr-crc command
    crc_p = subparsers.add_parser("khqr-crc", help="Compute CRC16 for a KHQR payload")
    crc_p.add_argument("payload", help="Payload ending with '6304'")

    # khqr-parse command
    parse_p = subparsers.add_parser("khqr-parse", help="Parse an EMVCo KHQR payload into structured fields")
    parse_p.add_argument("payload", help="Raw KHQR string")

    # sort command
    sort_p = subparsers.add_parser("sort", help="Sort Khmer words per Chuon Nath dictionary order")
    sort_p.add_argument("words", nargs="+", help="Khmer words to sort")

    # stats command
    stats_p = subparsers.add_parser("stats", help="Analyze Khmer text character statistics")
    stats_p.add_argument("text", help="Khmer string to analyze")

    # lookup command
    lookup_p = subparsers.add_parser("lookup", help="Look up standard UI terms in data/ui_terms.json")
    lookup_p.add_argument("query", nargs="?", default="", help="English, Khmer, or key search term (e.g. 'Settings', 'Save')")

    # lint command
    lint_p = subparsers.add_parser("lint", help="Lint a Khmer string for Unicode corruption, dotted circles, royal words, or decimal KHR")
    lint_p.add_argument("text", help="Text string to lint")

    # break command
    break_p = subparsers.add_parser("break", help="Inject Zero-Width Space (ZWSP) at syllable boundaries for word wrapping")
    break_p.add_argument("text", help="Khmer string to break")

    # address command
    addr_p = subparsers.add_parser("address", help="Format or parse a 4-tier Cambodian address")
    addr_p.add_argument("text", nargs="?", default="", help="Address string to parse")
    addr_p.add_argument("--street", help="Street & building")
    addr_p.add_argument("--sangkat", help="Sangkat / commune")
    addr_p.add_argument("--khan", help="Khan / district")
    addr_p.add_argument("--province", help="Capital / province")
    addr_p.add_argument("--postal-code", help="Postal code")
    addr_p.add_argument("--lang", default="km", choices=["km", "en"], help="Output language (km or en)")

    # fix command
    fix_p = subparsers.add_parser("fix", help="Auto-correct common Khmer localization and translation defects")
    fix_p.add_argument("text", nargs="?", default="", help="Text to auto-fix")
    fix_p.add_argument("--file", help="Path to JSON translation file to batch-fix")
    fix_p.add_argument("--write", action="store_true", help="Write changes directly back to file")

    # install-rules command
    rules_p = subparsers.add_parser("install-rules", help="Install token-efficient Khmer localization guardrails into AI agent configs")
    rules_p.add_argument("--target", default="cursor", choices=["cursor", "cursor-mdc", "claude", "windsurf", "copilot", "gemini", "agents", "all"])
    rules_p.add_argument("--tier", default="standard", choices=["nano", "standard", "enterprise"])
    rules_p.add_argument("--dest", default=".")
    rules_p.add_argument("--force", action="store_true")
    rules_p.add_argument("--dry-run", action="store_true")

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

    if args.command == "relative-time":
        print(format_khmer_relative_time(args.seconds, use_khmer_digits=args.khmer_digits))
        return 0

    if args.command == "khqr-crc":
        crc = calculate_khqr_crc16(args.payload)
        print(f"Computed CRC16: {crc}")
        print(f"Full KHQR: {args.payload}{crc}")
        return 0

    if args.command == "khqr-parse":
        parsed = parse_khqr(args.payload)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        return 0 if parsed["is_valid_format"] else 1

    if args.command == "sort":
        sorted_words = sort_khmer_words(args.words)
        print("\n".join(sorted_words))
        return 0

    if args.command == "stats":
        stats = get_khmer_character_stats(args.text)
        stats["is_khmer"] = is_khmer_text(args.text)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0

    if args.command == "lookup":
        results = lookup_ui_term(args.query)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    if args.command == "lint":
        res = lint_khmer_text(args.text)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res["is_clean"] else 1

    if args.command == "break":
        print(insert_khmer_word_breaks(args.text))
        return 0

    if args.command == "address":
        if args.street or args.sangkat or args.khan or args.province:
            comps = {
                "street": args.street or "",
                "sangkat": args.sangkat or "",
                "khan": args.khan or "",
                "province": args.province or "",
                "postal_code": args.postal_code or "",
            }
            print(format_cambodian_address(comps, lang=args.lang))
            return 0
        parsed = parse_cambodian_address(args.text)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        return 0

    if args.command == "fix":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
            total_fixed = 0
            if isinstance(data, dict):
                fixed_data = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        res = fix_khmer_text(v)
                        fixed_data[k] = res["fixed"]
                        if res["changes"]:
                            total_fixed += 1
                    else:
                        fixed_data[k] = v
                if args.write:
                    with open(args.file, "w", encoding="utf-8") as f:
                        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                    print(f"Fixed {total_fixed} strings in {args.file}")
                else:
                    print(json.dumps(fixed_data, indent=2, ensure_ascii=False))
            return 0
        res = fix_khmer_text(args.text)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    if args.command == "install-rules":
        try:
            from scripts.install_agent_rules import install_rules
        except ImportError:
            from install_agent_rules import install_rules
        res = install_rules(args.target, args.tier, args.dest, args.force, args.dry_run)
        print(json.dumps(res, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
