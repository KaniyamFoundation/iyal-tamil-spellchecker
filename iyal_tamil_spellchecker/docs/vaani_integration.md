# Vaani Spellchecker Integration

The `TamilinaiyaVaaniSpellcheckerPy` (Vaani) engine has been integrated into the project to provide high-quality, morphologically aware Tamil spellchecking and suggestions.

## Background
The previous implementation relied on a Bloom filter for fast lookup and a BK-tree for edit-distance based suggestions. While fast, this approach lacked awareness of Tamil's complex grammatical rules (derivatives, sandhi, etc.).

## Integration Details

### 1. Engine as a Package
The Vaani engine was converted into a structured Python package:
- Added `__init__.py` to the engine directory.
- Updated internal imports to be relative, allowing them to work correctly when imported by the main application.

### 2. Hybrid Strategy in `app.py`
The `/spellcheck` route now follows a multi-stage validation process:
1. **Bloom Filter (L1)**: Instant validation for common words.
2. **Vaani Engine (L2)**: If not in Bloom filter, the word is passed to Vaani for rule-based validation.
3. **LanguageTool (L3)**: Concurrent grammar checking.

## Custom Dictionary (Unification)
To provide total control over the spellchecker and allow for scalable management of custom terms, a multi-line folder structure is used:
- **Location**: `TamilinaiyaVaaniSpellcheckerPy/data/user_config/`
- **Files**:
    - `rightwordlist.txt`: The primary dictionary layer. Words added here act universally across both the fast web-router AND the deep morphologial engine.
    - `wrongwordlist.txt`: List of fragments or words to always mark as **Wrong** (one per line).
    - `replacements.txt`: List of mappings to enforce preferred vocabulary (format: `original|suggestion`).

*(Note: The legacy `User.txt` format is deprecated. `db_loader.py` now parses `rightwordlist.txt` natively to maintain an elegant single source of truth).*

### Priority Order (The Golden Bypass)
1. **Wrongwordlist**: If a word is in `wrongwordlist.txt`, it is immediately marked as wrong.
2. **Rightwordlist**: Web Router validates the word instantly. Simultaneously, the deep math engine treats it as a noun root, enabling it for dynamic word-splitting.
3. **Replacements**: Enforces stylistic or professional standards, superseding valid bloom checks.
4. **Bloom Filter**: Static read-only hash mapping trained on ~10M dictionary words.
5. **Vaani**: Rule-based morphological engine for complex derivations.
6. **BK-Tree**: Similarity-based absolute fallback for suggestions.

## Advanced Morphology Engine (Word Splitting)
The spellchecker includes highly sophisticated logic specifically built to resolve missing spaces and run-on string concatenations (a recurring issue in Tamil digital texts):
1. **Recursive N-Way Splits**: Automatically breaks massively joined structures (e.g. `அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்`) into native 3 or 4-layer bounds.
2. **Anti-Fragmentation Filter**: Calculates space metrics dynamically. If a 1-cut split exists, it actively deletes 2-cut variables (burying algorithmic bloat like `பிழை கள் தானாகவே` to prioritize `பிழைகள் தானாகவே`).
3. **Dangling Sandhi Protection**: Autonomously parses and accommodates terminal linker consonants (`க், ச், த், ப்`). For example, `தானாகவேகோடிட்டுக்` will still cleanly split, securely holding the syntax marker.
4. **Deep Udampadumey Sandhi De-concatenation**: Validates mathematically flawless Vowel + Bridge + Vowel structures (`செய்யவென்றே`). By structurally reversing the terminal suffix string (`வென்றே` -> `என்றே`), it successfully verifies noun/verb pairs, protecting natively combined grammar compounds without forcing unnecessary splits.
5. **Pure-Split Preemption Bypass**: Prioritizes valid unspaced text blocks over typo-level combinatorial guessing.
6. **Anti-Offensive Vulgarity Firewall**: Uses an isolated, computationally cheap `O(1)` validation set (`vulgar_splits.txt`) deeply embedded into the recursive splitter to instantly terminate mathematical tree branches that generate explicit or wildly inappropriate vocabulary fragments (`பேண்ட`), guaranteeing clean UX.

### Suggestions Fallback
- **Rule-Based Primary**: Suggestions are first sought from the Vaani engine, which understands word origins and suffixes.
- **BK-Tree Fallback**: If Vaani cannot provide suggestions, the BK-tree provides results based strictly on character similarity.

## Performance Impact
- The Vaani `DB.json` is loaded into memory during startup (~4.5MB).
- Strict Pure-Split prioritization keeps memory usage extremely low by short-circuiting expensive combination searches.
