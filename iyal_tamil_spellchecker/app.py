import os
import re
import sqlite3
import pickle
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import json
import time
import regex
from threading import Lock
from flask import Flask, render_template, request, jsonify, send_from_directory, g
from bloom_filter2 import BloomFilter
from pybktree import BKTree
from Levenshtein import distance as levenshtein_distance
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flasgger import Swagger
import concurrent.futures
from TamilinaiyaVaaniSpellcheckerPy import TamilinaiyaVaaniData, TamilinaiyaVaaniSpellchecker
import tamil_grammar_morphology


# ---------------------- Configuration ----------------------

BASE_DIR = Path(__file__).resolve().parent
BLOOM_PATH = BASE_DIR / "tamil_bloom.pkl"
BK_TREE_PATH = BASE_DIR / "bk_tree.pkl"
LOG_DIR = BASE_DIR / "logs"
USER_CONFIG_DIR = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "user_config"
TAMILINAIYA_VAANI_DB_PATH = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "DB.json"
BIGRAM_DB_PATH = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "bigrams_lite.db"
METRICS_FILE = BASE_DIR / "metrics.json"

# --- Rate Limit Constants ---
LIMIT_DEFAULT = ["200 per day", "50 per hour"]
LIMIT_SPELLCHECK = "20 per minute"
LIMIT_LOG_CORRECTION = "5 per minute"
WHITELISTED_IPS = ["127.0.0.1"]
MAX_CHARACTER_LIMIT = 50000

# Logging setup with Pathlib
DATE_STR = datetime.now().strftime("%Y-%m-%d")
MISS_LOG_DIR = LOG_DIR / "misses" / DATE_STR
CORRECTION_LOG_DIR = LOG_DIR / "corrections" / DATE_STR
MISS_LOG_DIR.mkdir(parents=True, exist_ok=True)
CORRECTION_LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------- Dataclasses ----------------------

@dataclass
class SpellCheckerResources:
    bloom: BloomFilter
    bk_tree: BKTree
    vaani: TamilinaiyaVaaniSpellchecker
    whitelist: set = field(default_factory=set)
    blacklist: set = field(default_factory=set)
    replacements: dict = field(default_factory=dict)
    bigrams: sqlite3.Connection = None

# ---------------------- Flask Setup ----------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://ta.wikisource.org"}})
Compress(app)
Swagger(app)

# --- Rate Limiter Setup ---
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=LIMIT_DEFAULT,
    storage_uri="memory://",
)

# 2. Whitelist IPs so they are never blocked
@limiter.request_filter
def ip_whitelist():
    return request.remote_addr in WHITELISTED_IPS

# --- Performance Telemetry ---
@app.before_request
def start_timer():
    g.start = time.time()

@app.after_request
def add_process_time_header(response):
    if hasattr(g, 'start'):
        diff = time.time() - g.start
        response.headers["X-Process-Time"] = f"{int(diff * 1000)}ms"
    return response

# 1. Custom JSON Error Response for Rate Limits
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "மகிழ்வுறுத்தல்கள் அதிகம் (Too Many Requests)",
        "message": f"தாமதத்திற்கு மன்னிக்கவும். மீண்டும் முயற்சிக்கவும். ({e.description})",
        "retry_after": e.description
    }), 429

metrics_lock = Lock()

def load_metrics():
    if not METRICS_FILE.exists():
        return {"total_words": 0, "corrections": 0, "no_suggestions": 0}
    with open(METRICS_FILE, "r") as f:
        return json.load(f)

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f)

# ---------------------- Resource Loader ----------------------

