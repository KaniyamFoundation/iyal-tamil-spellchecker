import json
import urllib.request
import urllib.parse
from pathlib import Path
import time
import re

def fetch_sparql(name, query):
    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "IyalFinalMaster/1.5 (tshrinivasan@gmail.com)",
        "Accept": "application/sparql-results+json"
    }
    params = urllib.parse.urlencode({'query': query})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    
    print(f"Fetching {name}...")
    try:
        time.sleep(2)
        with urllib.request.urlopen(req, timeout=35) as response:
            data = json.loads(response.read().decode())
            return [row['itemLabel']['value'] for row in data['results']['bindings']]
    except Exception as e:
        print(f"  Skipped {name}: {e}")
    return []

if __name__ == "__main__":
    # Complete Master Categories
    QUERIES = {
        "Countries_Capitals": "SELECT ?itemLabel WHERE { {?item wdt:P31 wd:Q6256.} UNION {?item wdt:P31 wd:Q51129.} SERVICE wikibase:label { bd:serviceParam wikibase:language 'ta'. } ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel)='ta') }",
        "World_Major_Cities": "SELECT ?itemLabel WHERE { ?item wdt:P31 wd:Q515. ?item wdt:P1082 ?pop. FILTER(?pop > 500000) SERVICE wikibase:label { bd:serviceParam wikibase:language 'ta'. } ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel)='ta') }",
        "TN_Places": "SELECT ?itemLabel WHERE { ?item wdt:P131* wd:Q1445. SERVICE wikibase:label { bd:serviceParam wikibase:language 'ta'. } ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel)='ta') } LIMIT 5000",
        "TN_Specifics": "SELECT ?itemLabel WHERE { {?item wdt:P31 wd:Q2385804.} UNION {?item wdt:P31 wd:Q4493.} ?item wdt:P131* wd:Q1445. SERVICE wikibase:label { bd:serviceParam wikibase:language 'ta'. } ?item rdfs:label ?itemLabel. FILTER(LANG(?itemLabel)='ta') } LIMIT 3000"
    }
    
    master_names = []
    for category, sparql in QUERIES.items():
        master_names.extend(fetch_sparql(category, sparql))
        
    unique_words = set()
    script_firewall = re.compile(r'[^\u0B80-\u0BFF\s]') 

    for full_name in master_names:
        clean_name = full_name.split(' (')[0].strip()
        words = clean_name.split()
        for w in words:
            w = w.strip(".,()\"'")
            if len(w) > 1 and not script_firewall.search(w):
                unique_words.add(w)
    
    # Manual high-value words often missed by Wikidata labels
    manual_boost = ["லண்டன்", "நியூயார்க்", "பாரிஸ்", "சிங்கப்பூர்", "மலேசியா", "இலங்கை", "நியூயார்க்"]
    unique_words.update(manual_boost)

    dest = Path("TamilinaiyaVaaniSpellcheckerPy/data/user_config/global_places.txt")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("# Master Global & TN Place Vocabulary\n")
        for w in sorted(list(unique_words)):
            f.write(f"{w}\n")
    
    print(f"\n✅ MASTER FETCH COMPLETE!")
    print(f"Final Count: {len(unique_words)} Atomized Tamil Words")
    print(f"File Saved: {dest}")
