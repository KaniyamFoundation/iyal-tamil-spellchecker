import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "நீங்கள்தட்டச்சுசெய்யும்போதேபின்னணியில்"

# Try with default splits (3)
print("Splits=3:", sc.get_split_suggestions(word, max_splits=3))

# Try with 4 splits
print("Splits=4:", sc.get_split_suggestions(word, max_splits=4))

# Try with 5 splits
print("Splits=5:", sc.get_split_suggestions(word, max_splits=5))
