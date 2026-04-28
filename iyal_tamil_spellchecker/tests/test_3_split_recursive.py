import sys
import os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

def get_multi_split_suggestions(word, max_splits=3):
    suggestions = []
    min_len = 3
    if len(word) < min_len * 2:
        return suggestions
        
    def recurse(remaining_word, parts, depth):
        if depth == max_splits:
            if len(remaining_word) >= min_len and sc.checkword(remaining_word, 7):
                suggestions.append(" ".join(parts + [remaining_word]))
            return

        # Always check if the current remaining chunk itself is fully valid to terminate early
        if len(remaining_word) >= min_len and sc.checkword(remaining_word, 7):
            if len(parts) > 0:
                suggestions.append(" ".join(parts + [remaining_word]))
                
        # Otherwise keep splitting
        for i in range(min_len, len(remaining_word) - min_len + 1):
            p1 = remaining_word[:i]
            if sc.checkword(p1, 7):
                recurse(remaining_word[i:], parts + [p1], depth + 1)

    recurse(word, [], 1)
    return list(dict.fromkeys(suggestions))

word = "அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்"
print(get_multi_split_suggestions(word))
print(get_multi_split_suggestions("தமிழ்நாடுஅரசு"))
