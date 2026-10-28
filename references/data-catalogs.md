# Machine-Readable Data Catalogs (`data/`) & Metadata Registry

This repository includes 21 structured, machine-readable datasets in `data/`. Consult `data/METADATA.json` for verified source authorities, update procedures, and licensing for all catalogs.

---

## Catalog Index

| Catalog File | Records | Authority / Source | Primary Usage |
| :--- | :--- | :--- | :--- |
| `data/ui_terms.json` | 100+ | Industry Standard / Tech Lexicon | Clean UI translations; prohibits hallucinations |
| `data/provinces.json` | 25 | National Institute of Statistics / ISO 3166-2:KH | Province & capital dropdowns |
| `data/banknotes.json` | 11 | National Bank of Cambodia (NBC) | Currency cash handling & cash register UI |
| `data/telecom_operators.json` | 10 | Telecommunication Regulator of Cambodia (TRC) | Carrier detection & MCC-MNC codes |
| `data/public_holidays.json` | 22 | Royal Government Sub-Decree (Anukret) | Payroll, working days, and calendar UI |
| `data/bakong_members.json` | 14 | NBC Bakong Payment System | Bank selection & KHQR acquiring bank routing |
| `data/khqr_mcc_codes.json` | 10 | ISO 18245 / NBC KHQR Standard | Merchant Category Codes for KHQR Tag 52 |
| `data/khmer_symbols.json` | 8 | Unicode Standard / Chuon Nath | Typography symbols (Khan, Bariyoosan, Lek Too) |
| `data/khmer_keyboard.json` | 18 | NiDA Standard Keyboard Mapping | Virtual keyboard layouts & key mappings |
| `data/phnom_penh_districts.json`| 14 | Ministry of Interior (MoI) | All 14 Khans of Phnom Penh capital |
| `data/siem_reap_districts.json` | 12 | Ministry of Interior (MoI) | All 12 districts of Siem Reap province |
| `data/battambang_districts.json`| 14 | Ministry of Interior (MoI) | All 14 districts of Battambang province |
| `data/kandal_districts.json`    | 11 | Ministry of Interior (MoI) | All 11 districts of Kandal province |
| `data/kampong_cham_districts.json`| 10 | Ministry of Interior (MoI) | All 10 districts of Kampong Cham province |
| `data/kampot_districts.json`    | 9  | Ministry of Interior (MoI) | All 9 districts of Kampot province |
| `data/preah_sihanouk_districts.json`| 5 | Ministry of Interior (MoI) | All 5 coastal districts of Preah Sihanouk |
| `data/khmer_consonants.json`   | 33 | Chuon Nath Dictionary / MoEYS | 33 consonants with series 1/2 and phonology |
| `data/khmer_independent_vowels.json`| 14| Unicode Standard / MoEYS | 14 non-deprecated independent vowels |
| `data/cambodia_postal_codes.json`| 12| Cambodia Post / MPTC | 6-digit postal codes (optional for delivery) |
| `data/cambodia_logistics.json` | 10 | Cambodian Logistics Association | Express couriers & delivery integrations |
| `data/cambodia_ministries.json`| 5  | Royal Government of Cambodia | Regulatory ministries & government portals |

---

## Token-Efficient Data Access for AI Agents

Rather than reading massive JSON files into context, agents should use the built-in lookup tools:

```bash
# Query UI terms without reading ui_terms.json
python3 scripts/khmer_utils.py lookup "Settings"
# or
node scripts/khmer_utils.js lookup "Settings"
```

Output:
```json
[
  {
    "key": "nav.settings",
    "en": "Settings",
    "km": "ការកំណត់",
    "category": "navigation",
    "avoid": "ការរៀបចំ"
  }
]
```
