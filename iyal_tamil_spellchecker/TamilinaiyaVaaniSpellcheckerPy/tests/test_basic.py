from db_loader import TamilinaiyaVaaniData
from spellchecker import TamilinaiyaVaaniSpellchecker

data = TamilinaiyaVaaniData('/home/shrini/dev/others/Tamilinaiya-Spellchecker/python_port/data/DB.json')
if data.load():
    print("Data loaded successfully.")
    checker = TamilinaiyaVaaniSpellchecker(data)
    
    test_words = ["அம்மா", "அம்மாவை", "தம்பி", "வாணி", "தமிழ்", "அமமா"]
    for word in test_words:
        res = checker.checkword(word, 0)
        print(f"Word: {word}, Valid: {res}")
else:
    print("Failed to load data.")
