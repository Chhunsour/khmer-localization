#!/usr/bin/env python3
"""
HR & Payroll Processing Example for Cambodia.

Demonstrates:
1. Chuon Nath dictionary order collation for sorting employee names in Khmer script.
2. Pay period formatting in Khmer solar months with Buddhist Era (BE = CE + 543).
3. Cambodian Tax on Salary (ToS) and NSSF deduction using integer minor units.
4. Generating formal bilingual payslips (ប័ណ្ណបើកប្រាក់បៀវត្ស).
5. Spelled-out net salary in formal Khmer words.

Run:
    python3 examples/hr_payroll.py
"""

import os
import sys
from datetime import date

# Allow importing scripts from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.khmer_utils import (
    format_khr,
    format_usd,
    calculate_money_total,
    format_currency_khmer_words,
    format_khmer_date,
    sort_khmer_words,
    normalize_cambodian_phone,
)


def calculate_cambodia_tax_on_salary_khr(taxable_salary_khr: int) -> int:
    """
    Progressive Cambodian Tax on Salary (ToS) brackets for resident individuals:
    - 0 to 1,500,000 KHR: 0%
    - 1,500,001 to 2,000,000 KHR: 5%
    - 2,000,001 to 8,500,000 KHR: 10%
    - 8,500,001 to 12,500,000 KHR: 15%
    - Over 12,500,000 KHR: 20%
    """
    if taxable_salary_khr <= 1_500_000:
        return 0
    elif taxable_salary_khr <= 2_000_000:
        return int(round((taxable_salary_khr * 0.05) - 75_000))
    elif taxable_salary_khr <= 8_500_000:
        return int(round((taxable_salary_khr * 0.10) - 175_000))
    elif taxable_salary_khr <= 12_500_000:
        return int(round((taxable_salary_khr * 0.15) - 600_000))
    else:
        return int(round((taxable_salary_khr * 0.20) - 1_225_000))


def run_payroll_flow():
    print("=" * 70)
    print(" 🇰🇭 CAMBODIAN HR PAYROLL & PAYSLIP SYSTEM (ប្រព័ន្ធបើកប្រាក់បៀវត្ស)")
    print("=" * 70)

    # 1. Employee Roster Collation per Chuon Nath Dictionary
    employee_roster = [
        {"name_km": "វណ្ណដា ហេង", "name_en": "Vanda Heng", "role": "Senior Engineer", "phone": "012 334 455", "base_khr": 5200000},
        {"name_km": "កញ្ចនា ស៊ុន", "name_en": "Kanchana Sun", "role": "UI/UX Designer", "phone": "098 776 655", "base_khr": 3800000},
        {"name_km": "ចំរើន គង់", "name_en": "Chamroeun Kong", "role": "QA Lead", "phone": "087 112 233", "base_khr": 4200000},
        {"name_km": "កុសល ចាន់", "name_en": "Kosal Chan", "role": "Backend Lead", "phone": "017 889 900", "base_khr": 6000000},
        {"name_km": "សុជាតា លី", "name_en": "Socheata Ly", "role": "Product Manager", "phone": "023 210 022", "base_khr": 5500000},
    ]

    # Extract Khmer names and sort per Chuon Nath standard
    names_km = [e["name_km"] for e in employee_roster]
    sorted_names = sort_khmer_words(names_km)

    print("EMPLOYEE ROSTER (SORTED BY CHUON NATH KHMER ALPHABETICAL ORDER):")
    sorted_roster = []
    for idx, name in enumerate(sorted_names, 1):
        emp = next(e for e in employee_roster if e["name_km"] == name)
        sorted_roster.append(emp)
        phone_info = normalize_cambodian_phone(emp["phone"])
        print(f" {idx}. {emp['name_km']:<16} | {emp['name_en']:<16} | {emp['role']:<18} | {phone_info['normalized_e164']}")
    print("-" * 70)

    # 2. Process Monthly Payroll for Target Employee
    target_emp = sorted_roster[0]  # First employee alphabetically (e.g. ក...)
    pay_period_date = date(2026, 10, 31)
    period_khmer = format_khmer_date(pay_period_date, include_be=True)

    base_salary_khr = target_emp["base_khr"]
    seniority_allowance_khr = 150000  # បំណាច់អតីតភាពការងារ
    attendance_bonus_khr = 80000      # ប្រាក់ឧបត្ថម្ភវត្តមានការងារ
    gross_salary_khr = base_salary_khr + seniority_allowance_khr + attendance_bonus_khr

    # Deductions: NSSF Employee Pension (2% of wage capped at 1.2M KHR wage ceiling -> max 24,000 KHR)
    nssf_pension_khr = 24000
    # Cambodian Tax on Salary
    tos_khr = calculate_cambodia_tax_on_salary_khr(gross_salary_khr)
    total_deductions_khr = nssf_pension_khr + tos_khr
    net_salary_khr = gross_salary_khr - total_deductions_khr

    # Spelled out net salary in Khmer words
    net_salary_words = format_currency_khmer_words(net_salary_khr, currency="KHR")

    # 3. Print Official Payslip (ប័ណ្ណបើកប្រាក់បៀវត្ស)
    print("OFFICIAL MONTHLY PAYSLIP (ប័ណ្ណបើកប្រាក់បៀវត្សប្រចាំខែ):")
    print(f"ការបរិច្ឆេទបើក (Pay Date) : {period_khmer}")
    print(f"ឈ្មោះនិយោជិត (Employee)  : {target_emp['name_km']} ({target_emp['name_en']})")
    print(f"មុខតំណែង (Job Role)     : {target_emp['role']}")
    print(f"លេខទូរស័ព្ទ (Contact)     : {normalize_cambodian_phone(target_emp['phone'])['normalized_e164']}")
    print("-" * 70)
    print("EARNINGS & ALLOWANCES (ប្រាក់ចំណូល):")
    print(f" - ប្រាក់ខែគោល (Base Salary)             : {format_khr(base_salary_khr)}")
    print(f" - បំណាច់អតីតភាពការងារ (Seniority Bonus)   : {format_khr(seniority_allowance_khr)}")
    print(f" - ប្រាក់រង្វាន់វត្តមាន (Attendance Bonus)   : {format_khr(attendance_bonus_khr)}")
    print(f"   សរុបប្រាក់ចំណូលដុល (Gross Earnings)      : {format_khr(gross_salary_khr)}")
    print("\nDEDUCTIONS (ការកាត់កងតាមច្បាប់):")
    print(f" - ភាគទាន ប.ស.ស. (NSSF Pension)          : -{format_khr(nssf_pension_khr)}")
    print(f" - ពន្ធលើប្រាក់បៀវត្ស (Tax on Salary)       : -{format_khr(tos_khr)}")
    print(f"   សរុបការកាត់កង (Total Deductions)       : -{format_khr(total_deductions_khr)}")
    print("-" * 70)
    print(f"ប្រាក់បៀវត្សសុទ្ធ (Net Take-Home Pay)     : {format_khr(net_salary_khr)}")
    print(f"ជាអក្សរ (In Khmer Words)                : {net_salary_words}")
    print("=" * 70)


if __name__ == "__main__":
    run_payroll_flow()
