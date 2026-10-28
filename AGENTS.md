# AGENTS.md - Developer & Agent Instructions for Khmer Localization

This repository provides production-grade Khmer language (`km` / `km-KH`) localization tools, isomorphic libraries, datasets, and quality audit engines.

---

## 1. Quick Verification & Test Commands

Always verify that your working tree passes tests and Unicode integrity checks:

```bash
# Run all unit tests (Python & Node.js isomorphic parity)
python3 -m unittest discover -s tests -p "test_*.py" -v

# Run strict Unicode integrity check (zero tolerance for dotted circles or orphan marks)
python3 scripts/check_khmer_unicode.py --strict .

# Run i18n code & locale audit
python3 scripts/audit_khmer_i18n.py

# Run runnable reference demonstrations
npm run example:checkout
npm run example:payroll
```

---

## 2. Zero-Token Policy for AI Agents

To minimize context token consumption and eliminate LLM translation hallucinations:

1. **Do NOT read large data files into context:**
   Instead of reading `data/ui_terms.json` (burning ~3,500 tokens), run:
   ```bash
   python3 scripts/khmer_utils.py lookup "<term>"
   # or Node.js:
   node scripts/khmer_utils.js lookup "<term>"
   ```

2. **Do NOT handcraft phone, currency, or KHQR algorithms:**
   Execute the tested CLI commands directly:
   ```bash
   # Phone normalization (+855)
   python3 scripts/khmer_utils.py phone "012 345 678"

   # Whole-riel KHR formatting (never fractional cents)
   python3 scripts/khmer_utils.py currency 25000 --currency KHR

   # Spelled-out Khmer numbers for official invoices
   python3 scripts/khmer_utils.py words 25000 --currency KHR

   # Bakong KHQR EMVCo CRC16 checksum
   python3 scripts/khmer_utils.py khqr-crc "<payload6304>"
   ```

3. **Fast Text Linting:**
   Verify generated copy for Unicode replacement characters, dotted circles, royal words, and decimal KHR:
   ```bash
   python3 scripts/khmer_utils.py lint "<khmer-text>"
   ```

4. **Model Context Protocol (MCP) Server:**
   This repository exposes native JSON-RPC stdio MCP servers:
   ```bash
   # Python MCP server
   python3 scripts/khmer_mcp_server.py

   # Node.js MCP server
   node scripts/khmer_mcp_server.js
   ```

---

## 3. The 5 Non-Negotiable Localization Rules

1. **Word Order:** Strictly `[Noun] + [Adjective]` (e.g. `តម្លៃសរុប` "Total Price", not `សរុបតម្លៃ`; `អ្នកប្រើប្រាស់សកម្ម` "Active Users", not `សកម្មអ្នកប្រើប្រាស់`).
2. **Currency:** Cambodian Riel (`KHR` / `៛`) uses whole-riel integers. **Never format KHR with decimal cents (`.00`)**.
3. **Register:** Professional modern digital tone. **Never use royal (*Reachasap*) or monastic (*Sanghasap*) vocabulary** (avoid `យាង`, `សោយ`, `ព្រះរាជ`, `និមន្ត`).
4. **String Truncation:** Never cut strings by UTF-16 code units (`.slice(0, n)`). Truncating after Coeng (`\u17D2`) causes broken **dotted circles (`U+25CC`)**. Always use `Intl.Segmenter` graphemes.
5. **Typography & Layout:** Apply CSS `line-height >= 1.6` to prevent vertical clipping of stacked vowels and subscripts. Preserve Zero-Width Spaces (`\u200B`) for browser word breaking.

---

## 4. Key References

- Drop-in copy-paste code snippets: `references/agent-fast-path.md`
- Pre-tuned system prompts for Cursor / Windsurf / Claude: `prompts/agent-system-prompts.md`
- Extended 9-step agent workflow and 4-layer governance: `references/agent-workflow.md`
- All 21 datasets in `data/`: `references/data-catalogs.md`
