# Khmer Unicode, Typography, and Font Engineering

This reference provides technical specifications for handling Khmer Unicode integrity, OpenType shaping, font rendering, and text transformation in web and mobile applications.

---

## 1. Khmer Unicode Architecture

The Khmer script is an **abugida** (alphasyllabary) encoded in the Unicode Standard across two dedicated blocks:
- **Khmer Block:** `U+1780` – `U+17FF`
- **Khmer Symbols Block:** `U+19E0` – `U+19FF`

### 1.1 Character Classes

```text
U+1780 .. U+17A2 : Consonants (35 standard, e.g. ក, ខ, គ, ...)
U+17A3 .. U+17A4 : Deprecated consonants (use U+17A2 with vowel signs)
U+17A5 .. U+17B3 : Independent Vowels (ស្រៈពេញតួ, e.g. ឥ, ឦ, ឧ, ឳ)
U+17B6 .. U+17C5 : Dependent Vowel Signs (ស្រៈនិស្ស័យ, illustrated with base consonant ក: កា, កិ, កី, កឹ, កឺ, កុ, កូ, កួ, កើ, កឿ, កៀ, កេ, កែ, កៃ, កោ, កៅ)
U+17C6 .. U+17D1 : Diacritics and Signs (illustrated with base ក/ប: កំ, កះ, កៈ, ប៉, ប៊, ក់, ករ៍, ក៍, ក៎, ក៏, ក័, ក៑)
U+17D2          : Khmer Sign Coeng (ជើង - Subscript consonant prefix, e.g. ក្ក, ក្ខ)
U+17D3          : Bathamasat (illustrated with base: ក៓ - Lunar calendar / divination sign)
U+17D4 .. U+17D6 : Punctuation (Khan ៕, Bariyoosan ៚, Colon ៖)
U+17D7          : Lek Too (ៗ - Repetition mark)
U+17D8 .. U+17DA : Punctuation (Beyyal ៘, Phnaek Muan ៙, Koomuut ៚)
U+17DB          : Khmer Currency Symbol Riel (៛)
U+17E0 .. U+17E9 : Khmer Digits (០, ១, ២, ៣, ៤, ៥, ៦, ៧, ៨, ៩)
```

### 1.2 Syllable Structure & The Coeng Sequence
Khmer syllables are formed around a base consonant. Subscript consonants (ជើងអក្សរ) do not have independent Unicode code points. Instead, they are encoded dynamically using a two-character sequence:
$$\text{Subscript Consonant} = \text{U+17D2 (Coeng)} + \text{Base Consonant}$$

**Example Syllable Composition (`កម្ពុជា` — Cambodia):**
1. Consonant Ka: `U+1780` (`ក`)
2. Consonant Mo: `U+1798` (`ម`)
3. Subscript sequence: Coeng `U+17D2` + Consonant Po `U+1796` (`ព`) $\rightarrow$ forms subscript **កម្ព**
4. Dependent Vowel U: `U+17BB` $\rightarrow$ forms **កម្ពុ**
5. Consonant Jo: `U+1787` (`ជ`)
6. Dependent Vowel Aa: `U+17B6` $\rightarrow$ forms **កម្ពុជា**

> [!CRITICAL]
> Never separate `U+17D2` from the consonant that follows it. Splitting this sequence destroys OpenType ligatures and produces broken rendering.

---

## 2. Invisible Typography Characters

### 2.1 Zero-Width Space (ZWSP — `U+200B`)
- **Purpose:** Khmer is written without visible spaces between words within a phrase. Digital layout engines rely on word boundary indicators to wrap lines properly.
- **Role in UI:** While modern operating systems (iOS, Android, macOS, Windows) incorporate dictionary-based word breaking in HarfBuzz / ICU, inserting `\u200B` at word boundaries is still the gold standard in web layout to prevent lines from breaking mid-syllable.
- **Safe Handling:** **NEVER strip `\u200B` with generic whitespace-clearing scripts or regexes.** Stripping ZWSP causes words to overflow containers or break across consonants.

### 2.2 Zero-Width Non-Joiner (ZWNJ — `U+200C`) and Zero-Width Joiner (ZWJ — `U+200D`)
- `U+200C` (ZWNJ): Used selectively to inhibit ligature formation or separate a prefix from an independent vowel.
- `U+200D` (ZWJ): Used in specific OpenType font implementations or historic text.

---

## 3. Common Encoding Failures & Visual Defects

### 3.1 Dotted Circle (U+25CC)
When a text rendering engine (such as HarfBuzz, DirectWrite, or CoreText) encounters a combining mark, dependent vowel, or Coeng sign without a valid base consonant, it renders a **dotted circle (`U+25CC`)** to indicate an orphaned or illegal character sequence.

**Common Causes:**
- Storing or copy-pasting a combining mark without its base consonant.
- Inverting typing order (e.g., typing vowel before subscript consonant).
- Naive string truncation that sliced a string between a base consonant and its combining marks.

