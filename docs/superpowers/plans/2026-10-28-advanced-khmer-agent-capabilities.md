# Advanced Khmer AI Agent Capabilities & Developer Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate `khmer-localization` into the definitive world-class Khmer localization and AI agent engineering toolkit by introducing automated translation fixing, natural relative time formatting, 4-tier address formatting/parsing, noun counting classifiers, expanded 250+ UI terms, interactive visual playground tabs, and active project Cursor rules.

**Architecture:** Build zero-dependency isomorphic implementations across Python (`scripts/khmer_utils.py`), Node.js (`scripts/khmer_utils.js`), and TypeScript (`scripts/khmer_utils.ts`). Expose all capabilities via zero-token CLI subcommands and native JSON-RPC MCP server tools (`scripts/khmer_mcp_server.py` and `scripts/khmer_mcp_server.js`).

**Tech Stack:** Python 3.10+ (standard library), Node.js (ECMAScript 2020+), TypeScript, HTML5/CSS3/JavaScript (vanilla, offline).

**Spec:** Self-contained specification derived from Cambodian digital commerce standards, National Bank of Cambodia (NBC), GDT tax invoicing, and Telecommunication Regulator of Cambodia (TRC).

## Global Constraints
- Zero external runtime dependencies in both Python and Node.js.
- Strict Unicode compliance: 0 literal dotted circles (`U+25CC`), 0 orphan Coeng subscripts (`U+17D2`), clean UTF-8 byte encoding.
- Isomorphic parity: every utility feature must exist in both Python and JavaScript/TypeScript.
- Full offline capability: playground and utilities must function with no network connectivity.
- Deterministic test coverage: 100% passing tests in `tests/`.

## Review Focus
1. Inverted word order auto-correction handles multiple substitutions in the same string without infinite loops or double replacements.
2. Decimal KHR stripping handles various currencies (`៛`, `KHR`, `riel`) and spacing variations (`25.00៛`, `25.00 KHR`, `1,250.00 ៛`).
3. Relative time formatter correctly distinguishes past ("មុន") vs. future ("ទៀត" / "ក្នុងរយៈពេល..."), including immediate proximity ("អម្បាញ់មិញ").
4. Address formatter handles partial components gracefully without undefined/None in output.
5. Classifier counting engine supports both Arabic and Khmer digits without corrupting noun phrase word order (`[Noun] + [Number] + [Classifier]`).

---

### Task 1: Khmer Translation & Text Auto-Fixer Engine

**Files:**
- Modify: `scripts/khmer_utils.py`
- Modify: `scripts/khmer_utils.js`
- Modify: `scripts/khmer_utils.ts`
- Modify: `scripts/khmer_mcp_server.py`
- Modify: `scripts/khmer_mcp_server.js`
- Test: `tests/test_khmer_autofix.py`

- [ ] Write failing test `tests/test_khmer_autofix.py` verifying:
  - Inverted word order fixes (`សរុបតម្លៃ` -> `តម្លៃសរុប`, `ថ្មីពាក្យសម្ងាត់` -> `ពាក្យសម្ងាត់ថ្មី`, `សកម្មអ្នកប្រើប្រាស់` -> `អ្នកប្រើប្រាស់សកម្ម`).
  - Decimal KHR removal (`25.00៛` -> `25៛`, `50.00 KHR` -> `50 KHR`).
  - Trailing Coeng `\u17D2` stripping.
  - Social register substitution (`យាងចូល` -> `ចូលគណនី`, `សោយ` -> `ពិសារ`).
  - Dotted circle removal.
- [ ] Implement `fix_khmer_text(text: str) -> Dict[str, Any]` in `scripts/khmer_utils.py` returning `{ "original": text, "fixed": fixed_text, "changes": [...] }`.
- [ ] Implement `fixKhmerText(text)` in `scripts/khmer_utils.js` and `khmer_utils.ts`.
- [ ] Add CLI subcommand `fix` in Python and Node.js.
- [ ] Add MCP tool `khmer_fix_text` in Python and Node.js MCP servers.
- [ ] Run unit tests and confirm pass.

---

### Task 2: Relative Time & Date Range Formatter

**Files:**
- Modify: `scripts/khmer_utils.py`
- Modify: `scripts/khmer_utils.js`
- Modify: `scripts/khmer_utils.ts`
- Modify: `scripts/khmer_mcp_server.py`
- Modify: `scripts/khmer_mcp_server.js`
- Test: `tests/test_khmer_relative_time.py`

- [ ] Write failing test `tests/test_khmer_relative_time.py` verifying:
  - Just now (< 10 seconds): "អម្បាញ់មិញ".
  - Seconds ago: "X វិនាទីមុន".
  - Minutes ago: "X នាទីមុន".
  - Hours ago: "X ម៉ោងមុន".
  - Yesterday: "ម្សិលមិញ".
  - Days ago: "X ថ្ងៃមុន".
  - Weeks ago: "X សប្តាហ៍មុន".
  - Months ago: "X ខែមុន".
  - Years ago: "X ឆ្នាំមុន".
  - Future: "ក្នុងរយៈពេល X នាទីទៀត", "ថ្ងៃស្អែក".