def load_resources() -> SpellCheckerResources:
    with open(BLOOM_PATH, "rb") as f:
        bloom = pickle.load(f)
    with open(BK_TREE_PATH, "rb") as f:
        bk_tree = pickle.load(f)
    
    # Load Vaani Data
    vaani_data = TamilinaiyaVaaniData(str(TAMILINAIYA_VAANI_DB_PATH))
    vaani_checker = None
    if vaani_data.load():
        vaani_data.load_user_data(str(USER_CONFIG_DIR / "rightwordlist.txt"))
        vaani_data.load_vulgar_words(str(USER_CONFIG_DIR / "vulgar_splits.txt"))
        vaani_checker = TamilinaiyaVaaniSpellchecker(vaani_data)
    else:
        print(f"Warning: Vaani DB could not be loaded from {TAMILINAIYA_VAANI_DB_PATH}")

    # Load overrides
    whitelist = set()
    blacklist = set()
    replacements = {}
    
    def read_config(filename):
        path = USER_CONFIG_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return []

    whitelist.update(read_config("rightwordlist.txt"))
    whitelist.update(read_config("global_places.txt"))
    blacklist.update(read_config("wrongwordlist.txt"))
    
    for line in read_config("replacements.txt"):
        if "|" in line:
            orig, sug = line.split("|", 1)
            replacements[orig.strip()] = [s.strip() for s in sug.split(",")]
        
    return SpellCheckerResources(
        bloom=bloom,
        bk_tree=bk_tree,
        vaani=vaani_checker,
        whitelist=whitelist,
        blacklist=blacklist,
        replacements=replacements,
        bigrams=None
    )

def setup_bigrams(resources: SpellCheckerResources):
    """Attempt to load the bigram database if it exists."""
    if BIGRAM_DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(BIGRAM_DB_PATH), check_same_thread=False)
            resources.bigrams = conn
            print("Bigram context database loaded successfully.")
        except Exception as e:
            print(f"Error loading Bigram DB: {e}")

res = load_resources()
setup_bigrams(res)

def suggest_word(word, prev_word=None, max_suggestions=5):
    if not res.bk_tree:
        return []
        
    candidates_raw = res.bk_tree.find(word, 2)
    if not candidates_raw and len(word) >= 10:
        candidates_raw = res.bk_tree.find(word, 3)
    # Filter candidates by length difference and first char matching (common Tamil typo trait)
    filtered = [w for d, w in candidates_raw if abs(len(w) - len(word)) <= 2 and w[0] == word[0]]
    
    if not filtered:
        return []

    # If we have a previous word and a bigram DB, rank the suggestions by frequency
    if prev_word and res.bigrams:
        scored = []
        try:
            cursor = res.bigrams.cursor()
            for cand in filtered:
                # Query frequency of the pair (prev_word, cand)
                cursor.execute("SELECT freq FROM bigrams WHERE word1=? AND word2=?", (prev_word, cand))
                row = cursor.fetchone()
                freq = row[0] if row else 0
                scored.append((cand, freq))
            
            # Sort by frequency (highest first)
            ranked = [pair[0] for pair in sorted(scored, key=lambda x: x[1], reverse=True)]
            return ranked[:max_suggestions]
        except Exception as e:
            print(f"Bigram ranking error: {e}")
            return sorted(filtered)[:max_suggestions]
    
    # Fallback to simple alphabetical or proximity sorting
    return sorted(filtered)[:max_suggestions]

def log_event(subfolder, content):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # Subfolder will be typically "misses" or "corrections"
    # The architecture uses: logs / folder / DATE_STR / timestamp.log
    folder = LOG_DIR / subfolder / DATE_STR
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / f"{timestamp}.log"
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"{content}\n")

# Version check caching
VERSION_CACHE = {
    "remote_version": None,
    "last_check": 0
}
VERSION_CHECK_INTERVAL = 3600  # Check once per hour
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/KaniyamFoundation/iyal-tamil-spellchecker/main/iyal_tamil_spellchecker/version.txt"

def get_cached_remote_version():
    now = time.time()
    if now - VERSION_CACHE["last_check"] > VERSION_CHECK_INTERVAL:
        try:
            with urllib.request.urlopen(REMOTE_VERSION_URL, timeout=3) as response:
                VERSION_CACHE["remote_version"] = response.read().decode('utf-8').strip()
                VERSION_CACHE["last_check"] = now
        except Exception as e:
            # We don't want to crash on network error, just log and wait a bit
            VERSION_CACHE["last_check"] = now - (VERSION_CHECK_INTERVAL - 300) # Retry in 5 mins
    return VERSION_CACHE["remote_version"]

# ---------------------- Routes ----------------------



