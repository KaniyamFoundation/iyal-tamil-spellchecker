import sys
import os

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

def split_suggestion(word):
    # Try splitting the word into two parts
    # Ensure minimum length for each part to avoid splitting single characters
    suggestions = []
    min_len = 3
    for i in range(min_len, len(word) - min_len + 1):
        part1 = word[:i]
        part2 = word[i:]
        
        # In Tamil, parts might be joined by a sandhi consonant
        # Example: பிழையின்றி + த் + தமிழ்த்தாய் -> பிழையின்றித்தமிழ்த்தாய்
        # We can test if part1 and part2 are valid.
        if sc.checkword(part1, 7) and sc.checkword(part2, 7):
            suggestions.append(f"{part1} {part2}")
            
    return suggestions

print("Testing split for 'பிழையின்றிதமிழ்த்தாய்'")
print(split_suggestion("பிழையின்றிதமிழ்த்தாய்"))
print("Testing split for 'தமிழ்நாடுஅரசு'")
print(split_suggestion("தமிழ்நாடுஅரசு"))
