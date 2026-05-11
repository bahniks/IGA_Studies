#! python3

from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from time import time
import csv
import random
import os.path
import os
import re

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding
from gui import GUI
from constants import TESTING, BUDGET


##################################################################################################################
# TEXTS #
#########

questionText = "Chcete koupit tento produkt?"

products_intro_1 = """Tímto končí první část studie.

Nyní bude následovat druhá část, která se týká rozhodování o nákupu běžných spotřebních produktů. Tato část má vlastní instrukce a vlastní mechanismus odměňování. Před jejím začátkem si prosím pečlivě přečtěte následující pravidla.

Během této studie budete činit sérii nákupních rozhodnutí u běžných spotřebních produktů.
V každém kroku uvidíte produkt, jeho charakteristiky, kategorii a cenu. Vaším úkolem bude rozhodnout, zda byste si daný produkt za uvedenou cenu koupil/a.
Původní ceny uvedené u slevových nabídek produktů použitých ve studii vycházejí z cen, za které výzkumný tým produkty nakoupil."""

products_intro_2 = f"""K této nákupní části studie máte k dispozici experimentální rozpočet {BUDGET} Kč.

Během studie učiníte sérii rozhodnutí typu: "Koupil/a byste si tento produkt za uvedenou cenu?"
Na konci studie budou náhodně vybrány dvě produktové kategorie. Z každé z těchto kategorií bude následně náhodně vybráno právě jedno Vaše rozhodnutí k realizaci. Celkem tedy budou realizována dvě Vaše rozhodnutí.
Pokud jste u vybraného produktu zvolil/a ANO, produkt za uvedenou cenu skutečně koupíte, tato částka se odečte z Vašeho rozpočtu a produkt obdržíte.
Pokud jste u vybraného produktu zvolil/a NE, produkt neobdržíte a žádná částka Vám nebude z Vašeho rozpočtu odečtena.
Zbytek experimentálního rozpočtu bude připočten k Vaší fixní odměně za účast."""

products_understanding_intro = """Než budete pokračovat, odpovězte prosím na následující kontrolní otázky, které ověří, zda rozumíte pravidlům nákupní části studie a způsobu realizace rozhodnutí."""

products_understanding_questions = [
    [
        "Kolik Vašich rozhodnutí bude na konci studie náhodně vybráno k realizaci?",
        [
            "Žádné",
            "Právě jedno",
            "Právě dvě",
        ],
        [
            "To není správně.\nNa konci studie budou k realizaci náhodně vybrána dvě Vaše rozhodnutí.",
            "To není správně.\nNa konci studie budou k realizaci náhodně vybrána dvě Vaše rozhodnutí.",
            "Správně.\nNa konci studie budou k realizaci náhodně vybrána dvě Vaše rozhodnutí.",
        ],
    ],
    [
        "Co se stane, pokud jste u náhodně vybrané volby produktu zvolili ANO?",
        [
            "Produkt nezískám, ale dostanu peněžní bonus.",
            "Produkt za cenu ve vylosované volbě skutečně koupím, částka se odečte z mého rozpočtu a produkt obdržím.",
            "Nic se nestane, jde jen o hypotetické rozhodnutí.",
        ],
        [
            "To není správně.\nPokud jste u náhodně vybrané volby produktu zvolili ANO, produkt za uvedenou cenu skutečně koupíte, částka se odečte z Vašeho experimentálního rozpočtu a produkt obdržíte.",
            "Správně.\nPokud jste u náhodně vybrané volby produktu zvolili ANO, produkt za uvedenou cenu skutečně koupíte, částka se odečte z Vašeho experimentálního rozpočtu a produkt obdržíte.",
            "To není správně.\nPokud jste u náhodně vybrané volby produktu zvolili ANO, produkt za uvedenou cenu skutečně koupíte, částka se odečte z Vašeho experimentálního rozpočtu a produkt obdržíte.",
        ],
    ],
]

products_intro_4 = """Nyní začne první část nákupní úlohy.
V této části uvidíte sérii produktů. U každého produktu odpovězte, zda byste si jej za uvedenou cenu koupil/a.
Rozhodujte se prosím tak, jako by se právě toto rozhodnutí mohlo stát tím, které bude na konci studie realizováno."""



finalText = """V úloze s nákupem výrobků byly vylosovány tyto dvě volby:
{}
{}
{}
Zbytek Vašeho rozpočtu, tj. {} je připočten k odměně za studii."""
chosenText = "Rozhodl/a jste se {}koupit {} za cenu {}."
receivedText = "Zakoupené produkty obdržíte od experimentátora."
oneReceivedText = "Zakoupený produkt obdržíte od experimentátora."
noProductsText = "Nezakoupil(a) jste žádný z vylosovaných produktů."

transparent = "Předchozí cena v tomto experimentu: {}"



##################################################################################################################


prices = ["low", "middle", "high"]
conditions = [
    ("baseline", "sale"),
    ("sale", "baseline"),
    ("baseline", "transparent")
]


