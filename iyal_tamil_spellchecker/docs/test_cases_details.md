# Iyal Tamil Spellchecker - Test Suite Documentation

This document provides a detailed overview of the automated test cases in the `iyal_tamil_spellchecker/tests` directory. The test suite is built on **pytest** and validates the multi-layered architecture of the Iyal Spellchecker, ensuring linguistic accuracy, architectural stability, and robust API performance.

## 🏃 Running the Tests
To run the complete test suite:
```bash
pytest -v
```

---

## 🏛️ Architecture Layer Tests

These tests isolate and validate specific components of the spelling validation pipeline (Levels 0 through 3).

### 1. Custom Overrides (Level 0)
**File:** `test_level0_config.py`
This module verifies that the user-defined dictionary configurations securely override internal engine rules.
*   **`test_whitelist_forces_correct`**: Ensures words placed in `rightwordlist.txt` automatically pass the spellchecker, regardless of whether they exist in the Bloom filter or Vaani engine.
*   **`test_blacklist_forces_wrong`**: Verifies that words in `wrongwordlist.txt` are flagged as incorrect, effectively blocking known typos that might theoretically bypass morphological logic.
*   **`test_replacements_exact_match`**: Tests that `replacements.txt` functions properly by strictly mapping incorrect patterns (e.g., "பஸ்") to exact target suggestions (e.g., "பேருந்து").

### 2. Noun Morphology Inflections (Whitelists Expansion)
**Files:** `test_morphology.py`, `test_morphology_200.py`
Validates rule-based reverse stripping for primary case endings, secondary postpositions, and Grantha characters.
*   **`test_derived_whitelist_words`**: Rigorously tests plural, instrumental, genitive, locative, comitative, and adverbial modifiers (e.g., `அருட்கொடைகளால்`, `அருட்கொடைகளின்`, `சுரேஷின்`, `குர்ஆனாகவே`) mapping back appropriately.

*   **`test_complex_derived_words_validation`**: Tests robust composite suffix strings executing safely over bulk arrays.



### 2. Bloom Filter Caching (Level 1)
**File:** `test_level1_bloom.py`
Validates the fast-pass initial cache layer.
*   **`test_bloom_filter_fast_hit`**: Ensures that exact matches in `tamil_bloom.pkl` are validated instantly. Note that because of the current app architecture, the background validation may still ping the rule engine, but the final `correct` flag is confidently asserted by this filter.
*   **`test_bloom_filter_miss_falls_to_vaani`**: Confirms that when a word is not found in the cache, the spellchecker successfully delegates the request to the Vaani Morphological engine.

### 3. Vaani Morphological Engine (Level 2)
**File:** `test_level2_vaani.py`
Direct unit tests on the core Vaani linguistic classes.
*   **`test_vaani_direct_codeuyir`**: Tests internal Tamil Unicode manipulation and vowel mapping (e.g., verifying that "கா" correctly strips down/builds back to expected base derivations like "அகா").
*   **`test_vaani_direct_compound`**: Tests `is_valid_compound` to ensure compound words that undergo phonological sandhi or vowel-dropping (*Kutriyalugaram* and *Udampadumey*) are successfully reconstructed (e.g., "படித்துணர்ந்தான்", "செய்யவென்றே").
*   **`test_vaani_direct_validate_words`**: Tests the `validate_words` payload generation logic directly without the Flask wrapper.

### 4. BK-Tree Suggestions (Level 3)
**File:** `test_level3_bktree.py`
Validates the fuzzy search fallback layer that provides typo suggestions.
*   **`test_bktree_fallback_suggestions`**: Verifies that when a word is wrong and the Vaani engine cannot build a grammatical alternative, the BK-Tree is queried for nearest-neighbor approximations based on Levenshtein distance.
*   **`test_bktree_filters_bad_candidates`**: Ensures the suggestions are high quality by verifying that candidates with differing initial starting letters from the misspelled word are dropped, a common heuristic for Tamil spelling intent.

---

## 🌐 API, Integration & Performance Tests

These tests use the Flask test client to simulate real-world browser and API interactions.

### 1. Main API Endpoints
**File:** `test_api_v1.py`
*   **`test_health` / `test_apidocs_swagger`**: Validates basic application routing and Swagger integration.
*   **`test_instrumentation_headers`**: Verifies that every response includes an `X-Process-Time` timing header.
*   **`test_api_versioning_consistency`**: Verifies that `/v1/spellcheck` and the root `/spellcheck` both function identically.
*   **`test_batch_mode`**: Ensures that passing a list of words correctly returns batched results.
*   **`test_grammar_pronoun_agreement`**: End-to-end verification of the rule-based pronoun/verb agreement (e.g., "அவன்" failing if combined with "வந்தாள்").
*   **`test_grammar_dot_spacing`**: Ensures sentences missing a space after a period (e.g., "முடிகிறது.அடுத்த") generate a spacing suggestion.
*   **`test_caching_performance`**: A benchmark test validating that identical text payloads sent twice process significantly faster the second time.

### 2. Rate Limits & Payload Restrictions
**File:** `test_api_limits.py`
*   **`test_rate_limiting_429`**: Hits the API rapidly with a mock external IP to confirm `429 Too Many Requests` is raised successfully.
*   **`test_whitelist_bypasses_ratelimit`**: Confirms that requests originating from internal/whitelisted IPs (`127.0.0.1`) do not increment the rate limiter.
*   **`test_payload_too_large_413`**: Verifies the `MAX_CHARACTER_LIMIT` (50,000 characters) logic successfully rejects oversized documents.

### 3. LanguageTool Integration
**File:** `test_languagetool_mock.py`
*   **`test_languagetool_integration_mocked`**: Uses Python's `unittest.mock` to simulate a JSON response from the local LanguageTool server, validating that the API seamlessly parses and attaches grammar errors without requiring the actual server to be online.
*   **`test_languagetool_timeout_mocked`**: Simulates a network timeout (`urllib.error`) to ensure the application degrades gracefully and continues spellchecking without crashing.

### 4. Contextual Bigram Testing
**File:** `test_grammar_context.py`
*   **`test_grammar_agreement`**: A parameterized suite checking specific bigram frequencies against the SQLite database (e.g., "அவள் வந்தான்" vs "அவள் வந்தாள்"). It verifies that the "better" phonetic match has a substantially higher historical frequency before suggesting a change.

---

## 🧪 Legacy & Script Tests
In addition to Pytest files, the `tests/` directory includes historic scripts that validate edge cases or debug the C# to Python migration.

*   **`test_app.py` / `test_app2.py` / `proper_test.py`**: Manual script runs to spot-check the core loop on complex terms like "கொடுத்துதவினான்".
*   **`test_recursion.py`**: A manual script for debugging recursive deep-splitting for exceptionally long compound words.
*   **`test_split.py` / `test_split_error.py`**: Specific sandbox scripts handling words like "தமிழ்நாடுஅரசு" which are valid when spaced appropriately.
*   **`need_fix.org`**: An active tracking file generated by the team documenting edge cases that currently produce invalid suggestions (e.g., `எஸ்.ஐ.ஆர்`, `விட்டுக்கொடுகாத்`), serving as a backlog for future logic refinement.
