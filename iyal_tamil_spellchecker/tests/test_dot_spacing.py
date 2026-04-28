import json
from app import app

def test_dot_spacing():
    client = app.test_client()
    
    # 1. Test Sentence Join (Should Fail)
    text1 = "பதிவாகியுள்ளன.இதுகுறித்து"
    print(f"Testing combined sentence: '{text1}'")
    response = client.post('/spellcheck', json={"text": text1})
    data = json.loads(response.data)
    found_error = any(r['word'] == text1 for r in data['results'])
    suggestion = next((r['suggestions'][0] for r in data['results'] if r['word'] == text1), None)
    print(f"  Flagged: {found_error}, Suggestion: {suggestion}")
    
    # 2. Test Abbreviation (Should be Fine - no grammar error for the whole string)
    text2 = "எஸ்.ஐ.ஆர்"
    print(f"Testing abbreviation: '{text2}'")
    response = client.post('/spellcheck', json={"text": text2})
    data = json.loads(response.data)
    found_error = any(r['word'] == text2 for r in data['results'])
    print(f"  Flagged as spacing error: {found_error}")

if __name__ == "__main__":
    test_dot_spacing()
