import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def debug_full_pipeline():
    print("--- DEBUGGING FULL PIPELINE ---")
    db_path = "TamilinaiyaVaaniSpellcheckerPy/data/DB.json"
    vd = TamilinaiyaVaaniData(db_path)
    vd.load()
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    word = "உருவாக்கப்டுவார்"
    print(f"1. Testing Word: {word}")
    
    # Step A: Generate Candidates
    candidates = sc.get_suggestions(word)
    print(f"2. Found {len(candidates)} candidates.")
    
    # Step B: Filter through checkword
    # This is exactly what validate_words[297] does
    valid_suggestions = []
    target = "உருவாக்கப்படுவார்"
    
    print(f"3. Searching for '{target}' in candidates...")
    if target in candidates:
        print(f"   - Match found in pool.")
        print(f"4. Checking if '{target}' is rejected by checkword...")
        # type_code 7 is used for suggestions validation
        if sc.checkword(target, 7):
            print(f"   - SUCCESS: '{target}' passed checkword!")
            valid_suggestions.append(target)
        else:
            print(f"   - FAILURE: '{target}' was REJECTED by checkword logic.")
    else:
        print(f"   - FAILURE: '{target}' not even in the candidate pool!")

    # Step C: Final Result from validate_words
    print("\n5. Running final validate_words call:")
    final_res = sc.validate_words([word])
    print(f"   - Final Result: {final_res}")

if __name__ == "__main__":
    debug_full_pipeline()
