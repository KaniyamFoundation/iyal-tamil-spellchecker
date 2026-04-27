import sys
import os

# Add root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from TamilinaiyaVaaniSpellcheckerPy import TamilinaiyaVaaniData, TamilinaiyaVaaniSpellchecker

def run_matrix():
    db_path = os.path.join(ROOT_DIR, "TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
    data = TamilinaiyaVaaniData(db_path)
    if not data.load():
        print("Failed to load DB")
        return

    checker = TamilinaiyaVaaniSpellchecker(data)
    
    test_words = [
        ("தமிழ்", True),
        ("வணக்கம்", True),
        ("தானாகவே", True),
        ("முழுமை", True),
        ("முழுமையாக்கப்பட்டது", True),
        ("முழுமையாக்கப்ப", False),
        ("அதன", False),
        ("வந்த", True),
        ("வந்த்", False),
        ("சென்ற", True),
        ("சென்ற்", False),
    ]
    
    print(f"{'Word':<20} | Expected | " + " | ".join([f"T{i}" for i in range(7)]))
    print("-" * 65)
    
    for word, expected in test_words:
        results = []
        for code in range(7):
            res = checker.checkword(word, code)
            marker = "✅" if res else "❌"
            # Highlight mismatch with expected
            if res != expected:
                marker = "⚠️" if res else "⭕" # ⚠️ means false positive, ⭕ means false negative
            results.append(marker)
        
        expected_marker = "CORR" if expected else "WRNG"
        print(f"{word:<20} | {expected_marker:<8} | " + " | ".join(results))

    print("\nLegend:")
    print("✅ Correct identification as correct")
    print("❌ Correct identification as wrong")
    print("⚠️ False Positive (Should be wrong, but marked correct)")
    print("⭕ False Negative (Should be correct, but marked wrong)")

if __name__ == "__main__":
    run_matrix()
