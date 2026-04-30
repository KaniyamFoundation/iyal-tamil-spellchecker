# Iyal Tamil Spellchecker - Changelog

### 0.0.5 (2026-04-29)
*   **Morphological Precision**:
    *   Added strict validation for short roots (<= 2 chars) to prevent "syllable fragments" from passing spellcheck.
    *   Expanded `wrongwordlist.txt` with 100+ common suffix fragments (ழைகள், களின், ச்சு, etc.) to catch accidental word splits.
    *   Improved plural suffix stripping for `க்கள்`, `ங்கள்`, `ற்கள்`, and `ட்கள்`.
*   **UI/UX Improvements**:
    *   Implemented a dynamic **Info Box** with GitHub version check and update notifications.
    *   Optimized editor layout for a wider, more symmetric desktop workspace (320px side panels).
    *   Fixed Undo/Redo behavior to ignore background highlights and only track manual edits.
*   **Bug Fixes**:
    *   Fixed a critical issue where `Ctrl+Z` would delete large blocks of text if timed specifically with the spellchecker.
    *   Resolved false positives for common word fragments mistakenly present in the cache.
*   **Testing**:
    *   Added `test_version_check.py` for update logic.
    *   Expanded `test_regression_cases.py` with 15+ new cases for plural forms and fragments.
