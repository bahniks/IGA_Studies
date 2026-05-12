from tkinter import *
from tkinter import ttk

import random
import os

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding, Wait
from gui import GUI
from constants import COORDINATION_ROUNDS, COORDINATION_SUCCESS, COORDINATION_PREFERENCE
from login import Login


################################################################################
# TEXTS

instructionsC0 = """Nyní začíná první rozhodovací úloha.

Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři.

Pozorně si přečtěte pokyny na další obrazovce, abyste porozuměl(a) studii a své roli v ní."""

instructionsC1a = f"""V této úloze budete náhodně spárováni s {COORDINATION_ROUNDS} účastníky a s každým z nich budete hrát dvě kola.

V každém kole si oba současně zvolíte jednu možnost: Volbu A nebo Volbu B. Vaše odměna závisí na Vaší volbě i na volbě druhého účastníka.

<b>Výplatní tabulka je uvedena níže:</b>"""

instructionsC1b = f"""Číslo před lomítkem v tabulce označuje výplatu pro Hráče 1 a číslo za lomítkem označuje výplatu pro Hráče 2.

Obecně lze výplaty shrnout takto:
• Pokud Hráč 1 zvolí možnost A, obdrží {COORDINATION_PREFERENCE} Kč.
• Pokud Hráč 2 zvolí možnost B, obdrží {COORDINATION_PREFERENCE} Kč.
• Navíc oba účastníci obdrží {COORDINATION_SUCCESS} Kč, pokud zvolí stejnou volbu.
    

Po každém kole obdržíte informaci o volbě druhého hráče a výplatě v daném kole.

Jedno náhodně vybrané kolo určí Vaši odměnu za tuto úlohu. Na konci studie se dozvíte, jaká byla Vaše role a jaký je výsledek rozhodnutí Vás a druhého účastníka.

Odpovězte prosím na následující kontrolní otázky, abychom ověřili, že jste instrukcím porozuměli."""

instructionsC2 = f"""Nyní hrajete {{}}. kolo s {{}} partnerem.

Ve hře s tímto partnerem <b>je Vám přiřazena role {{}}</b>.

Pro připomenutí:
• Pokud Hráč 1 zvolí možnost A, obdrží {COORDINATION_PREFERENCE} Kč.
• Pokud Hráč 2 zvolí možnost B, obdrží {COORDINATION_PREFERENCE} Kč.
• Navíc oba účastníci obdrží {COORDINATION_SUCCESS} Kč, pokud zvolí stejnou volbu."""

order = ["prvním", "druhým", "třetím"]

coordinationBeliefText = """Odhadněte pravděpodobnost, že se Vaše volba shoduje s volbou Vašeho partnera."""


coordControl1 = "Co se stane, pokud si oba účastníci zvolí Volbu A?"
coordAnswers1 = [
        f"Hráč 1 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS} Kč",
        f"Oba obdrží {COORDINATION_SUCCESS} Kč",
        f"Oba obdrží {COORDINATION_PREFERENCE} Kč",
]
coordFeedback1 = [
        "Správně.",
        f"Nesprávně. Pokud si oba účastníci zvolí Volbu A, Hráč 1 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS} Kč.",
        f"Nesprávně. Pokud si oba účastníci zvolí Volbu A, Hráč 1 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS} Kč.",
]

coordControl2 = "Co se stane, pokud si oba účastníci zvolí Volbu B?"
coordAnswers2 = [
        f"Hráč 1 obdrží {COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč",
        f"Oba obdrží {COORDINATION_SUCCESS} Kč",
        f"Výplata bude zvolena náhodně v rozmezí mezi 0 Kč a {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč",
]
coordFeedback2 = [
        "Správně.",
        f"Nesprávně. Pokud si oba účastníci zvolí Volbu B, Hráč 1 obdrží {COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč.",
        f"Nesprávně. Pokud si oba účastníci zvolí Volbu B, Hráč 1 obdrží {COORDINATION_PREFERENCE} Kč a Hráč 2 obdrží {COORDINATION_SUCCESS + COORDINATION_PREFERENCE} Kč.",
]

coordControlTexts = [
    [coordControl1, coordAnswers1, coordFeedback1],
    [coordControl2, coordAnswers2, coordFeedback2],
]

