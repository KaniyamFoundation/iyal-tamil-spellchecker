import json
from app import app

def test_irandu_correction():
    client = app.test_client()
    word = "இரன்டு"
    
    print(f"Testing word: '{word}'")
    response = client.post('/spellcheck', json={"text": word})
    data = json.loads(response.data)
    result = data['results'][0]
    
    print(f"  Correct: {result['correct']}")
    print(f"  Suggestions: {result.get('suggestions')}")
    
    if not result['correct'] and "இரண்டு" in result.get('suggestions', []):
        print("  SUCCESS: 'இரன்டு' is now correctly flagged and has the right suggestion.")
    else:
        print("  FAILURE: Word is still marked as correct or suggestion is missing.")

if __name__ == "__main__":
    test_irandu_correction()
