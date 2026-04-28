import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()
sc = TamilinaiyaVaaniSpellchecker(vd)

word = "செய்யவென்றே"
print("செய்ய valid?", sc.checkword("செய்ய", 0))
print("வென்றே valid?", sc.checkword("வென்றே", 0))
print("என்றே valid?", sc.checkword("என்றே", 0))

# Try dynamic udampadumey split
split_p1 = "செய்ய"
split_p2 = "வென்றே"

vowel_map = {
    'வ': 'அ', 'வா': 'ஆ', 'வி': 'இ', 'வீ': 'ஈ', 'வு': 'உ', 'வூ': 'ஊ',
    'வெ': 'எ', 'வே': 'ஏ', 'வை': 'ஐ', 'வொ': 'ஒ', 'வோ': 'ஓ', 'வௌ': 'ஔ',
    'ய': 'அ', 'யா': 'ஆ', 'யி': 'இ', 'யீ': 'ஈ', 'யு': 'உ', 'யூ': 'ஊ',
    'யெ': 'எ', 'யே': 'ஏ', 'யை': 'ஐ', 'யொ': 'ஒ', 'யோ': 'ஓ', 'யௌ': 'ஔ',
}

# In pure strings: "வெ" is 'வ' \u0bb5 + 'ெ' \u0bc6
def get_vowel_equivalent(part2):
    # Map raw tamil consonant+vowel sequence to the pure vowel letter
    first_char = part2[0]
    if first_char not in ['வ', 'ய']: return None
    
    mapping = {
        "": "அ", "\u0bbe": "ஆ", "\u0bbf": "இ", "\u0bc0": "ஈ", "\u0bc1": "உ", "\u0bc2": "ஊ",
        "\u0bc6": "எ", "\u0bc7": "ஏ", "\u0bc8": "ஐ", "\u0bca": "ஒ", "\u0bcb": "ஓ", "\u0bcc": "ஔ"
    }
    
    modifier = ""
    if len(part2) > 1 and part2[1] in mapping:
        modifier = part2[1]
        
    vowel = mapping.get(modifier, None)
    if not vowel: return None
    
    # Construct the base word
    new_part2 = vowel + part2[1:] if modifier == "" else vowel + part2[2:]
    return new_part2

print("Converted:", get_vowel_equivalent("வென்றே"))
