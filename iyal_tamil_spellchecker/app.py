import os
import re
import sqlite3
import pickle
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import regex
from bloom_filter2 import BloomFilter
from pybktree import BKTree
from Levenshtein import distance as levenshtein_distance


from datetime import datetime

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

#def log_event(log_path, content):
#    with open(log_path, "a", encoding="utf-8") as f:
#        f.write(f"[{content}\n")


# ---------------------- Spell Checker ----------------------
def load_resources():
    with open(BLOOM_PATH, "rb") as f:
        bloom = pickle.load(f)
    with open(BK_TREE_PATH, "rb") as f:
        bk_tree = pickle.load(f)
    return bloom, bk_tree

bloom, bk_tree = load_resources()

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
    version = "0.0.1"
    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version = f.read().strip()
    except:
        pass
    return render_template("editor.html", version=version)



@app.route("/spellcheck", methods=["POST"])
def spellcheck():
    text = request.json.get("text", "")
    words = regex.findall(r"\p{Tamil}+", text)

    seen = set()
    results = []
    for word in words:
        if word in seen:
            continue
        seen.add(word)
        if word in bloom:
            results.append({"word": word, "correct": True})
        else:
            suggestions = suggest_word(word)
            if not suggestions:
#                log_event("misses", f"Unknown word: {word}")
                log_event(MISS_LOG_PATH, f"{word}")
            results.append({
                "word": word,
                "correct": False,
                "suggestions": suggestions
            })
    return jsonify(results)

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
    app.run(debug=True)
