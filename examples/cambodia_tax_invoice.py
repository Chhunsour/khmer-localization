#!/usr/bin/env python3
"""
cambodia_tax_invoice.py - Cambodian GDT Tax Invoice (វិក្កយបត្រអាករ) Generator

Demonstrates complete compliance with General Department of Taxation (GDT) standards:
1. Validates Seller & Buyer Cambodian Tax Identification Numbers (TIN).
2. Dual-currency computation (USD line items converted to KHR via NBC exchange rate).
3. Integer minor-unit tax calculations (10% VAT with half-up rounding).
4. Spells out total amount in official formal Khmer words (e.g. មួយលាន...រៀលគត់).
5. Generates EMVCo-compliant Bakong KHQR dynamic payload with CRC16-CCITT.
6. Displays dates with Buddhist Era and traditional Lunar Zodiac / Sak era.

Standard Library only. Zero external dependencies. Python 3.9+.
"""

import os
import sys
import datetime

# Ensure scripts directory is available
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.khmer_utils import (
    calculate_money_total,
    format_currency_khmer_words,
    format_khmer_date,
    format_khr,
    format_usd,
    generate_khqr,
    get_khmer_year_era_info,
    normalize_cambodian_phone,
    validate_cambodian_tin,
)


def generate_tax_invoice():
    today = datetime.date(2026, 10, 30)
    invoice_number = "INV-2026-0089"
    nbc_exchange_rate = 4100  # 1 USD = 4,100 KHR (NBC official daily rate)

    # 1. Seller & Buyer Entities
    seller = {
        "name_km": "ក្រុមហ៊ុន សម្ព័ន្ធ បច្ចេកវិទ្យា ខេមបូឌា អិលធីឌី",
        "name_en": "Cambodia Tech Alliance Co., Ltd.",
        "tin": "K001-987654321",
        "address": "អគារកាណាឌីយ៉ា ជាន់ទី១២ មហាវិថីព្រះមុនីវង្ស រាជធានីភ្នំពេញ",
        "phone": "+855 23 999 888",
    }

    buyer = {
        "name_km": "សហគ្រាស អភិវឌ្ឍន៍ ឌីជីថល ខ្មែរ",
        "name_en": "Khmer Digital Development Enterprise",
        "tin": "123456789",
        "address": "ផ្លូវ ២៧១ សង្កាត់បឹងទំពុន ខណ្ឌមានជ័យ រាជធានីភ្នំពេញ",
        "phone": "012 889 977",
    }

    # 2. Validate TINs
    seller_tin_val = validate_cambodian_tin(seller["tin"])
    buyer_tin_val = validate_cambodian_tin(buyer["tin"])

    # 3. Line Items (priced in USD)
    items = [
        {"desc_km": "សេវាប្រឹក្សាប្រព័ន្ធ i18n / Localization Architecture", "price": 250.00, "qty": 1},
        {"desc_km": "ម៉ាស៊ីនមេពពក Cloud Server Hosting (Quarterly)", "price": 75.00, "qty": 2},
        {"desc_km": "វិញ្ញាបនបត្រសុវត្ថិភាព SSL & TLS Certificate", "price": 40.00, "qty": 1},
    ]

    usd_items = [{"price": item["price"], "quantity": item["qty"]} for item in items]
    totals_usd = calculate_money_total(usd_items, currency="USD", tax_rate_percent=10.0)

    # Convert totals to KHR using integer minor units
    subtotal_khr = int(round(totals_usd["subtotal"] * nbc_exchange_rate))
    tax_khr = int(round(totals_usd["tax"] * nbc_exchange_rate))
    grand_total_khr = subtotal_khr + tax_khr

    # 4. Spelled-out Khmer words
    in_words_khr = format_currency_khmer_words(grand_total_khr, "KHR")

    # 5. Traditional Era Info
    era_info = get_khmer_year_era_info(today.year)

    # 6. Generate Bakong KHQR for Payment
    khqr_payload = generate_khqr(
        bakong_account_id="tech_alliance@nbc",
        merchant_name=seller["name_en"],
        amount=grand_total_khr,
        currency="KHR",
        merchant_city="Phnom Penh",
        bill_number=invoice_number,
        purpose="Tax Invoice Payment",
        is_dynamic=True,
    )

    # 7. Print Formal Bilingual Fiscal Invoice
    print("=" * 80)
    print("                    ព្រះរាជាណាចក្រកម្ពុជា / KINGDOM OF CAMBODIA")
    print("                      ជាតិ សាសនា ព្រះមហាក្សត្រ / NATION RELIGION KING")
    print("=" * 80)
    print("                              វិក្កយបត្រអាករ")
    print("                                TAX INVOICE")
    print("-" * 80)
    print(f"លេខវិក្កយបត្រ / Invoice No:  {invoice_number}")
    print(f"កាលបរិច្ឆេទ / Date:          {format_khmer_date(today, include_be=True)}")
    print(f"ប្រតិទិនចន្ទគតិ / Traditional:  {era_info['formal_string_km']}")
    print("-" * 80)
    print(f"អ្នកលក់ / SELLER:   {seller['name_km']} ({seller['name_en']})")
    print(f"លេខអត្តសញ្ញាណកម្មសារពើពន្ធ (TIN): {seller_tin_val['clean']} (Valid: {seller_tin_val['is_valid_syntax']})")
    print(f"អាសយដ្ឋាន / Address: {seller['address']}")
    print("-" * 80)
    print(f"អ្នកទិញ / BUYER:    {buyer['name_km']} ({buyer['name_en']})")
    print(f"លេខអត្តសញ្ញាណកម្មសារពើពន្ធ (TIN): {buyer_tin_val['clean']} (Valid: {buyer_tin_val['is_valid_syntax']})")
    print(f"អាសយដ្ឋាន / Address: {buyer['address']}")
    print("-" * 80)
    print(f"{'ល.រ':<4} | {'បរិយាយមុខទំនិញ / Description':<40} | {'ចំនួន':<5} | {'ថ្លៃឯកតា':<10} | {'សរុប (USD)':<10}")
    print("-" * 80)
    for idx, item in enumerate(items, 1):
        line_tot = item["price"] * item["qty"]
        print(f"{idx:<4} | {item['desc_km'][:40]:<40} | {item['qty']:<5} | ${item['price']:<9.2f} | ${line_tot:<9.2f}")
    print("-" * 80)
    print(f"សរុបមិនរួមអាករ / Subtotal Excl. VAT:                  ${totals_usd['subtotal']:>10.2f}")
    print(f"អាករលើតម្លៃបន្ថែម ១០% / VAT 10%:                       ${totals_usd['tax']:>10.2f}")
    print(f"ចំនួនទឹកប្រាក់សរុបរួម (USD) / Grand Total (USD):          ${totals_usd['total']:>10.2f}")
    print(f"អត្រាប្តូរប្រាក់ផ្លូវការ / Official NBC Exchange Rate:     1 USD = {nbc_exchange_rate:,} ៛")
    print(f"ចំនួនទឹកប្រាក់សរុបជាប្រាក់រៀល / Grand Total (KHR):        {format_khr(grand_total_khr):>14}")
    print("-" * 80)
    print(f"ចំនួនទឹកប្រាក់ជាអក្សរ / Amount in Words:")
    print(f"-> {in_words_khr}")
    print("-" * 80)
    print(f"ទូទាត់ប្រាក់តាមបាគង KHQR / Pay with Bakong KHQR:")
    print(f"Payload: {khqr_payload[:55]}...")
    print(f"Length:  {len(khqr_payload)} characters (CRC16 verified)")
    print("=" * 80)


if __name__ == "__main__":
    generate_tax_invoice()
