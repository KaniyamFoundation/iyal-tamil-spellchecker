import json

DB_PATH = 'TamilinaiyaVaaniSpellcheckerPy/data/DB.json'

def graft_passive():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    eword = data['DB'][3]
    
    # 1. Add 'ப்படு' as a suffix for 'இ' verbs
    # Grafting to Devanagari 'द15' which is the code for stems ending in 'ப்படு'
    if 'இ' in eword:
        print("Grafting passive suffixes to 'இ' verbs...")
        eword['இ'][0]['ப்படு'] = '①U15'
        eword['இ'][0]['ப்படுவார்'] = '2'
        eword['இ'][0]['ப்படுவார்கள்'] = '2'
        eword['இ'][0]['ப்படுவது'] = '2'
    
    if 'ஆ' in eword:
         print("Grafting passive suffixes to 'ஆ' verbs...")
         eword['ஆ'][0]['ப்படு'] = '①U15'
         eword['ஆ'][0]['ப்படுவார்'] = '2'
         eword['ஆ'][0]['ப்படுவார்கள்'] = '2'
         eword['ஆ'][0]['ப்படுவது'] = '2'

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    graft_passive()
