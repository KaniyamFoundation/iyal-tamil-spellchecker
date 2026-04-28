import urllib.request
import urllib.parse
import json

text = "கடைசி தொண்டன்"
data = urllib.parse.urlencode({'language': 'ta', 'text': text}).encode('utf-8')
try:
    req = urllib.request.Request('http://localhost:8081/v2/check', data=data)
    with urllib.request.urlopen(req, timeout=10) as res:
        lt_response = json.loads(res.read().decode('utf-8'))
        print("Matches found:", len(lt_response.get("matches", [])))
        for match in lt_response.get("matches", []):
            print(match.get("message"))
            print(match.get("replacements"))
except Exception as e:
    print("LT Server error:", e)
