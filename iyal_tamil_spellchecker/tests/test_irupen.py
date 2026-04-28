import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "இருப்பேண்டா"
print("Validation:", sc.validate_words([word]))
print("Split Suggestions:", sc.get_split_suggestions(word))
print("is_valid இருப்:", sc.checkword("இருப்", 7) or sc.checkword("இரு", 7))
print("is_valid பேண்ட:", sc.checkword("பேண்ட", 7))
print("is_valid பேண்டா?", sc.checkword("பேண்டா", 7))
print("is_valid இருப்பேண்டா?", sc.checkword("இருப்பேண்டா", 0))

