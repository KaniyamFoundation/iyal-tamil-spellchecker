# Vaani Data Dictionary (DB.json)

This document defines the schema and data types used in `DB.json`, the core morphological database for the Iyal Tamil Spellchecker.

## 📁 File Overview
*   **Location**: `TamilinaiyaVaaniSpellcheckerPy/data/DB.json`
*   **Format**: JSON (single-root object with a "DB" list containing one main dictionary).
*   **Purpose**: Stores mappings for morphological validation, colloquial-to-formal conversion, and suffix resolution.

---

## 🏗️ Data Schema

Each entry in the main dictionary follows this format:

```json
"சறே": [
  {
    "t": "0",
    "w": "சுகிறே"
  }
]
```

### Field Definitions

| Field | Key Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **Input Key** | N/A | String | The word fragment, root, or colloquial form to be analyzed. |
| **Type** | `t` | String (Int) | A category code that tells the engine how to process this specific mapping (see below). |
| **Target** | `w` | String | The correct, formal, or base form mapping for the input key. |

---

## 🏷️ Type Codes (`t`)

Based on architectural analysis, the type codes roughly correspond to the following logic:

| Type Code | Meaning | Example |
| :--- | :---: | :--- |
| **0** | **Base Mapping** | Standard phonetic or morphological replacement. |
| **1** | **Suffix Resolution** | Maps spoken suffix endings to formal written forms (e.g., `ல` -> `ல்`). |
| **3** | **Plural/Group** | Handles variants of plural markers (e.g., `ங்க` -> `கள்`). |
| **9** | **Special Correction** | Hardcoded corrections for specific irregular words or high-frequency errors. |

---

## 🛠️ Data Usage in Pipeline
1.  **Normalization**: When a word is processed, the engine looks for these keys to "formalize" the word segments.
2.  **Suffix Stripping**: The engine uses these maps to peel away suffixes and find the root word in the main dictionary.
3.  **Suggestion Generation**: When a misspelling is found, `DB.json` provides the "Target" (`w`) as a primary source for rule-based suggestions.

---
*Created: 2026-04-27*
