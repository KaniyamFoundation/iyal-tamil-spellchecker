import os
import sqlite3
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def test_essential_files_exist():
    """Verify all required data and config files are present"""
    required_files = [
        BASE_DIR / "tamil_bloom.pkl",
        BASE_DIR / "bk_tree.pkl",
        BASE_DIR / "metrics.json",
        BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "DB.json",
        BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "bigrams_lite.db",
    ]
    
    for file_path in required_files:
        assert file_path.exists(), f"Essential file missing: {file_path}"
        assert file_path.stat().st_size > 0, f"Essential file is empty: {file_path}"

def test_user_config_structure():
    """Verify user configuration directory and files"""
    config_dir = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "user_config"
    assert config_dir.is_dir(), "User config directory missing"
    
    config_files = [
        "rightwordlist.txt",
        "wrongwordlist.txt",
        "replacements.txt",
        "vulgar_splits.txt"
    ]
    
    for cf in config_files:
        p = config_dir / cf
        assert p.exists(), f"Config file missing: {cf}"

def test_bigram_db_integrity():
    """Verify the bigram SQLite database is valid"""
    db_path = BASE_DIR / "TamilinaiyaVaaniSpellcheckerPy" / "data" / "bigrams_lite.db"
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        # Check if the expected table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bigrams'")
        assert cursor.fetchone() is not None, "Table 'bigrams' not found in database"
        conn.close()
    except Exception as e:
        assert False, f"Bigram DB integrity check failed: {e}"

def test_languagetool_service_running():
    """Verify LanguageTool is responding on port 8081"""
    # This is a requirement for grammar checking
    try:
        url = "http://localhost:8081/v2/languages"
        response = urllib.request.urlopen(url, timeout=2)
        assert response.status == 200, f"LanguageTool returned status {response.status}"
    except Exception as e:
        assert False, f"LanguageTool service is NOT running on localhost:8081. Error: {e}"
