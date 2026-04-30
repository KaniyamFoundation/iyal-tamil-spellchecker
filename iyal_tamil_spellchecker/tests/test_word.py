import sys
import os
import pickle
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy import TamilinaiyaVaaniData, TamilinaiyaVaaniSpellchecker



# Load resources
with open('tamil_bloom.pkl', 'rb') as f:

    bloom = pickle.load(f)

print("In Bloom:", 'தொடங்கும்போது' in bloom)

data = TamilinaiyaVaaniData('TamilinaiyaVaaniSpellcheckerPy/data/DB.json')
data.load()
v = TamilinaiyaVaaniSpellchecker(data)
print("In Vaani:", v.checkword('தொடங்கும்போது', 0))

