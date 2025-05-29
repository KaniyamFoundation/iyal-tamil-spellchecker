import os
import re
import sqlite3
import pickle
import zlib
import hashlib
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from glob import glob
from bloom_filter2 import BloomFilter
from Levenshtein import distance as levenshtein_distance
from pybktree import BKTree
from time import time
import regex  # Used for grapheme splitting

from flask import Flask, render_template, request, jsonify, send_from_directory

# ---------------------- Configuration ----------------------


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BLOOM_PATH = BASE_DIR + "/" + "tamil_bloom.pkl"
BK_TREE_PATH = BASE_DIR + "/" +  "bk_tree.pkl"

# ---------------------- Flask Setup ----------------------
app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("editor.html")


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
            results.append({
                "word": word,
                "correct": False,
                "suggestions": suggestions
            })
    return jsonify(results)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.run(debug=True)

    
