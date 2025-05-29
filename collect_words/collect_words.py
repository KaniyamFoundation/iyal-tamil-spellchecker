import os
import json
import hashlib
import re
import time
from collections import Counter, defaultdict
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Configuration
ROOT_FOLDER = "/home/shrini/dev/llm-data"  #  Replace this with your actual root folder path
WORD_FREQ_FILE = "tamil_words.txt"
FREQUENT_WORDS_FILE = "frequent_tamil_words.txt"
MOST_USED_WORDS_FILE = "most_used_tamil_words.txt"
CACHE_FILE = "file_cache.json"
FREQUENT_THRESHOLD = 20

TAMIL_REGEX = re.compile(r"[\u0B80-\u0BFF]+")


def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_tamil_words(text):
    return TAMIL_REGEX.findall(text)


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(hash_to_files):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(hash_to_files, f, ensure_ascii=False, indent=2)


def load_existing_word_freq():
    freq = defaultdict(int)
    if os.path.exists(WORD_FREQ_FILE):
        with open(WORD_FREQ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                word, count = line.strip().rsplit(" ", 1)
                freq[word] = int(count)
    return freq


def save_word_freq(freq):
    sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    # Save all words with counts
    with open(WORD_FREQ_FILE, "w", encoding="utf-8") as f:
        for word, count in sorted_items:
            f.write(f"{word} {count}\n")

    # Save frequent words with counts
    with open(FREQUENT_WORDS_FILE, "w", encoding="utf-8") as f:
        for word, count in sorted_items:
            if count >= FREQUENT_THRESHOLD:
                f.write(f"{word} {count}\n")

    # Save most used words (just the words)
    with open("words/" + MOST_USED_WORDS_FILE, "w", encoding="utf-8") as f:
        for word, count in sorted_items:
            if count >= FREQUENT_THRESHOLD:
                f.write(f"{word}\n")


def process_file(file_path, known_hashes):
    try:
        file_hash = get_file_hash(file_path)
        if file_hash in known_hashes:
            return None

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        words = extract_tamil_words(content)
        word_counter = Counter(words)
        return file_path, file_hash, word_counter

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def process_file_wrapper(args):
    return process_file(*args)


def get_all_text_files(root_folder):
    all_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(".txt"):
                full_path = os.path.join(dirpath, filename)
                all_files.append(full_path)
    return all_files


def main():
    start_time = time.time()
    hash_to_files = load_cache()
    word_freq = load_existing_word_freq()

    known_hashes = set(hash_to_files.keys())
    all_files = get_all_text_files(ROOT_FOLDER)
    total_files = len(all_files)

    print(f"Found {total_files} text files. Starting processing...")

    task_args = [(fp, known_hashes) for fp in all_files]

    updated = False
    file_counter = 0

    with Pool(cpu_count()) as pool:
        results = list(tqdm(
            pool.imap_unordered(process_file_wrapper, task_args),
            total=total_files,
            desc="Processing"
        ))

    for result in results:
        if result is None:
            continue

        file_path, file_hash, word_counter = result
        for word, count in word_counter.items():
            word_freq[word] += count

        hash_to_files.setdefault(file_hash, []).append(file_path)
        file_counter += 1
        updated = True

    if updated:
        save_word_freq(word_freq)
        save_cache(hash_to_files)

        print("Output files updated:")
        print(f" - {WORD_FREQ_FILE}")
        print(f" - {FREQUENT_WORDS_FILE}")
        print(f" - {MOST_USED_WORDS_FILE}")
        print(f" - {CACHE_FILE}")
    else:
        print("No new or changed files found. Everything is up to date.")

    print(f"Files processed: {file_counter}/{total_files}")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