@app.route("/")
def index():
    version = "0.0.3"
    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        pass

    messages = ""
    try:
        if os.path.exists("messages.txt"):
            with open("messages.txt", "r", encoding="utf-8") as f:
                messages = f.read()
    except:
        pass

    remote_version = get_cached_remote_version()
    update_available = False
    if remote_version:
        try:
            l = [int(x) for x in version.split('.')]
            r = [int(x) for x in remote_version.split('.')]
            if r > l:
                update_available = True
        except:
            pass

    return render_template("editor.html", version=version, messages=messages, update_available=update_available, remote_version=remote_version)


# ---------------------- Grammar Rules ----------------------

# Map of common pronouns to their expected verb suffixes
PRONOUN_AGREEMENT = {
    "நான்": "ேன்",
    "நீ": "ாய்",
    "அவன்": "ான்",
    "அவள்": "ாள்",
    "அவர்": "ார்",
    "அது": "து",
    "நாம்": "ோம்",
    "நாங்கள்": "ோம்",
    "நீங்கள்": "ீர்கள்",
    "அவர்கள்": "ார்கள்",
    "அவை": "ன"
}


# Initialize
metrics_store = load_metrics()

@app.route("/spellcheck", methods=["POST"])
@app.route("/v1/spellcheck", methods=["POST"])
@limiter.limit(LIMIT_SPELLCHECK)
def spellcheck():
    """
    Tamil Spellcheck API
    ---
    tags:
      - Core API
    parameters:
      - in: body
        name: body
        schema:
          id: SpellcheckRequest
          required:
            - text
          properties:
            text:
              type: string
              description: The Tamil text to check (or a list of strings for batch mode)
              example: "அவன் வந்தாள்"
    responses:
      200:
        description: List of words with correctness and suggestions
    """
    input_data = request.json.get("text", "")
    
    # Batch processing support
    if isinstance(input_data, list):
        batch_results = []
        for item in input_data:
            # For batches, we return the error dictionary directly without the HTTP code
            res_item = process_single_text(str(item))
            if isinstance(res_item, tuple):
                batch_results.append(res_item[0]) # Just the error body
            else:
                batch_results.append(res_item)
        return jsonify({"batch_results": batch_results})
    
    # Handle single request (can return 413 tuple)
    result = process_single_text(str(input_data))
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)

