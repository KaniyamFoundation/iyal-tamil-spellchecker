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
from flask import Flask, render_template, request, jsonify, send_from_directory
import regex
from bloom_filter2 import BloomFilter
from pybktree import BKTree
from Levenshtein import distance as levenshtein_distance
from threading import Lock
import json
from flask_cors import CORS
import concurrent.futures
from TamilinaiyaVaaniSpellcheckerPy import TamilinaiyaVaaniData, TamilinaiyaVaaniSpellchecker


# ---------------------- Configuration ----------------------

BASE_DIR = Path(__file__).resolve().parent
BLOOM_PATH = BASE_DIR / "tamil_bloom.pkl"
BK_TREE_PATH = BASE_DIR / "bk_tree.pkl"
LOG_DIR = BASE_DIR / "logs"
USER_CONFIG_DIR = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "user_config"
TAMILINAIYA_VAANI_DB_PATH = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "DB.json"
BIGRAM_DB_PATH = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "bigrams_lite.db"
METRICS_FILE = BASE_DIR / "metrics.json"

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
    candidates_raw = res.bk_tree.find(word, 2)
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

# ---------------------- Routes ----------------------


@app.route("/")
def index():
    version = "0.0.3"
    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        pass
    return render_template("editor.html", version=version)

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
def spellcheck():
    text = request.json.get("text", "")
    
    # 1. First, scan for Spacing Errors (Missing space after dot)
    # Pattern: Long Tamil word + dot + Tamil word (e.g., பதிவாகியுள்ளன.இதுகுறித்து)
    # We ignore short parts (1-2 chars) to allow initials like எஸ்.ஐ.ஆர்
    results = []
    spacing_matches = list(regex.finditer(r"(\p{Tamil}{3,})\.(\p{Tamil}+)", text))
    for match in spacing_matches:
        full_match = match.group(0)
        pre = match.group(1)
        post = match.group(2)
        
        results.append({
            "word": full_match,
            "correct": False,
            "suggestions": [pre + ". " + post],
            "type": "grammar",
            "message": "முற்றுப்புள்ளிக்குப் பின் இடைவெளி தேவை (Missing space after period)"
        })

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
            with urllib.request.urlopen(req, timeout=45) as res:
                lt_response = json.loads(res.read().decode('utf-8'))
                for match in lt_response.get("matches", []):
                    offset = match.get("offset")
                    length = match.get("length")
                    err_word = text[offset:offset+length]
                    replacements = [r["value"] for r in match.get("replacements", [])]
                    grammar_errors.append({
                        "word": err_word,
                        "suggestions": replacements,
                        "message": match.get("message", ""),
                        "shortMessage": match.get("shortMessage", "")
                    })
        except Exception as e:
            print("LanguageTool API error:", e)
        return grammar_errors

    # Start the grammar check concurrently while we process the BK Tree local spelling
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_grammar = executor.submit(fetch_lt_grammar, text)

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
            
            # 0. Check Custom Dictionary Overrides
            if word in res.blacklist:
                is_correct = False
            elif word in res.whitelist:
                is_correct = True
            elif word in res.replacements:
                is_correct = False
                suggestions = res.replacements[word]
            else:
                # 1. Check Bloom filter for speed
                if word in res.bloom:
                    is_correct = True
                
                # 2. If not in Bloom, consult Vaani
                if not is_correct and res.vaani:
                    v_res = vaani_results_map.get(word)
                    if v_res:
                        if v_res[1] == "correct":
                            is_correct = True
                        else:
                            is_correct = False
                            # Vaani suggestions are comma separated
                            if v_res[1] and v_res[1] != "wrong":
                                suggestions = v_res[1].split(",")
            
            # Fallback to BK-tree if no suggestions from Vaani and it's still wrong
            if not is_correct and not suggestions:
                suggestions = suggest_word(word, prev_word=prev_word)
                if not suggestions:
                    log_event("misses", f"{word}")
                    local_no_suggestions += 1
            
            # Clean up suggestions: remove the word itself and maintain uniqueness
            if not is_correct and suggestions:
                if word in suggestions:
                    is_correct = True
                    suggestions = []
                    # Remove word if it slipped in, and keep order
                    suggestions = [s for s in suggestions if s != word]
            
            # 3. Contextual Grammar Refinement (N-Gram checking for correctly spelled but contextually wrong words)
            # This catches errors like "அவன் வந்தாள்" (should be வந்தான்)
            if is_correct and prev_word and res.bigrams:
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
                    # Generate the correct version by swapping suffixes
                    root = word[:-len(current_suffix)]
                    correct_form = root + expected_suffix
                    # Verify if the generated form is actually a word
                    if correct_form in res.bloom or (res.vaani and res.vaani.checkword(correct_form)):
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
    return jsonify({
        "results": results,
        "grammar_errors": grammar_errors,
        "metrics": metrics_store
    })        
    

@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics_store)

@app.route("/log_correction", methods=["POST"])
def log_correction():
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
    app.run(host='localhost', port=5001,debug=True)
    #app.run(debug=True)
