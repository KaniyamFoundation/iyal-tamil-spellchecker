import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "எடுத்துகிட்டேன்"
sugs = sc.get_suggestions(word)
print("Fuzzy Suggestions:", sugs)
unique_sug = list(dict.fromkeys(sugs))
for nword in unique_sug:
    if sc.checkword(nword, 7):
        print("Found matching nword:", nword)
    split_sugs = sc.get_split_suggestions(nword)
    if "எடுத்து கொண்டேன்" in split_sugs:
        print("Produced from split of:", nword)

