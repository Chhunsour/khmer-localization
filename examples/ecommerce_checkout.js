#!/usr/bin/env node
/**
 * E-Commerce Checkout & Invoice Generation Example for Cambodia (Node.js).
 *
 * Demonstrates:
 * 1. Validating Cambodian phone numbers (Mobile vs Landline, Area codes).
 * 2. Minor-unit integer financial calculation (tax, subtotal) with zero floating-point drift.
 * 3. KHQR payload generation (EMVCo TLV format with CRC16-CCITT) and payload parsing.
 * 4. Spelled-out invoice total in formal Khmer words.
 * 5. Khmer text truncation and Buddhist Era date formatting.
 *
 * Run:
 *   node examples/ecommerce_checkout.js
 */

const {
  normalizeCambodianPhone,
  formatKHR,
  formatUSD,
  calculateMoneyTotal,
  formatCurrencyKhmerWords,
  generateKhqr,
  parseKhqr,
  formatKhmerDate,
  safeTruncateKhmer,
} = require("../scripts/khmer_utils");

function runCheckoutFlow() {
  console.log("=".repeat(65));
  console.log(" 🇰🇭 CAMBODIAN E-COMMERCE CHECKOUT SIMULATION (Node.js)");
  console.log("=".repeat(65));

  // 1. Customer Details & Phone Validation
  const customerNameKm = "សុខា ម៉េង (Sokha Meng)";
  const customerPhoneRaw = "012 889 977";
  const deliveryAddress = "ផ្ទះលេខ 42, ផ្លូវ 310, សង្កាត់បឹងកេងកងទី១, ខណ្ឌបឹងកេងកង, រាជធានីភ្នំពេញ";

  const phone = normalizeCambodianPhone(customerPhoneRaw);
  console.log(`Customer Name   : ${customerNameKm}`);
  console.log(`Raw Phone       : ${customerPhoneRaw}`);
  console.log(`Canonical E.164 : ${phone.normalized_e164}`);
  console.log(`Domestic Trunk  : ${phone.normalized_domestic}`);
  console.log(`Line Type       : ${phone.line_type}`);
  console.log(`Area / Category : ${phone.area_name || phone.length_category}`);
  console.log(`Address         : ${safeTruncateKhmer(deliveryAddress, 35)}`);
  console.log("-".repeat(65));

  // 2. Cart Items & Calculation (in KHR minor units = 1 Riel per unit)
  const cartItemsKhr = [
    { nameKm: "អាវយឺតកប្បាស (Cotton T-Shirt)", unitPrice: 28000, quantity: 2 },
    { nameKm: "កាបូបស្ពាយធ្វើដំណើរ (Travel Backpack)", unitPrice: 65000, quantity: 1 },
    { nameKm: "ដបទឹកសុខភាព (Stainless Water Bottle)", unitPrice: 18500, quantity: 2 },
  ];

  // Calculate financial totals (10% VAT in Cambodia)
  const calc = calculateMoneyTotal({
    items: cartItemsKhr.map((item) => ({ price: item.unitPrice, quantity: item.quantity })),
    currency: "KHR",
    taxRatePercent: 10.0,
    roundingMode: "half_up",
  });

  console.log("CART BREAKDOWN (KHR):");
  for (const item of cartItemsKhr) {
    const itemTotal = item.unitPrice * item.quantity;
    console.log(` - ${item.nameKm.padEnd(40, " ")} x${item.quantity} = ${formatKHR(itemTotal)}`);
  }

  console.log(`\nSubtotal        : ${calc.subtotal_formatted}`);
  console.log(`Tax (10% VAT)   : ${calc.tax_formatted}`);
  console.log(`Total Amount    : ${calc.total_formatted}`);

  // 3. Spelled-out Total in Formal Khmer Words
  const totalWords = formatCurrencyKhmerWords(calc.total, "KHR");
  console.log(`Total in Words  : ${totalWords}`);
  console.log("-".repeat(65));

  // 4. Generate Bakong KHQR for Payment
  const now = new Date();
  const yyyymmdd = now.toISOString().slice(0, 10).replace(/-/g, "");
  const billNumber = `INV-${yyyymmdd}-0842`;
  const merchantBakongId = "sokha_store@aclb";
  const merchantName = "SOKHA STORE ONLINE";

  const khqrPayload = generateKhqr({
    bakongAccountId: merchantBakongId,
    merchantName,
    amount: calc.total,
    currency: "KHR",
    billNumber,
    storeLabel: "ONLINE-APP",
    terminalLabel: "POS-01",
  });

  console.log("BAKONG KHQR PAYMENT SPECIFICATION:");
  console.log(`Merchant ID     : ${merchantBakongId}`);
  console.log(`Bill Number     : ${billNumber}`);
  console.log(`KHQR Payload    : ${khqrPayload}`);

  // 5. Verify / Parse KHQR Payload
  const parsedQr = parseKhqr(khqrPayload);
  console.log(`CRC16 Valid     : ${parsedQr.is_valid_crc} (Checksum: ${parsedQr.crc_expected})`);
  console.log(`QR Currency     : ${parsedQr.currency_name} (${parsedQr.currency_code})`);
  console.log(`QR Amount       : ${parsedQr.amount}`);
  console.log(`QR Merchant     : ${parsedQr.merchant_name}`);
  console.log(`QR Bakong ID    : ${parsedQr.bakong_account_id}`);
  console.log("-".repeat(65));

  // 6. Cambodian Fiscal Invoice Header
  const beDate = formatKhmerDate(now, { includeBE: true });
  console.log("CAMBODIAN FISCAL INVOICE HEADER (វិក្កយបត្រ):");
  console.log(`កាលបរិច្ឆេទ (Date)  : ${beDate}`);
  console.log(`លេខវិក្កយបត្រ (Invoice): ${billNumber}`);
  console.log(`អតិថិជន (Customer) : ${customerNameKm}`);
  console.log(`ទឹកប្រាក់សរុប (Total): ${calc.total_formatted} (${totalWords})`);
  console.log("=".repeat(65));
}

if (require.main === module) {
  runCheckoutFlow();
}

module.exports = { runCheckoutFlow };
