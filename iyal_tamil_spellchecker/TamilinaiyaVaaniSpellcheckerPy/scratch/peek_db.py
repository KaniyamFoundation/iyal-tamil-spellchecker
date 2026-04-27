import json

with open('/home/shrini/dev/others/Tamilinaiya-Spellchecker/python_port/data/DB.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
    db = data['DB']
    print("DB indices and types:")
    for i in range(len(db)):
        print(f"Index {i}: {type(db[i])} - size {len(db[i])}")
    
    # Peek Oword (Index 4)
    print("\nOword Peek:")
    for k in list(db[4].keys())[:5]:
        print(f"  {k}: {db[4][k]}")
        
    # Peek Eword (Index 3)
    print("\nEword Peek:")
    for k in list(db[3].keys())[:5]:
        print(f"  {k}: {len(db[3][k])} blocks")
        for b in range(len(db[3][k])):
             if db[3][k][b]:
                print(f"    Block {b}: {list(db[3][k][b].keys())[:3]}")
