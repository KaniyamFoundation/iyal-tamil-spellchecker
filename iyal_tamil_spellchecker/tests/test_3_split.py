import sys
import os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்"
res = sc.validate_words([word])
print(f"Suggestions for {word}:")
print(res[0][1])
