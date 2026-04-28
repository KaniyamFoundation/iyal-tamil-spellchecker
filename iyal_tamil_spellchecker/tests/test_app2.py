import sys, os
sys.path.append(os.getcwd())
from app import load_resources

res = load_resources()
bloom = res.bloom
bk_tree = res.bk_tree
tamilinaiya_vaani_checker = res.vaani
custom_whitelist = res.whitelist
custom_blacklist = res.blacklist
custom_replacements = res.replacements

word = "கொடுத்துதவினான்"
print("In custom_whitelist?", word in custom_whitelist)
print("In bloom?", word in bloom)
print("Validate_words:", tamilinaiya_vaani_checker.validate_words([word]))
print("Checkword given 0:", tamilinaiya_vaani_checker.checkword(word, 0))
print("Is valid compound:", tamilinaiya_vaani_checker.is_valid_compound(word))
