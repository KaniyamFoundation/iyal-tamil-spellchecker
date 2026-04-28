import os
import re

def full_replace():
    # We want to replace standalone "Vaani" with "Vaani"
    # But NOT if it's already "Vaani"
    # Pattern: Look for "Vaani" NOT preceded by "Tamilinaiya"
    pattern = re.compile(r'(?<!Tamilinaiya)Vaani', re.IGNORECASE)
    
    files_to_update = [
        "app.py",
        "CHANGES.md",
        "docs/progress.md",
        "docs/architecture.md",
        "docs/project_context.md",
        "docs/tamilinaiyavaani_integration.md",
        "TamilinaiyaVaaniSpellcheckerPy/data/data_dictionary.md",
        "tests/test_components.py",
        "tests/test_integrated_spellcheck.py",
        "tests/test_vaani_engine.py",
        "scripts/update_db.py"
    ]
    
    for relative_path in files_to_update:
        if os.path.exists(relative_path):
            print(f"Updating {relative_path}...")
            with open(relative_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace while preserving case of the match if possible, 
            # but usually they are "Vaani" or "vaani"
            new_content = pattern.sub("Vaani", content)
            
            if new_content != content:
                with open(relative_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  Done.")
            else:
                print(f"  No changes needed.")

if __name__ == "__main__":
    full_replace()
