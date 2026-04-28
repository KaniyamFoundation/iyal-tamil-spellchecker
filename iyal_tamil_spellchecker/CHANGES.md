# Changelog

All notable changes to the Iyal Tamil Spellchecker project will be documented in this file.

## [0.0.3] - 2026-04-28

### Added
- **Deep Udampadumey Sandhi Engine (உடம்படுமெய்ப் புணர்ச்சி)**: Implemented mathematical reverse-concatenation inside the morphology core, allowing perfectly conjoined dynamic compounds (e.g., `செய்யவென்றே`) to validate as correct automatically without aggressively splitting into independent nouns.
- **Dynamic Vulgarity Firewall**: Abstracted the N-Way recursive word split blacklist into `user_config/vulgar_splits.txt`, loaded dynamically via `db_loader`. This fundamentally blocks computationally "legal" but socially inappropriate vocabulary from ever rendering in suggestions.
- **Multi-Slot Suggestion Dropdowns**: Extended `replacements.txt` parser to natively parse comma-separated text into dropdown menus in real-time (e.g., `இருப்பேண்டா|இருப்பேன்,இருப்பேன்டா,இருக்கிறேன்`).
- Integrated Tamilinaiya Vanni (Vaani) rule-based spellchecker engine for superior accuracy.
- Added support for morphologically aware Tamil suggestions and sandhi/punarchi rules.
- Implemented a hybrid spellchecking strategy combining Bloom filters and Vaani.
- **Unified Custom Configuration System**:
    - Created a folder-based configuration (`user_config/`) for scalable vocabulary management.
    - Added support for multi-line **Rightwordlist** (always correct) and **Wrongwordlist** (always wrong fragments).
    - Implemented **Preferred Replacements** mapping (e.g., "போட்டோ" -> "நிழற்படம்").
    - **Priority Precedence**: Custom replacements now take priority over the Bloom filter, allowing users to override common loan words.
- **Vocabulary Expansion**: Added hundreds of common English loan words and their inflected forms to the default replacement list (Bus, Bank, Phone, etc.).
- **Automated Testing Suite**: Created a `tests/` directory with integration and component tests to ensure long-term stability.
- Initial local development documentation in README.

### Changed
- Improved UI and performance for long content processing (non-blocking batch-streaming).
- Refined menu coordinates for better user experience.
- Updated localhost port in README for consistency.

### Fixed
- **Native OS DOM Override Fix**: Inserted `spellcheck="false"` strictly bounding the DOM manipulation scope to prevent macOS/Windows native Tamil dictionaries from overlapping our `<span class="misspelled">` CSS classes during ZWNJ decomposed inputs (`க`+`ெ`+`ா`).
- Resolved a bug where words found in the BK-tree (like "ஒட்டுக") were incorrectly flagged as errors.
- Fixed a logic flaw where Rule-based results could overwrite verified Bloom filter results.
- Corrected relative import issues allowing the engine to be run both standalone and as a package.
- Project configuration issues with improved `.gitignore`.

## [0.0.2] - 2026-04-10

### Added
- Integrated LanguageTool for Tamil grammar checking.
- Enhanced batch processing UI with T/ETA telemetry.
- Mobile responsiveness improvements.

## [0.0.1] - 2025-10-29

### Added
- Initial project structure and Tamil spellchecking core.
- Flask application for web interface.
- Basic BK-tree based spell correction.
