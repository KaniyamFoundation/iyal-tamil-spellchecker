# Changelog

All notable changes to the Iyal Tamil Spellchecker project will be documented in this file.

## [0.0.3] - 2026-04-28

### Added
- **Deep Udampadumey Sandhi Engine (உடம்படுமெய்ப் புணர்ச்சி)**: Implemented mathematical reverse-concatenation inside the morphology core, allowing perfectly conjoined dynamic compounds (e.g., `செய்யவென்றே`) to validate as correct automatically without aggressively splitting into independent nouns.
- **Kutriyalugaram Reverse-Validation (குற்றியலுகரம்)**: Added native support for vowel-dropping compounds (e.g., `படித்துணர்ந்தான்`). The engine now autonomously restores the missing 'u' and starting vowels at grammar junctions, enabling thousands of complex verb-compounds to pass without manual dictionary updates.
- **LRU Algorithmic Caching**: Integrated `functools.lru_cache` on core morphological methods (`checkword`, `checkviku`). This dramatically accelerates large-document processing by memoizing complex Tamil grammatical derivative calculations.
- **O(1) Suggestion Cache Optimization**: Replaced the legacy list-based $O(N)$ cache with a high-performance hash dictionary. This fixes a scalability bottleneck in large documents, providing near-instantaneous validation for repeated words.
- **Ultra-Lite 26MB Context Engine**: Optimized the massive 2.2GB corpus ingestion into a highly-compressed 26MB SQLite index. Achieved an 85% size reduction through **Top-N per-word pruning** (Top 100k words, Top-3 continuations) and `VACUUM` compaction.
- **Subject-Verb Grammar Shadowing**: Implemented a "Grammar Shadow Matcher" that detects correctly spelled words that are contextually invalid (e.g., mismatching gender/number).

- **Heuristic Pronoun Agreement Fallback**: Added a rule-based layer (`PRONOUN_AGREEMENT`) to ensure robust subject-verb harmony for common pronouns (அவன், அவள், அவர்கள், etc.) even for rare verbs.
- **Pythonic Resource Architecture (Dataclasses)**: Refactored `app.py` to use Python `dataclasses` for centralized resource management. All engine components (Bloom, BK-Tree, Vaani, and Overrides) are now encapsulated in a single type-safe object.

- **O(1) User-Word Search Index**: Converted the `rightwordlist.txt` lookup engine from a List to a **Set**. This replaces $O(N)$ linear scans with instant constant-time lookups, significantly improving speed for users with massive custom dictionaries.
- **Pathlib Integration**: Migrated the entire backend from `os.path` strings to **`pathlib.Path`** objects, ensuring more robust and platform-independent directory handling for logs and configuration.
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
