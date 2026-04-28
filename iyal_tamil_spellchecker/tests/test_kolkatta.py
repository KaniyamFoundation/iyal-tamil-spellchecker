import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

word = "கொல்கத்தாவுக்கு"
print("Length:", len(word))
print("Chars:", [c for c in word])
print("Unicode:", [hex(ord(c)) for c in word])

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

print("Validate_words:", sc.validate_words([word]))

# Correct spelling using pure compound "கொ"
correct_word = "கொல்கத்தாவுக்கு"
print("\nCorrect word Unicode:", [hex(ord(c)) for c in correct_word])
print("Validate_words (correct):", sc.validate_words([correct_word]))