- [ ] Implement `format_khmer_relative_time(diff_seconds: int, use_khmer_digits: bool = False) -> str` in `scripts/khmer_utils.py`.
- [ ] Implement `formatKhmerRelativeTime(diffSeconds, useKhmerDigits = false)` in `scripts/khmer_utils.js` and `khmer_utils.ts`.
- [ ] Add CLI subcommand `relative-time` in Python and Node.js.
- [ ] Add MCP tool `khmer_format_relative_time` in Python and Node.js MCP servers.
- [ ] Run unit tests and confirm pass.

---

### Task 3: Cambodian 4-Tier Address Formatter & Parser

**Files:**
- Modify: `scripts/khmer_utils.py`
- Modify: `scripts/khmer_utils.js`
- Modify: `scripts/khmer_utils.ts`
- Modify: `scripts/khmer_mcp_server.py`
- Modify: `scripts/khmer_mcp_server.js`
- Test: `tests/test_cambodian_address.py`

- [ ] Write failing test `tests/test_cambodian_address.py` verifying:
  - Formatting address dictionary into standard Khmer address line: `[Building/Street], [Sangkat], [Khan], [Capital/Province], [Postal Code]`.
  - Formatting bilingual English address line.
  - Parsing address strings into component dictionary.
- [ ] Implement `format_cambodian_address(components: Dict[str, str], lang: str = "km") -> str` in `scripts/khmer_utils.py`.
- [ ] Implement `parse_cambodian_address(text: str) -> Dict[str, str]` in `scripts/khmer_utils.py`.
- [ ] Implement isomorphic equivalents in `scripts/khmer_utils.js` and `khmer_utils.ts`.
- [ ] Add CLI subcommand `address` in Python and Node.js.
- [ ] Add MCP tool `khmer_format_address` in Python and Node.js MCP servers.
- [ ] Run unit tests and confirm pass.

---

### Task 4: Noun Counting Classifiers & UI Terms Expansion (250+ Terms)

**Files:**
- Create: `data/khmer_classifiers.json`
- Modify: `data/ui_terms.json`
- Modify: `data/METADATA.json`
- Modify: `scripts/khmer_utils.py`
- Modify: `scripts/khmer_utils.js`
- Modify: `scripts/khmer_utils.ts`
- Test: `tests/test_khmer_classifiers.py`
- Modify: `tests/test_ui_terms.py`
- Modify: `tests/test_data_metadata.py`

- [ ] Create `data/khmer_classifiers.json` containing 16 essential Cambodian noun classifiers with usage domain and examples.
- [ ] Implement `format_khmer_count(noun: str, count: int, classifier: Optional[str] = None, use_khmer_digits: bool = False) -> str` in Python, JS, and TS.
- [ ] Expand `data/ui_terms.json` to 250+ terms with mobile app patterns (biometrics, notifications, gestures, OTP).
- [ ] Update `data/METADATA.json` to reflect new catalog and updated 250+ count.
- [ ] Update tests to assert >= 250 terms and valid schema.
- [ ] Run all tests and confirm pass.

---

### Task 5: Interactive Visual Playground Upgrade

**Files:**
- Modify: `playground/index.html`

- [ ] Add "Auto-Fixer" tab to interactive playground.
- [ ] Add "Relative Time" calculator tab to playground.
- [ ] Add "Delivery Address" builder with live Khmer and English preview.
- [ ] Update embedded dictionary data to include all 250+ UI terms.
- [ ] Verify clean offline browser execution and responsive mobile rendering.

---

### Task 6: Direct Project Guardrails & Documentation Updates

**Files:**
- Create: `.cursor/rules/khmer-localization.mdc`
- Modify: `README.md`
- Modify: `SKILL.md`
- Modify: `.github/workflows/tests.yml`

- [ ] Install `.cursor/rules/khmer-localization.mdc` directly in the repository for immediate developer guardrails.
- [ ] Update `README.md` with new metrics, MCP tools, and visual tables.
- [ ] Update `SKILL.md` with new zero-token CLI subcommands.
- [ ] Update `.github/workflows/tests.yml` to verify new CLI subcommands.

---

### Task 7: Final Verification & Git Commit/Push

- [ ] Run full test suite: `python3 -m unittest discover -s tests -p "test_*.py" -v`.
- [ ] Run strict Unicode audit: `python3 scripts/check_khmer_unicode.py --strict .`.
- [ ] Run i18n scanner: `python3 scripts/audit_khmer_i18n.py`.
- [ ] Run runnable examples: checkout and payroll.
- [ ] Stage, commit, and push to `origin improve-skill-token-usage`.
