import pickle
import os
import sys

# Add root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from TamilinaiyaVanniSpellcheckerPy import TamilinaiyaVaaniData, TamilinaiyaVaaniSpellchecker

def test_bloom():
    print("Testing Bloom Filter...")
    with open(os.path.join(ROOT_DIR, "tamil_bloom.pkl"), "rb") as f:
        bloom = pickle.load(f)
    
    word = "தானாகவே"
    print(f"  '{word}' in bloom: {word in bloom}")

def test_vaani():
    print("\nTesting TamilinaiyaVaani Engine...")
    db_path = os.path.join(ROOT_DIR, "TamilinaiyaVanniSpellcheckerPy/data/DB.json")
    user_path = os.path.join(ROOT_DIR, "TamilinaiyaVanniSpellcheckerPy/data/User.txt")
    
    data = TamilinaiyaVaaniData(db_path)
    if data.load():
        data.load_user_data(user_path)
        checker = TamilinaiyaVaaniSpellchecker(data)
        
        words = ["தமழ்", "தானாகவே"]
        results = checker.validate_words(words)
        for word, res in zip(words, results):
            print(f"  Word: {word}, Result: {res}")

if __name__ == "__main__":
    test_bloom()
    test_vaani()
