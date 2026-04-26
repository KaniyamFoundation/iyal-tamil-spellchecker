# Changelog

All notable changes to the Iyal Tamil Spellchecker project will be documented in this file.

## [Unreleased]

### Added
- Integrated Tamilinaiya Vanni (TamilinaiyaVaani) rule-based spellchecker engine for superior accuracy.
- Added support for morphologically aware Tamil suggestions and sandhi/punarchi rules.
- Implemented a hybrid spellchecking strategy combining Bloom filters and TamilinaiyaVaani.
- **Unified Custom Configuration System**:
    - Created a folder-based configuration (`user_config/`) for scalable vocabulary management.
    - Added support for multi-line **Whitelist** (always correct) and **Blacklist** (always wrong fragments).
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
