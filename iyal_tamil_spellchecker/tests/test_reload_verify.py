import json
from app import app

def test_new_words():
    # This will trigger a fresh initialization of app.py globals
    client = app.test_client()
    words = ["பஸ்ஸில்", "டிக்கெட்டை"]
    
    print("Verifying Fresh Load of Overrides...")
    for word in words:
        response = client.post('/spellcheck', json={"text": word})
        data = json.loads(response.data)
        result = data['results'][0]
        print(f"Word: {word}, Correct: {result['correct']}, Suggestion: {result.get('suggestions')}")
        if not result['correct']:
            print(f"  SUCCESS: {word} is now correctly flagged.")
        else:
            print(f"  FAILURE: {word} is still marked as correct.")

if __name__ == "__main__":
    test_new_words()
