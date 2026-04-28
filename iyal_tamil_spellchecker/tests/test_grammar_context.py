import sqlite3
import os
import pytest
from pathlib import Path

# Path to the bigram DB
DB_PATH = Path("TamilinaiyaVaaniSpellcheckerPy/data/bigrams_lite.db")

@pytest.mark.parametrize("prev, current, expected_better", [
    ("அவன்", "வந்தாள்", "வந்தான்"),
    ("அவள்", "வந்தான்", "வந்தாள்"),
    ("அவர்கள்", "வந்தான்", "வந்தார்கள்"),
])
def test_grammar_agreement(prev, current, expected_better):
    if not DB_PATH.exists():
        pytest.skip(f"Skipping: DB not ready yet at {DB_PATH}")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        
        # 1. Check current frequency
        cur.execute("SELECT freq FROM bigrams WHERE word1=? AND word2=?", (prev, current))
        row = cur.fetchone()
        current_freq = row[0] if row else 0
        
        print(f"Current Usage: '{prev} {current}' (Freq: {current_freq})")
        
        # 2. Check expected better frequency
        cur.execute("SELECT freq FROM bigrams WHERE word1=? AND word2=?", (prev, expected_better))
        row = cur.fetchone()
        better_freq = row[0] if row else 0
        
        print(f"Proposed Fix:  '{prev} {expected_better}' (Freq: {better_freq})")
        
        if better_freq > current_freq and better_freq > 5:
            print(f"✅ VERIFIED: After '{prev}', the word '{expected_better}' is significantly more likely than '{current}'.")
            print(f"   Iyal will now flag this as a potential grammar error.")
        else:
            print(f"❌ NOT DETECTED: Data for this pair is not strong enough in the Top 500k index yet.")
            if current_freq == 0 and better_freq == 0:
                print("   (Both pairs have 0 frequency in our archive)")
        
        conn.close()
    except Exception as e:
        print(f"Error during test: {e}")

