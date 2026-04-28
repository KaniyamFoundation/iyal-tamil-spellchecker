import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

import time
for word in ["பார்த்தழித்தான்", "சாப்பிட்டழித்தான்", "எடுத்தெறிந்தாள்", "கண்டுகளித்தார்கள்", "கண்டுகளித்தார்", "கொடுத்துதவினான்", "பார்த்துகந்தான்"]:
    t1 = time.time()
    sugs = sc.validate_words([word])
    print(f"{word}: {sugs[0][0] == 0 and 'WRONG' or 'CORRECT'} (took {time.time()-t1:.2f}s)")
sugs = sc.get_split_suggestions("கொடுத்துதவினான்")
print("Split Suggestions:", sugs)
fuzzy = sc.get_suggestions("கொடுத்துதவினான்")[:5]
print("Fuzzy:", fuzzy)
