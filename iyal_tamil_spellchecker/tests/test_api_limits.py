import pytest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, LIMIT_SPELLCHECK

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ensure limiter is enabled during testing
    app.config['RATELIMIT_ENABLED'] = True
    
    with app.test_client() as client:
        yield client

def test_rate_limiting_429(client):
    """Verify that exceeding limits results in 429."""
    # We will simulate a user from an IP that is NOT whitelisted
    limit_count = int(LIMIT_SPELLCHECK.split()[0])
    
    for _ in range(limit_count):
        response = client.post(
            '/v1/spellcheck', 
            json={"text": "வணக்கம்"},
            environ_base={'REMOTE_ADDR': '192.168.1.100'} # Mock non-whitelisted IP
        )
        assert response.status_code == 200
        
    # The next one should hit the limit
    response = client.post(
        '/v1/spellcheck', 
        json={"text": "வணக்கம்"},
        environ_base={'REMOTE_ADDR': '192.168.1.100'}
    )
    assert response.status_code == 429
    data = json.loads(response.data)
    assert "error" in data
    assert "Too Many Requests" in data["error"]

def test_whitelist_bypasses_ratelimit(client):
    """Verify that 127.0.0.1 bypasses rate limits."""
    limit_count = int(LIMIT_SPELLCHECK.split()[0])
    
    # We hit it exactly limit_count + 2 times
    for _ in range(limit_count + 2):
        response = client.post(
            '/v1/spellcheck', 
            json={"text": "வணக்கம்"},
            environ_base={'REMOTE_ADDR': '127.0.0.1'} # Whitelisted IP
        )
        assert response.status_code == 200

def test_payload_too_large_413(client):
    """Verify that payloads exceeding 50,000 characters from non-whitelisted IP are rejected."""
    large_text = "அ " * 26000 # ~52,000 chars
    response = client.post(
        '/v1/spellcheck', 
        json={"text": large_text},
        environ_base={'REMOTE_ADDR': '192.168.1.101'}
    )
    assert response.status_code == 413
    data = json.loads(response.data)
    assert "உரை மிக நீளமானது" in data["error"]
