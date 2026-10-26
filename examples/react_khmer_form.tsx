import React, { useState, useId, useMemo, ChangeEvent, FormEvent } from "react";
import {
  normalizeCambodianPhone,
  formatKHR,
  formatUSD,
  formatCurrencyKhmerWords,
  safeTruncateKhmer,
} from "../scripts/khmer_utils";

type SupportedLocale = "km" | "en";

interface FormState {
  fullName: string;
  phoneNumber: string;
  currency: "KHR" | "USD";
  amount: string;
  notes: string;
}

const UI_STRINGS: Record<SupportedLocale, Record<string, string>> = {
  km: {
    pageTitle: "ទម្រង់ទូទាត់ប្រាក់ និងព័ត៌មានអតិថិជន",
    fullNameLabel: "ឈ្មោះពេញ (អតិថិជន)",
    fullNamePlaceholder: "ឧ. សុខា ម៉េង",
    phoneLabel: "លេខទូរស័ព្ទ (កម្ពុជា)",
    phonePlaceholder: "012 345 678 ឬ +855 12 345 678",
    currencyLabel: "រូបិយប័ណ្ណ",
    amountLabel: "ចំនួនទឹកប្រាក់",
    amountPlaceholderKHR: "ឧ. 25000 (ប្រាក់រៀលគ្មានកាក់ទេ)",
    amountPlaceholderUSD: "ឧ. 10.50",
    notesLabel: "កំណត់សម្គាល់បន្ថែម",
    notesPlaceholder: "ព័ត៌មានលម្អិតអំពីការដឹកជញ្ជូន ឬបញ្ជាទិញ...",
    previewTitle: "ផ្ទៀងផ្ទាត់ទិន្នន័យមុននឹងដាក់ស្នើ",
    submitButton: "បញ្ជាក់ និងបន្តការទូទាត់",
    inWordsPrefix: "ជាអក្សរ:",
    lineTypeMobile: "ទូរស័ព្ទចល័ត",
    lineTypeFixed: "ទូរស័ព្ទលើតុ",
    invalidPhoneMsg: "លេខទូរស័ព្ទមិនត្រឹមត្រូវ (សូមបញ្ចូលលេខ ៨ ឬ ៩ ខ្ទង់)",
    langToggle: "English",
  },
  en: {
    pageTitle: "Customer Payment & Checkout Form",
    fullNameLabel: "Full Name",
    fullNamePlaceholder: "e.g. Sokha Meng",
    phoneLabel: "Phone Number (Cambodia)",
    phonePlaceholder: "012 345 678 or +855 12 345 678",
    currencyLabel: "Currency",
    amountLabel: "Payment Amount",
    amountPlaceholderKHR: "e.g. 25000 (whole riels, no decimals)",
    amountPlaceholderUSD: "e.g. 10.50",
    notesLabel: "Order Notes",
    notesPlaceholder: "Delivery instructions or order specifics...",
    previewTitle: "Review Details Before Submission",
    submitButton: "Confirm & Proceed to Payment",
    inWordsPrefix: "In Words:",
    lineTypeMobile: "Mobile",
    lineTypeFixed: "Landline",
    invalidPhoneMsg: "Invalid phone syntax (expected 8 or 9 national digits)",
    langToggle: "ភាសាខ្មែរ",
  },
};

/**
 * Production-ready bilingual Khmer/English React Checkout Form.
 * Demonstrates typography safeguard (line-height >= 1.7), grapheme-safe truncation,
 * Cambodian phone normalization, and integer minor-unit dual currency handling.
 */
