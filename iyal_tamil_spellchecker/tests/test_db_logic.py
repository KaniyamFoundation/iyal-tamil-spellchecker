import sys
import os

# Add the project root to path
sys.path.append(os.getcwd())

from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def test_db_update():
    print("Loading Vaani Data...")
    db_path = "TamilinaiyaVaaniSpellcheckerPy/data/DB.json"
    vd = TamilinaiyaVaaniData(db_path)
    vd.load()
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    word = "பயிற்றுவிக்கப்டும்"
    print(f"Testing word: '{word}'")
    
    # validate_words returns [count, suggestion_string]
    results = sc.validate_words([word])
    res = results[0]
    
    print(f"Result: {res}")
    if "பயிற்றுவிக்கப்படும்" in res[1]:
        print("SUCCESS: Engine now suggests the correct form!")
    else:
        print("FAILURE: Engine did not provide the correct suggestion.")

if __name__ == "__main__":
    test_db_update()
