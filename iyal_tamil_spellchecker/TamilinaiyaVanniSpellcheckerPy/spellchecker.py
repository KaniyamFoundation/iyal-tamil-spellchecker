import re
import unicodedata
try:
    from .db_loader import TamilinaiyaVaaniData
except ImportError:
    from db_loader import TamilinaiyaVaaniData

class TamilinaiyaVaaniSpellchecker:
    def __init__(self, data: TamilinaiyaVaaniData):
        self.data = data
        self.peyar = "MLTYWNEIQOGDHVXBPSളவ"
        self.speyar = "CAJ"
        self.venai = "ஆலனசளணஇழஉஓடதदधபநमயரறवउपकतईटरलळएचஜ"
        self.nonderi = "Z"
        self.deri = self.peyar + self.speyar + self.venai + "FUKഡဂஜദப"
        
        self.vauyir = {"வா":"ஆ","வி":"இ","வீ":"ஈ","வு":"உ","வூ":"ஊ","வெ":"எ","வே":"ஏ","வை":"ஐ","வொ":"ஒ","வோ":"ஓ","வௌ":"ஒள"}
        self.yauyir = {"யா":"ஆ","யி":"இ","யீ":"ஈ","யு":"உ","யூ":"ஊ","யெ":"எ","யே":"ஏ","யை":"ஐ","யொ":"ஒ","யோ":"ஓ","யௌ":"ஒள"}
        self.auyir = {"ா":"ஆ","ி":"இ","ீ":"ஈ","ு":"உ","ூ":"ஊ","ெ":"எ","ே":"ஏ","ை":"ஐ","ொ":"ஒ","ோ":"ஓ","ௌ":"ஒள"}
        
        self.cacheword = []
        self.cachesug = []

    def istamil(self, aword):
        for a in aword:
            if 2944 <= ord(a) <= 3071:
                return True
        return False

    def codeuyir(self, part):
        if len(part) < 1:
            return part
        elu = part[0]
        if len(part) > 1:
            if elu in self.auyir:
                return part.replace(elu, self.auyir[elu], 1)
            # Check if it's a consonant that needs 'அ'
            if 2965 <= ord(elu) <= 2997:
                return "அ" + part
        return part

    def derivative(self, part, v, sv, sugges):
        if part is not None:
            if "①" in part or ("②" in part and sugges == 0):
                kudu = part[-3]
                elai = part[-2:]
                if self.checkviku(v, sv, "", kudu, elai, sugges):
                    return True
                if self.splitviku(sv, kudu, elai, sugges):
                    return True
            else:
                if sv == "":
                    return True
        return False

    def splitviku(self, viku, cod, scod, sugges):
        for c in range(1, len(viku)):
            subpaku = viku[:c]
            subviku = viku[c:]
            if self.checkviku("", subpaku, subviku, cod, scod, sugges):
                return True
        if self.checkviku("", "", viku, cod, scod, sugges):
            return True
        return False

    def checkviku(self, p, v, sv, c, sc, sugges):
        if c == "அ":
            if sv != "": return False
            secondword = p[-1:] + v if p else v
            sw = secondword
            if len(sw) >= 2:
                for d, val in self.vauyir.items():
                    if sw[:2] == d:
                        sw = sw.replace(d, val, 1)
                        break
                if sw.startswith("வ"):
                    sw = "அ" + sw[1:]
            if self.checkword(sw, 1):
                return True
            if sw != secondword:
                if self.checkword(secondword, 1):
                    return True
            return False

        if c == "ஆ":
            if sv != "": return False
            secondword = p[-1:] + v if p else v
            sw = secondword
            if len(sw) >= 2:
                for d, val in self.yauyir.items():
                    if sw[:2] == d:
                        sw = sw.replace(d, val, 1)
                        break
                if sw.startswith("ய"):
                    sw = "அ" + sw[1:]
            if self.checkword(sw, 1):
                return True
            if sw != secondword:
                if self.checkword(secondword, 1):
                    return True
            return False

        if c == "இ":
            if sv != "": return False
            secondword = p[-1:] + v if p else v
            return self.checkword(secondword, 1)

        if c == "உ":
            if sv != "": return False
            secondword = self.codeuyir(v)
            return self.checkword(secondword, 2)

        if c == "ஊ":
            if sv != "": return False
            secondword = p[-1:] + v if p else v
            return self.checkword(secondword, 2)

        if c == "எ":
            if sv != "": return False
            secondword = p[-1:] + v if p else v
            return self.checkword(secondword, 6)

        if v == "" and c in self.nonderi:
            return True

        blocks = ""
        if sc == "15": blocks = "01234567"
        elif sc == "25": blocks = "0123456"
        elif sc == "07": blocks = "012345"
        elif sc == "10": blocks = "01235"
        elif sc == "11": blocks = "012356"
        elif sc == "09": blocks = "02"
        elif sc == "06": blocks = "023"
        elif sc == "05": blocks = "013"
        elif sc == "04": blocks = "03"
        elif sc == "03": blocks = "13"
        elif sc == "02": blocks = "2"
        elif sc == "01": blocks = "1"
        elif sc == "16": blocks = "3"
        elif sc == "17": blocks = "0"
        elif sc == "08": blocks = "4"
        elif sc == "18": blocks = "4"
        elif sc == "19": blocks = "5"
        elif sc == "20": blocks = "6"
        elif sc == "21": blocks = "7"
        elif sc == "24": blocks = "34"

        for d in range(8):
            if str(d) not in blocks:
                continue
            try:
                # Eword[c][d][v]
                # self.data.Eword is a list of dictionaries per code
                # In C#, Eword[c] returns a list of dictionaries? No, it's dynamic.
                # Usually Eword is mapped by code.
                # Let's check how Eword is structured in the data.
                code_data = self.data.Eword.get(c)
                if code_data and len(code_data) > d:
                    v_part = code_data[d].get(v)
                    if v_part is not None:
                        if self.derivative(v_part, v, sv, sugges):
                            return True
            except:
                continue

        if sv == "" and v != "" and c in self.deri:
            if self.splitviku(v, c, sc, sugges):
                return True
        return False

    def checkword(self, sol, type_code):
        sugges = 1 if type_code == 7 else 0
        for a in range(len(sol), 0, -1):
            paku = sol[:a]
            viku = sol[a:]
            qcodes = self.data.Oword.get(paku)
            if qcodes:
                for b in qcodes:
                    if b.get('s') is not None:
                        return False
                    t = b.get('t', '')
                    if not t: continue
                    code = t[0]
                    subcode = t[1:]
                    
                    if type_code == 0: pass
                    elif type_code == 1:
                        if (code not in self.peyar or subcode != "15") and (code not in self.speyar): continue
                    elif type_code == 2:
                        if code not in self.venai or subcode != "15": continue
                    elif type_code == 3:
                        if code not in self.venai and code not in self.peyar: continue
                    elif type_code == 4:
                        if code not in self.nonderi: continue
                    elif type_code == 6:
                        if subcode != "15": continue
                    elif type_code == 5:
                        if code in self.peyar and paku == sol and code in self.speyar and code != "M":
                            return True
                        else:
                            return False
                    
                    if self.checkviku(paku, viku, "", code, subcode, sugges):
                        return True
        return False

    def validate_words(self, mwords, opt=True, mode="list"):
        # Porting gpathil11
        results = []
        parinthu = [[0, "wrong"] for _ in range(len(mwords))]
        ottran = [[0, 1] for _ in range(len(mwords))] # [verified, suggestions]

        for i in range(len(mwords)):
            word = mwords[i]
            sandi = ""
            punarchi = False
            
            if ottran[i][0] == 1: continue
            if len(word) < 1:
                parinthu[i] = [-1, ""]
                continue
            
            if len(word) == 2:
                if re.search(r'[ா-்]', word[-1]):
                    ottran[i][0] = 1
                    parinthu[i] = [0, "correct"]
                    continue
            
            if len(word) == 1:
                ottran[i][0] = 1
                parinthu[i] = [0, "correct"]
                continue
                
            word = word.replace("ொ", "ொ").replace("ோ", "ோ")
            
            # Sandhi remover
            if i + 2 < len(mwords) and len(mwords[i+2]) > 0:
                ottru = mwords[i][-2:]
                methi = mwords[i][:-2]
                muthal = mwords[i+2][0]
                if re.match(r'[கசதப]்', ottru):
                    if muthal + "்" == ottru:
                        word = methi
                        sandi = ottru
                elif ottru == "ட்":
                    if re.match(r'[கசதப]', muthal):
                        word = methi + "ள்"
                        punarchi = True
                elif ottru == "ற்":
                    if re.match(r'[கசதப]', muthal):
                        word = methi + "ல்"
                        punarchi = True
                elif ottru == "ங்":
                    if muthal == "க":
                        word = methi + "ம்"
                        sandi = "ங்"
                        punarchi = True
                elif ottru == "ஞ்":
                    if muthal == "ச":
                        word = methi + "ம்"
                        sandi = "ஞ்"
                        punarchi = True
                elif ottru == "ந்":
                    if muthal == "த":
                        word = methi + "ம்"
                        sandi = "ந்"
                        punarchi = True

            # Cache check
            composed_word = word + sandi
            for idx, cword in enumerate(self.cacheword):
                if cword == composed_word:
                    b = self.cachesug[idx]
                    parinthu[i][1] = b
                    if not self.istamil(b): parinthu[i][0] = 0
                    elif ',' not in b: parinthu[i][0] = 1
                    else: parinthu[i][0] = len(b.split(','))
                    ottran[i][0] = 1
                    break
            
            if ottran[i][0] == 0:
                if word in self.data.user_oword:
                    ottran[i][0] = 1
                    parinthu[i] = [0, "correct"]
            
            if ottran[i][0] == 0:
                if self.checkword(word, 0):
                    ottran[i][0] = 1
                    parinthu[i] = [0, "correct"]
            
            # Suggestion logic
            if opt and ottran[i][0] == 0:
                suggestions = self.get_suggestions(word)
                unique_sug = list(dict.fromkeys(suggestions)) # Remove duplicates
                
                for nword in unique_sug:
                    if self.checkword(nword, 7):
                        if punarchi:
                            # Handle punarchi/sandhi in suggestions
                            if nword.endswith("ள்"):
                                self.add_parinthu(parinthu, i, nword[:-1] + "ட்")
                            elif nword.endswith("ல்"):
                                self.add_parinthu(parinthu, i, nword[:-1] + "ற்")
                            elif nword.endswith("ம்"):
                                self.add_parinthu(parinthu, i, nword[:-1] + sandi)
                        else:
                            self.add_parinthu(parinthu, i, nword + sandi)
                
                if parinthu[i][0] > 0:
                    ottran[i][0] = 1

            if len(word) > 0 and composed_word not in self.cacheword:
                self.cacheword.append(composed_word)
                self.cachesug.append(parinthu[i][1])

        return parinthu

    def add_parinthu(self, parinthu, i, w):
        if w not in parinthu[i][1]:
            if parinthu[i][0] > 0:
                parinthu[i][0] += 1
                parinthu[i][1] += "," + w
            else:
                parinthu[i][0] = 1
                parinthu[i][1] = w
        return parinthu

    def get_suggestions(self, c):
        sug = []
        for a, values in self.data.gword.items():
            if a in c:
                for k in values:
                    b = k.get('t')
                    d = k.get('w')
                    if b == "9":
                        supersug = c.replace(a, d)
                        if self.checkword(supersug, 0):
                            return [supersug]
                        else:
                            # Recursive suggest with marker 's'
                            suggest = self.get_suggestions(c.replace(a, "s"))
                            sug.extend([s.replace("s", d) for s in suggest])
                    else:
                        sug.extend(self.get_sample(b, c, a, d))
        
        # Special logic from C#
        sug.extend(self.get_sample("100", c, "", "்"))
        sug.extend(self.get_sample("100", c, "", "ா"))
        sug.extend(self.get_sample("100", c, "", "ி"))
        sug.extend(self.get_sample("100", c, "", "ை"))
        sug.extend(self.get_sample("101", c, "", ""))
        sug.extend(self.get_sample("102", c, "", "1"))
        sug.extend(self.get_sample("102", c, "", "2"))
        sug.extend(self.get_sample("102", c, "", "3"))
        
        # getsuggestion2 logic (cluster combinations)
        sug.extend(self.get_suggestions2(c))
        
        return sug

    def get_suggestions2(self, word):
        sugword = ["க்க,க", "ச்ச,ச", "த்த,த", "ப்ப,ப", "ற,ர", "ல,ள,ழ", "ந,ன,ண"]
        sug = []
        limit = len(word)
        temp_word = word
        for _ in range(limit):
            sug1 = []
            flag = False
            for clusters in sugword:
                poss = clusters.split(",")
                if not flag:
                    for p in poss:
                        if not flag and len(temp_word) >= len(p):
                            if temp_word.startswith(p):
                                temp_word = temp_word[len(p):]
                                sug1 = self.combination(sug, poss)
                                flag = True
                                break
            if not sug1:
                if len(temp_word) > 0:
                    sug = self.combination(sug, [temp_word[0]])
                    temp_word = temp_word[1:]
            else:
                sug = sug1
                if len(sug) > 1000: return []
            if not temp_word: break
        return sug

    def combination(self, word_list, sug_list):
        if not word_list: return sug_list
        res = []
        for s in sug_list:
            for w in word_list:
                res.append(w + s)
        return res

    def is_mat(self, v1, v2):
        return v2 > 0 and v1 == ""

    def get_sample(self, code, word, fstr, tstr):
        sample = []
        if code == "0":
            sample.append(word.replace(fstr, tstr))
            for m in re.finditer(re.escape(fstr), word, re.IGNORECASE):
                count = m.start()
                sample.append(word[:count] + tstr + word[count + len(fstr):])
        
        elif code == "1":
            matches = list(re.finditer(re.escape(fstr) + r"([ா-்]|)", word, re.IGNORECASE))
            if matches:
                incre = 0
                a = word
                for m in matches:
                    c1 = m.group(0)
                    c2 = m.group(1)
                    count = m.start()
                    if self.is_mat(c2, count):
                        a = a[:count + incre] + tstr + a[count + len(c1) + incre:]
                        incre += len(tstr) - len(c1)
                        sample.append(word[:count] + tstr + word[count + len(c1):])
                sample.append(a)

        elif code == "2":
            matches = list(re.finditer(re.escape(fstr), word, re.IGNORECASE))
            if matches:
                incre = 0
                a = word
                for m in matches:
                    c1 = m.group(0)
                    count = m.start()
                    if count > 0:
                        a = a[:count + incre] + tstr + a[count + len(c1) + incre:]
                        incre += len(tstr) - len(c1)
                        sample.append(word[:count] + tstr + word[count + len(c1):])
                sample.append(a)

        elif code == "3":
            if word.endswith(fstr):
                sample.append(word[:-len(fstr)] + tstr)

        elif code == "4":
            if word.startswith(fstr):
                sample.append(tstr + word[len(fstr):])

        elif code == "5":
            for m in re.finditer(re.escape(fstr), word, re.IGNORECASE):
                c1 = m.group(0)
                count = m.start()
                if 0 < count < len(word) - 1:
                    sample.append(word[:count] + tstr + word[count + len(c1):])

        elif code == "101":
            # [க-ஹ]ர([^ா-்]|)
            matches = list(re.finditer(r'[க-ஹ]ர([^ா-்]|)', word, re.IGNORECASE))
            if matches:
                a = word
                for m in matches:
                    count = m.start(1) # index of ர (actually part of the match)
                    # The C# index was m.Groups[1].Index
                    a = a[:count - 1] + "ா" + a[count:]
                    sample.append(word[:count - 1] + "ா" + word[count:])
                sample.append(a)

        elif code == "102":
            diff = int(tstr)
            for i in range(len(word) - (diff * 2) + 1):
                if word[i : i + diff] == word[i + diff : i + (diff * 2)]:
                    sample.append(word[:i] + word[i + diff:])

        elif code == "100":
            matches = list(re.finditer(r'[க-ஹ]([ா-்]|)', word, re.IGNORECASE))
            if matches:
                incre = 0
                a = word
                for m in matches:
                    c1 = m.group(0)
                    c2 = m.group(1)
                    count = m.start()
                    if self.is_mat(c2, count):
                        a = a[:count + incre] + c1 + tstr + a[count + len(c1) + incre:]
                        incre += len(tstr)
                        sample.append(word[:count] + c1 + tstr + word[count + len(c1):])
                sample.append(a)
            
            # Additional shifters from C#
            for m in re.finditer(r'[க-ஹ]' + re.escape(tstr) + r'[க-ஹ]([ா-்]|)', word, re.IGNORECASE):
                c1 = m.group(0)
                c2 = m.group(1)
                count = m.start()
                if self.is_mat(c2, count):
                    a = word[:count] + c1[0] + c1[2] + tstr + word[count + len(c1):]
                    sample.append(a)

            for m in re.finditer(r'[க-ஹ]([ா-்]|)[க-ஹ]' + re.escape(tstr), word, re.IGNORECASE):
                c1 = m.group(0)
                c2 = m.group(1)
                count = m.start()
                if self.is_mat(c2, count):
                    a = word[:count] + c1[0] + tstr + c1[1] + word[count + len(c1):]
                    sample.append(a)
                    
        return sample
