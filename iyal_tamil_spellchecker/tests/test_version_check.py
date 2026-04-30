import pytest
from app import app, VERSION_CACHE, get_cached_remote_version
import unittest.mock as mock
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_version_comparison_logic(client):
    """Verify that update_available is correctly calculated in the index route."""
    # We need to mock 'open' but ONLY for the 'version.txt' file.
    # Otherwise, Flask can't load the template.
    original_open = open
    def side_effect(path, *args, **kwargs):
        if str(path).endswith("version.txt"):
            return mock.mock_open(read_data="0.0.1").return_value
        return original_open(path, *args, **kwargs)

    with mock.patch("builtins.open", side_effect=side_effect):
        with mock.patch("app.get_cached_remote_version", return_value="0.0.2"):
            response = client.get("/")
            html = response.data.decode('utf-8')
            assert "புதிய பதிப்பு கிடைக்கிறது!" in html
            assert "0.0.2" in html
            assert "0.0.1" in html

def test_no_update_logic(client):
    """Verify that no update message is shown if versions match or local is higher."""
    original_open = open
    def side_effect_same(path, *args, **kwargs):
        if str(path).endswith("version.txt"):
            return mock.mock_open(read_data="0.0.5").return_value
        return original_open(path, *args, **kwargs)

    # Case 1: Same version
    with mock.patch("builtins.open", side_effect=side_effect_same):
        with mock.patch("app.get_cached_remote_version", return_value="0.0.5"):
            response = client.get("/")
            html = response.data.decode('utf-8')
            assert "புதிய பதிப்பு கிடைக்கிறது!" not in html

    def side_effect_higher(path, *args, **kwargs):
        if str(path).endswith("version.txt"):
            return mock.mock_open(read_data="0.0.6").return_value
        return original_open(path, *args, **kwargs)

    # Case 2: Local is higher
    with mock.patch("builtins.open", side_effect=side_effect_higher):
        with mock.patch("app.get_cached_remote_version", return_value="0.0.5"):
            response = client.get("/")
            html = response.data.decode('utf-8')
            assert "புதிய பதிப்பு கிடைக்கிறது!" not in html

def test_version_check_caching():
    """Verify that the remote version check is cached correctly."""
    with mock.patch("urllib.request.urlopen") as mock_url:
        # Use MagicMock for context manager support
        mock_response = mock.MagicMock()
        mock_response.read.return_value = b"1.2.3"
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response
        
        # Reset cache
        VERSION_CACHE["remote_version"] = None
        VERSION_CACHE["last_check"] = 0
        
        # First call should hit the network
        v1 = get_cached_remote_version()
        assert v1 == "1.2.3"
        assert mock_url.call_count == 1
        
        # Second call within interval should NOT hit the network
        v2 = get_cached_remote_version()
        assert v2 == "1.2.3"
        assert mock_url.call_count == 1

def test_version_check_failure_graceful():
    """Verify that version check failures don't crash the app."""
    with mock.patch("urllib.request.urlopen", side_effect=Exception("Network Down")):
        # Reset cache
        VERSION_CACHE["remote_version"] = None
        VERSION_CACHE["last_check"] = 0
        
        v = get_cached_remote_version()
        assert v is None
        # Verify it set a retry cooldown (last_check should be non-zero)
        assert VERSION_CACHE["last_check"] > 0
