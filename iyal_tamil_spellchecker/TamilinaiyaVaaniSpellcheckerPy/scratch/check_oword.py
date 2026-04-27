import json
import re

with open('/home/shrini/dev/others/Tamilinaiya-Spellchecker/python_port/data/DB.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()
    content = re.sub(r',\s*([\}\]])', r'\1', content)
    data = json.loads(content)
    oword = data['DB'][4]
    
    for word in ["அம்மா", "அம்", "தம்பி", "வாணி"]:
        if word in oword:
            print(f"{word}: {oword[word]}")
        else:
            print(f"{word} not in Oword")
