from db_loader import TamilinaiyaVaaniData
from spellchecker import TamilinaiyaVaaniSpellchecker

data = TamilinaiyaVaaniData('/home/shrini/dev/others/Tamilinaiya-Spellchecker/python_port/data/DB.json')
if data.load():
    print("Data loaded successfully.")
    checker = TamilinaiyaVaaniSpellchecker(data)
    
    test_words = ["அம்ம", "அமமா", "தமிழ்", "தமழ்"]
    results = checker.validate_words(test_words)
    
    for word, res in zip(test_words, results):
        status = "Correct" if res[1] == "correct" else "Wrong"
        suggestions = res[1] if status == "Wrong" else "-"
        print(f"Word: {word:10} Status: {status:10} Suggestions: {suggestions}")
else:
    print("Failed to load data.")
