import sys
import os

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
import time

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

# Manually test if fuzzy candidate gives correct split
candidates = sc.get_suggestions("பிழையின்றிதமிழ்தாய்")
found = set()
for c in candidates:
    res = sc.get_split_suggestions(c)
    for r in res:
        found.add(r)
        
print("Found using fuzzy splits:", list(found))

