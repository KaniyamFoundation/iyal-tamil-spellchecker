import sys
import os

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "உருவாக்கப்படட"
print("Without rule:")
print(sc.validate_words([word]))

# Add rule and test again
vd.gword["ப்படட"] = [{"t": "1", "w": "ப்பட"}]
sc = TamilinaiyaVaaniSpellchecker(vd)

print("\nWith rule 'ப்படட' -> 'ப்பட':")
print(sc.validate_words([word]))