def process_single_text(text):
    # Safety Check: Character Limit (Enforced only for non-whitelisted API users)
    if len(text) > MAX_CHARACTER_LIMIT and request.remote_addr not in WHITELISTED_IPS:
        return {
            "error": "உரை மிக நீளமானது (Text too long)",
            "message": f"மன்னிக்கவும், ஒரு நேரத்தில் {MAX_CHARACTER_LIMIT} எழுத்துக்களை மட்டுமே சரிபார்க்க முடியும். சிறிய பகுதிகளாகப் பயன்படுத்தவும்."
        }, 413
    
    # 1. First, scan for Spacing Errors (Missing space after dot)
    results = tamil_grammar_morphology.find_spacing_errors(text)

    # 2. Extract and check individual words
    words = regex.findall(r"\p{Tamil}+", text)

    seen = set()
    local_corrections = 0
    local_no_suggestions = 0
    def fetch_lt_grammar(text):
        grammar_errors = []
        try:
            #Check with local LanguageTool server
            data = urllib.parse.urlencode({'language': 'ta', 'text': text}).encode('utf-8')
            req = urllib.request.Request('http://localhost:8081/v2/check', data=data)
            with urllib.request.urlopen(req, timeout=45) as res_lt:
                lt_response = json.loads(res_lt.read().decode('utf-8'))
                for match in lt_response.get("matches", []):
                    offset = match.get("offset")
                    length = match.get("length")
                    err_word = text[offset:offset+length]
                    replacements = [r["value"] for r in match.get("replacements", [])]
                    grammar_errors.append({
                        "word": err_word,
                        "error_type": "grammar",
                        "suggestions": replacements,
                        "message": match.get("message", ""),
                        "shortMessage": match.get("shortMessage", "")
                    })

        except Exception as e:
            print("LanguageTool API error:", e)
        return grammar_errors

    # Start the grammar check concurrently while we process the BK Tree local spelling
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_grammar = executor.submit(tamil_grammar_morphology.fetch_lt_grammar, text)

        # Get suggestions from TamilinaiyaVaani if available
        vaani_results_map = {}
        if res.vaani:
            vaani_parinthu = res.vaani.validate_words(words)
            vaani_results_map = {words[i]: vaani_parinthu[i] for i in range(len(words))}

        prev_word = None
        for word in words:
            if word in seen:
                # We still need to update prev_word to maintain context for the NEXT word
                prev_word = word
                continue
            seen.add(word)
            
            is_correct = False
            suggestions = []
            error_type = "spelling"
            
            # 0. Check Custom Dictionary Overrides
            if word in res.blacklist:
                is_correct = False
                error_type = "blacklist"
            elif word in res.replacements:
                is_correct = False
                suggestions = res.replacements[word]
                error_type = "colloquial"
            elif word in res.whitelist:
                is_correct = True

            else:
                # 1. Check Bloom filter for speed
                if word in res.bloom:
                    is_correct = True
                
                # 2. Check for trailing sandhi consonants (க, ச, த, ப + ்)
                if not is_correct:
                    base_sandhi = tamil_grammar_morphology.get_base_sandhi_word(word)
                    if base_sandhi:
                        if base_sandhi in res.bloom or base_sandhi in res.whitelist or (res.vaani and res.vaani.checkword(base_sandhi, 0)):
                            is_correct = True
                        else:
                            # Check if the sandhi-stripped word is a derived variant
                            possible_roots = tamil_grammar_morphology.get_derived_viku_variants(base_sandhi)
                            for r_word in possible_roots:
                                if r_word in res.bloom or r_word in res.whitelist or (res.vaani and res.vaani.checkword(r_word, 0)):
                                    is_correct = True
                                    break

                
                # 2.5. Check derived words of valid roots (Noun Case Endings / Coordinating Suffixes)
                if not is_correct:
                    possible_roots = tamil_grammar_morphology.get_derived_viku_variants(word)
                    for r_word in possible_roots:
                        # Stricter validation for very short roots (likely syllables/noise in Bloom)
                        if len(r_word) <= 2:
                            if r_word in res.whitelist or (res.vaani and res.vaani.checkword(r_word, 0)):
                                is_correct = True
                                break
                        else:
                            if r_word in res.bloom or r_word in res.whitelist or (res.vaani and res.vaani.checkword(r_word, 0)):
                                is_correct = True
                                break
                
                # 3. If not in Bloom and not sandhi-stripped, consult Vaani
                if not is_correct and res.vaani:
                    v_res = vaani_results_map.get(word)
                    if v_res:
                        if v_res[1] == "correct":
                            is_correct = True
                        else:
                            if v_res[1] and v_res[1] != "wrong":
                                suggestions = v_res[1].split(",")
            
                if not is_correct and prev_word:
                    combined = prev_word + word
                    if combined in res.bloom or combined in res.whitelist or (res.vaani and res.vaani.checkword(combined, 0)):
                        suggestions.insert(0, combined)
                        error_type = "sandhi"
            
            # Fallback to BK-tree if no suggestions from Vaani and it's still wrong
            if not is_correct:
                bk_sugs = suggest_word(word, prev_word=prev_word)
                if not suggestions:
                    suggestions = bk_sugs
                    if not suggestions:
                        log_event("misses", f"{word}")
                        local_no_suggestions += 1
                elif bk_sugs:
                    # Append unique bk-tree suggestions
                    suggestions.extend([s for s in bk_sugs if s not in suggestions])
            
            # Clean up suggestions: remove the word itself and maintain uniqueness
            if not is_correct and suggestions:
                unique_sugs = []
                for s in suggestions:
                    s_clean = s.strip()
                    if s_clean and s_clean != word and s_clean not in unique_sugs:
                        unique_sugs.append(s_clean)
                
                # Smart Heuristic: If we have legitimate typo corrections (no spaces),
                # drop the split suggestions (contain spaces) to prevent nonsensical splits.
                non_splits = [s for s in unique_sugs if " " not in s]
                splits = [s for s in unique_sugs if " " in s]
                
                if non_splits and error_type != "colloquial":
                    suggestions = non_splits[:5]
                else:
                    suggestions = (splits + non_splits)[:5]

                    error_type = "sandhi"

            
            # 3. Contextual Grammar Refinement (N-Gram checking for correctly spelled but contextually wrong words)
            # This catches errors like "அவன் வந்தாள்" (should be வந்தான்)
            if False and is_correct and prev_word and res.bigrams:
                try:
                    cursor = res.bigrams.cursor()
                    # Current frequency
                    cursor.execute("SELECT freq FROM bigrams WHERE word1=? AND word2=?", (prev_word, word))
                    row = cursor.fetchone()
                    current_freq = row[0] if row else 0
                    
                    # Only investigate if current connection is weak/missing
                    if current_freq < 2:
                        # Find morphological "neighbors" (edit distance 1 or 2)
                        neighbors = res.bk_tree.find(word, 2)
                        better_matches = []
                        
                        for dist, neighbor in neighbors:
                            if neighbor == word: continue
                            
                            # Check if the neighbor has a strong connection to prev_word
                            cursor.execute("SELECT freq FROM bigrams WHERE word1=? AND word2=?", (prev_word, neighbor))
                            n_row = cursor.fetchone()
                            n_freq = n_row[0] if n_row else 0
                            
                            # If a neighbor is significantly more likely (e.g., freq > 10), it's probably what the user meant
                            if n_freq > 10: 
                                better_matches.append((neighbor, n_freq))
                        
                        if better_matches:
                            # We found a legitimate grammar mismatch!
                            is_correct = False
                            # Sort by frequency and add to suggestions
                            better_matches.sort(key=lambda x: x[1], reverse=True)
                            suggestions = [m[0] for m in better_matches] + suggestions
                            # Uniqueness
                            suggestions = list(dict.fromkeys(suggestions))
                except Exception as e:
                    print(f"Grammar refinement error: {e}")

            # 4. Rule-Based Pronominal Agreement (Fallback for sparse N-grams)
            if is_correct and prev_word in PRONOUN_AGREEMENT:
                expected_suffix = PRONOUN_AGREEMENT[prev_word]
                # If current word looks like a verb (ends in common verb endings) but doesn't match the pronoun
                # common_verb_endings = ["ான்", "ாள்", "ார்", "து", "ேன்", "ோம்", "ாய்", "ீர்கள்", "ார்கள்", "ன"]
                verb_endings = list(PRONOUN_AGREEMENT.values())
                
                current_suffix = None
                for ve in verb_endings:
                    if word.endswith(ve):
                        current_suffix = ve
                        break
                
                if current_suffix and current_suffix != expected_suffix:
                    # Mismatch found! e.g. "அவர்கள்" followed by something ending in "ான்"
                    is_correct = False
                    error_type = "grammar"
                    # Generate the correct version by swapping suffixes
                    root = word[:-len(current_suffix)]
                    correct_form = root + expected_suffix
                    # Verify if the generated form is actually a word
                    if correct_form in res.bloom or (res.vaani and res.vaani.checkword(correct_form, 0)):
                        suggestions = [correct_form] + suggestions
                    
            # Update context for next word
            prev_word = word
            
            if is_correct:
                results.append({"word": word, "correct": True})
            else:
                local_corrections += 1
                results.append({
                    "word": word,
                    "correct": False,
                    "error_type": error_type,
                    "suggestions": suggestions
                })

        grammar_errors = future_grammar.result()

   # Update persistent metrics
    with metrics_lock:
            # Update and save metrics
        metrics_store["total_words"] += len(words)
        metrics_store["corrections"] += local_corrections
        metrics_store["no_suggestions"] += local_no_suggestions
        save_metrics(metrics_store)
    return {
        "results": results,
        "grammar_errors": grammar_errors,
        "metrics": metrics_store
    }

@app.route("/metrics", methods=["GET"])
@app.route("/v1/metrics", methods=["GET"])
def get_metrics():
    """Metrics API"""
    return jsonify(metrics_store)

@app.route("/log_correction", methods=["POST"])
@app.route("/v1/log_correction", methods=["POST"])
@limiter.limit(LIMIT_LOG_CORRECTION)
def log_correction():
    """Log user correction"""
    data = request.get_json()
    original = data.get("original")
    selected = data.get("selected")
    log_event("corrections", f"{original} -> {selected}")
    return jsonify({"status": "ok"})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    #app.run(host='localhost', port=5001,debug=True)
    # Resource reset triggered!

    app.run(host='localhost', port=5000,debug=True)
    #app.run(debug=True)