class Choices(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        file_path = os.path.join(os.path.dirname(__file__), "products.tsv")
        with open(file_path, encoding = "utf-8", newline = "") as f:
            reader = csv.DictReader(f, delimiter = "\t")
            self.infos = [row for row in reader if row.get("file")]
        random.shuffle(self.infos)

        self.run_index = int(self.root.status.get("products_run_index", 0))
        self.condition_index = min(self.run_index, 1)
        self.root.status["products_conditions"] = self._get_or_create_conditions()

        self.file.write("Products\n")

        self.selected = {}
        if self.run_index == 0 or "products_all_choices" not in self.root.status:
            self.root.status["products_all_choices"] = []
        self.all_choices = self.root.status["products_all_choices"]
        self.current = None

        self.order = -1

        self.product = OneProduct(self)
        self.product.grid(column = 0, row = 1)

        self.trialText = ttk.Label(self, text = "", font = "helvetica 15", background = "white", justify = "left", width = 15)
        self.trialText.grid(column = 0, row = 0, pady = 30, padx = 10, sticky = NE)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)

        self.proceed()

    def _get_or_create_conditions(self):
        existing = self.root.status.get("products_conditions")
        product_ids = {info["id"] for info in self.infos}

        if isinstance(existing, dict) and all(pid in existing for pid in product_ids):
            return existing

        generated = {}
        for info in self.infos:
            generated[info["id"]] = {
                "condition_pair": random.choice(conditions),
                "price_level": random.choice(prices),
            }
        return generated

    @staticmethod
    def _price_to_float(price_text):
        match = re.search(r"-?\d+(?:[\.,]\d+)?", str(price_text))
        if not match:
            return None
        return float(match.group(0).replace(",", "."))

    def proceed(self):
        self.order += 1
        self.trialText["text"] = f"Produkt {self.order + 1:>3}/{len(self.infos)}"

        if self.order == len(self.infos) or (TESTING and self.order == 10):
            if self.condition_index == 1:
                drawn = random.sample(self.all_choices, min(2, len(self.all_choices)))
                while len(drawn) < 2:
                    drawn.append(drawn[0] if drawn else {"label": "", "shown_price": "", "choice": "no"})
                lines = []
                total_spent = 0
                bought_number = 0
                for ch in drawn:
                    bought = ch["choice"] == "yes"
                    prefix = "" if bought else "ne"
                    lines.append(chosenText.format(prefix, ch["label"], ch["shown_price"]))
                    if bought:
                        bought_number += 1
                        price_val = self._price_to_float(ch["shown_price"])
                        if price_val is not None:
                            total_spent += price_val
                remainder = BUDGET - total_spent
                remainder_str = f"{remainder:.2f} Kč"
                if bought_number == 0:
                    receive = noProductsText
                elif bought_number == 1:
                    receive = oneReceivedText
                else:
                    receive = receivedText
                self.root.status["results"] += [finalText.format(lines[0].replace(",", "."), lines[1].replace(",", "."), receive, remainder_str)]
                self.root.status["reward"] += (BUDGET - total_spent)
            self.nextFun()
        else:
            self.current = dict(self.infos[self.order])
            cond_info = self.root.status["products_conditions"][self.current["id"]]
            pair = cond_info["condition_pair"]
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError("condition_pair must be a 2-item tuple/list in products_conditions")

            display_condition = pair[self.condition_index]
            price_level = cond_info.get("price_level", "middle")
            baseline_price = self.current.get(price_level, self.current.get("middle", ""))
            high_price = self.current.get("high", "")
            middle_price = self.current.get("middle", "")

            self.current["display_condition"] = display_condition
            self.current["price_level"] = price_level
            self.current["baseline_price"] = baseline_price
            self.current["high_price"] = high_price
            self.current["middle_price"] = middle_price

            if display_condition == "baseline":
                self.current["shown_price"] = baseline_price
                self.current["discount_pct"] = None
                self.current["transparent_text"] = ""
            else:
                high_val = self._price_to_float(high_price)
                middle_val = self._price_to_float(middle_price)
                if high_val and middle_val is not None and high_val > 0:
                    discount_pct = int(round((high_val - middle_val) / high_val * 100))
                else:
                    discount_pct = 0
                self.current["shown_price"] = middle_price
                self.current["discount_pct"] = discount_pct
                self.current["transparent_text"] = transparent.format(high_price) if display_condition == "transparent" else ""

            self.product.showProduct(self.current)
            self.t0 = time()

    def record_choice(self, choice):
        if self.current is None:
            return

        if choice == "yes":
            self.selected[self.current["id"]] = self.current["shown_price"]

        self.all_choices.append({
            "id": self.current["id"],
            "label": self.current["label"],
            "shown_price": self.current["shown_price"],
            "choice": choice,
        })

        elapsed = time() - self.t0
        self.file.write("\t".join([
            self.id,
            str(self.order + 1),
            self.current["id"],
            self.current["label"],
            self.current["size"],
            self.current["category"],
            self.current["display_condition"],
            self.current["price_level"],
            self.current["shown_price"],
            choice,
            str(elapsed),
        ]) + "\n")
        self.proceed()

    def nextFun(self):
        self.root.status["products_run_index"] = self.run_index + 1
        if self.root.status["bag"] != "-1":
            data = "_".join([i for i in self.selected.keys()]) + "|" + "_".join([i for i in self.selected.values()])
            data = {'id': self.id, 'round': "products", 'offer': data}
            self.sendData(data)
        super().nextFun()


