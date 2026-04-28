import sys, os, urllib.request, json
import urllib.parse

words_to_test = [
    "வந்திருக்கிறான்",
    "கற்றறிந்தேன்",
    "பத்தாயிரம்",
    "சுற்றுப்பயணம்",
    "விட்டெறிந்தான்",  # விட்டு + எறிந்தான்
    "நின்றாடினாள்", # நின்று + ஆடினாள்
    "கேட்டுக்கொண்டான்",
    "கண்டுபிடித்தான்",
    "பார்த்திருந்தேன்", # இது இகரம்? பார்த்து + இருந்தேன் = பார்த்திருந்தேன். 'பார்த்து' -> த் + உ.
    "சொல்லியிருந்தாள்", # சொல்லி + இருந்தாள் = சொல்லியிருந்தாள் (not kutriyalugaram, that's udampadumey ய்)
    "எடுத்துரைத்தான்", # எடுத்து + உரைத்தான்
    "சென்றடைந்தார்", # சென்று + அடைந்தார்
    "படித்துணர்ந்தான்" # படித்து + உணர்ந்தான்
]

def check(word):
    data = json.dumps({"text": word}).encode('utf-8')
    req = urllib.request.Request('http://localhost:5001/spellcheck', data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        response = json.loads(res.read().decode('utf-8'))
        results = response.get("results", [])
        if results and not results[0]["correct"]:
            return results[0]["suggestions"]
        return "CORRECT"

for w in words_to_test:
    print(f"{w}: {check(w)}")

