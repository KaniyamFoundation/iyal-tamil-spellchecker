import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.urllib.request.urlopen')
def test_languagetool_integration_mocked(mock_urlopen, client):
    """Verify LanguageTool grammar check logic using a mock response."""
    # Create a mock response object that behaves like urllib response
    mock_response = MagicMock()
    
    # Simulate a typical LanguageTool JSON response
    mock_lt_json = {
        "software": {"name": "LanguageTool", "version": "6.5"},
        "language": {"name": "Tamil", "code": "ta"},
        "matches": [
            {
                "message": "Grammar mistake detected.",
                "shortMessage": "Grammar",
                "offset": 5,
                "length": 8,
                "replacements": [{"value": "வந்தான்"}],
                "context": {"text": "அவன் வந்தாள்"}
            }
        ]
    }
    
    mock_response.read.return_value = json.dumps(mock_lt_json).encode('utf-8')
    # Use context manager protocol for the mock response
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    response = client.post('/v1/spellcheck', json={"text": "அவன் வந்தாள்"})
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert "grammar_errors" in data
    assert len(data["grammar_errors"]) == 1
    
    error = data["grammar_errors"][0]
    assert error["word"] == "வந்தாள்"
    assert "வந்தான்" in error["suggestions"]
    assert error["message"] == "Grammar mistake detected."

@patch('app.urllib.request.urlopen')
def test_languagetool_timeout_mocked(mock_urlopen, client):
    """Verify application handles LanguageTool timeout gracefully."""
    import urllib.error
    # Simulate a timeout exception
    mock_urlopen.side_effect = Exception("Timeout")
    
    response = client.post('/v1/spellcheck', json={"text": "தமிழ் இனிது"})
    data = json.loads(response.data)
    
    assert response.status_code == 200
    # Should complete without crashing, grammar_errors should be empty
    assert "grammar_errors" in data
    assert len(data["grammar_errors"]) == 0
