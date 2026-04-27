# Iyal Tamil Spellchecker Architecture

This document describes the technical architecture and request flow of the Iyal Tamil Spellchecker (v0.0.3+).

## 🛠️ System Overview

The system is designed as a **Priority-Based Hybrid Validation Pipeline** that balances speed (Bloom Filters) with accuracy (Rule-based Morphology) and user control (Custom Overrides).

### 🎨 Visual Architecture
![Iyal Engine Architecture](/home/shrini/.gemini/antigravity/brain/c91cdb11-3d2b-483b-9014-068ebfc41dc6/iyal_architecture_premium_1777310397701.png)

### 🗺️ Request Flow Diagram (ASCII)
```text
[ USER UI (Vanilla JS) ] 
       |
       | (Batch Streaming POST)
       v
[ FLASK BACKEND (app.py) ]
       |
       +--- 1. CUSTOM OVERRIDES (rightwordlist.txt, wrongwordlist.txt, replacements.txt)
       |
       +--- 2. L1 CACHE (Bloom Filter: Instant Dictionary Check)
       |
       +--- 3. L2 ENGINE (Vaani: Morphological Rule-Check)
       |
       +--- 4. L3 FALLBACK (BK-Tree: Fuzzy Similarity Search)
       |
       v
[ JSON RESPONSE ] --> (UI Highlight / Suggestion Menu)
```

### 🛰️ Flow Diagram (Mermaid)
```mermaid
graph TD
    A[User Input] --> B[JS Editor: Batching & Streaming]
    B --> C[Flask API: /spellcheck]
    
    subgraph "Backend Pipeline (Priority Ordered)"
    C --> E{Layer 1: Custom Config}
    
    E -- "Wrongwordlist?" --> E1[Mark Wrong]
    E -- "Rightwordlist?" --> E2[Mark Correct]
    E -- "Replacement?" --> E3[Add Suggestion]
    
    E3 --> F
    E2 --> Final[Build JSON Result]
    E1 --> F
    
    F{Layer 2: Bloom Filter}
    F -- "Found?" --> Final
    F -- "Not Found?" --> G{Layer 3: Vaani}
    
    G -- "Grammatically Correct?" --> Final
    G -- "Morphological Error?" --> G1[Generate Root-based Suggestions]
    
    G1 --> H{Layer 4: BK-Tree}
    G -- "Unknown Word?" --> H
    H --> H1[Fuzzy Match Suggestions]
    H1 --> Final
    end
    
    Final --> I[JS Editor: Real-time UI Update]
    I --> J[Highlighting & Context Menus]
```


use https://www.eraser.io to generate a beautiful diagram 
---

## 🏗️ Detailed Layer Breakdown

### 1. The Frontend (Vanilla JS)
*   **Editor**: A `contenteditable` area with custom rendering for underlines.
*   **Streaming**: Large texts are split into batches and sent as asynchronous POST requests to prevent UI freezing.
*   **Interaction**: Handles context menus for picking suggestions and real-time telemetry (Words/sec, ETA).

### 2. The Custom Layer (Priority 1)
*   **Rightwordlists**: Project-specific names or technical terms.
*   **Wrongwordlists**: Prevents common fragments or noisy results from the rule-based engine.
*   **Replacements**: Enforces formal Tamil vocabulary (e.g., `Bus` -> `பேருந்து`).
*   *Note*: Checked **before** the dictionary to allow users to override standard dictionary terms.

## 🚀 Scalability: Handling Large Content

To process huge documents (e.g., 50+ pages) without crashing the server or freezing the browser, Iyal uses a **Batch-and-Stream** strategy:

1.  **Client-Side Partitioning**: When a user clicks 'Check', the JavaScript editor splits the text into small batches (default: ~200 words).
2.  **Parallel Asynchronous POSTs**: Instead of one giant request, Iyal sends multiple small requests in sequence. This prevents **HTTP Timeouts** and ensures the server never has to hold a massive document in memory at once.
3.  **Stateless Backend Processing**: Each request to `/spellcheck` is independent. The backend processes the batch, generates suggestions, and returns JSON. 
4.  **Non-Blocking UI**: The UI remains interactive. Results are streamed back into the editor as they arrive, highlighting errors in real-time while the rest of the document is still being checked.
5.  **Telemetry Dashboard**: A real-time counter displays processing speed (Words/sec) and a dynamic ETA, giving the user constant feedback on long-running tasks.