export function ReactKhmerPaymentForm() {
  const [locale, setLocale] = useState<SupportedLocale>("km");
  const [form, setForm] = useState<FormState>({
    fullName: "",
    phoneNumber: "",
    currency: "KHR",
    amount: "25000",
    notes: "",
  });

  const t = UI_STRINGS[locale];
  const nameId = useId();
  const phoneId = useId();
  const currencyId = useId();
  const amountId = useId();
  const notesId = useId();

  // Validate Cambodian phone number on the fly
  const phoneValidation = useMemo(() => {
    if (!form.phoneNumber.trim()) return null;
    return normalizeCambodianPhone(form.phoneNumber);
  }, [form.phoneNumber]);

  // Financial calculation & spelling out in Khmer words
  const parsedAmount = parseFloat(form.amount) || 0;
  const formattedAmount = useMemo(() => {
    return form.currency === "KHR"
      ? formatKHR(parsedAmount)
      : formatUSD(parsedAmount);
  }, [form.currency, parsedAmount]);

  const amountInWords = useMemo(() => {
    if (parsedAmount <= 0) return "";
    return formatCurrencyKhmerWords(parsedAmount, form.currency);
  }, [form.currency, parsedAmount]);

  // Safe preview truncation (preserves Coeng subscript clusters and combining marks)
  const notesPreview = useMemo(() => {
    return safeTruncateKhmer(form.notes, 40);
  }, [form.notes]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (phoneValidation && !phoneValidation.is_valid_syntax) {
      alert(t.invalidPhoneMsg);
      return;
    }
    alert(
      locale === "km"
        ? `បានបញ្ជាក់ការទូទាត់ចំនួន ${formattedAmount} (${amountInWords}) សម្រាប់ ${phoneValidation?.normalized_e164 || form.phoneNumber}`
        : `Confirmed payment of ${formattedAmount} for ${phoneValidation?.normalized_e164 || form.phoneNumber}`
    );
  };

  return (
    <div
      lang={locale}
      dir="ltr"
      style={{
        fontFamily: "'Kantumruy Pro', 'Siemreap', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        lineHeight: 1.75, // Vital for Khmer: prevents clipping of stacked vowels (e.g. U+17B8, U+17BA) and Coeng subscripts (U+17D2)
        maxWidth: "600px",
        margin: "2rem auto",
        padding: "1.5rem",
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
        color: "#1f2937",
      }}
    >
      {/* Header & Language Switcher */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 700 }}>{t.pageTitle}</h2>
        <button
          type="button"
          onClick={() => setLocale((prev) => (prev === "km" ? "en" : "km"))}
          style={{
            padding: "0.4rem 0.8rem",
            backgroundColor: "#f3f4f6",
            border: "1px solid #d1d5db",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: 600,
          }}
          aria-label="Toggle language"
        >
          {t.langToggle}
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
        {/* Full Name */}
        <div>
          <label htmlFor={nameId} style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>
            {t.fullNameLabel}
          </label>
          <input
            id={nameId}
            type="text"
            value={form.fullName}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setForm({ ...form, fullName: e.target.value })}
            placeholder={t.fullNamePlaceholder}
            style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem" }}
            required
          />
        </div>

        {/* Phone Number */}
        <div>
          <label htmlFor={phoneId} style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>
            {t.phoneLabel}
          </label>
          <input
            id={phoneId}
            type="tel"
            value={form.phoneNumber}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setForm({ ...form, phoneNumber: e.target.value })}
            placeholder={t.phonePlaceholder}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "6px",
              border: phoneValidation && !phoneValidation.is_valid_syntax ? "1px solid #ef4444" : "1px solid #d1d5db",
              fontSize: "1rem",
            }}
            required
          />
          {phoneValidation && (
            <div style={{ fontSize: "0.85rem", marginTop: "0.3rem" }}>
              {phoneValidation.is_valid_syntax ? (
                <span style={{ color: "#059669" }}>
                  ✓ {phoneValidation.normalized_e164} ({phoneValidation.line_type === "fixed_line" ? t.lineTypeFixed : t.lineTypeMobile}
                  {phoneValidation.area_name ? ` - ${phoneValidation.area_name}` : ""})
                </span>
              ) : (
                <span style={{ color: "#dc2626" }}>⚠ {t.invalidPhoneMsg}</span>
              )}
            </div>
          )}
        </div>

        {/* Currency & Amount */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "1rem" }}>
          <div>
            <label htmlFor={currencyId} style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>
              {t.currencyLabel}
            </label>
            <select
              id={currencyId}
              value={form.currency}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                setForm({ ...form, currency: e.target.value as "KHR" | "USD" })
              }
              style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem" }}
            >
              <option value="KHR">KHR (៛)</option>
              <option value="USD">USD ($)</option>
            </select>
          </div>

          <div>
            <label htmlFor={amountId} style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>
              {t.amountLabel}
            </label>
            <input
              id={amountId}
              type="number"
              step={form.currency === "KHR" ? "100" : "0.01"}
              min="0"
              value={form.amount}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setForm({ ...form, amount: e.target.value })}
              placeholder={form.currency === "KHR" ? t.amountPlaceholderKHR : t.amountPlaceholderUSD}
              style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem" }}
              required
            />
          </div>
        </div>

        {/* Live In-Words Calculation Display */}
        {amountInWords && (
          <div
            style={{
              padding: "0.75rem",
              backgroundColor: "#f0fdf4",
              border: "1px solid #bbf7d0",
              borderRadius: "6px",
              fontSize: "0.9rem",
              color: "#166534",
            }}
          >
            <strong>{t.inWordsPrefix}</strong> {amountInWords}
          </div>
        )}

        {/* Notes with Grapheme-Safe Preview */}
        <div>
          <label htmlFor={notesId} style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>
            {t.notesLabel}
          </label>
          <textarea
            id={notesId}
            rows={3}
            value={form.notes}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setForm({ ...form, notes: e.target.value })}
            placeholder={t.notesPlaceholder}
            style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db", fontSize: "1rem" }}
          />
          {notesPreview && (
            <div style={{ fontSize: "0.85rem", color: "#6b7280", marginTop: "0.2rem" }}>
              Preview: <em>{notesPreview}</em>
            </div>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          style={{
            padding: "0.8rem",
            backgroundColor: "#2563eb",
            color: "#ffffff",
            border: "none",
            borderRadius: "6px",
            fontSize: "1rem",
            fontWeight: 600,
            cursor: "pointer",
            marginTop: "0.5rem",
          }}
        >
          {t.submitButton}
        </button>
      </form>
    </div>
  );
}

export default ReactKhmerPaymentForm;
