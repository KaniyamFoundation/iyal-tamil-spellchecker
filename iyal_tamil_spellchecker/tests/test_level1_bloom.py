import pytest
import os
import sys
from unittest.mock import patch
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_bloom_filter_fast_hit(client):
    """Test that if a word is in Bloom filter, it's marked correct without falling to Vaani."""
    with patch('app.res') as mock_res:
        mock_res.bloom = {"தமிழ்"}
        mock_res.whitelist = set()
        mock_res.blacklist = set()
        mock_res.replacements = {}
        
        class MockVaani:
            def checkword(self, *args, **kwargs):
                return False
            def validate_words(self, words):
                return [[0, "wrong"] for _ in words]
        
        mock_res.vaani = MockVaani()
        mock_res.bk_tree = None
        
        response = client.post('/v1/spellcheck', json={"text": "தமிழ்"})
        data = json.loads(response.data)
        assert data["results"][0]["correct"] is True

def test_bloom_filter_miss_falls_to_vaani(client):
    """Test that if a word misses Bloom filter, it falls back to Vaani."""
    with patch('app.res') as mock_res:
        mock_res.bloom = set() # Empty bloom
        mock_res.whitelist = set()
        mock_res.blacklist = set()
        mock_res.replacements = {}
        
        class MockVaani:
            def validate_words(self, words):
                # Return 'correct' for the test word
                return [[0, "correct"] if w == "புதியசொல்" else [0, "wrong"] for w in words]
        
        mock_res.vaani = MockVaani()
        mock_res.bk_tree = None
        
        response = client.post('/v1/spellcheck', json={"text": "புதியசொல்"})
        data = json.loads(response.data)
        assert data["results"][0]["correct"] is True
