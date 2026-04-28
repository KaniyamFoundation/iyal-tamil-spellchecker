import json
import os
import re

class TamilinaiyaVaaniData:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = {}
        self.gword = []
        self.tword = {}
        self.tranrule = {}
        self.Eword = []
        self.Oword = {}
        self.user_oword = []
        self.user_gword = []

    def load(self):
        if not os.path.exists(self.db_path):
            print(f"Error: {self.db_path} not found.")
            return False
            
        with open(self.db_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            # Remove trailing commas before } or ]
            content = re.sub(r',\s*([\}\]])', r'\1', content)
            data = json.loads(content)
            # In C#:
            # Oword = db["DB"][4];
            # Eword = db["DB"][3];
            # tranrule = db["DB"][2];
            # tword = db["DB"][1];
            # gword = db["DB"][0];
            db_list = data.get("DB", [])
            if len(db_list) >= 5:
                self.gword = db_list[0]
                self.tword = db_list[1]
                self.tranrule = db_list[2]
                self.Eword = db_list[3]
                self.Oword = db_list[4]
            return True

    def load_user_data(self, user_txt_path):
        if not os.path.exists(user_txt_path):
            return
        with open(user_txt_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            self.user_oword = lines

