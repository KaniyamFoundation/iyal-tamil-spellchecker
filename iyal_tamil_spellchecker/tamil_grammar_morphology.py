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
    
    # Suffix -உம் (e.g. 'ஹெலிகாப்டரும்')
    if word.endswith("ும்"):
        possible_roots.append(word[:-2])
        if word.endswith("ரும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("லும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("ளும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("னும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("மும்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("வும்"): possible_roots.append(word[:-3] + "வு")
    # Suffix -ஐ (e.g. 'ஹெலிகாப்டரை', 'புதுப்பொலிவை')
    elif word.endswith("ை"):
        if word.endswith("ரை"): possible_roots.append(word[:-2] + "்")
        if word.endswith("லை"): possible_roots.append(word[:-2] + "்")
        if word.endswith("ளை"): possible_roots.append(word[:-2] + "்")
        if word.endswith("னை"): possible_roots.append(word[:-2] + "்")
        if word.endswith("வை"):
            possible_roots.append(word[:-2] + "வு")
            possible_roots.append(word[:-2])
    # Suffix -க்கு / -உக்கு (e.g. 'ஹெலிகாப்டருக்கு')
    elif word.endswith("ுக்கு"):
        possible_roots.append(word[:-4])
        if word.endswith("ருக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("லுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("ளுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("னுக்கு"): possible_roots.append(word[:-5] + "்")
        if word.endswith("வுக்கு"): possible_roots.append(word[:-5] + "வு")
    # Suffix -இல் (e.g. 'ஹெலிகாப்டரில்')
    elif word.endswith("ில்"):
        if word.endswith("ரில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("லில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("ளில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("னில்"): possible_roots.append(word[:-3] + "்")
        if word.endswith("வில்"): possible_roots.append(word[:-3] + "வு")
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
