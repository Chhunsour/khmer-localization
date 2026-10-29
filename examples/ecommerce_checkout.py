#!/usr/bin/env python3
"""
E-Commerce Checkout & Invoice Generation Example for Cambodia.

Demonstrates:
1. Validating Cambodian phone numbers (Mobile vs Landline, Telco detection).
2. Minor-unit integer financial calculation (tax, discount, subtotal) with zero floating-point drift.
3. KHQR payload generation (EMVCo TLV format with CRC16-CCITT) and payload parsing.
4. Spelled-out invoice total in formal Khmer words.
5. Khmer text truncation and Buddhist Era date formatting.

Run:
    python3 examples/ecommerce_checkout.py
"""

import os
import sys
from datetime import datetime

# Allow importing scripts from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.khmer_utils import (
    normalize_cambodian_phone,
    format_khr,
    format_usd,
    calculate_money_total,
    format_currency_khmer_words,
    generate_khqr,
    parse_khqr,
    format_khmer_date,
    safe_truncate_khmer,
    validate_cambodian_id,
)


def run_checkout_flow():
    print("=" * 65)
    print(" 🇰🇭 CAMBODIAN E-COMMERCE CHECKOUT SIMULATION")
    print("=" * 65)

    # 1. Customer Details & Phone Validation
    customer_name_km = "សុខា ម៉េង (Sokha Meng)"
    customer_phone_raw = "012 889 977"
    customer_id_raw = "១២-០១២៣-៤៥៦៧"
    delivery_address = "ផ្ទះលេខ 42, ផ្លូវ 310, សង្កាត់បឹងកេងកងទី១, ខណ្ឌបឹងកេងកង, រាជធានីភ្នំពេញ"

    phone = normalize_cambodian_phone(customer_phone_raw)
    cust_id = validate_cambodian_id(customer_id_raw)
    print(f"Customer Name   : {customer_name_km}")
    print(f"Customer ID     : {cust_id['normalized']} ({cust_id['id_type']}, Province: {cust_id['province_code']})")
    print(f"Raw Phone       : {customer_phone_raw}")
    print(f"Canonical E.164 : {phone['normalized_e164']}")
    print(f"Domestic Trunk  : {phone['normalized_domestic']}")
    print(f"Line Type       : {phone['line_type']}")
    print(f"Area / Category : {phone['area_name'] or phone['length_category']}")
    print(f"Address         : {safe_truncate_khmer(delivery_address, 35)}")
    print("-" * 65)

    # 2. Cart Items & Calculation (in KHR minor units = 1 Riel per unit)
    cart_items_khr = [
        {"name_km": "អាវយឺតកប្បាស (Cotton T-Shirt)", "unit_price": 28000, "quantity": 2},
        {"name_km": "កាបូបស្ពាយធ្វើដំណើរ (Travel Backpack)", "unit_price": 65000, "quantity": 1},
        {"name_km": "ដបទឹកសុខភាព (Stainless Water Bottle)", "unit_price": 18500, "quantity": 2},
    ]

    # Calculate financial totals (10% VAT in Cambodia)
    calc = calculate_money_total(
        items=[{"price": item["unit_price"], "quantity": item["quantity"]} for item in cart_items_khr],
        currency="KHR",
        tax_rate_percent=10.0,  # 10.00% VAT
        rounding_mode="half_up",
    )

    print("CART BREAKDOWN (KHR):")
    for item in cart_items_khr:
        item_total = item["unit_price"] * item["quantity"]
        print(f" - {item['name_km']:<40} x{item['quantity']} = {format_khr(item_total)}")

    print(f"\nSubtotal        : {calc['subtotal_formatted']}")
    print(f"Tax (10% VAT)   : {calc['tax_formatted']}")
    print(f"Total Amount    : {calc['total_formatted']}")

    # 3. Spelled-out Total in Formal Khmer Words
    total_words = format_currency_khmer_words(calc["total"], currency="KHR")
    print(f"Total in Words  : {total_words}")
    print("-" * 65)

    # 4. Generate Bakong KHQR for Payment
    now = datetime.now()
    bill_number = f"INV-{now.strftime('%Y%m%d')}-0842"
    merchant_bakong_id = "sokha_store@aclb"
    merchant_name = "SOKHA STORE ONLINE"

    khqr_payload = generate_khqr(
        bakong_account_id=merchant_bakong_id,
        merchant_name=merchant_name,
        amount=calc["total"],
        currency="KHR",
        bill_number=bill_number,
        store_label="ONLINE-APP",
        terminal_label="POS-01",
    )

    print("BAKONG KHQR PAYMENT SPECIFICATION:")
    print(f"Merchant ID     : {merchant_bakong_id}")
    print(f"Bill Number     : {bill_number}")
    print(f"KHQR Payload    : {khqr_payload}")

    # 5. Verify / Parse KHQR Payload
    parsed_qr = parse_khqr(khqr_payload)
    print(f"CRC16 Valid     : {parsed_qr['is_valid_crc']} (Checksum: {parsed_qr['crc_expected']})")
    print(f"QR Currency     : {parsed_qr['currency_name']} ({parsed_qr['currency_code']})")
    print(f"QR Amount       : {parsed_qr['amount']}")
    print(f"QR Merchant     : {parsed_qr['merchant_name']}")
    print(f"QR Bakong ID    : {parsed_qr['bakong_account_id']}")
    print("-" * 65)

    # 6. Cambodian Fiscal Invoice Header
    be_date = format_khmer_date(now.date(), include_be=True)
    print("CAMBODIAN FISCAL INVOICE HEADER (វិក្កយបត្រ):")
    print(f"កាលបរិច្ឆេទ (Date)  : {be_date}")
    print(f"លេខវិក្កយបត្រ (Invoice): {bill_number}")
    print(f"អតិថិជន (Customer) : {customer_name_km}")
    print(f"ទឹកប្រាក់សរុប (Total): {calc['total_formatted']} ({total_words})")
    print("=" * 65)


if __name__ == "__main__":
    run_checkout_flow()
