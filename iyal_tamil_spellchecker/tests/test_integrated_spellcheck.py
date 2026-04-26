import json
import os
import sys

# Add root to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def test_spellcheck():
    client = app.test_client()
    
    test_cases = [
        {"text": "தானாகவே", "expected_correct": True, "desc": "Common word in Bloom filter"},
        {"text": "தமழ்", "expected_correct": False, "expected_suggestion": "தமிழ்", "desc": "TamilinaiyaVaani rule-based correction"},
        {"text": "ஒட்டுக", "expected_correct": True, "desc": "Word found in BK-tree should be correct"},
        {"text": "தமிழ்", "expected_correct": True, "desc": "Basic correct word"}
    ]
    
    print("Starting Integrated Spellcheck Tests...\n")
    
    for case in test_cases:
        print(f"Testing: {case['desc']} ('{case['text']}')")
        response = client.post('/spellcheck', json={"text": case['text']})
        data = json.loads(response.data)
        
        result = data['results'][0]
        word_correct = result['correct']
        suggestions = result.get('suggestions', [])
        
        if word_correct == case['expected_correct']:
            if not word_correct:
                if case['expected_suggestion'] in suggestions:
                    print(f"  SUCCESS: Correctly identified as wrong. Suggestion '{case['expected_suggestion']}' found.")
                else:
                    print(f"  FAILURE: Suggestion '{case['expected_suggestion']}' NOT found in {suggestions}")
            else:
                print(f"  SUCCESS: Correctly identified as correct.")
        else:
            print(f"  FAILURE: Expected correct={case['expected_correct']}, got {word_correct}")
        print("-" * 30)

if __name__ == "__main__":
    test_spellcheck()
