import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    from app import load_resources
    import app as app_mod
    app_mod.res = load_resources()
    with app.test_client() as client:
        yield client


def test_derived_whitelist_words(client):
    """
    Test that words derived from base roots in the rightwordlist.txt
    resolve successfully as correct words across case layers.
    """
    payloads = [
        {"text": "அருட்கொடை"},
        {"text": "அருட்கொடைகள்"},
        {"text": "அருட்கொடையை"},
        {"text": "அருட்கொடைக்கு"},
        {"text": "அருட்கொடைகளுக்கு"},
        {"text": "அருட்கொடைகளில்"},
        {"text": "அருட்கொடைகளால்"},
        {"text": "அருட்கொடையினால்"},
        {"text": "அருட்கொடைகளினால்"},
        {"text": "அருட்கொடையிலிருந்து"},
        {"text": "அருட்கொடைகளிலிருந்து"},
        {"text": "அருட்கொடையின்"},
        {"text": "அருட்கொடைகளின்"},
        {"text": "அருட்கொடையோடு"},
        {"text": "அருட்கொடைகளோடு"},
        {"text": "சுரேஷ்"},
        {"text": "சுரேஷை"},
        {"text": "சுரேஷுக்கு"},
        {"text": "சுரேஷின்"},
        {"text": "சுரேஷோடு"},
        {"text": "சுரேஷால்"},
        {"text": "சுரேஷிலிருந்து"},
        {"text": "குர்ஆனாக"},
        {"text": "குர்ஆனாகவே"},
        {"text": "ஈஸ்ட்வுட்டை"},
        {"text": "ஈஸ்ட்வுட்டுக்கு"},
        {"text": "ஈஸ்ட்வுட்டில்"},
        {"text": "ஈஸ்ட்வுட்டிலிருந்து"},
        {"text": "ஈஸ்ட்வுட்டின்"},
        {"text": "ஈஸ்ட்வுட்டோடு"},
        {"text": "ஈஸ்ட்வுட்டால்"},
        {"text": "சோதனைரூட்டை"},
        {"text": "சோதனைரூட்டுக்கு"},
        {"text": "சோதனைரூட்டில்"},
        {"text": "சோதனைரூட்டின்"},
        {"text": "சோதனைரூட்டால்"},
        {"text": "சோதனைரூட்டை"},
        {"text": "சோதனைரூத்தை"},
        {"text": "சோதனைரூத்துக்கு"},
        {"text": "சோதனைரூத்தில்"},
        {"text": "சோதனைரூத்தின்"},
        {"text": "சோதனைரூத்தால்"},
        {"text": "சோதனைரூப்பைக்"},
        {"text": "சோதனைரூப்புக்கு"},
        {"text": "சோதனைரூப்பில்"},
        {"text": "சோதனைரூக்கை"},
        {"text": "சோதனைரூக்குக்கு"},
        {"text": "சோதனைரூக்கில்"},
        {"text": "சோதனைரூச்சை"},
        {"text": "சோதனைரூச்சுக்கு"},
        {"text": "சோதனைரூச்சில்"}






    ]
    
    for payload in payloads:


        res = client.post("/v1/spellcheck", json={"text": payload["text"]})
        data = json.loads(res.data)
        word_data = data["results"][0]
        assert word_data["correct"] is True, f"Failed to resolve morphology for: {payload['text']}"
