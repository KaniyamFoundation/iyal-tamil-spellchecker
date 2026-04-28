import sys, os, urllib.request, json

test_words = [
    "படித்துணர்ந்தார்கள்",
    "கேட்டுணர்ந்தான்",
    "பார்த்தழித்தான்",
    "உரத்துரைத்தான்"
]

def check(word):
    data = json.dumps({"text": word}).encode('utf-8')
    req = urllib.request.Request('http://localhost:5001/spellcheck', data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            response = json.loads(res.read().decode('utf-8'))
            results = response.get("results", [])
            if results and results[0]["correct"]:
                return "CORRECT"
            else:
                return "WRONG"
    except Exception as e:
        return f"ERROR: {e}"

for w in test_words:
    print(f"{w}: {check(w)}")
