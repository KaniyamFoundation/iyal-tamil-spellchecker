import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
import re

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "தானாகவேகோடிட்டுக்"
print("checkword தானாகவே:", sc.checkword("தானாகவே", 7))
print("checkword கோடிட்டுக்:", sc.checkword("கோடிட்டுக்", 7))
print("checkword கோடிட்டு:", sc.checkword("கோடிட்டு", 7))

sugs = sc.get_split_suggestions(word)
print("split suggestions:", sugs)
