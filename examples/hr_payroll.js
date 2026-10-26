#!/usr/bin/env node
/**
 * HR & Payroll Processing Example for Cambodia (Node.js).
 *
 * Demonstrates:
 * 1. Chuon Nath dictionary order collation for sorting employee names in Khmer script.
 * 2. Pay period formatting in Khmer solar months with Buddhist Era (BE = CE + 543).
 * 3. Cambodian Tax on Salary (ToS) and NSSF deduction using integer minor units.
 * 4. Generating formal bilingual payslips (ប័ណ្ណបើកប្រាក់បៀវត្ស).
 * 5. Spelled-out net salary in formal Khmer words.
 *
 * Run:
 *   node examples/hr_payroll.js
 */

const {
  formatKHR,
  formatCurrencyKhmerWords,
  formatKhmerDate,
  sortKhmerWords,
  normalizeCambodianPhone,
} = require("../scripts/khmer_utils");

function calculateCambodiaTaxOnSalaryKhr(taxableSalaryKhr) {
  if (taxableSalaryKhr <= 1500000) {
    return 0;
  } else if (taxableSalaryKhr <= 2000000) {
    return Math.round(taxableSalaryKhr * 0.05 - 75000);
  } else if (taxableSalaryKhr <= 8500000) {
    return Math.round(taxableSalaryKhr * 0.1 - 175000);
  } else if (taxableSalaryKhr <= 12500000) {
    return Math.round(taxableSalaryKhr * 0.15 - 600000);
  } else {
    return Math.round(taxableSalaryKhr * 0.2 - 1225000);
  }
}

function runPayrollFlow() {
  console.log("=".repeat(70));
  console.log(" 🇰🇭 CAMBODIAN HR PAYROLL & PAYSLIP SYSTEM (Node.js)");
  console.log("=".repeat(70));

  // 1. Employee Roster Collation per Chuon Nath Dictionary
  const employeeRoster = [
    { nameKm: "វណ្ណដា ហេង", nameEn: "Vanda Heng", role: "Senior Engineer", phone: "012 334 455", baseKhr: 5200000 },
    { nameKm: "កញ្ចនា ស៊ុន", nameEn: "Kanchana Sun", role: "UI/UX Designer", phone: "098 776 655", baseKhr: 3800000 },
    { nameKm: "ចំរើន គង់", nameEn: "Chamroeun Kong", role: "QA Lead", phone: "087 112 233", baseKhr: 4200000 },
    { nameKm: "កុសល ចាន់", nameEn: "Kosal Chan", role: "Backend Lead", phone: "017 889 900", baseKhr: 6000000 },
    { nameKm: "សុជាតា លី", nameEn: "Socheata Ly", role: "Product Manager", phone: "023 210 022", baseKhr: 5500000 },
  ];

  const namesKm = employeeRoster.map((e) => e.nameKm);
  const sortedNames = sortKhmerWords(namesKm);

  console.log("EMPLOYEE ROSTER (SORTED BY CHUON NATH KHMER ALPHABETICAL ORDER):");
  const sortedRoster = [];
  sortedNames.forEach((name, idx) => {
    const emp = employeeRoster.find((e) => e.nameKm === name);
    sortedRoster.push(emp);
    const phoneInfo = normalizeCambodianPhone(emp.phone);
    console.log(
      ` ${idx + 1}. ${emp.nameKm.padEnd(16, " ")} | ${emp.nameEn.padEnd(16, " ")} | ${emp.role.padEnd(18, " ")} | ${phoneInfo.normalized_e164}`
    );
  });
  console.log("-".repeat(70));

  // 2. Process Monthly Payroll for Target Employee
  const targetEmp = sortedRoster[0];
  const payPeriodDate = new Date(2026, 9, 31); // October 31, 2026
  const periodKhmer = formatKhmerDate(payPeriodDate, { includeBE: true });

  const baseSalaryKhr = targetEmp.baseKhr;
  const seniorityAllowanceKhr = 150000;
  const attendanceBonusKhr = 80000;
  const grossSalaryKhr = baseSalaryKhr + seniorityAllowanceKhr + attendanceBonusKhr;

  const nssfPensionKhr = 24000;
  const tosKhr = calculateCambodiaTaxOnSalaryKhr(grossSalaryKhr);
  const totalDeductionsKhr = nssfPensionKhr + tosKhr;
  const netSalaryKhr = grossSalaryKhr - totalDeductionsKhr;

  const netSalaryWords = formatCurrencyKhmerWords(netSalaryKhr, "KHR");

  // 3. Print Official Payslip
  console.log("OFFICIAL MONTHLY PAYSLIP (ប័ណ្ណបើកប្រាក់បៀវត្សប្រចាំខែ):");
  console.log(`ការបរិច្ឆេទបើក (Pay Date) : ${periodKhmer}`);
  console.log(`ឈ្មោះនិយោជិត (Employee)  : ${targetEmp.nameKm} (${targetEmp.nameEn})`);
  console.log(`មុខតំណែង (Job Role)     : ${targetEmp.role}`);
  console.log(`លេខទូរស័ព្ទ (Contact)     : ${normalizeCambodianPhone(targetEmp.phone).normalized_e164}`);
  console.log("-".repeat(70));
  console.log("EARNINGS & ALLOWANCES (ប្រាក់ចំណូល):");
  console.log(` - ប្រាក់ខែគោល (Base Salary)             : ${formatKHR(baseSalaryKhr)}`);
  console.log(` - បំណាច់អតីតភាពការងារ (Seniority Bonus)   : ${formatKHR(seniorityAllowanceKhr)}`);
  console.log(` - ប្រាក់រង្វាន់វត្តមាន (Attendance Bonus)   : ${formatKHR(attendanceBonusKhr)}`);
  console.log(`   សរុបប្រាក់ចំណូលដុល (Gross Earnings)      : ${formatKHR(grossSalaryKhr)}`);
  console.log("\nDEDUCTIONS (ការកាត់កងតាមច្បាប់):");
  console.log(` - ភាគទាន ប.ស.ស. (NSSF Pension)          : -${formatKHR(nssfPensionKhr)}`);
  console.log(` - ពន្ធលើប្រាក់បៀវត្ស (Tax on Salary)       : -${formatKHR(tosKhr)}`);
  console.log(`   សរុបការកាត់កង (Total Deductions)       : -${formatKHR(totalDeductionsKhr)}`);
  console.log("-".repeat(70));
  console.log(`ប្រាក់បៀវត្សសុទ្ធ (Net Take-Home Pay)     : ${formatKHR(netSalaryKhr)}`);
  console.log(`ជាអក្សរ (In Khmer Words)                : ${netSalaryWords}`);
  console.log("=".repeat(70));
}

if (require.main === module) {
  runPayrollFlow();
}

module.exports = { runPayrollFlow, calculateCambodiaTaxOnSalaryKhr };
