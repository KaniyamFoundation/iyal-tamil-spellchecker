import pytest
import sys
import os
from pathlib import Path

# Add project root to sys.path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
