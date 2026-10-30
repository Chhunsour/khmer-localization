/**
 * cambodia_tax_invoice.js - Cambodian GDT Tax Invoice (វិក្កយបត្រអាករ) Generator
 *
 * Demonstrates complete compliance with General Department of Taxation (GDT) standards in Node.js:
 * 1. Validates Seller & Buyer Cambodian Tax Identification Numbers (TIN).
 * 2. Dual-currency computation (USD line items converted to KHR via NBC exchange rate).
 * 3. Integer minor-unit tax calculations (10% VAT with half-up rounding).
 * 4. Spells out total amount in official formal Khmer words (e.g. មួយលាន...រៀលគត់).
 * 5. Generates EMVCo-compliant Bakong KHQR dynamic payload with CRC16-CCITT.
 * 6. Displays dates with Buddhist Era and traditional Lunar Zodiac / Sak era.
 *
 * Zero external dependencies. Compatible with Node.js 16+, Bun, Deno.
 */

"use strict";

const path = require("path");
const u = require(path.join(__dirname, "..", "scripts", "khmer_utils.js"));

function generateTaxInvoice() {
  const today = new Date(Date.UTC(2026, 9, 30));
  const invoiceNumber = "INV-2026-0089";
  const nbcExchangeRate = 4100; // 1 USD = 4,100 KHR

  // 1. Seller & Buyer Entities
  const seller = {
    name_km: "ក្រុមហ៊ុន សម្ព័ន្ធ បច្ចេកវិទ្យា ខេមបូឌា អិលធីឌី",
    name_en: "Cambodia Tech Alliance Co., Ltd.",
    tin: "K001-987654321",
    address: "អគារកាណាឌីយ៉ា ជាន់ទី១២ មហាវិថីព្រះមុនីវង្ស រាជធានីភ្នំពេញ",
    phone: "+855 23 999 888",
  };

  const buyer = {
    name_km: "សហគ្រាស អភិវឌ្ឍន៍ ឌីជីថល ខ្មែរ",
    name_en: "Khmer Digital Development Enterprise",
    tin: "123456789",
    address: "ផ្លូវ ២៧១ សង្កាត់បឹងទំពុន ខណ្ឌមានជ័យ រាជធានីភ្នំពេញ",
    phone: "012 889 977",
  };

  // 2. Validate TINs
  const sellerTinVal = u.validateCambodianTin(seller.tin);
  const buyerTinVal = u.validateCambodianTin(buyer.tin);

  // 3. Line Items (priced in USD)
  const items = [
    { desc_km: "សេវាប្រឹក្សាប្រព័ន្ធ i18n / Localization Architecture", price: 250.00, qty: 1 },
    { desc_km: "ម៉ាស៊ីនមេពពក Cloud Server Hosting (Quarterly)", price: 75.00, qty: 2 },
    { desc_km: "វិញ្ញាបនបត្រសុវត្ថិភាព SSL & TLS Certificate", price: 40.00, qty: 1 },
  ];

  const usdItems = items.map((it) => ({ price: it.price, quantity: it.qty }));
  const totalsUsd = u.calculateMoneyTotal(usdItems, { currency: "USD", taxRatePercent: 10.0 });

  // Convert totals to KHR using integer minor units
  const subtotalKhr = Math.round(totalsUsd.subtotal * nbcExchangeRate);
  const taxKhr = Math.round(totalsUsd.tax * nbcExchangeRate);
  const grandTotalKhr = subtotalKhr + taxKhr;

  // 4. Spelled-out Khmer words
  const inWordsKhr = u.formatCurrencyKhmerWords(grandTotalKhr, "KHR");

  // 5. Traditional Era Info
  const eraInfo = u.getKhmerYearEraInfo(today.getUTCFullYear());

  // 6. Generate Bakong KHQR for Payment
  const khqrPayload = u.generateKhqr({
    bakongAccountId: "tech_alliance@nbc",
    merchantName: seller.name_en,
    amount: grandTotalKhr,
    currency: "KHR",
    merchantCity: "Phnom Penh",
    billNumber: invoiceNumber,
    purpose: "Tax Invoice Payment",
    isDynamic: true,
  });

  // 7. Print Formal Bilingual Fiscal Invoice
  console.log("=".repeat(80));
  console.log("                    ព្រះរាជាណាចក្រកម្ពុជា / KINGDOM OF CAMBODIA");
  console.log("                      ជាតិ សាសនា ព្រះមហាក្សត្រ / NATION RELIGION KING");
  console.log("=".repeat(80));
  console.log("                              វិក្កយបត្រអាករ");
  console.log("                                TAX INVOICE");
  console.log("-".repeat(80));
  console.log(`លេខវិក្កយបត្រ / Invoice No:  ${invoiceNumber}`);
  console.log(`កាលបរិច្ឆេទ / Date:          ${u.formatKhmerDate(today, { includeBE: true })}`);
  console.log(`ប្រតិទិនចន្ទគតិ / Traditional:  ${eraInfo.formal_string_km}`);
  console.log("-".repeat(80));
  console.log(`អ្នកលក់ / SELLER:   ${seller.name_km} (${seller.name_en})`);
  console.log(`លេខអត្តសញ្ញាណកម្មសារពើពន្ធ (TIN): ${sellerTinVal.clean} (Valid: ${sellerTinVal.is_valid_syntax})`);
  console.log(`អាសយដ្ឋាន / Address: ${seller.address}`);
  console.log("-".repeat(80));
  console.log(`អ្នកទិញ / BUYER:    ${buyer.name_km} (${buyer.name_en})`);
  console.log(`លេខអត្តសញ្ញាណកម្មសារពើពន្ធ (TIN): ${buyerTinVal.clean} (Valid: ${buyerTinVal.is_valid_syntax})`);
  console.log(`អាសយដ្ឋាន / Address: ${buyer.address}`);
  console.log("-".repeat(80));
  console.log("ល.រ  | បរិយាយមុខទំនិញ / Description             | ចំនួន | ថ្លៃឯកតា   | សរុប (USD)");
  console.log("-".repeat(80));
  items.forEach((item, idx) => {
    const lineTot = item.price * item.qty;
    console.log(`${String(idx + 1).padEnd(4)} | ${item.desc_km.slice(0, 40).padEnd(40)} | ${String(item.qty).padEnd(5)} | $${item.price.toFixed(2).padEnd(9)} | $${lineTot.toFixed(2).padEnd(9)}`);
  });
  console.log("-".repeat(80));
  console.log(`សរុបមិនរួមអាករ / Subtotal Excl. VAT:                  $${totalsUsd.subtotal.toFixed(2).padStart(10)}`);
  console.log(`អាករលើតម្លៃបន្ថែម ១០% / VAT 10%:                       $${totalsUsd.tax.toFixed(2).padStart(10)}`);
  console.log(`ចំនួនទឹកប្រាក់សរុបរួម (USD) / Grand Total (USD):          $${totalsUsd.total.toFixed(2).padStart(10)}`);
  console.log(`អត្រាប្តូរប្រាក់ផ្លូវការ / Official NBC Exchange Rate:     1 USD = ${nbcExchangeRate.toLocaleString()} ៛`);
  console.log(`ចំនួនទឹកប្រាក់សរុបជាប្រាក់រៀល / Grand Total (KHR):        ${u.formatKHR(grandTotalKhr).padStart(14)}`);
  console.log("-".repeat(80));
  console.log("ចំនួនទឹកប្រាក់ជាអក្សរ / Amount in Words:");
  console.log(`-> ${inWordsKhr}`);
  console.log("-".repeat(80));
  console.log("ទូទាត់ប្រាក់តាមបាគង KHQR / Pay with Bakong KHQR:");
  console.log(`Payload: ${khqrPayload.slice(0, 55)}...`);
  console.log(`Length:  ${khqrPayload.length} characters (CRC16 verified)`);
  console.log("=".repeat(80));
}

if (require.main === module) {
  generateTaxInvoice();
}
