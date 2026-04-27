import os
import re
import sqlite3
import pickle
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOOM_PATH = os.path.join(BASE_DIR, "tamil_bloom.pkl")
BK_TREE_PATH = os.path.join(BASE_DIR, "bk_tree.pkl")
LOG_DIR = os.path.join(BASE_DIR, "logs")

date_str = datetime.now().strftime("%Y-%m-%d")
# Logging Setup
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSION_ID = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
MISS_LOG_PATH = os.path.join(LOG_DIR, "misses", f"{date_str}")
CORRECTION_LOG_PATH = os.path.join(LOG_DIR, "corrections", f"{date_str}")

os.makedirs(os.path.dirname(MISS_LOG_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CORRECTION_LOG_PATH), exist_ok=True)

# ---------------------- Flask Setup ----------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://ta.wikisource.org"}})

#def log_event(log_path, content):
#    with open(log_path, "a", encoding="utf-8") as f:
#        f.write(f"[{content}\n")



METRICS_FILE = os.path.join(BASE_DIR, "metrics.json")
metrics_lock = Lock()

def load_metrics():
    if not os.path.exists(METRICS_FILE):
        return {"total_words": 0, "corrections": 0, "no_suggestions": 0}
    with open(METRICS_FILE, "r") as f:
        return json.load(f)

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f)

        
# ---------------------- Spell Checker ----------------------
TAMILINAIYA_VAANI_DB_PATH = os.path.join(BASE_DIR, "TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
TAMILINAIYA_VAANI_USER_PATH = os.path.join(BASE_DIR, "TamilinaiyaVaaniSpellcheckerPy/data/User.txt")
USER_CONFIG_DIR = os.path.join(BASE_DIR, "TamilinaiyaVaaniSpellcheckerPy/data/user_config")

def load_resources():
    with open(BLOOM_PATH, "rb") as f:
        bloom = pickle.load(f)
    with open(BK_TREE_PATH, "rb") as f:
        bk_tree = pickle.load(f)
    
    # Load Vaani Data
    tamilinaiya_vaani_data = TamilinaiyaVaaniData(TAMILINAIYA_VAANI_DB_PATH)
    if not tamilinaiya_vaani_data.load():
        print("Warning: TamilinaiyaVaani DB could not be loaded")
        tamilinaiya_vaani_checker = None
    else:
        # We can still point to User.txt for the engine if needed, 
        # but we'll manage the main overrides in app.py directly
        # tamilinaiya_vaani_data.load_user_data(TAMILINAIYA_VAANI_USER_PATH)
        tamilinaiya_vaani_checker = TamilinaiyaVaaniSpellchecker(tamilinaiya_vaani_data)
        
    # Load User-defined overrides from dedicated config folder
    custom_whitelist = set()
    custom_blacklist = set()
    custom_replacements = {}
    
    def read_config_file(filename):
        path = os.path.join(USER_CONFIG_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return []

    # 1. Whitelist
    for word in read_config_file("rightwordlist.txt"):
        custom_whitelist.add(word)
        
    # 2. Blacklist
    for word in read_config_file("wrongwordlist.txt"):
        custom_blacklist.add(word)
        
    # 3. Replacements
    for line in read_config_file("replacements.txt"):
        if "|" in line:
            orig, sug = line.split("|", 1)
            custom_replacements[orig.strip()] = sug.strip()
        
    return bloom, bk_tree, tamilinaiya_vaani_checker, custom_whitelist, custom_blacklist, custom_replacements

bloom, bk_tree, tamilinaiya_vaani_checker, custom_whitelist, custom_blacklist, custom_replacements = load_resources()

def suggest_word(word, max_suggestions=5):
    candidates = bk_tree.find(word, 2)
    filtered = [(w, d) for d, w in candidates if abs(len(w) - len(word)) <= 2 and w[0] == word[0]]
    return [w for w, d in sorted(filtered, key=lambda x: x[1])[:max_suggestions]]

def log_event(subfolder, content):
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    folder = os.path.join(LOG_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{timestamp}.log")
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
        tamilinaiya_vaani_results_map = {}
        if tamilinaiya_vaani_checker:
            # tamilinaiya_vaani_checker.validate_words expects a list of words
            # It returns a list of [count, suggestion_string]
            tamilinaiya_vaani_parinthu = tamilinaiya_vaani_checker.validate_words(words)
            tamilinaiya_vaani_results_map = {words[i]: tamilinaiya_vaani_parinthu[i] for i in range(len(words))}

        for word in words:
            if word in seen:
                continue
            seen.add(word)
            
            is_correct = False
            suggestions = []
            
            # 0. Check Custom Dictionary Overrides
            if word in custom_blacklist:
                is_correct = False
            elif word in custom_whitelist:
                is_correct = True
            elif word in custom_replacements:
                is_correct = False
                suggestions = [custom_replacements[word]]
            else:
                # 1. Check Bloom filter for speed
                if word in bloom:
                    is_correct = True
                
                # 2. If not in Bloom, consult Vaani
                if not is_correct and tamilinaiya_vaani_checker:
                    v_res = tamilinaiya_vaani_results_map.get(word)
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
                suggestions = suggest_word(word)
                if not suggestions:
                    log_event(MISS_LOG_PATH, f"{word}")
                    local_no_suggestions += 1
            
            # Clean up suggestions: remove the word itself and maintain uniqueness
            if not is_correct and suggestions:
                if word in suggestions:
                    is_correct = True
                    suggestions = []
                else:
                    # Remove word if it slipped in, and keep order
                    suggestions = [s for s in suggestions if s != word]
            
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
    log_event(CORRECTION_LOG_PATH, f"{original} -> {selected}")
    return jsonify({"status": "ok"})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    #app.run(host='localhost', port=5001,debug=True)
    app.run(debug=True)
