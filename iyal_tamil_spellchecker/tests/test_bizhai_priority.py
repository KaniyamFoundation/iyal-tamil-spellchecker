import sys, os
sys.path.append(os.getcwd())
from TamilinaiyaVaaniSpellcheckerPy.spellchecker import TamilinaiyaVaaniSpellchecker
from TamilinaiyaVaaniSpellcheckerPy.db_loader import TamilinaiyaVaaniData

vd = TamilinaiyaVaaniData("TamilinaiyaVaaniSpellcheckerPy/data/DB.json")
vd.load()

class MyChecker(TamilinaiyaVaaniSpellchecker):
    def test_log(self, text):
        print(f"Testing: {text}")
        
    def add_parinthu(self, parinthu, i, w):
        super().add_parinthu(parinthu, i, w)

    def validate_words(self, mwords, opt=True, mode="list"):
        # We will override validate_words here to test the logic change
        parinthu = [[0, "wrong"] for _ in range(len(mwords))]
        ottran = [[0, 1] for _ in range(len(mwords))]
        
        for i in range(len(mwords)):
            word = mwords[i]
            ottran[i][0] = 0
            
            # (skip irrelevant setup for mock)
            if self.checkword(word, 0):
                ottran[i][0] = 1
                parinthu[i] = [0, "correct"]
                continue
                
            if opt and ottran[i][0] == 0:
                # 1. Direct Pure Split (Absolute Priority)
                pure_splits = self.get_split_suggestions(word)
                if pure_splits:
                    for sw in pure_splits:
                        self.add_parinthu(parinthu, i, sw)
                    if parinthu[i][0] > 0:
                        ottran[i][0] = 1
                    continue # SKIP ALL FUZZY LOGIC!
                    
                suggestions = self.get_suggestions(word)
                # ... same old fuzzy logic
                for nword in list(dict.fromkeys(suggestions)):
                    if self.checkword(nword, 7):
                        self.add_parinthu(parinthu, i, nword)
                    split_sugs = self.get_split_suggestions(nword)
                    for sw in split_sugs:
                        self.add_parinthu(parinthu, i, sw)
                        
                if parinthu[i][0] > 0:
                    ottran[i][0] = 1
                    
        return parinthu

sc = MyChecker(vd)
print(sc.validate_words(["பிழைகள்தானாகவே"])[0][1])
