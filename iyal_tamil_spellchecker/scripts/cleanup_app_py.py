import os

def fix_double_names():
    target_file = "app.py"
    if not os.path.exists(target_file):
        return
        
    print(f"Cleaning up {target_file}...")
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define replacements to fix the "double name" issue and standardize to tamilinaiyavaani
    replacements = {
        "tamilinaiya_Vaani_data": "tamilinaiya_vaani_data",
        "TAMILINAIYA_Vaani_DB_PATH": "TAMILINAIYA_VAANI_DB_PATH",
        "TAMILINAIYA_Vaani_USER_PATH": "TAMILINAIYA_VAANI_USER_PATH",
        "tamilinaiya_Vaani_checker": "tamilinaiya_vaani_checker",
        "tamilinaiya_Vaani_results_map": "tamilinaiya_vaani_results_map",
        "tamilinaiya_Vaani_parinthu": "tamilinaiya_vaani_parinthu"
    }
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
    
    if new_content != content:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully cleaned up app.py")

if __name__ == "__main__":
    fix_double_names()