### 3.2 Mojibake
Occurs when UTF-8 encoded Khmer text is read or decoded as Windows-1252 or ISO-8859-1.
- **Corrupted Display:** `áž€áŸ’ážœáž»áž‡áž¶`
- **Correct Display:** `កម្ពុជា`
- **Root Cause:** Missing `charset="utf-8"` in HTTP headers or `<meta charset="utf-8">` in HTML, or reading database strings with a legacy collation.

### 3.3 Replacement Character (U+FFFD)
Indicates that invalid byte sequences were encountered during a lossy character set conversion. Once text contains `U+FFFD`, the original characters cannot be algorithmically recovered; the source data must be restored from UTF-8 backups.

---

## 4. Safe vs. Unsafe String Transformations

### 4.1 String Length and Slicing

#### UNSAFE: Naive Substring / Slice
```javascript
// BROKEN: Slices through combining marks and coeng sequences
const text = "កម្ពុជា"; // 7 code units
const preview = text.substring(0, 3); 
// Slicing at index 3 cuts right after Coeng (U+17D2) without the subscript consonant!
// Renders broken dotted circle in browsers.
```

#### SAFE: Grapheme Cluster Slicing
In modern JavaScript/TypeScript, use `Intl.Segmenter` with `{ granularity: 'grapheme' }` to slice strings at visual syllable cluster boundaries:

```typescript
export function safeTruncateKhmer(text: string, maxGraphemes: number): string {
  if (!text) return "";
  
  // Intl.Segmenter correctly groups base consonants with coengs and vowels
  const segmenter = new Intl.Segmenter("km", { granularity: "grapheme" });
  const segments = Array.from(segmenter.segment(text));
  
  if (segments.length <= maxGraphemes) {
    return text;
  }
  
  return segments.slice(0, maxGraphemes).map(s => s.segment).join("") + "…";
}
```

In Python:
```python
import unicodedata

def safe_truncate_khmer(text: str, max_chars: int) -> str:
    """Truncate text without splitting combining mark sequences."""
    if len(text) <= max_chars:
        return text
    
    # Do not cut immediately before a combining mark
    cut_idx = max_chars
    while cut_idx > 0 and unicodedata.combining(text[cut_idx:cut_idx+1]):
        cut_idx -= 1
        
    return text[:cut_idx] + "…"
```

### 4.2 Case Conversion
Khmer has no concept of uppercase or lowercase letters.
- Calling `.toUpperCase()` or `.toLowerCase()` on Khmer characters has no effect on Khmer script.
- However, applying CSS `text-transform: uppercase` to a container with mixed Khmer and English can distort font line metrics or cause English acronyms to change size unexpectedly. Prefer styling specific Latin classes rather than applying global transforms.

### 4.3 Regex Word Boundaries (`\b`)
Standard regex `\b` relies on ASCII word characters (`\w`). It treats Khmer script as non-word symbols or fails completely when words are not delimited by spaces.
- **Do not use `/\b[A-Za-z0-9]+\b/`** expecting it to delimit Khmer words.
- For search tokenization, rely on an ICU-based dictionary tokenizer or explicitly segment at `\u200B` and whitespace.

---

## 5. CSS Typography & Font Engineering

Khmer glyphs have vertical ascenders (top diacritics like Nikahit `U+17C6`, e.g. `កំ`, or Samyok Sannya `U+17D0`, e.g. `ក័`) and deep descenders (subscript consonants with Coeng `U+17D2`, e.g. `ក្ក` or `ក្ភ`, and bottom vowels, e.g. `កុ`, `កូ`). If CSS line height or overflow properties are too tight, browsers will clip these marks.

### 5.1 Recommended CSS Font Stack
Modern digital applications should define a resilient fallback stack:

```css
:root {
  --font-khmer: "Kantumruy Pro", "Noto Sans Khmer", "Khmer Sangam MN", "Leelawadee UI", sans-serif;
}

body, html {
  font-family: var(--font-khmer);
  /* Minimum recommended line-height for Khmer UI is 1.6 to 1.8 */
  line-height: 1.7;
  /* Prevent horizontal word overflow on narrow mobile screens */
  overflow-wrap: break-word;
  word-break: normal;
}
```

### 5.2 Font Hierarchy by Operating System
| OS / Platform | Primary System Font | Fallback Font |
| :--- | :--- | :--- |
| **iOS / macOS** | `Khmer Sangam MN` | `Khmer MN` |
| **Android / ChromeOS** | `Noto Sans Khmer` | `Roboto` |
| **Windows** | `Leelawadee UI` | `Khmer UI`, `DaunPenh` |
| **Cross-Platform Web** | `Kantumruy Pro` (Google Fonts) | `Battambang`, `Noto Sans Khmer` |

### 5.3 Mobile Clipping Prevention Checklist
1. **Line Height:** Never use `line-height: 1.0` or `line-height: 1.2` for Khmer text. Use `line-height: 1.6` to `1.8` minimum.
2. **Button Padding:** Provide at least `8px` to `12px` vertical padding (`py-2` or `py-3` in Tailwind CSS) so top diacritics and bottom coengs are not clipped by button borders.
3. **Container Overflow:** Avoid fixed `height` with `overflow: hidden` on text containers; use `min-height` with flex or grid layout.
