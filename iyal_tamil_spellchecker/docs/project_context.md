# Project Context & Architectural Decisions

This document summarizes the core logic, reasoning, and discussions for the Iyal Tamil Spellchecker project to facilitate smooth future development.

## 🏗️ Core Architecture: The Hybrid Pipeline
The spellchecker uses a multi-layered validation strategy to balance speed (Bloom filter) with psychological/morphological accuracy (Vaani).

1.  **Level 0: Custom Overrides** (Located in `user_config/`)
    *   **Priority 1: Wrongwordlist** (Fails words explicitly marked as wrong, e.g., word fragments).
    *   **Priority 2: Rightwordlist** (Passes words explicitly marked as correct, e.g., names).
    *   **Priority 3: Replacements** (Enforces formal vocabulary, e.g., "Phone" -> "Kaipesi").
    *   *Decision*: We moved Replacements *before* the Bloom filter to allow users to override common loan words that might technically be in the dictionary but are not preferred.

2.  **Level 1: Bloom Filter** (`tamil_bloom.pkl`)
    *   Used for lightning-fast membership checks of ~1M valid Tamil words.

3.  **Level 2: Vaani Engine** (Rule-based)
    *   Morphologically aware engine that handles suffixes/prefixes and grammatical derivations.

4.  **Level 3: BK-Tree** (`bk_tree.pkl`)
    *   Fuzzy-match fallback for finding suggestions based on edit distance.

## ✍️ Grammar & Spacing Rules
*   **Missing Space After Period**: We implemented a rule to catch merged sentences (e.g., `பதிவாகியுள்ளன.இதுகுறித்து`).
*   **Abbreviation Threshold**: To avoid flagging initials (e.g., `எஸ்.ஐ.ஆர்`) or honorifics (e.g., `திரு.`), we use a **5-code-point threshold**. 
    *   *Decision*: Only words longer than 4 characters followed by a dot are flagged, which effectively whitelists almost all Tamil initials and abbreviations automatically.

## 📜 Custom Configuration Strategy
We moved from a single string-based `User.txt` to a **Folder-based structure** (`user_config/`).
*   **Why?**: To support multi-line files and comments, making it easier to manage hundreds of custom words across `rightwordlist.txt`, `wrongwordlist.txt`, and `replacements.txt`.
*   **Sandhi Challenge**: We discussed the complexity of "Smart Inflection Transfer" (e.g., merging "Photo + ai" to get "Nizharpada-ththa-i").
*   **Conclusion**: While we implemented basic stem-matching, we recommended **manual entries** for common inflected forms in `replacements.txt` to ensure 100% grammatical accuracy.

## 🎨 UI Architecture Discussion
*   **Current State**: Vanilla JavaScript + HTML Templates.
*   **Decision**: Keep as Vanilla JS for now to maintain an extremely low footprint and simplicity.
*   **Future Path**: If the UI requires complex state handling (like a real-time collaborative side-panel or deeper integration with grammar tools), React is the designated framework for migration. 

## ⚖️ Credits & Attribution
Recent updates to `editor.html` and documentation formalize the contributions of:
*   Tamil Virtual University (TVU)
*   Sama Technologies
*   Thamizha Team
*   Neechalkaran (Vaani original lead)

---
*Last Updated: 2026-04-26 (v0.0.3)*