### 3. The Dictionary Layer (Bloom Filter)
*   **Technology**: Probabilistic data structure (`tamil_bloom.pkl`).
*   **Performance**: Near-instant check (O(1)) for ~1 million valid Tamil words.

### 4. The Morphological Layer (Vaani)
*   **Logic**: Uses a rule-based engine to break down words into root + suffix (Sandhi analysis).
*   **Features**: Validates complex derivations that aren't in standard lists and generates suggestions that respect Tamil joining rules.

### 5. The Fuzzy Layer (BK-Tree)
*   **Technology**: Metric tree based on Levenshtein distance.
*   **Purpose**: If all other engines fail, it finds the "nearest" words in the corpus to offer last-resort suggestions.

---

## 📡 External Integrations
*   **LanguageTool**: A sidecar Java service used for concurrent grammar checking (e.g., subject-verb agreement).

## 🗄️ Data Storage
*   `user_config/`: Plain-text files for user overrides (`rightwordlist.txt`, `wrongwordlist.txt`, `replacements.txt`).
*   `data/DB.json`: The rule-set for the Vaani engine.
*   `tamil_bloom.pkl` / `bk_tree.pkl`: Pre-indexed dictionary and fuzzy-search trees.

## 🛡️ Security Considerations & Hardening

Currently, the application is optimized for local/internal use. For public deployment, the following security architecture is recommended:

### 1. Existing Protections
*   **XSS Prevention**: The Jinja2 template engine automatically escapes user input. Suggestions and corrections rendered in the UI should always use `.innerText` rather than `.innerHTML` in JavaScript.
*   **Input Filtering**: The spellcheck logic primarily extracts Tamil unicode characters (`\p{Tamil}`), which inherently filters out most common script injection payloads.

### 2. Future Security Roadmap
*   **Rate Limiting**: Implementation of `Flask-Limiter` to prevent automated DOS (Denial of Service) attacks on the rule-based engine.
*   **Payload Validation**:
    *   Enforce a maximum request size (e.g., 2MB) in Flask (`MAX_CONTENT_LENGTH`).
    *   Validate input JSON schema to ensure only legitimate text is processed.
*   **Deployment Hardening**:
    *   **Debug Mode**: `debug=True` must be disabled in production to prevent stack trace leakage.
    *   **WSGI Server**: Use `Gunicorn` or `Waitress` instead of the built-in Flask development server.
    *   **Reverse Proxy**: Deploy behind `Nginx` to handle SSL/TLS termination and provide additional request filtering.
*   **CORS Policy**: Configure a strict `Cross-Origin Resource Sharing` policy to allow only authorized domains to consume the spellchecker API.
*   **HTML Awareness**: Implement sanitization layers to ensure that spellchecking logic does not inadvertently parse or execute embedded HTML tags within user-provided content.

## 🚀 Future Roadmap: Phase 2

### 1. HTML Layout & Table Retention
*   **Problem**: Highlighting currently disrupts the raw DOM structure, which can break tables and complex CSS designs.
*   **Plan**: Implement a **Recursive DOM Walker** in the frontend. This will allow the engine to find and wrap words within text nodes specifically, leaving `<table>`, `<div>`, and `<span>` layout tags untouched.
*   **Option**: Migrate to **TipTap / ProseMirror** for a professional rich-text experience that supports native "decorations" without direct HTML manipulation.

### 2. Refining Tamil Grammar Rules
*   **Rule Expansion**: While the *connection* to LanguageTool is complete, we plan to develop and contribute **Advanced Syntactic Rules** (e.g., subject-verb agreement, gender-suffix harmony) to catch errors that basic spellcheckers miss.

### 3. API & Ecosystem
*   **Developer SDK**: Provide automated API documentation (Swagger/OpenAPI).
*   **Internet Security**: Implement full payload sanitization and IP-based rate limiting.
