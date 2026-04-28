import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker

@pytest.fixture(scope="module")
def vaani_engine():
    data = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
    if data.load():
        return TamilinaiyaVaaniSpellchecker(data)
    else:
        pytest.fail("Failed to load Vaani DB")

def test_vaani_direct_istamil(vaani_engine):
    assert vaani_engine.istamil("தமிழ்") is True
    assert vaani_engine.istamil("English") is False
    assert vaani_engine.istamil("தமிழ்English") is True # Contains Tamil

def test_vaani_direct_codeuyir(vaani_engine):
    # Tests internal uyir mapping logic
    assert vaani_engine.codeuyir("ாக") == "ஆக"
    assert vaani_engine.codeuyir("ிக") == "இக"
    assert vaani_engine.codeuyir("கா") == "அகா"

def test_vaani_direct_compound(vaani_engine):
    # Tests is_valid_compound directly
    assert vaani_engine.is_valid_compound("படித்துணர்ந்தான்") is True
    assert vaani_engine.is_valid_compound("செய்யவென்றே") is True
    
def test_vaani_direct_validate_words(vaani_engine):
    words = ["தமிழ்", "தமழ்"]
    results = vaani_engine.validate_words(words)
    assert results[0][1] == "correct" or results[0][0] > 0
    assert results[1][1] != "correct"
    assert "தமிழ்" in results[1][1]
