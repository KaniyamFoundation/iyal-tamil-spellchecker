import sys
import os

# Add the project root to path
sys.path.append(os.getcwd())

from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def verify_engine(word, expected_suggestion):
    print(f"Loading Vaani Data...")
    db_path = "TamilinaiyaVaaniSpellcheckerPy/data/DB.json"
    vd = TamilinaiyaVaaniData(db_path)
    vd.load()
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    print(f"Testing: '{word}' -> Expected: '{expected_suggestion}'")
    results = sc.validate_words([word])
    res = results[0]
    
    print(f"Resulting Suggestion: {res[1]}")
    if expected_suggestion in res[1]:
        print("✅ SUCCESS: Correction verified.")
        return True
    else:
        print("❌ FAILURE: Correction not found.")
        return False

if __name__ == "__main__":
    # Test our latest addition
    verify_engine("பயிற்றுவிக்கப்டும்", "பயிற்றுவிக்கப்படும்")
