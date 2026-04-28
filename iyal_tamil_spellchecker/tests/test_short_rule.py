import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def test_short_rule():
    # Load original data
    db_path = "TamilinaiyaVaaniSpellcheckerPy/data/DB.json"
    vd = TamilinaiyaVaaniData(db_path)
    vd.load()
    
    # Manually inject the short rule into gword (index 0)
    # Using type '1' for cluster safety
    vd.gword["ப்டு"] = [{"t": "1", "w": "ப்படு"}]
    
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    word = "உருவாக்கப்டுவார்"
    print(f"Testing word: '{word}' with short rule 'ப்டு' -> 'ப்படு'")
    
    # get_suggestions returns a list of suggested words
    suggestions = sc.get_suggestions(word)
    print(f"Suggestions generated: {suggestions}")
    
    if "உருவாக்கப்படுவார்" in suggestions:
        print("✅ SUCCESS: The short rule fixed the long word!")
    else:
        print("❌ FAILURE: Short rule did not match.")

if __name__ == "__main__":
    test_short_rule()
