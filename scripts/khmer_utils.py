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

Standard Library only. Compatible with Python 3.9+.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
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


KHMER_ZODIAC_ANIMALS: List[Tuple[str, str]] = [
    ("ជូត", "Rat"),
    ("ឆ្លូវ", "Ox"),
    ("ខាល", "Tiger"),
    ("ថោះ", "Rabbit"),
    ("រោង", "Dragon"),
    ("ម្សាញ់", "Snake"),
    ("មមី", "Horse"),
    ("មមែ", "Goat"),
    ("វក", "Monkey"),
    ("រកា", "Rooster"),
    ("ច", "Dog"),
    ("កុរ", "Pig"),
]


def get_khmer_lunar_zodiac(ce_year: int) -> Dict[str, str]:
    """
    Returns the Khmer 12-animal zodiac year (ឆ្នាំទាំង១២) for a Common Era year.
    Calculation: (ce_year - 4) % 12
    E.g. 2024 -> ឆ្នាំរោង (Dragon), 2025 -> ឆ្នាំម្សាញ់ (Snake), 2026 -> ឆ្នាំមមី (Horse).
    """
    idx = (ce_year - 4) % 12
    km, en = KHMER_ZODIAC_ANIMALS[idx]
    return {
        "year": str(ce_year),
        "zodiac_km": km,
        "zodiac_en": en,
        "full_km": f"ឆ្នាំ{km}",
    }


KHMER_SAK_ERAS: List[Tuple[str, str]] = [
    ("សំរឹទ្ធិស័ក", "10th Sak (Samriddhisak)"),
    ("ឯកស័ក", "1st Sak (Ekasak)"),
    ("ទោស័ក", "2nd Sak (Toasak)"),
    ("ត្រីស័ក", "3rd Sak (Treisak)"),
    ("ចត្វាស័ក", "4th Sak (Chatvasak)"),
    ("បញ្ចស័ក", "5th Sak (Panjasak)"),
    ("ឆស័ក", "6th Sak (Chhasak)"),
    ("សប្តស័ក", "7th Sak (Saptasak)"),
    ("អដ្ឋស័ក", "8th Sak (Atthasak)"),
    ("នព្វស័ក", "9th Sak (Nopphasak)"),
]


def get_khmer_sak_era(ce_year: int) -> Dict[str, Any]:
    """
    Returns the Khmer Sak era (ស័កទាំង១០) for a Common Era year.
    Calculation: (ce_year + 2) % 10.
    E.g. 2024 -> ឆស័ក (6th Sak), 2025 -> សប្តស័ក (7th Sak), 2026 -> អដ្ឋស័ក (8th Sak).
    """
    be_year = to_buddhist_era(ce_year)
    sak_idx = (ce_year + 2) % 10
    km, en = KHMER_SAK_ERAS[sak_idx]
    sak_num = 10 if sak_idx == 0 else sak_idx
    return {
        "ce_year": ce_year,
        "be_year": be_year,
        "sak_number": sak_num,
        "sak_km": km,
        "sak_en": en,
    }


def get_khmer_year_era_info(ce_year: int) -> Dict[str, Any]:
    """
    Returns complete combined traditional Cambodian year information:
    Buddhist Era, Animal Zodiac (ឆ្នាំទាំង១២), and Sak era (ស័កទាំង១០).
    E.g. 2026 -> 'ព.ស. ២៥៧០ ឆ្នាំមមី អដ្ឋស័ក'
    """
    zodiac = get_khmer_lunar_zodiac(ce_year)
    sak = get_khmer_sak_era(ce_year)
    be_str = str(sak["be_year"]).translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))
    full_formal = f"ព.ស. {be_str} {zodiac['full_km']} {sak['sak_km']}"
    return {
        "ce_year": ce_year,
        "be_year": sak["be_year"],
        "be_year_km": be_str,
        "zodiac_km": zodiac["zodiac_km"],
        "zodiac_en": zodiac["zodiac_en"],
        "sak_km": sak["sak_km"],
        "sak_en": sak["sak_en"],
        "sak_number": sak["sak_number"],
        "formal_string_km": full_formal,
    }


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
        "point_of_initiation": None,
        "mcc": None,
        "bill_number": None,
        "store_label": None,
        "terminal_label": None,
        "purpose_of_transaction": None,
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

        if "01" in tags:
            val_01 = tags["01"]
            result["point_of_initiation"] = "dynamic" if val_01 == "12" else ("static" if val_01 == "11" else val_01)

        if "52" in tags:
            result["mcc"] = tags["52"]

        # Extract Tag 62 sub-tags
        if "62" in tags and isinstance(tags["62"], dict):
            sub_62 = tags["62"].get("sub_tags", {})
            if "01" in sub_62:
                result["bill_number"] = sub_62["01"]
            if "07" in sub_62:
                result["store_label"] = sub_62["07"]
            if "08" in sub_62:
                result["terminal_label"] = sub_62["08"]
            if "09" in sub_62:
                result["purpose_of_transaction"] = sub_62["09"]

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


