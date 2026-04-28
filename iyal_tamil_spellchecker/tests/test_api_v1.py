import json
import pytest
import urllib.request
from pathlib import Path

def test_health(client):
    """Verify health endpoint is active"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "OK"

def test_apidocs_swagger(client):
    """Verify Swagger UI is loading correctly"""
    response = client.get('/apidocs/')
    assert response.status_code == 200
    assert b"swagger-ui" in response.data.lower()

def test_instrumentation_headers(client):
    """Verify X-Process-Time header exists and is valid"""
    response = client.post('/v1/spellcheck', json={"text": "வணக்கம்"})
    assert "X-Process-Time" in response.headers
    process_time = response.headers["X-Process-Time"]
    assert process_time.endswith("ms")
    # Extract number and ensure it's numeric
    time_val = process_time.replace("ms", "")
    assert time_val.isdigit()

def test_api_versioning_consistency(client):
    """Verify legacy and v1 routes return identical results for basic text"""
    text = "அவன் வந்தாள்"
    res_root = client.post('/spellcheck', json={"text": text})
    res_v1 = client.post('/v1/spellcheck', json={"text": text})
    
    assert res_root.status_code == 200
    assert res_v1.status_code == 200
    
    data_root = res_root.get_json()
    data_v1 = res_v1.get_json()
    
    # Compare results list (ignoring dynamic metrics if they changed in between)
    assert data_root["results"] == data_v1["results"]

def test_batch_mode(client):
    """Verify API handles lists of strings correctly"""
    text_list = ["வணக்கம்", "உலகே", "பிழைதிருத்தி"]
    response = client.post('/v1/spellcheck', json={"text": text_list})
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "batch_results" in data
    assert len(data["batch_results"]) == 3
    # Check if first result looks like a results dictionary
    assert "results" in data["batch_results"][0]

def test_grammar_pronoun_agreement(client):
    """Verify heuristic pronominal agreement logic"""
    # "அவன்" (He) + "வந்தாள்" (Came - Female) = Wrong
    text = "அவன் வந்தாள்"
    response = client.post('/v1/spellcheck', json={"text": text})
    data = response.get_json()
    
    # Find the entry for 'வந்தாள்'
    result_item = next((item for item in data["results"] if item["word"] == "வந்தாள்"), None)
    
    assert result_item is not None
    assert result_item["correct"] is False
    # Heuristic should suggest 'வந்தான்'
    assert "வந்தான்" in result_item["suggestions"]

def test_grammar_dot_spacing(client):
    """Verify missing space after dot detection"""
    text = "பதிவாகியுள்ளன.இதுகுறித்து"
    response = client.post('/v1/spellcheck', json={"text": text})
    data = response.get_json()
    
    # This specifically checks for custom 'grammar' type errors in results
    result_item = next((item for item in data["results"] if item.get("type") == "grammar"), None)
    
    assert result_item is not None
    assert " " in result_item["suggestions"][0]
    assert "பதிவாகியுள்ளன. இதுகுறித்து" in result_item["suggestions"]

def test_metrics_persistence(client):
    """Verify that metrics increment after processing words"""
    # Get initial metrics
    initial_res = client.get('/v1/metrics')
    initial_metrics = initial_res.get_json()
    initial_total = initial_metrics.get("total_words", 0)
    
    # Process some words
    client.post('/v1/spellcheck', json={"text": "தமிழ் இனிது"})
    
    # Get updated metrics
    updated_res = client.get('/v1/metrics')
    updated_metrics = updated_res.get_json()
    
    assert updated_metrics["total_words"] == initial_total + 2

@pytest.mark.skipif(not Path("/home/shrini/.config/systemd/user/languagetool.service").exists(), 
                    reason="LanguageTool service configuration not found")
def test_languagetool_integration(client):
    """Test if LanguageTool is reachable (if configured)"""
    try:
        # We don't check via client because it's an external call inside app.py
        # but we can check if it's responding on port 8081
        urllib.request.urlopen("http://localhost:8081/", timeout=2)
    except Exception:
        pytest.skip("LanguageTool server not reachable on localhost:8081")
    
    text = "அவன் வந்தாள்" # LT also catches this
    response = client.post('/v1/spellcheck', json={"text": text})
    data = response.get_json()
    
    # Check if grammar_errors list has content from LT
    # (Note: LT might return nothing if it's not well trained for this specific case, 
    # but usually it should)
    assert "grammar_errors" in data

def test_morphology_kutriyalugaram(client):
    """Verify Kutriyalugaram reverse-validation (Compound restoration)"""
    # படித்து + உணர்ந்தான் -> படித்துணர்ந்தான்
    word = "படித்துணர்ந்தான்"
    response = client.post('/v1/spellcheck', json={"text": word})
    data = response.get_json()
    assert data["results"][0]["correct"] is True

    # சென்று + அடைந்தார் -> சென்றடைந்தார்
    word = "சென்றடைந்தார்"
    response = client.post('/v1/spellcheck', json={"text": word})
    data = response.get_json()
    assert data["results"][0]["correct"] is True

def test_morphology_udampadumey(client):
    """Verify Udampadumey Sandhi Engine (உடம்படுமெய்)"""
    # செய்ய + என்றே -> செய்யவென்றே
    word = "செய்யவென்றே"
    response = client.post('/v1/spellcheck', json={"text": word})
    data = response.get_json()
    assert data["results"][0]["correct"] is True

def test_caching_performance(client):
    """Verify that repeated requests are significantly faster due to LRU/Bloom caching"""
    text = "தமிழ் மொழியின் சிறப்பு மிக்க வரலாறு மிக நீண்டது. " * 50 # Large sample
    
    # First run (Cold cache)
    res1 = client.post('/v1/spellcheck', json={"text": text})
    time1 = int(res1.headers["X-Process-Time"].replace("ms", ""))
    
    # Second run (Hot cache)
    res2 = client.post('/v1/spellcheck', json={"text": text})
    time2 = int(res2.headers["X-Process-Time"].replace("ms", ""))
    
    # Note: On CI/shared hosts, first run might be extremely fast too, but generally time2 < time1
    # or time2 should be extremely low (near O(1) loop)
    assert time2 <= time1
    assert time2 < 500 # Should be very fast regardless of text length if cached

def test_custom_overrides_priority(client):
    """Verify that user configurations (right/wrong/replacements) take precedence"""
    # 1. Test Wrongwordlist (Force fail even if it might be valid)
    # Assuming 'க' is in wrongwordlist.txt or we can use a known one
    # For now, we test the logic that results are added
    # We'll check if any word from res.blacklist fails
    
    # 2. Test Replacements
    # Logic: 'பஸ்' is mapped to 'பேருந்து' in replacements.txt
    text = "பஸ்"
    response = client.post('/v1/spellcheck', json={"text": text})
    data = response.get_json()
    # It should be wrong and suggest 'பேருந்து'
    assert data["results"][0]["correct"] is False
    assert "பேருந்து" in data["results"][0]["suggestions"]
