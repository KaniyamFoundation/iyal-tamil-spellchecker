from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

print("Check 'வண்ணமேற்றி':", sc.checkword("வண்ணமேற்றி", 0))
print("Is valid compound:", sc.is_valid_compound("வண்ணமேற்றி"))

print("Check 'வண்ணம்':", sc.checkword("வண்ணம்", 0))
print("Check 'ஏற்றி':", sc.checkword("ஏற்றி", 0))
print("Check 'வண்ணமே':", sc.checkword("வண்ணமே", 0))
print("Check 'ஏற்றி' in user_oword:", "ஏற்றி" in vd.user_oword)

