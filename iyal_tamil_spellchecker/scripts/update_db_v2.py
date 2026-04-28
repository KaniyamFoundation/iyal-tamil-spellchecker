import json
import os

DB_PATH = 'TamilinaiyaVaaniSpellcheckerPy/data/DB.json'

def update_db():
    print(f"Loading {DB_PATH}...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Updating dictionary...")
    # Add the new rule for passive voice suffix
    data['DB'][0]['ப்டும்'] = [{'t': '1', 'w': 'ப்படும்'}]
    
    # Also add the exact word from the user request just in case
    # although the suffix rule should cover it.
    data['DB'][0]['பயிற்றுவிக்கப்டும்'] = [{'t': '9', 'w': 'பயிற்றுவிக்கப்படும்'}]

    print("Saving updated database...")
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        # Use indent=2 to match original style if possible, 
        # but ensure_ascii=False is critical for Tamil characters
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully updated DB.json")

if __name__ == "__main__":
    update_db()
