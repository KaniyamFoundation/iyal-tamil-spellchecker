import regex

def get_base_sandhi_word(word):
    """
    Checks if a word ends in a trailing sandhi consonant (க, ச, த, ப + ்)
    and returns the base word without the sandhi.
    """
    if regex.search(r'[கசதப]்$', word):
        return word[:-2]
    return None

def get_derived_viku_variants(word):
    """
    Strips common noun case suffixes and coordinating particles to identify potential roots.
    """
    possible_roots = []
    # Grantha Consonant Suffix Stripping (ஷ், ஸ், ஜ், ஹ்)
    # 1. Accusative (-ஐ e.g. சுரேஷை)
    if word.endswith("ஷை") or word.endswith("ஸை") or word.endswith("ஜை") or word.endswith("ஹை"):
        possible_roots.append(word[:-1] + "்")
    
    # 2. Dative (-உக்கு e.g. சுரேஷுக்கு)
    elif word.endswith("ஷுக்கு") or word.endswith("ஸுக்கு") or word.endswith("ஜுக்கு") or word.endswith("ஹுக்கு"):
        possible_roots.append(word[:-5] + "்")
        
    # 3. Genitive (-இன் e.g. சுரேஷின்)
    elif word.endswith("ஷின்") or word.endswith("ஸின்") or word.endswith("ஜின்") or word.endswith("ஹின்"):
        possible_roots.append(word[:-3] + "்")
        
    # 4. Comitative (-ோடு e.g. சுரேஷோடு)
    elif word.endswith("ஷோடு") or word.endswith("ஸோடு") or word.endswith("ஜோடு") or word.endswith("ஹோடு"):
        possible_roots.append(word[:-3] + "்")
        
    # 5. Instrumental (-ஆல் e.g. சுரேஷால்)
    elif word.endswith("ஷால்") or word.endswith("ஸால்") or word.endswith("ஜால்") or word.endswith("ஹால்"):
        possible_roots.append(word[:-3] + "்")
        
    # 6. Ablative (-இலிருந்து e.g. சுரேஷிலிருந்து)
    elif word.endswith("ஷிலிருந்து") or word.endswith("ஸிலிருந்து") or word.endswith("ஜிலிருந்து") or word.endswith("ஹிலிருந்து"):
        possible_roots.append(word[:-9] + "்")


    # Suffix -உம் (e.g. 'ஹெலிகாப்டரும்')
    elif word.endswith("ும்"):

        possible_roots.append(word[:-2])
        if word.endswith("ரும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("லும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("ளும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("னும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("மும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("வும்"): possible_roots.append(word[:-3] + "வு")
    # Suffix -ஐ (e.g. 'ஹெலிகாப்டரை', 'புதுப்பொலிவை')
    elif word.endswith("ை"):
        if word.endswith("களை"):
            possible_roots.append(word[:-3])
        elif word.endswith("யை"):
            possible_roots.append(word[:-2])
        elif word.endswith("ரை"): possible_roots.append(word[:-2] + "்")
        elif word.endswith("லை"): possible_roots.append(word[:-2] + "்")
        elif word.endswith("ளை"): possible_roots.append(word[:-2] + "்")
        elif word.endswith("னை"): possible_roots.append(word[:-2] + "்")
        elif word.endswith("வை"):
            possible_roots.append(word[:-2] + "வு")
            possible_roots.append(word[:-2])

    # Suffix -க்கு / -உக்கு (e.g. 'ஹெலிகாப்டருக்கு', 'அருட்கொடைக்கு')
    elif word.endswith("க்கு"):

        if word.endswith("களுக்கு"):
            possible_roots.append(word[:-7])
        possible_roots.append(word[:-4])
        if word.endswith("ருக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("லுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("ளுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("னுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("வுக்கு"): possible_roots.append(word[:-5] + "வு")

    # Suffix -இல் (e.g. 'ஹெலிகாப்டரில்')
    elif word.endswith("ில்"):
        if word.endswith("களில்"):
            possible_roots.append(word[:-5])
        if word.endswith("ரில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("லில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("ளில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("னில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("வில்"): possible_roots.append(word[:-3] + "வு")

    # Suffix -ஆல் (Instrumental Case)
    elif word.endswith("ஆல்") or word.endswith("னால்"):
        if word.endswith("களினால்"):
            possible_roots.append(word[:-7])
        elif word.endswith("யினால்"):
            possible_roots.append(word[:-6])
        elif word.endswith("களால்"):
            possible_roots.append(word[:-5])
        else:
            possible_roots.append(word[:-3])

    # Suffix -இருந்து / -இலிருந்து (Ablative Case)
    elif word.endswith("இருந்து") or word.endswith("ருந்து"):
        if word.endswith("களிலிருந்து"):

            possible_roots.append(word[:-11])
        elif word.endswith("யிலிருந்து"):
            possible_roots.append(word[:-10])
        elif word.endswith("இலிருந்து"):
            possible_roots.append(word[:-9])
        else:
            possible_roots.append(word[:-7])


    # Suffix -ஆக / -ஆகவே
    elif word.endswith("ாகவே") or word.endswith("யாகவே"):
        possible_roots.append(word[:-4] + "்")
        possible_roots.append(word[:-4])
    elif word.endswith("ாக") or word.endswith("யாக"):
        possible_roots.append(word[:-2] + "்")
        possible_roots.append(word[:-2])


    # Suffix -இன் / -உடைய (Genitive Case)

    elif word.endswith("இன்") or word.endswith("ன்") or word.endswith("உடைய"):
        if word.endswith("களுடைய"):
            possible_roots.append(word[:-6])
        elif word.endswith("உடைய"):
            possible_roots.append(word[:-4])
        elif word.endswith("களின்"):
            possible_roots.append(word[:-5])
        elif word.endswith("யின்"):
            possible_roots.append(word[:-4])
        else:
            possible_roots.append(word[:-3])



    # Suffix -ோடு / -ஒடு (Comitative Case)
    elif word.endswith("ோடு") or word.endswith("ஒடு"):
        if word.endswith("களோடு"):
            possible_roots.append(word[:-5])
        elif word.endswith("யோடு"):
            possible_roots.append(word[:-4])

    # Suffix -கள் (Plural)
    elif word.endswith("கள்"):
        possible_roots.append(word[:-3])



    return possible_roots

import urllib.request
import urllib.parse
import json

def find_spacing_errors(text):
    """
    Scans for missing spaces after a dot following a long Tamil word.
    """
    results = []
    spacing_matches = list(regex.finditer(r"(\p{Tamil}{5,})\.(\p{Tamil}+)", text))
    for match in spacing_matches:
        full_match = match.group(0)
        pre = match.group(1)
        post = match.group(2)
        
        results.append({
            "word": full_match,
            "correct": False,
            "suggestions": [pre + ". " + post],
            "type": "grammar",
            "message": "முற்றுப்புள்ளிக்குப் பின் இடைவெளி தேவை (Missing space after period)"
        })
    return results

def fetch_lt_grammar(text):
    """
    Communicates with local LanguageTool server to evaluate global structural errors.
    """
    grammar_errors = []
    try:
        data = urllib.parse.urlencode({'language': 'ta', 'text': text}).encode('utf-8')
        req = urllib.request.Request('http://localhost:8081/v2/check', data=data)
        with urllib.request.urlopen(req, timeout=45) as res_lt:
            lt_response = json.loads(res_lt.read().decode('utf-8'))
            for match in lt_response.get("matches", []):
                offset = match.get("offset")
                length = match.get("length")
                err_word = text[offset:offset+length]
                replacements = [r["value"] for r in match.get("replacements", [])]
                grammar_errors.append({
                    "word": err_word,
                    "suggestions": replacements,
                    "message": match.get("message", ""),
                    "shortMessage": match.get("shortMessage", "")
                })
    except Exception as e:
        print("LanguageTool API error:", e)
    return grammar_errors
