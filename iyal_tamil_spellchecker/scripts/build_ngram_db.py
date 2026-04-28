import os
import regex
from collections import Counter, defaultdict
import sqlite3
from pathlib import Path
import tqdm

def build_db(source_dirs, db_path, word1_limit=100000, top_n_per_word=3):
    stats = defaultdict(Counter)
    word_freqs = Counter() # To find the most common word1s
    
    tamil_pattern = regex.compile(r'\p{Tamil}+')
    url_pattern = regex.compile(r'https?://\S+|%[0-9a-fA-F]{2}')
    valid_solitary = set("ஆஈஊஏஐஓஔ")
    
    total_files = []
    for s_dir in source_dirs:
        path = Path(s_dir)
        if not path.exists(): continue
        total_files.extend(list(path.rglob("*.txt")))
        
    print(f"Index complete. Total files: {len(total_files)}")
    
    for file_path in tqdm.tqdm(total_files, desc="Processing"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                content = url_pattern.sub(' ', content)
                words = [w for w in tamil_pattern.findall(content) if len(w) > 1 or w in valid_solitary]
                
                if len(words) < 2: continue
                
                for i in range(len(words) - 1):
                    w1, w2 = words[i], words[i+1]
                    stats[w1][w2] += 1
                    word_freqs[w1] += 1
        except Exception:
            continue

    print(f"Finding Top {word1_limit} core words...")
    core_words = set(w for w, f in word_freqs.most_common(word1_limit))

    print(f"Pruning bigrams...")
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=OFF;") # Size optimization
    cur.execute("DROP TABLE IF EXISTS bigrams")
    cur.execute("CREATE TABLE bigrams (word1 TEXT, word2 TEXT, freq INTEGER)")
    
    data_to_insert = []
    for w1 in core_words:
        if w1 not in stats: continue
        # Only Top 3 continuations for core words, must appear at least 5 times
        for w2, freq in stats[w1].most_common(top_n_per_word):
            if freq >= 5:
                data_to_insert.append((w1, w2, freq))
    
    print(f"Writing {len(data_to_insert)} high-quality entries to SQLite...")
    cur.executemany("INSERT INTO bigrams VALUES (?, ?, ?)", data_to_insert)
    cur.execute("CREATE INDEX idx_w1 ON bigrams(word1)")
    
    conn.commit()
    print("Compacting database...")
    cur.execute("VACUUM;")
    conn.close()
    print(f"Ultra-Lite Database build complete at {db_path}")

if __name__ == "__main__":
    SOURCES = ["/home/shrini/dev/llm-data/rss-feeds/rss-archive", "/var/www/html/tamil_datasets/text-files"]
    DB = "TamilinaiyaVaaniSpellcheckerPy/data/bigrams_lite.db"
    build_db(SOURCES, DB, word1_limit=100000, top_n_per_word=3)