class OneProduct(Canvas):
    def __init__(self, root):
        super().__init__(root, highlightbackground = "white", highlightcolor = "white")

        self["background"] = "white"

        self.root = root

        self.product = Product(self)
        self.product.grid(column = 1, row = 0)

        self.label = ttk.Label(self, text = "", background = "white", font = "helvetica 15 bold", width = 55, anchor = "center")
        self.label.grid(column = 1, row = 1, pady = 8)

        self.categoryLabel = ttk.Label(self, text = "", background = "white", font = "helvetica 11")
        self.categoryLabel.grid(column = 1, row = 2, pady = 1)

        self.priceFrame = Frame(self, background = "white")
        self.priceFrame.grid(column = 1, row = 3, pady = 4)

        self.priceSingleLabel = ttk.Label(self.priceFrame, text = "", background = "white", font = "helvetica 16 bold")
        self.highPriceFont = tkfont.Font(family = "helvetica", size = 14, weight = "normal", overstrike = 1)
        self.highPriceLabel = ttk.Label(self.priceFrame, text = "", background = "white", font = self.highPriceFont)
        self.salePriceLabel = ttk.Label(self.priceFrame, text = "", background = "white", font = "helvetica 16 bold")
        self.transparentLabel = ttk.Label(self.priceFrame, text = "", background = "white", font = "helvetica 12")

        self.questionLabel = ttk.Label(self, text = questionText, background = "white", font = "helvetica 15")
        self.questionLabel.grid(column = 1, row = 4, pady = 10)

        self.buttons = Frame(self, background = "white")
        self.buttons.grid(column = 1, row = 5, pady = 5)
        button_style = ttk.Style()
        button_style.configure("ProductsChoice.TButton", font = "helvetica 15")
        self.yesButton = ttk.Button(self.buttons, text = "Ano", command = lambda: self.choose("yes"), style = "ProductsChoice.TButton")
        self.yesButton.grid(column = 0, row = 0, padx = 10)
        self.noButton = ttk.Button(self.buttons, text = "Ne", command = lambda: self.choose("no"), style = "ProductsChoice.TButton")
        self.noButton.grid(column = 1, row = 0, padx = 10)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)

    def showProduct(self, product):
        self.product.changeImage(product["file"])
        self.label["text"] = f"{product['label']} ({product['size']})"
        self.categoryLabel["text"] = product["category"]

        # Keep a fixed three-row price block in all conditions to avoid layout jumps.
        self.highPriceLabel["text"] = ""
        self.salePriceLabel["text"] = ""
        self.transparentLabel["text"] = ""
        self.highPriceLabel.grid(column = 0, row = 0, pady = 1)
        self.salePriceLabel.grid(column = 0, row = 1, pady = 1)
        self.transparentLabel.grid(column = 0, row = 2, pady = (2, 0))
        self.priceSingleLabel.grid_forget()

        if product["display_condition"] == "baseline":
            self.salePriceLabel["text"] = product["shown_price"]
            return

        self.highPriceLabel["text"] = product["high_price"]

        discount_text = f" (-{abs(product['discount_pct'])} %)" if product["discount_pct"] is not None else ""
        self.salePriceLabel["text"] = f"{product['middle_price']}{discount_text}"

        if product["display_condition"] == "transparent":
            self.transparentLabel["text"] = product["transparent_text"]

    def choose(self, choice):
        self.root.record_choice(choice)


class Product(Label):
    def __init__(self, root):
        super().__init__(root, background = "white", foreground = "white", relief = "flat", borderwidth = 10)
        self.config(width = 460, height = 460)
        self["anchor"] = "center"

    def changeImage(self, file):
        file = os.path.join(os.path.dirname(__file__), "Products", file)
        self.image = PhotoImage(file = file)
        self["image"] = self.image




ProductsIntro1 = (InstructionsFrame, {"text": products_intro_1, "height": "auto"})
ProductsIntro2 = (InstructionsFrame, {"text": products_intro_2, "height": "auto"})
ProductsIntroUnderstanding = (
    InstructionsAndUnderstanding,
    {
        "text": products_understanding_intro,
        "controlTexts": products_understanding_questions,
        "name": "ProductsInstructionsAndUnderstanding",
        "randomize": False,
        "height": "auto",
        "finalButton": "Pokračovat",
    },
)
ProductsIntro4 = (InstructionsFrame, {"text": products_intro_4, "height": "auto"})




def main():
    os.chdir(os.path.dirname(os.getcwd()))
    from login import Login
    from intros import Ending
    GUI([
        Login,
        Choices,
        ProductsIntro1,
        ProductsIntro2,
        #ProductsIntroUnderstanding,
        ProductsIntro4,
        Choices,
        Ending,
    ])


if __name__ == "__main__":
    main()

