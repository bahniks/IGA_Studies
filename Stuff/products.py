#! python3

from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from time import time, sleep
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

products_intro_1 = """Tímto končí další část studie.

Nyní bude následovat druhá část, která se týká rozhodování o nákupu produktů. Tato část má vlastní mechanismus odměňování. Před jejím začátkem si prosím pečlivě přečtěte následující instrukce.

Během této studie budete činit sérii nákupních rozhodnutí u běžných spotřebních produktů.
V každém kroku uvidíte produkt, jeho charakteristiky, kategorii a cenu. Vaším úkolem bude rozhodnout, zda byste si daný produkt za uvedenou cenu koupil/a.

U některých produktů budou uvedeny původní ceny a sleva. Původní ceny uvedené u takovýchto slevových nabídek odpovídají cenám, za které výzkumný tým produkty nakoupil."""

products_intro_2 = f"""V této nákupní části studie máte k dispozici rozpočet {BUDGET} Kč.

Nákupní úloha bude rozdělena do dvou částí. Mezi nimi budete požádán/a o vyplnění krátkých úloh a dotazníků.

Na konci studie budou náhodně vybrány dvě produktové kategorie. Z každé z těchto kategorií bude následně náhodně vybráno právě jedno Vaše rozhodnutí k realizaci. <b>Celkem tedy budou realizována dvě Vaše rozhodnutí</b>.

Pokud jste u vybraného produktu zvolil/a <b>ANO</b>, produkt za uvedenou cenu skutečně koupíte, tato částka se odečte z Vašeho rozpočtu a produkt obdržíte.
Pokud jste u vybraného produktu zvolil/a <b>NE</b>, produkt neobdržíte a žádná částka Vám nebude z Vašeho rozpočtu odečtena.

Zbytek rozpočtu z této části studie bude připočten k Vaší celkové odměně."""

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


questionnaires_trans_intro = """Tímto končí první část nákupní úlohy.

Než přejdeme k druhé části nákupní úlohy, čekají Vás krátké úlohy a dotazníky. Prosím odpovídejte pozorně."""


products_intro_5 = """Nyní bude pokračovat druhá část nákupní úlohy.

Tato část bude probíhat stejným způsobem jako první část. Opět budete činit nákupní rozhodnutí u běžných spotřebních produktů. U každého produktu odpovězte, zda byste si jej za uvedenou cenu koupil/a.

Mohou se Vám zobrazit i produkty, které jste již viděl/a v předchozí části, avšak s jinou cenovou nabídkou.

Rozhodujte se prosím opět tak, jako by se právě toto rozhodnutí mohlo stát tím, které bude na konci studie realizováno."""


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

        control_file_path = os.path.join(os.path.dirname(__file__), "products_control.tsv")
        with open(control_file_path, encoding = "utf-8", newline = "") as f:
            reader = csv.DictReader(f, delimiter = "\t")
            self.control_infos = [row for row in reader if row.get("file")]

        self.run_index = int(self.root.status.get("products_run_index", 0))
        self.condition_index = min(self.run_index, 1)
        self.root.status["products_conditions"] = self._get_or_create_conditions()
        self.control_product = self._get_control_product_for_run()
        self.trials = self._build_trials_with_control(self.control_product)

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

    def _get_control_product_for_run(self):
        if not self.control_infos:
            return None

        order = self.root.status.get("products_control_order")
        if not isinstance(order, list) or len(order) != len(self.control_infos):
            order = list(range(len(self.control_infos)))
            random.shuffle(order)
            self.root.status["products_control_order"] = order

        control_idx = order[self.run_index % len(order)]
        return dict(self.control_infos[control_idx])

    def _build_trials_with_control(self, control_product):
        trials = list(self.infos)
        if control_product is None:
            return trials

        mid = len(trials) // 2
        start = max(0, mid - 2)
        end = min(len(trials), mid + 2)
        insert_at = random.randint(start, end)
        control_item = dict(control_product)
        control_item["is_control"] = True
        trials.insert(insert_at, control_item)
        return trials

    def _get_or_create_conditions(self):
        existing = self.root.status.get("products_conditions")
        product_ids = {info["id"] for info in self.infos}

        if isinstance(existing, dict) and all(pid in existing for pid in product_ids):
            return existing

        total_products = len(self.infos)
        condition_price_pairs = [(condition_pair, price_level) for condition_pair in conditions for price_level in prices]
        pair_count = len(condition_price_pairs)
        per_pair = total_products // pair_count
        remainder = total_products % pair_count

        shuffled_condition_price_pairs = list(condition_price_pairs)
        random.shuffle(shuffled_condition_price_pairs)

        balanced_pairs = []
        for idx, condition_price_pair in enumerate(shuffled_condition_price_pairs):
            extra = 1 if idx < remainder else 0
            balanced_pairs.extend([condition_price_pair] * (per_pair + extra))
        random.shuffle(balanced_pairs)

        generated = {}
        for info, (condition_pair, price_level) in zip(self.infos, balanced_pairs):
            generated[info["id"]] = {
                "condition_pair": condition_pair,
                "price_level": price_level,
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
        self.trialText["text"] = f"Produkt {self.order + 1:>3}/{len(self.trials)}"

        if self.order == len(self.trials) or (TESTING and self.order == 10):
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
            self.current = dict(self.trials[self.order])
            if self.current.get("is_control"):
                self.current["display_condition"] = "baseline"
                self.current["price_level"] = "control"
                self.current["baseline_price"] = self.current.get("price", "")
                self.current["high_price"] = ""
                self.current["middle_price"] = ""
                self.current["shown_price"] = self.current.get("price", "")
                self.current["discount_pct"] = None
                self.current["transparent_text"] = ""
            else:
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

    def gothrough(self):
        # Simulate a full run with random purchase decisions.
        while self.order < len(self.trials) - 1 and (not TESTING or self.order < 10):
            choice = random.choice(["yes", "no"])
            self.record_choice(choice)
            self.update()
            sleep(0.02)


class OneProduct(Canvas):
    def __init__(self, root):
        super().__init__(root, highlightbackground = "white", highlightcolor = "white")

        self["background"] = "white"

        self.root = root

        self.product = Product(self)
        self.product.grid(column = 1, row = 0)

        self.label = ttk.Label(self, text = "", background = "white", font = "helvetica 15 bold", width = 70, anchor = "center")
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
ProductsEnd1 = (InstructionsFrame, {"text": questionnaires_trans_intro, "height": "auto"})
ProductsIntro5 = (InstructionsFrame, {"text": products_intro_5, "height": "auto"})




def main():
    os.chdir(os.path.dirname(os.getcwd()))
    from login import Login
    from intros import Ending
    GUI([
        Login,
        Choices,
        ProductsIntro1,
        ProductsIntro2,
        ProductsIntroUnderstanding,
        ProductsIntro4,
        ProductsIntro5,
        ProductsEnd1,
        Choices,
        Ending,
    ])


if __name__ == "__main__":
    main()

