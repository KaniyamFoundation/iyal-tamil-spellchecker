import urllib.request
import urllib.parse
import json

req = urllib.request.Request('http://localhost:5001/spellcheck', 
                             data=json.dumps({"text": "நான் வந்தான்"}).encode('utf-8'),
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as res:
    print(res.read().decode('utf-8'))
