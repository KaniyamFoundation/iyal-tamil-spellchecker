import sys, os
sys.path.append(os.getcwd())

# Setup 1: via standalone logic
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
v1 = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
v1.load()
s1 = TamilinaiyaVaaniSpellchecker(v1)

# Setup 2: via app.py loader
from app import load_resources
res = load_resources()
b = res.bloom
bt = res.bk_tree
s2 = res.vaani
w = res.whitelist
b2 = res.blacklist
r = res.replacements

w = "கொடுத்துதவினான்"
print("S1:", s1.checkword(w, 0))
print("S2:", s2.checkword(w, 0))
