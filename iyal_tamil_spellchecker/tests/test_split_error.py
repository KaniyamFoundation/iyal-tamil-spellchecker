import sys
import os

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
import time

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "பிழையின்றிதமிழ்தாய்" # missing 'த்'
print(f"Testing validation for: {word}")

start = time.time()
res = sc.validate_words([word])
end = time.time()

print(res)
print(f"Time Taken: {end - start:.4f} seconds")
