import os

def rename_imports():
    old_name = "TamilinaiyaVaaniSpellcheckerPy"
    new_name = "TamilinaiyaVaaniSpellcheckerPy"
    
    # We also want to replace "Vaani" (standalone) with "Vaani" in case I missed any
    # (But my previous script already did that for some files)
    
    for root, dirs, files in os.walk("."):
        # Skip some dirs
        if ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith((".py", ".md", ".org", ".txt", ".sh")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content.replace(old_name, new_name)
                    
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated imports/paths in {path}")
                except Exception as e:
                    print(f"Could not process {path}: {e}")

if __name__ == "__main__":
    rename_imports()
