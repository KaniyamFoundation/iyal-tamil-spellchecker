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

def test_bktree_fallback_suggestions(client):
    """Test that BK Tree is called and provides suggestions when Bloom and Vaani miss."""
    with patch('app.res') as mock_res:
        mock_res.bloom = set()
        mock_res.whitelist = set()
        mock_res.blacklist = set()
        mock_res.replacements = {}
        
        class MockVaani:
            def validate_words(self, words):
                return [[0, "wrong"] for w in words]
        
        class MockBKTree:
            def find(self, word, distance):
                # Returns list of (distance, word) tuples
                return [(1, "தமிழ்"), (2, "அமிழ்")]
        
        mock_res.vaani = MockVaani()
        mock_res.bk_tree = MockBKTree()
        mock_res.bigrams = None # Disable bigram sorting
        
        response = client.post('/v1/spellcheck', json={"text": "தமழ்"})
        data = json.loads(response.data)
        
        assert data["results"][0]["correct"] is False
        assert "தமிழ்" in data["results"][0]["suggestions"]

def test_bktree_filters_bad_candidates(client):
    """Test that BK Tree suggestions filter out words with different starting chars."""
    with patch('app.res') as mock_res:
        mock_res.bloom = set()
        mock_res.whitelist = set()
        mock_res.blacklist = set()
        mock_res.replacements = {}
        
        class MockVaani:
            def validate_words(self, words):
                return [[0, "wrong"] for w in words]
        
        class MockBKTree:
            def find(self, word, distance):
                # 'அமிழ்' starts with 'அ' while target 'தமழ்' starts with 'த'
                # The suggest_word function drops words that don't share the first character
                return [(1, "தமிழ்"), (2, "அமிழ்")]
        
        mock_res.vaani = MockVaani()
        mock_res.bk_tree = MockBKTree()
        mock_res.bigrams = None
        
        response = client.post('/v1/spellcheck', json={"text": "தமழ்"})
        data = json.loads(response.data)
        
        suggestions = data["results"][0]["suggestions"]
        assert "தமிழ்" in suggestions
        assert "அமிழ்" not in suggestions # Should be filtered out due to w[0] == word[0] logic
