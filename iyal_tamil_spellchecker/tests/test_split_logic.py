import sys
import os
import time

sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def run_split_tests():
    print("Loading Dictionary for Split-Logic testing...\n")
    vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
    vd.load()
    sc = TamilinaiyaVaaniSpellchecker(vd)
    
    # These are specific concatenations to robustly test the logic.
    test_cases = [
        ("தமிழ்நாடுஅரசு", "தமிழ்நாடு அரசு"),
        ("பிழையின்றிதமிழ்தாய்", "பிழையின்றி தமிழ்த்தாய்"), # Tests fuzzy error + missing space combined!
        ("இன்றுமழை", "இன்று மழை"),
        ("காலைஉணவு", "காலை உணவு"),
        ("நான்செல்கிறேன்", "நான் செல்கிறேன்"),
        ("மதுரைக்குசென்றான்", "மதுரைக்கு சென்றான்"),
        ("புத்தகம்வாசித்தான்", "புத்தகம் வாசித்தான்"),
        ("கணினிஅறிவியல்", "கணினி அறிவியல்"),
        ("உலகவரலாறு", "உலக வரலாறு"),
        ("தொழில்நுட்பவளர்ச்சி", "தொழில்நுட்ப வளர்ச்சி"),
        ("செய்திகள்படிக்க", "செய்திகள் படிக்க"),
        ("மனிதஉரிமை", "மனித உரிமை"),
        ("சென்னைமாநகர", "சென்னை மாநகர"),
        ("பள்ளிமாணவர்கள்", "பள்ளி மாணவர்கள்"),
        ("நீதிமன்றவழக்கு", "நீதிமன்ற வழக்கு"),
        ("அங்கிங்கெனாதபடிஎங்கும்பிரகாசமாய்", "அங்கிங்கெனாதபடி எங்கும் பிரகாசமாய்"),
    ]
    
    passed = 0
    print("="*50)
    for word, expected in test_cases:
        res = sc.validate_words([word])
        sug_str = res[0][1]
        
        if expected in sug_str:
            passed += 1
            print(f"✅ PASS | {word} >> Suggested: {expected}")
        else:
            print(f"❌ FAIL | {word} >> Expected: '{expected}' | Generated: '{sug_str}'")
            
    print("="*50)
    print(f"Split Logic Test Score: {passed}/{len(test_cases)}")

if __name__ == '__main__':
    run_split_tests()
