# TamilinaiyaVaani Spellchecker Integration

The `TamilinaiyaVanniSpellcheckerPy` (TamilinaiyaVaani) engine has been integrated into the project to provide high-quality, morphologically aware Tamil spellchecking and suggestions.

## Background
The previous implementation relied on a Bloom filter for fast lookup and a BK-tree for edit-distance based suggestions. While fast, this approach lacked awareness of Tamil's complex grammatical rules (derivatives, sandhi, etc.).

## Integration Details

### 1. Engine as a Package
The TamilinaiyaVaani engine was converted into a structured Python package:
- Added `__init__.py` to the engine directory.
- Updated internal imports to be relative, allowing them to work correctly when imported by the main application.

### 2. Hybrid Strategy in `app.py`
The `/spellcheck` route now follows a multi-stage validation process:
1. **Bloom Filter (L1)**: Instant validation for common words.
2. **TamilinaiyaVaani Engine (L2)**: If not in Bloom filter, the word is passed to TamilinaiyaVaani for rule-based validation.
3. **LanguageTool (L3)**: Concurrent grammar checking.

## Custom Dictionary (Overrides)
To provide total control over the spellchecker and allow for scalable management of custom terms, a multi-line folder structure is used:
- **Location**: `TamilinaiyaVanniSpellcheckerPy/data/user_config/`
- **Files**:
    - `whitelist.txt`: List of words to always mark as **Correct** (one per line).
    - `blacklist.txt`: List of fragments or words to always mark as **Wrong** (one per line).
    - `replacements.txt`: List of mappings to enforce preferred vocabulary (format: `original|suggestion`).

### Priority Order
1. **Blacklist**: If a word is in `blacklist.txt`, it is immediately marked as wrong.
2. **Whitelist**: If a word is in `whitelist.txt`, it is immediately marked as correct.
3. **Replacements**: If a word matches a rule in `replacements.txt`, it is marked as wrong (even if it exists in the Bloom filter) and the replacement is offered.
4. **Bloom Filter**: Standard dictionary check for fast validation.
5. **TamilinaiyaVaani**: Rule-based morphological engine for complex derivations.
6. **BK-Tree**: Similarity-based absolute fallback for suggestions.

### 3. Suggestions
- **Rule-Based Primary**: Suggestions are first sought from the TamilinaiyaVaani engine, which understands word origins and suffixes.
- **BK-Tree Fallback**: If TamilinaiyaVaani cannot provide suggestions, the BK-tree is used as a fallback to provide results based on character similarity.

## Performance Impact
- The TamilinaiyaVaani `DB.json` is loaded into memory during startup (~4.5MB).
- Suggestions are now significantly more accurate for valid Tamil word forms.
