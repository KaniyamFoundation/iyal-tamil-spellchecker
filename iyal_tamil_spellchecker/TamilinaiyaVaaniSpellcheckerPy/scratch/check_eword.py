import json
import re

with open('/home/shrini/dev/others/Tamilinaiya-Spellchecker/python_port/data/DB.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()
    content = re.sub(r',\s*([\}\]])', r'\1', content)
    data = json.loads(content)
    eword = data['DB'][3]
    
    for code in ["W", "Y", "T"]:
        if code in eword:
            print(f"Code {code}: {type(eword[code])}")
            if isinstance(eword[code], list):
                print(f"  Length: {len(eword[code])}")
                for i, block in enumerate(eword[code]):
                    if block:
                        print(f"  Block {i} sample keys: {list(block.keys())[:5]}")
        else:
            print(f"Code {code} not in Eword")
