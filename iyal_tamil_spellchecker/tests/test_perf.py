import sys, os, time
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

# Create a list of 1000 words (with repeats)
words = ["படித்துணர்ந்தார்கள்", "கேட்டுணர்ந்தான்", "வந்திருக்கிறான்", "எடுத்தெறிந்தாள்"] * 250

t1 = time.time()
sc.validate_words(words)
t2 = time.time()
print(f"First run (1000 words): {t2-t1:.4f}s")

t1 = time.time()
sc.validate_words(words)
t2 = time.time()
print(f"Second run (cached): {t2-t1:.4f}s")
