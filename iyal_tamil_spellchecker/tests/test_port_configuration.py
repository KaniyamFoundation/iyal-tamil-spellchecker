import pytest
from pathlib import Path

def test_app_port_configuration():
    """Ensure that the Flask development server always targets port 5000."""
    app_file = Path(__file__).parent.parent / "app.py"
    content = app_file.read_text(encoding="utf-8")
    
    # Verify that the port is explicitly set to 5000
    assert "port=5000" in content, "The application port should always be configured as 5000 in app.py before committing."


