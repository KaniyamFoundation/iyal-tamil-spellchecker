import sys
import os

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def run_split_tests():
    print("Loading Dictionary for Split-Logic testing...\n")
    vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
    vd.load()
    vd.user_oword.append("அங்கிங்கெனாதபடி")
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    test_cases = [
        ("அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்", "அங்கிங்கெனாதபடி எங்கும் பிரகாசமாய்"),
    ]
    
    for word, expected in test_cases:
        res = sc.validate_words([word])
        sug_str = res[0][1]
        
        if expected in sug_str:
            print(f"✅ PASS | {word} >> Suggested: {expected}")
        else:
            print(f"❌ FAIL | {word} >> Expected: '{expected}' | Generated: '{sug_str}'")

if __name__ == '__main__':
    run_split_tests()