coordResultText = """<b>Informace o výsledcích za {}. kolo s {} partnerem</b>

Vaše role: {}
Vaše volba: {}
Volba druhého účastníka: {}
Vaše výplata v tomto kole: {} Kč
Výplata druhého účastníka v tomto kole: {} Kč"""


def _coordination_payoffs(my_choice, partner_choice):
    my_payoff = 0
    partner_payoff = 0
    if my_choice == "A":
        my_payoff += COORDINATION_PREFERENCE
    if partner_choice == "B":
        partner_payoff += COORDINATION_PREFERENCE
    if my_choice == partner_choice:
        my_payoff += COORDINATION_SUCCESS
        partner_payoff += COORDINATION_SUCCESS
    return my_payoff, partner_payoff

nextRoundText = """Nyní budete hrát další kolo s jiným partnerem. Vaše role může zůstat stejná nebo se změnit."""


class CoordinationPayoffTable(Frame):
    def __init__(self, root, highlight_outcome=None):
        super().__init__(root, background="white", highlightbackground="white", highlightcolor="white")

        self.configure(padx=8, pady=8)

        headers = ["", "Hráč 2: A", "Hráč 2: B"]
        for column, text in enumerate(headers):
            label = ttk.Label(
                self,
                text=text,
                background="white",
                font="helvetica 15 bold",
                padding=8,
                relief="solid",
                anchor="center",
            )
            label.grid(row=1, column=column, sticky="nsew")

        row_specs = [
            ("Hráč 1: A", f"{COORDINATION_SUCCESS + COORDINATION_PREFERENCE} / {COORDINATION_SUCCESS}", f"{COORDINATION_PREFERENCE} / {COORDINATION_PREFERENCE}"),
            ("Hráč 1: B", "0 / 0", f"{COORDINATION_SUCCESS} / {COORDINATION_SUCCESS + COORDINATION_PREFERENCE}"),
        ]

        for row, (row_label, value_a, value_b) in enumerate(row_specs, start=2):
            row_choice = "A" if row == 2 else "B"
            row_header = ttk.Label(
                self,
                text=row_label,
                background="white",
                font="helvetica 15 bold",
                padding=8,
                relief="solid",
                anchor="center",
            )
            row_header.grid(row=row, column=0, sticky="nsew")

            for column, value in enumerate((value_a, value_b), start=1):
                partner_choice = "A" if column == 1 else "B"
                is_highlighted = highlight_outcome == (row_choice, partner_choice)
                cell = ttk.Label(
                    self,
                    text=value,
                    background="#fff4cc" if is_highlighted else "white",
                    font="helvetica 15 bold" if is_highlighted else "helvetica 15",
                    padding=8,
                    relief="solid",
                    anchor="center",
                )
                cell.grid(row=row, column=column, sticky="nsew")

        for column in range(3):
            self.columnconfigure(column, weight=1)


class InstructionsCoordination(InstructionsAndUnderstanding):
    def __init__(self, root):
        super().__init__(
            root,
            text=instructionsC1a,
            height=7,
            width=90,
            name="Coordination Control Questions",
            randomize=False,
            controlTexts=coordControlTexts,
            fillerHeight=170,
            finalButton="Pokračovat",
            prompt=None,
        )

        self.payoff_table = CoordinationPayoffTable(self)
        self.bottom_text = Text(
            self,
            font="helvetica 15",
            relief="flat",
            background="white",
            width=90,
            height=14,
            wrap="word",
            highlightbackground="white",
            pady=8,
        )
        self.bottom_text.insert("1.0", instructionsC1b)
        self.bottom_text.config(state="disabled")

        self.controlFrame.grid_forget()
        self.next.grid_forget()

        self.payoff_table.grid(row=2, column=0, columnspan=3, sticky="n")
        self.bottom_text.grid(row=3, column=0, columnspan=3, sticky="n")
        self.controlFrame.grid(row=5, column=1, sticky=W)
        self.next.grid(row=6, column=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=0)
        self.rowconfigure(6, weight=1)



