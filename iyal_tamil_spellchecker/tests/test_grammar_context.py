import sqlite3
import os
from pathlib import Path

# Path to the bigram DB
DB_PATH = Path("TamilinaiyaVaaniSpellcheckerPy/data/bigrams_lite.db")

def test_grammar_agreement(prev, current, expected_better):
    if not DB_PATH.exists():
        print(f"Skipping: DB not ready yet at {DB_PATH}")
        return
    
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

if __name__ == "__main__":
    print("\nIyal Contextual Grammar Verification")
    print("=" * 40)
    
    print("\nCase 1: Gender Mismatch (He -> She-Verb)")
    test_grammar_agreement("அவன்", "வந்தாள்", "வந்தான்")
    
    print("\nCase 2: Gender Mismatch (She -> He-Verb)")
    test_grammar_agreement("அவள்", "வந்தான்", "வந்தாள்")
    
    print("\nCase 3: Plurality Mismatch (They -> He-Verb)")
    test_grammar_agreement("அவர்கள்", "வந்தான்", "வந்தார்கள்")

    print("\n" + "=" * 40)
    if not DB_PATH.exists():
        print("NOTE: The database build is still active. Please run this script again in a few minutes.")
    else:
        print("Tests complete.")
