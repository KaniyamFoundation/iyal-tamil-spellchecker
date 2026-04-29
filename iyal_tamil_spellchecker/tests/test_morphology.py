import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Trigger reloading to load the updated rightwordlist.txt
        client.get("/v1/metrics") 
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
        {"text": "குர்ஆனாகவே"}


    ]
    
    for payload in payloads:
        res = client.post("/v1/spellcheck", json={"text": payload["text"]})
        data = json.loads(res.data)
        word_data = data["results"][0]
        assert word_data["correct"] is True, f"Failed to resolve morphology for: {payload['text']}"
