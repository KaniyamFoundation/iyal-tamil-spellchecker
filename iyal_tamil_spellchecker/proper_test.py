import sys, os
sys.path.append(os.getcwd())
from app import load_resources
res = load_resources()
s2 = res.vaani

for w in [
    "கண்டுகளித்தார்கள்", 
    "பார்த்தழித்தான்", 
    "வந்துசேர்ந்தான்", 
    "எடுத்துரைத்தான்", 
    "கொடுத்துதவினான்", 
    "எடுத்தெறிந்தாள்",
    "நின்றாடினாள்",
    "கற்றறிந்தேன்"
]:
    res = s2.validate_words([w])[0]
    print(f"{w}: {'VALID' if res[1] == 'correct' else 'INVALID -> ' + str(res)}")

for w in [
    "எழுந்திருக்கிறான்",
    "சென்றொழிந்தான்",
    "விட்டெறிந்தார்கள்",
    "சொல்லித்தொலைந்தான்",
    "பார்த்துருவானான்",
    "கேட்டுணர்ந்தான்",
    "உரத்துரைத்தான்",
    "படித்துணர்ந்தார்கள்"
]:
    res = s2.validate_words([w])[0]
    print(f"{w}: {'VALID' if res[1] == 'correct' else 'INVALID -> ' + str(res)}")
