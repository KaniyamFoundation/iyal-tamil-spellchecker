import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

def is_valid_compound_new(self, word):
    if len(word) < 4: return False
    mapping = {
        "": "அ", "\u0bbe": "ஆ", "\u0bbf": "இ", "\u0bc0": "ஈ", "\u0bc1": "உ", "\u0bc2": "ஊ",
        "\u0bc6": "எ", "\u0bc7": "ஏ", "\u0bc8": "ஐ", "\u0bca": "ஒ", "\u0bcb": "ஓ", "\u0bcc": "ஔ"
    }
    kutri_cons = ['க', 'ச', 'ட', 'த', 'ப', 'ற']
    
    for i in range(1, len(word)):
        p1_prefix = word[:i]
        p2_suffix = word[i:]
        
        # 1. Udampadumey
        if self.checkword(p1_prefix, 0):
            if p2_suffix:
                first_char = p2_suffix[0]
                if first_char in ['வ', 'ய']:
                    modifier = ""
                    if len(p2_suffix) > 1 and p2_suffix[1] in mapping:
                        modifier = p2_suffix[1]
                    vowel = mapping.get(modifier)
                    if vowel:
                        pure_p2 = vowel + (p2_suffix[2:] if modifier else p2_suffix[1:])
                        if self.checkword(pure_p2, 0):
                            return True
                            
        # 2. Kutriyalugaram
        char = word[i]
        if char in kutri_cons:
            modifier = ""
            if i + 1 < len(word) and word[i+1] in mapping:
                modifier = word[i+1]
            vowel = mapping.get(modifier)
            
            p1 = p1_prefix + char + "ு"
            p2 = vowel + (word[i+2:] if modifier else word[i+1:])
            
            if self.checkword(p1, 0) and self.checkword(p2, 0):
                return True
    return False

TamilinaiyaVaaniSpellchecker.is_valid_compound = is_valid_compound_new

test_words = [
    "படித்துணர்ந்தார்கள்",
    "கேட்டுணர்ந்தான்",
    "பார்த்தழித்தான்",
    "உரத்துரைத்தான்",
    "வந்திருக்கிறான்",
    "எடுத்தெறிந்தாள்"
]

for w in test_words:
    res = sc.is_valid_compound(w)
    print(f"{w}: {res}")