def format_khqr_merchant_name(name: str) -> str:
    """
    Sanitize and format EMVCo Tag 59 (Merchant Name) for Bakong KHQR.

    Rules:
    - Strips invalid ASCII control characters, newlines, and quotes.
    - Limits length to maximum 25 characters (EMVCo Tag 59 specification).
    - Falls back to 'MERCHANT' if empty or invalid.
    """
    if not name or not isinstance(name, str):
        return "MERCHANT"

    sanitized = re.sub(r"[\r\n\t]+", " ", name)
    sanitized = re.sub(r'[\"\';<>\\`]+', "", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if not sanitized:
        return "MERCHANT"

    return sanitized[:25]


def generate_khqr(
    bakong_account_id: str,
    merchant_name: str,
    amount: float | int,
    currency: str = "KHR",
    merchant_city: str = "Phnom Penh",
    bill_number: str = "",
    store_label: str = "",
    terminal_label: str = "",
    purpose: str = "",
    mcc: str = "5999",
    is_dynamic: bool = True,
) -> str:
    """
    Generate an EMVCo compliant Bakong KHQR payment payload with CRC16 checksum.
    Decouples payload generation from bank settlement or API authentication.
    """
    def _format_tlv(tag: str, value: str) -> str:
        return f"{tag}{len(value):02d}{value}"

    # Tag 00: Payload Format Indicator (01)
    # Tag 01: Point of Initiation Method (12 = Dynamic, 11 = Static)
    init_method = "12" if is_dynamic else "11"
    parts = [_format_tlv("00", "01"), _format_tlv("01", init_method)]

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
    parts.append(_format_tlv("59", format_khqr_merchant_name(merchant_name)))

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
    if purpose:
        sub_62 += _format_tlv("09", purpose[:25])
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


# --- 8. Cambodian National Identification (ID) Validation ---

def validate_cambodian_id(id_val: str) -> Dict[str, Any]:
    """
    Validate and normalize a Cambodian National Identification Card (អត្តសញ្ញាណប័ណ្ណសញ្ជាតិខ្មែរ).

    Supports:
    - 9-digit legacy laminated national IDs.
    - 10-digit smart biometric ID cards (GDI / Ministry of Interior).
    - Khmer numerals (០-៩) and Arabic digits (0-9).
    - Permissive formatting (strips whitespace, dashes, and periods).

    Returns a structured dictionary with normalized formats and validity status.
    """
    if not isinstance(id_val, str):
        id_val = str(id_val) if id_val is not None else ""

    raw = id_val
    # Convert Khmer digits to Arabic digits
    normalized = re.sub(
        r"[\u17E0-\u17E9]",
        lambda m: str(ord(m.group(0)) - 0x17E0),
        raw,
    )
    # Strip whitespace, hyphens, and delimiters
    clean_digits = re.sub(r"[\s\-\./,]+", "", normalized)

    if not clean_digits.isdigit():
        return {
            "raw": raw,
            "normalized": clean_digits,
            "khmer_digits": "",
            "is_valid": False,
            "id_type": None,
            "province_code": None,
            "error": "National ID contains non-numeric characters",
        }

    length = len(clean_digits)
    if length not in (9, 10):
        return {
            "raw": raw,
            "normalized": clean_digits,
            "khmer_digits": "",
            "is_valid": False,
            "id_type": None,
            "province_code": None,
            "error": f"Invalid ID length ({length} digits). Expected 9 or 10 digits.",
        }

    id_type = "smart_id" if length == 10 else "legacy_id"
    province_code = clean_digits[:2]
    khmer_digits = "".join(chr(0x17E0 + int(c)) for c in clean_digits)

    return {
        "raw": raw,
        "normalized": clean_digits,
        "khmer_digits": khmer_digits,
        "is_valid": True,
        "id_type": id_type,
        "province_code": province_code,
        "error": None,
    }


# --- 9. Cambodian Vehicle License Plate Parser ---

def parse_khmer_license_plate(plate_str: str) -> Dict[str, Any]:
    """
    Parse and validate Cambodian vehicle license plates (ក្រសួងសាធារណការ និងដឹកជញ្ជូន - MPWT).

    Supports:
    - Standard civilian cars: '2A-1234', '2BC-5678', 'ភ្នំពេញ 2BC-1234', 'Phnom Penh 2BC-1234'.
    - Motorcycles: '1A-1234', '1AB-5678', 'ភ្នំពេញ 1FD-1234'.
    - Official state plates: 'រដ្ឋ 01 2-1234', 'STATE'.
    - National police: 'ន.ប 1-2345'.
    - Royal Cambodian Armed Forces: 'ខ.ម 02 1-2345'.
    """
    if not isinstance(plate_str, str):
        plate_str = str(plate_str) if plate_str is not None else ""

    raw = plate_str.strip()
    normalized = re.sub(
        r"[\u17E0-\u17E9]",
        lambda m: str(ord(m.group(0)) - 0x17E0),
        raw,
    )

    result: Dict[str, Any] = {
        "raw": raw,
        "normalized": normalized,
        "is_valid_format": False,
        "plate_type": "unknown",
        "category": None,
        "province": None,
        "series": None,
        "number": None,
        "error": None,
    }

    if not normalized:
        result["error"] = "Empty license plate string"
        return result

    # Check State / Official plates
    if "រដ្ឋ" in raw or normalized.upper().startswith("STATE"):
        result["is_valid_format"] = True
        result["plate_type"] = "state"
        result["category"] = "Government / State Official"
        return result

    if "ន.ប" in raw or "នប" in raw:
        result["is_valid_format"] = True
        result["plate_type"] = "police"
        result["category"] = "National Police (នគរបាលជាតិ)"
        return result

    if "ខ.ម" in raw or "ខម" in raw:
        result["is_valid_format"] = True
        result["plate_type"] = "military"
        result["category"] = "Royal Cambodian Armed Forces (កងយោធពលខេមរភូមិន្ទ)"
        return result

    pattern = r"^(?:(.+?)\s+)?([1-9][A-Za-z]{1,3})[\s\-]+(\d{3,5})$"
    m = re.match(pattern, normalized)
    if m:
        prov, series, num = m.groups()
        series_upper = series.upper()
        class_digit = int(series_upper[0])

        result["is_valid_format"] = True
        result["province"] = prov.strip() if prov else None
        result["series"] = series_upper
        result["number"] = num

        if class_digit == 1:
            result["plate_type"] = "motorcycle"
            result["category"] = "Motorcycle (ទោចក្រយានយន្ត)"
        elif class_digit == 2:
            result["plate_type"] = "civilian_car"
            result["category"] = "Automobile / Passenger Vehicle (រថយន្តទេសចរណ៍)"
        elif class_digit in (3, 4):
            result["plate_type"] = "commercial"
            result["category"] = "Commercial / Freight Vehicle (រថយន្តដឹកទំនិញ)"
        else:
            result["plate_type"] = "special"
            result["category"] = "Special Heavy Equipment (គ្រឿងចក្រពិសេស)"

        return result

    result["error"] = "Unrecognized Cambodian license plate structure"
    return result


# --- 9. Cambodian Tax Identification Number (TIN) Validator ---

def validate_cambodian_tin(input_str: str) -> Dict[str, Any]:
    """
    Validates a Cambodian Tax Identification Number (TIN / VATTIN) issued by GDT.
    Accepts:
    - 9-digit standard corporate TIN (e.g. '123456789' or '000123456')
    - Entity-prefixed TIN (e.g. 'K001-123456789', 'B001-123456789', 'L123456789')
    - Khmer numerals (e.g. '១២៣៤៥៦៧៨៩')
    """
    result: Dict[str, Any] = {
        "raw": input_str,
        "clean": None,
        "is_valid_syntax": False,
        "tin_type": "invalid",
        "entity_type": "unknown",
        "branch_code": None,
        "digits": None,
        "error": None,
    }
    if not input_str or not isinstance(input_str, str):
        result["error"] = "Input TIN is empty or invalid"
        return result

    raw = input_str.strip()
    # Normalize Khmer numerals to ASCII
    normalized = re.sub(
        r"[\u17E0-\u17E9]",
        lambda m: str(ord(m.group(0)) - 0x17E0),
        raw,
    )
    # Strip spaces and punctuation except dashes
    clean_str = re.sub(r"[\s\.\,]+", "", normalized)

    # 1. Check prefixed branch format: e.g. K001-123456789 or B001-123456789 or K-123456789
    branch_match = re.match(r"^([KBLEkble])(\d{3})?[\-]?(\d{9})$", clean_str)
    if branch_match:
        prefix, branch, digits = branch_match.groups()
        prefix_upper = prefix.upper()
        result["clean"] = f"{prefix_upper}{branch or '001'}-{digits}"
        result["is_valid_syntax"] = True
        result["digits"] = digits
        result["branch_code"] = branch or "001"
        result["tin_type"] = "branch_tin" if branch else "vat_tin"
        if prefix_upper == "K":
            result["entity_type"] = "corporate"
        elif prefix_upper == "B":
            result["entity_type"] = "branch"
        elif prefix_upper == "L":
            result["entity_type"] = "sole_proprietorship"
        else:
            result["entity_type"] = "general"
        return result

    # 2. Check pure 9-digit format
    digits_only = re.sub(r"[\-]", "", clean_str)
    if re.match(r"^\d{9}$", digits_only):
        result["clean"] = digits_only
        result["is_valid_syntax"] = True
        result["digits"] = digits_only
        result["tin_type"] = "standard_tin"
        result["entity_type"] = "general"
        return result

    result["error"] = "TIN must consist of 9 digits, optionally prefixed by entity code (e.g. K001-123456789)"
    return result


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

    return 0


if __name__ == "__main__":
    sys.exit(main())
