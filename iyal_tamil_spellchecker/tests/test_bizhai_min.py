import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

sugs = sc.get_split_suggestions("பிழைகள்தானாகவே")
print("Original suggestions:", sugs)

# apply min heuristic
if sugs:
    min_spaces = min(s.count(" ") for s in sugs)
    sugs = [s for s in sugs if s.count(" ") == min_spaces]
print("Filtered suggestions:", sugs)
