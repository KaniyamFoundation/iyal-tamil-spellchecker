import sys, os, time
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

# Typos trigger expensive suggestions
words = ["படித்துணர்ந்தார்கள", "கேட்டுணர்ந்தா"] * 50

t1 = time.time()
sc.validate_words(words)
t2 = time.time()
print(f"First run (100 typos): {t2-t1:.4f}s")

t1 = time.time()
sc.validate_words(words)
t2 = time.time()
print(f"Second run (cached): {t2-t1:.4f}s")
