#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from collections import defaultdict

import random
import os
import urllib.request
import urllib.parse
import csv

from common import InstructionsFrame
from gui import GUI
from constants import TESTING, URL, COORDINATION_ROUNDS






class Login(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "Počkejte na spuštění experimentu", height = 3, font = 15, width = 45, proceed = False)

        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def login(self):             
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': self.root.status["code"], 'offer': "login"})
                data = data.encode('ascii')
                if URL == "TEST":                                                       
                    response = self._test_login_response()
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                    except Exception:
                        self.changeText("Server nedostupný")
                if response == "login_successful" or response == "already_logged":
                    self.changeText("Přihlášen")
                    self.root.status["logged"] = True
                elif response == "ongoing":
                    self.changeText("Do studie se již nelze připojit")
                elif response == "no_open":
                    self.changeText("Studie není otevřena")
                elif response == "closed":
                    self.changeText("Studie je uzavřena pro přihlašování")
                elif response == "not_grouped":
                    self.changeText("V experimentu nezbylo místo. Zavolejte prosím experimentátora zvednutím ruky.")
                elif self._is_login_payload(response):
                    self.root.status["selected_products"] = self._parse_selected_products_response(response)
                    self.root.status["co_roles"] = self._parse_coordination_roles_response(response)
                    self.progressBar.stop()
                    self.write(response)
                    self.nextFun()
                    break
                elif response:
                    self.changeText("Neplatná odpověď serveru při přihlašování")
            count += 1                  
            sleep(0.1)    

    def run(self):
        self.progressBar.start()
        self.login()

    def write(self, response):
        self.file.write("Login" + "\n")
        self.file.write(self.id + "\t" + "\t".join(response.split("|")) + "\n\n")        

    @staticmethod
    def _parse_product_token(token):
        token = str(token).strip()
        if "_" in token:
            code, presentation = token.rsplit("_", 1)
            return {"code": code.strip(), "presentation": presentation.strip().upper()}
        return {"code": token, "presentation": "CONTROL"}

    def _parse_selected_products_response(self, response):
        token1, token2, _ = str(response).split("|")
        return [self._parse_product_token(token1), self._parse_product_token(token2)]

    @staticmethod
    def _is_login_payload(response):
        parts = str(response).split("|")
        return len(parts) == 3 and all(str(p).strip() for p in parts)

    @staticmethod
    def _parse_coordination_roles_response(response):
        _, _, roles_token = str(response).split("|")
        role_values = roles_token.split("_")
        parsed = {}
        for i, role in enumerate(role_values, start=1):
            role_text = str(role).strip()
            if role_text not in ("1", "2"):
                raise ValueError(f"Invalid coordination role value from server: {role}")
            parsed[i] = role_text
        return parsed

    def _test_login_response(self):
        products_path = os.path.join(os.path.dirname(__file__), "products.tsv")
        with open(products_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            product_ids = [row.get("id", "").strip() for row in reader if row.get("id")]

        control_products_path = os.path.join(os.path.dirname(__file__), "products_control.tsv")
        with open(control_products_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            control_ids = [row.get("id", "").strip() for row in reader if row.get("id")]

        token_pool = [f"{pid}_{random.choice(['1', '2'])}" for pid in product_ids]
        token_pool.extend(control_ids)

        chosen = random.sample(token_pool, 2)
        coord_roles = "_".join([random.choice(["1", "2"]) for _ in range(COORDINATION_ROUNDS)])
        return "|".join(chosen + [coord_roles])

    def gothrough(self):
        self.run()