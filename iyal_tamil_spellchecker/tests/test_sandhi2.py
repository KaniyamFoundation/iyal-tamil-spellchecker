import sys, os, re
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

def is_valid(w):
    if sc.checkword(w, 7): return True
    if re.search(r'[கசதப]்$', w):
        return sc.checkword(w[:-2], 7)
    return False

print("தானாகவேக்", is_valid("தானாகவேக்"))
print("கோடிட்டுக்", is_valid("கோடிட்டுக்"))
