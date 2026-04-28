import sys, os
sys.path.append(os.getcwd())
from app import load_resources

bloom, bk_tree, tamilinaiya_vaani_checker, custom_whitelist, custom_blacklist, custom_replacements = load_resources()

word = "கொடுத்துதவினான்"
print("In custom_whitelist?", word in custom_whitelist)
print("In bloom?", word in bloom)
print("Validate_words:", tamilinaiya_vaani_checker.validate_words([word]))
print("Checkword given 0:", tamilinaiya_vaani_checker.checkword(word, 0))
print("Is valid compound:", tamilinaiya_vaani_checker.is_valid_compound(word))
