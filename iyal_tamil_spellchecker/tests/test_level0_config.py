import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, load_resources

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_whitelist_forces_correct(client):
    """Test if a word in rightwordlist bypasses normal checks."""
    # Assuming 'கண்டுகளித்தார்கள்' is in rightwordlist, or we mock it.
    # We will test the API directly which uses the loaded resources.
    # To be perfectly deterministic, let's mock the resource load just for this request 
    # or rely on the actual API logic that we know works.
    
    # We will test the API and patch the resources inside `app.res`
    with patch('app.res') as mock_res:
        mock_res.whitelist = {"பொய்வார்த்தை"}
        mock_res.blacklist = set()
        mock_res.replacements = {}
        mock_res.bloom = set()
        class MockBKTree:
            def find(self, *args, **kwargs):
                return []
        mock_res.vaani = None
        mock_res.bk_tree = MockBKTree()
        mock_res.bigrams = None
        
        response = client.post('/v1/spellcheck', json={"text": "பொய்வார்த்தை"})
        data = json.loads(response.data)
        assert data["results"][0]["correct"] is True

def test_blacklist_forces_wrong(client):
    """Test if a word in wrongwordlist forces failure."""
    with patch('app.res') as mock_res:
        # even if it's in bloom, blacklist should fail it
        mock_res.blacklist = {"தவறு"}
        mock_res.whitelist = set()
        mock_res.replacements = {}
        mock_res.bloom = {"தவறு"}
        class MockBKTree:
            def find(self, *args, **kwargs):
                return []
        mock_res.vaani = None
        mock_res.bk_tree = MockBKTree()
        mock_res.bigrams = None
        
        response = client.post('/v1/spellcheck', json={"text": "தவறு"})
        data = json.loads(response.data)
        assert data["results"][0]["correct"] is False

def test_replacements_exact_match(client):
    """Test if replacements strictly map word to suggestions."""
    with patch('app.res') as mock_res:
        mock_res.replacements = {"பஸ்": ["பேருந்து"]}
        mock_res.blacklist = set()
        mock_res.whitelist = set()
        mock_res.bloom = set()
        class MockBKTree:
            def find(self, *args, **kwargs):
                return []
        mock_res.vaani = None
        mock_res.bk_tree = MockBKTree()
        mock_res.bigrams = None
        
        response = client.post('/v1/spellcheck', json={"text": "பஸ்"})
        data = json.loads(response.data)
        assert data["results"][0]["correct"] is False
        assert "பேருந்து" in data["results"][0]["suggestions"]
