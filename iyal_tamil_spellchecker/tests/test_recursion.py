import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
vd.user_oword.append("அங்கிங்கெனாதபடி")
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்"

suggestions = []
min_len = 3
max_splits = 3

def recurse(remaining_word, parts, depth):
    print(f"Depth {depth}: remaining='{remaining_word}', parts={parts}")
    if depth == max_splits:
        cw = sc.checkword(remaining_word, 7)
        print(f"  Max depth reached. Checking '{remaining_word}': {cw}")
        if len(remaining_word) >= min_len and cw:
            suggestions.append(" ".join(parts + [remaining_word]))
        return
        
    cw_full = sc.checkword(remaining_word, 7)
    if len(remaining_word) >= min_len and cw_full:
        if len(parts) > 0:
            suggestions.append(" ".join(parts + [remaining_word]))
            
    for i in range(min_len, len(remaining_word) - min_len + 1):
        p1 = remaining_word[:i]
        cw = sc.checkword(p1, 7)
        if cw:
            print(f"  Found valid part: '{p1}'")
            recurse(remaining_word[i:], parts + [p1], depth + 1)

recurse(word, [], 1)
print("Result:", list(dict.fromkeys(suggestions)))
