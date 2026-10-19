# Contributing to `khmer-localization`

Thank you for your interest in contributing to the **`khmer-localization`** Agent Skill! This project aims to empower AI coding assistants and developers worldwide to build high-quality software for Khmer-speaking users and the Cambodian tech ecosystem.

---

## Code of Conduct & Core Values

1. **Practical & Verified Guidance:** We prioritize battle-tested, production-ready recommendations over generic theory.
2. **Respect for Linguistic Nuance:** We avoid wooden, literal machine translations and favor natural, context-appropriate digital Khmer phrasing.
3. **No Unverified Claims:** When contributing regulatory, numbering, or banking standards, always cite official sources (e.g., TRC, MPTC, NBC, ITU-T) with access dates.

---

## Development & Testing Workflow

### Requirements
- **Python 3.10+** (standard library only; no virtualenv or pip dependencies required).
- Standard text editor with UTF-8 encoding support.

### Running Tests
Before submitting any pull request or proposing changes, run the automated test suite locally:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

All tests must pass with zero failures and zero errors.

### Testing the Unicode Checker
You can also run the checker against sample files or the repository itself:

```bash
python3 scripts/check_khmer_unicode.py --strict .
```

---

## Contribution Areas

### 1. Linguistic & Translation Guidelines (`references/khmer-writing-guide.md`)
- If you notice awkward or unnatural Khmer phrasing, submit an issue or PR suggesting improved terminology.
- Provide the English term, the proposed natural Khmer term, context of use, and an explanation of why the proposed translation is preferable.
- When proposing domain-specific vocabulary (e.g., fintech, medical, legal), explain the local Cambodian industry consensus.

### 2. Regional Formatting Updates (`references/cambodia-formatting.md`)
- If the Telecommunication Regulator of Cambodia (TRC) or Ministry of Post and Telecommunications (MPTC) issues new numbering regulations, prefix allocations, or numbering plan changes, please submit an update.
- Always include links to the official regulatory notice, press release, or Gazette publication.

### 3. Unicode & Font Rendering (`references/unicode-and-typography.md`)
- Contributions documenting font metrics, rendering bugs across specific mobile OS versions, or OpenType shaping edge cases are highly welcome.

### 4. Integrity Checker Script (`scripts/check_khmer_unicode.py`)
- The script must strictly use **Python's standard library only**. Do not introduce external dependencies.
- Ensure all new checks include corresponding unit tests in `tests/test_check_khmer_unicode.py`.
- Never classify valid Khmer typography characters (such as Zero-Width Space `\u200B`) as errors.

---

## Submitting Pull Requests

1. **Fork the repository** and create a feature branch (`git checkout -b feature/my-feature`).
2. **Make your changes**, ensuring clean UTF-8 encoding.
3. **Run tests** and verify everything passes cleanly.
4. **Write clear commit messages** explaining the rationale for your changes.
5. **Open a Pull Request** describing what was changed and any references/citations used.
