import sys, os
sys.path.append(os.getcwd())
from app import load_resources, suggest_word

bloom, bk_tree, tamilinaiya_vaani_checker, custom_whitelist, custom_blacklist, custom_replacements = load_resources()

word = "கொடுத்துதவினான்"
is_correct = False
suggestions = []

if word in bloom:
    is_correct = True
    print("Found in bloom")

tamilinaiya_vaani_parinthu = tamilinaiya_vaani_checker.validate_words([word])
print("Vaani raw list:", tamilinaiya_vaani_parinthu)
tamilinaiya_vaani_results_map = {word: tamilinaiya_vaani_parinthu[0]}

if not is_correct and tamilinaiya_vaani_checker:
    v_res = tamilinaiya_vaani_results_map.get(word)
    print("Vaani res map:", v_res)
    if v_res:
        if v_res[1] == "correct":
            is_correct = True
        else:
            is_correct = False
            if v_res[1] and v_res[1] != "wrong":
                suggestions = v_res[1].split(",")

if not is_correct and not suggestions:
    suggestions = suggest_word(word)

if not is_correct and suggestions:
    if word in suggestions:
        is_correct = True
        suggestions = []
    else:
        suggestions = [s for s in suggestions if s != word]

print("FINAL is_correct:", is_correct)
print("FINAL suggestions:", suggestions)

