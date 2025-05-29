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

# ---------------------- Configuration ----------------------
CORPUS_DIR = "../collect_words/words"

#CORPUS_DIR = "./corpus"
#DB_PATH = "tamil_index.db"
BLOOM_PATH = "tamil_bloom.pkl"
HASH_DB_PATH = "file_hashes.pkl"
#UNIQUE_WORDS_PATH = "unique_words.pkl"
BK_TREE_PATH = "bk_tree.pkl"
BLOOM_CAPACITY = 10_000_000
BLOOM_ERROR_RATE = 0.001

# ---------------------- Utilities ----------------------

def get_all_text_files(base_path):
    return glob(os.path.join(base_path, "**/*.txt"), recursive=True)

def split_graphemes(word):
    """Split a word into grapheme clusters"""
    return regex.findall(r'\X', word)

def tokenize_tamil(text):
    """Tokenize Tamil text into words"""
    return re.findall(r'[\u0B80-\u0BFF]+', text)

def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"Hashing failed for {path}: {e}")
        return None

def process_file(path):
    words = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                words.update(tokenize_tamil(line.strip()))
    except Exception as e:
        print(f"Error processing {path}: {e}")
    return path, list(words)

# ---------------------- Indexing ----------------------


def build_index():
    print("Scanning files...")
    all_files = get_all_text_files(CORPUS_DIR)

    if os.path.exists(HASH_DB_PATH):
        with open(HASH_DB_PATH, "rb") as f:
            old_hashes = pickle.load(f)
    else:
        old_hashes = {}

    file_paths = []
    new_hashes = {}
    for path in all_files:
        h = file_hash(path)
        if h and (path not in old_hashes or old_hashes[path] != h):
            file_paths.append(path)
            new_hashes[path] = h

    if not file_paths:
        print("No new or changed files. Index is up to date.")
        return

    print(f"{len(file_paths)} new or changed files detected.")

    start_time = time()
    results = []
    with Pool(cpu_count()) as pool:
        for result in tqdm(pool.imap_unordered(process_file, file_paths), total=len(file_paths), desc="Indexing Files"):
            results.append(result)

    all_words = set()
    for _, words in results:
        all_words.update(words)

    if os.path.exists(BLOOM_PATH):
        with open(BLOOM_PATH, "rb") as f:
            bloom = pickle.load(f)
    else:
        bloom = BloomFilter(max_elements=BLOOM_CAPACITY, error_rate=BLOOM_ERROR_RATE)

    for word in tqdm(all_words, desc="Updating Bloom"):
        bloom.add(word)

    with open(BLOOM_PATH, "wb") as f:
        pickle.dump(bloom, f)

#    with open(UNIQUE_WORDS_PATH, "wb") as f:
#        pickle.dump(all_words, f)

    print("Building BK-tree for fast suggestions...")
    bk_tree = BKTree(levenshtein_distance, list(all_words))
    with open(BK_TREE_PATH, "wb") as f:
        pickle.dump(bk_tree, f)

    old_hashes.update(new_hashes)
    with open(HASH_DB_PATH, "wb") as f:
        pickle.dump(old_hashes, f)


    print(f"Indexing completed in {time() - start_time:.2f} seconds.")


build_index()
