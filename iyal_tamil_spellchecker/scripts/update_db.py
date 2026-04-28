import json
import os

DB_PATH = 'TamilinaiyaVaaniSpellcheckerPy/data/DB.json'

def add_rule(wrong_term, right_term, type_code="1", target_index=0):
    """
    Safely adds a rule to the large DB.json file.
    wrong_term: The incorrect fragment/word.
    right_term: The suggested correction.
    type_code: '1' for suffix, '0' for base, '9' for special.
    target_index: 0 for gword, 4 for oword.
    """
    print(f"Loading {DB_PATH}...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Adding rule: {wrong_term} -> {right_term} (Type {type_code})")
    data['DB'][target_index][wrong_term] = [{'t': type_code, 'w': right_term}]

    print("Saving updated database...")
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully updated DB.json")

if __name__ == "__main__":
    # Example usage for adding more rules:
    # add_rule("wrong", "right", "1")
    pass
