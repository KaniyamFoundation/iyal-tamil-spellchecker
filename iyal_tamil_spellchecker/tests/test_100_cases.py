import sys
import os
import time

# Add root directory to path
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

def run_comprehensive_tests():
    print("Loading TamilinaiyaVaani Engine for 100 Comprehensive Tests...")
    vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
    vd.load()
    sc = TamilinaiyaVaaniSpellchecker(vd)

    # test cases: (input_word, expected_suggestion_to_contain, category)
    # If expected == "correct", it implies the word is valid and needs no suggestions.
    test_cases = [
        # --- 1. Valid Words (Baseline) ---
        ("தமிழ்", "correct", "Baseline"),
        ("கணினி", "correct", "Baseline"),
        ("சமூக", "correct", "Baseline"),
        ("அரசு", "correct", "Baseline"),
        ("மாநகராட்சி", "correct", "Baseline"),
        ("உருவாக்கப்பட்ட", "correct", "Baseline"),
        ("பல்கலைக்கழகங்களில்", "correct", "Baseline"),
        ("அதிகாரிகள்", "correct", "Baseline"),
        ("முயன்றது", "correct", "Baseline"),
        ("வேண்டும்", "correct", "Baseline"),
        
        # --- 2. Passive Voice Enhancements (The Logic Fixes) ---
        ("உருவாக்கப்படுவார்", "correct", "Passive Voice"),
        ("உருவாக்கப்படும்", "correct", "Passive Voice"),
        ("உருவாக்கப்படுவது", "correct", "Passive Voice"),
        ("பதிவேற்றப்பட்டது", "correct", "Passive Voice"),
        ("அஞ்சப்படும்", "correct", "Passive Voice"),
        ("செய்யப்படும்", "correct", "Passive Voice"),
        ("எழுதப்படும்", "correct", "Passive Voice"),
        ("மதிப்பிடப்படும்", "correct", "Passive Voice"),
        ("கழிக்கப்படும்", "correct", "Passive Voice"),
        ("பார்க்கப்படும்", "correct", "Passive Voice"),

        # --- 3. Global Fragments added to DB.json ---
        ("எற்பட்டு", "ஏற்பட்டு", "Global DB Fragments"),
        ("எற்படும்", "ஏற்படும்", "Global DB Fragments"),
        ("ஜந்து", "ஐந்து", "Global DB Fragments"),
        ("ஜந்தொழில்", "ஐந்தொழில்", "Global DB Fragments"),
        ("பல்கலைக்கழங்களில்", "பல்கலைக்கழகங்களில்", "Global DB Fragments"),
        ("அறிக்கைகையின்", "அறிக்கையின்", "Global DB Fragments"),
        ("பாதிக்காதததை", "பாதிக்காததை", "Global DB Fragments"),
        ("முழுவதிற்கு", "முழுவதற்கு", "Global DB Fragments"),
        ("சுமூகமான", "சுமுகமான", "Global DB Fragments"),
        ("புழகத்த", "புழக்கத்த", "Global DB Fragments"),
        ("மணம்மிகு", "மணமிகு", "Global DB Fragments"),
        ("உள்ளுர்", "உள்ளூர்", "Global DB Fragments"),
        ("உள்ளுரில்", "உள்ளூரில்", "Global DB Fragments"),
        ("அமைப்படுவது", "அமைக்கப்படுவது", "Global DB Fragments"),
        ("சொத்துகலான", "சொத்துகளான", "Global DB Fragments"),
        ("பொருளாதாரகலான", "பொருளாதாரகளான", "Global DB Fragments"),
        ("உருவாக்கப்படட", "உருவாக்கப்பட", "Global DB Fragments"),
        ("பார்க்கப்படட", "பார்க்கப்பட", "Global DB Fragments"),
        ("பனீர்", "பன்னீர்", "Global DB Fragments"),
        ("பனீராக", "பன்னீராக", "Global DB Fragments"),

        # --- 4. User Config Replacements (replacements.txt) ---
        ("போலீஸ்", "காவல்துறை", "Targeted Replacements"),
        ("டிரைவர்", "ஓட்டுநர்", "Targeted Replacements"),
        ("கம்ப்யூட்டர்", "கணினி", "Targeted Replacements"),
        ("ஸ்கூல்", "பள்ளி", "Targeted Replacements"),
        ("பேங்க்", "வங்கி", "Targeted Replacements"),
        ("புக்", "புத்தகம்", "Targeted Replacements"),
        ("நியூஸ்", "செய்தி", "Targeted Replacements"),
        ("ரெண்டு", "இரண்டு", "Targeted Replacements"),
        ("இப்ப", "இப்பொழுது", "Targeted Replacements"),
        ("மனு", "விண்ணப்பம்", "Targeted Replacements"),
        ("லிங்க்", "இணைப்பு", "Targeted Replacements"),
        ("மீட்டிங்", "கூட்டம்", "Targeted Replacements"),
        ("ஏசி", "குளிர்சாதனம்", "Targeted Replacements"),
        ("வாட்ச்", "கடிகாரம்", "Targeted্ত্র"), # Typo handling text check
        ("நெனச்சு", "நினைத்து", "Targeted Replacements"),
        ("தேங்க்ஸ்", "நன்றி", "Targeted Replacements"),
        ("விபத்துக்குளாகின்ற", "விபத்துக்குள்ளாகின்ற", "Targeted Replacements"),
        ("சிசிச்சை", "சிகிச்சை", "Targeted Replacements"),
        ("உணவங்கள்", "உணவகங்கள்", "Targeted Replacements"),
        ("தவனை", "தவணை", "Targeted Replacements"),
        ("ஊடகவியளர்களுக்கும்", "ஊடகவியலாளர்களுக்கும்", "Targeted Replacements"),
        ("கையாலாகாதனத்தால்", "கையாலாகாத்தனத்தால்", "Targeted Replacements"),
        ("முயற்சித்தது", "முயன்றது", "Targeted Replacements"),
        ("முயற்சிக்கிறது", "முயல்கிறது", "Targeted Replacements"),
        ("வேண்டும", "வேண்டும்", "Targeted Replacements"),
        ("அமல்நடத்த", "அமல்படுத்த", "Targeted Replacements"),
        ("நியாமான", "நியாயமான", "Targeted Replacements"),
        
        # --- 5. Custom Word Splitting / Joined Words ---
        ("தமிழ்நாடுஅரசு", "தமிழ்நாடு அரசு", "Missing Spaces"),
        ("உள்ளாட்சிதேர்தல்", "உள்ளாட்சி தேர்தல்", "Missing Spaces"),
        ("பள்ளிமாணவர்கள்", "பள்ளி மாணவர்கள்", "Missing Spaces"),
        ("பிழையின்றிதமிழ்தாய்", "பிழையின்றி தமிழ்த்தாய்", "Missing Spaces & Faulty spelling"),
        ("செய்திகள்படிக்க", "செய்திகள் படிக்க", "Missing Spaces"),
        ("விளையாட்டுமைதானம்", "விளையாட்டு மைதானம்", "Missing Spaces"),
        ("வருவாய்த்துறை", "வருவாய்த் துறை", "Missing Spaces"),
        ("உலகவரலாறு", "உலக வரலாறு", "Missing Spaces"),
        ("மனிதஉரிமை", "மனித உரிமை", "Missing Spaces"),
        ("தொழில்நுட்பவளர்ச்சி", "தொழில்நுட்ப வளர்ச்சி", "Missing Spaces"),
    ]

    print(f"\nRunning {len(test_cases)} tests...\n")
    
    passed = 0
    failed = 0
    failed_cases = []

    start_time = time.time()
    
    for i, (word, expected, category) in enumerate(test_cases):
        res = sc.validate_words([word])
        
        code = res[0][0]
        sug_str = res[0][1]
        
        success = False
        if expected == "correct":
            if code == 0 and sug_str == "correct":
                success = True
        else:
            if code > 0 and expected in sug_str:
                success = True

        if success:
            passed += 1
            # print(f"[{i+1}/{len(test_cases)}] ✅ PASS | {word} -> {expected}")
        else:
            failed += 1
            failed_cases.append((word, expected, sug_str))
            print(f"[{i+1}/{len(test_cases)}] ❌ FAIL | Word: {word} | Expected: {expected} | Got: {sug_str}")

    end_time = time.time()

    print("\n" + "="*40)
    print("TEST SUITE RESULTS")
    print("="*40)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Time Taken:  {end_time - start_time:.2f} seconds")
    print("="*40)

    if failed > 0:
        print("\nReview of Failed Cases:")
        for w, e, g in failed_cases:
            print(f" - {w}: Wanted '{e}', but got '{g}'")

if __name__ == "__main__":
    run_comprehensive_tests()
