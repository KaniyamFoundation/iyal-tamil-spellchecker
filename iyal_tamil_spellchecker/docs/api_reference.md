# Iyal Tamil Spellchecker API Reference

The Iyal Tamil Spellchecker exposes a lightning-fast RESTful JSON API via Flask. It bridges the native Python morphological engine (Vaani) with the local LanguageTool Java server.

By default, the server runs on `http://localhost:5001`.

---

## 0. API Documentation (Swagger UI)
Iyal includes a built-in interactive documentation portal.

**URL:** `/apidocs/`  
**Description:** Provides a visual sandbox to test endpoints, explore request/response schemas, and view the OpenAPI specification.

---

## 1. Spell and Grammar Check
Validates text for morphological spelling errors, missing spaces, and contextual grammar rules simultaneously via multi-threading.

**Endpoints:** 
- `POST /spellcheck`
- `POST /v1/spellcheck` (Versioned route)

**Content-Type:** `application/json`

**Request Payload:**
```json
{
  "text": "அவன் வந்தாள்"
}
```
**Alternative: Batch Mode**
You can pass a list of strings to check multiple snippets in parallel.
```json
{
  "text": ["அவன் வந்தான்", "அவள் வந்தாள்"]
}
```

**Response Payload (200 OK):**
```json
{
  "grammar_errors": [
    {
      "message": "Grammar rule violation message from LanguageTool.",
      "shortMessage": "Short error title",
      "suggestions": ["Correction1", "Correction2"],
      "word": "err_word"
    }
  ],
  "metrics": {
    "corrections": 15,
    "no_suggestions": 2,
    "total_words": 1500
  },
  "results": [
    {
      "correct": true,
      "word": "உங்களது"
    },
    {
      "correct": false,
      "suggestions": ["சரியான", "சரியாக"],
      "word": "சரியன",
      "type": "grammar",           // Only present for custom engine-level regex spacing exceptions
      "message": "Error details"    // Only present for custom engine-level regex spacing exceptions
    }
  ]
}
```

---

## 2. Telemetry: Log Correction Selection
Records the end-users explicitly selected corrections. This is appended locally to track spellchecker accuracy and identify domain-specific missing words.

**Endpoints:** 
- `POST /log_correction`
- `POST /v1/log_correction` (Versioned route)

**Content-Type:** `application/json`

**Request Payload:**
```json
{
  "original": "தட்டச்சுசெய்யும்போதே",
  "selected": "தட்டச்சு செய்யும்போதே"
}
```

**Response Payload (200 OK):**
```json
{
  "status": "ok"
}
```

---

## 3. Live Server Metrics
Retrieves the persistent lifetime telemetry statistics of the spellchecker server cache.

**Endpoints:** 
- `GET /metrics`
- `GET /v1/metrics` (Versioned route)

**Response Payload (200 OK):**
```json
{
  "corrections": 4200,
  "no_suggestions": 12,
  "total_words": 450000
}
```

---

## 4. Health Check
Simple network ping endpoint to verify the API is online and responding. Used by deployment load-balancers.

**Endpoint:** `GET /health`  

**Response Payload (200 OK):**
`OK`

---

## 5. Performance Instrumentation
Every response from the Iyal API includes a performance header to help developers monitor server load and processing speed.

| Header | Description | Example |
| :--- | :--- | :--- |
| `X-Process-Time` | The wall-clock time spent processing the request on the server (in ms) | `45ms` |
| `Content-Encoding` | Compression format (if enabled via `Flask-Compress`) | `gzip` |