class CoordinationGame(InstructionsFrame):
    def __init__(self, root):
        block = root.status.get("co_block", 1)
        trial = root.status.get("co_trial", 1)
        role_label = f"Hráč {trial}"
        order_index = max(0, min(len(order) - 1, block - 1))
        partner_ordinal = order[order_index]
        text = instructionsC2.format(trial, partner_ordinal, role_label)
        super().__init__(root, text=text, height="auto", font=15, width=85)

        self.block = block
        self.trial = trial
        self.decision_var = StringVar()
        self.prediction_var = IntVar(value=50)

        ttk.Style().configure("TButton", font="helvetica 15")
        ttk.Style().configure("Coordination.Horizontal.TScale", background="white")

        self.payoff_table = CoordinationPayoffTable(self)
        self.payoff_table.grid(row=2, column=0, columnspan=3, pady=(1, 2), sticky="n")

        self.choice_prompt_label = ttk.Label(
            self,
            text="Vyberte prosím jednu z následujících možností:",
            font="helvetica 15 bold",
            background="white",
        )
        self.choice_prompt_label.grid(row=3, column=0, columnspan=3, pady=(0, 2))

        choice_frame = Canvas(self, background="white", highlightbackground="white", highlightcolor="white")
        choice_frame.grid(row=4, column=1, pady=2)

        self.option_a_button = ttk.Button(
            choice_frame,
            text="Volba A",
            command=lambda: self._selected("A"),
        )
        self.option_a_button.grid(row=0, column=0, padx=20, pady=6, sticky=W)

        self.option_b_button = ttk.Button(
            choice_frame,
            text="Volba B",
            command=lambda: self._selected("B"),
        )
        self.option_b_button.grid(row=0, column=1, padx=20, pady=6, sticky=W)

        # Fixed-height fillers keep layout stable before hidden widgets appear.
        self.filler_prediction = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=50, width=1)
        self.filler_prediction.grid(row=5, column=0, columnspan=1, sticky=W)

        self.filler_scale = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=50, width=1)
        self.filler_scale.grid(row=6, column=0, columnspan=1, sticky=W)

        self.filler_probability = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=50, width=1)
        self.filler_probability.grid(row=7, column=0, columnspan=1, sticky=NW)

        self.filler_next = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=50, width=1)
        self.filler_next.grid(row=8, column=0, columnspan=1, sticky=W)

        self.prediction_label = ttk.Label(
            self,
            text=coordinationBeliefText,
            font="helvetica 15",
            background="white",
        )
        self.prediction_label.grid(row=5, column=0, columnspan=3, pady=4)
        self.prediction_label.grid_remove()

        self.prediction_scale = ttk.Scale(
            self,
            orient=HORIZONTAL,
            from_=0,
            to=100,
            length=400,
            variable=self.prediction_var,
            command=self._update_prediction_label,
            style="Coordination.Horizontal.TScale",
        )
        self.prediction_scale.grid(row=6, column=1, pady=2)
        self.prediction_scale.grid_remove()

        self.prediction_value_label = ttk.Label(
            self,
            text="50 %",
            font="helvetica 15",
            background="white",
        )
        self.prediction_value_label.grid(row=7, column=0, columnspan=3, pady=4)
        self.prediction_value_label.grid_remove()

        self.next.grid(row=8, column=1, pady=8)
        self.next.grid_remove()

        # Override inherited row weights from InstructionsFrame to avoid vertical stretching
        # around the inserted payoff table and prompt rows.
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=0)
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.rowconfigure(8, weight=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(2, weight=2)

    def _selected(self, decision):
        self.decision_var.set(decision)
        self.option_a_button.config(state="disabled")
        self.option_b_button.config(state="disabled")
        self.prediction_label.grid()
        self.prediction_scale.grid()
        self.prediction_value_label.grid()
        self.next.grid()

    def _update_prediction_label(self, value):
        val = int(round(float(value)))
        self.prediction_var.set(val)
        self.prediction_value_label["text"] = "{} %".format(val)

    def nextFun(self):
        if not self.decision_var.get():
            return
        self.write()
        self.destroy()
        self.root.nextFrame()

    def _ensure_status(self):
        self.root.status.setdefault("co_block", 1)
        self.root.status.setdefault("co_trial", 1)
        self.root.status.setdefault("co_decisions", {})

    def write(self):
        self._ensure_status()
        decision = self.decision_var.get()
        prediction = int(self.prediction_var.get())

        self.root.status["co_decisions"].setdefault(self.block, {})
        self.root.status["co_decisions"][self.block][self.trial] = {
            "decision": decision,
            "prediction": prediction,
        }

        data = {
            "id": self.id,
            "round": "coordination{}_{}".format(self.block, self.trial),
            "offer": "{}_{}".format(decision, prediction),
        }
        self.sendData(data)

        if self.trial == 2:
            self.root.status["co_block"] = self.block + 1
            self.root.status["co_trial"] = 1

        self.file.write("CoordinationGame\n")
        self.file.write(
            "\t".join([self.id, str(self.block), str(self.trial), decision, str(prediction)])
        )
        self.file.write("\n\n")

    def gothrough(self):
        self._selected(random.choice(["A", "B"]))
        self.prediction_var.set(50)
        self._update_prediction_label("50")
        sleep = __import__("time").sleep
        sleep(0.1)
        self.nextFun()


class WaitCoordination(Wait):
    def __init__(self, root):
        super().__init__(root, what="coordination")

    def test(self):
        return random.choice(["A", "B"])

    def processResponse(self, response):
        block = self.root.status.get("co_block", 1)
        trial = 1

        partner_decision = response.strip().upper()
        if partner_decision not in ("A", "B"):
            partner_decision = random.choice(["A", "B"])

        my_trial = self.root.status.get("co_decisions", {}).get(block, {}).get(trial, {})
        my_decision = my_trial.get("decision", "A")
        prediction = int(my_trial.get("prediction", 50))

        coordinated = my_decision == partner_decision
        my_payoff, partner_payoff = _coordination_payoffs(my_decision, partner_decision)

        self.root.status.setdefault("co_results", {})
        self.root.status["co_results"].setdefault(block, {})
        self.root.status["co_results"][block][trial] = {
            "my_decision": my_decision,
            "partner_decision": partner_decision,
            "coordinated": coordinated,
            "payoff": my_payoff,
            "partner_payoff": partner_payoff,
            "prediction": prediction,
        }

        # After first-trial feedback, continue with trial 2 for the same participant.
        self.root.status["co_trial"] = 2


class CoordinationRoundResult(InstructionsFrame):
    def __init__(self, root):
        block = root.status.get("co_block", 1)
        trial = 1
        result = root.status.get("co_results", {}).get(block, {}).get(trial, {})

        my_choice = result.get("my_decision", "-")
        partner_choice = result.get("partner_decision", "-")
        role_label = "Hráč 1"
        payoff = result.get("payoff")
        partner_payoff = result.get("partner_payoff")
        if payoff is None or partner_payoff is None:
            if my_choice in ("A", "B") and partner_choice in ("A", "B"):
                payoff, partner_payoff = _coordination_payoffs(my_choice, partner_choice)
            else:
                payoff, partner_payoff = 0, 0
        order_index = max(0, min(len(order) - 1, block - 1))
        partner_ordinal = order[order_index]

        text = coordResultText.format(trial, partner_ordinal, role_label, my_choice, partner_choice, payoff, partner_payoff)
        super().__init__(root, text=text, height=9, font=15, width=70)

        highlight = (my_choice, partner_choice) if my_choice in ("A", "B") and partner_choice in ("A", "B") else None
        self.result_table = CoordinationPayoffTable(self, highlight_outcome=highlight)
        self.next.grid_forget()
        self.result_table.grid(row=2, column=0, columnspan=3, pady=(8, 6), sticky="n")
        self.next.grid(row=3, column=1)



################################################################################
# Tuples for use in frame lists

IntroCoordination = (
    InstructionsFrame,
    {
        "text": instructionsC0,
        "height": "auto",
        "width": 80,
        "font": 15,
    },
)

NextRoundInfo = (
    InstructionsFrame,
    {
        "text": nextRoundText,
        "height": "auto",
        "width": 80,
        "font": 15,
    },
)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    from intros import Ending
    from games import WaitResults

    GUI([
        Login,
        IntroCoordination,
        InstructionsCoordination,
        *([CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame, NextRoundInfo] * (COORDINATION_ROUNDS-1)),
        CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame,
        WaitResults,
        Ending,
    ])
