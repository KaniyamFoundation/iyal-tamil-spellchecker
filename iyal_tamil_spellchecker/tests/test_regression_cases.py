import pytest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, load_resources

@pytest.fixture(autouse=True)
def unmock_resources():
    """Ensure previous tests' MagicMocks don't pollute global app.res"""
    import app
    app.res = load_resources()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_initials_dot_spacing(client):
    """Verify எஸ்.ஐ.ஆர் is not aggressively space-flagged."""
    import app
    app.res = load_resources()
    response = client.post('/v1/spellcheck', json={"text": "எஸ்.ஐ.ஆர்"})
    data = json.loads(response.data)
    # It should either be completely True or not flagged for spaces
    for r in data["results"]:
        if r["word"] == "எஸ்.ஐ.ஆர்":
            assert r.get("correct") is True

@pytest.mark.parametrize("word", [
    "தான்", "படுத்திய", "வேண்டுமா", "ஒரே", "பகுதிய", 
    "தீர்ந்து", "இவரது", "தனது", "அதிகாரிகளின்", 
    "பிடித்துக்", "வரலாறே", "செய்ய", "ஆயுதமாகிப்", "வண்ணமேற்றி"
])
def test_valid_common_words_pass(client, word):
    """Ensure common valid words pass checks without false flags."""
    import app
    app.res = load_resources()
        
    response = client.post('/v1/spellcheck', json={"text": word})
    data = json.loads(response.data)
    assert data["results"][0]["correct"] is True

def test_spoken_dialect_correction(client):
    """Verify சமைச்சாலும் suggests the formal சமைத்தாலும்."""
    import app
    app.res = load_resources()
    response = client.post('/v1/spellcheck', json={"text": "சமைச்சாலும்"})
    data = json.loads(response.data)
    assert data["results"][0]["correct"] is False
    assert "சமைத்தாலும்" in data["results"][0]["suggestions"]
    # Ensure it's not exclusively returning bad space splits
    assert "சமைச் சாலும்" not in data["results"][0]["suggestions"]

def test_typo_correction_over_splits(client):
    """Verify typo correction replaces lucky space splits."""
    import app
    app.res = load_resources()
    response = client.post('/v1/spellcheck', json={"text": "ஆண்கலைப்"})
    data = json.loads(response.data)
    assert data["results"][0]["correct"] is False
    assert "ஆண்களைப்" in data["results"][0]["suggestions"]
    assert "ஆண் கலைப்" not in data["results"][0]["suggestions"]

def test_deep_fuzzy_correction(client):
    """Verify long words find distant typo fixes (distance 3)."""
    import app
    app.res = load_resources()
    response = client.post('/v1/spellcheck', json={"text": "விட்டுக்கொடுகாத்"})
    data = json.loads(response.data)
    assert data["results"][0]["correct"] is False
    # Catching 'விட்டுக்கொடுக்க'
    assert any("விட்டுக்கொடுக்க" in s for s in data["results"][0]["suggestions"])
