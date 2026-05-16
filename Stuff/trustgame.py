from tkinter import *
from tkinter import ttk
from time import sleep

import random
import os

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding, Wait
from gui import GUI
from constants import URL, TRUST_ENDOWMENT, TRUST_ROUNDS
from login import Login


################################################################################
# TEXTS
instructionsT0 = """Nyní začíná další úloha.

Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři.

Pozorně si přečtěte pokyny na další obrazovce, abyste porozuměl(a) úloze a své roli v ní."""


instructionsT1 = """Tato úloha se skládá z {} kol. V každém kole budete náhodně spárován(a) s dalším účastníkem studie. Oba obdržíte {} Kč.

Bude Vám náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role. Protože nebudete předem vědět, jak by se rozhodl druhý účastník jako hráč A, budete uvádět své volby pro různé možnosti jeho rozhodnutí.

Tuto úlohu budete hrát celkem {}krát. Před každým kolem dostanete informaci o slovech blízkých druhému hráči, která vybral v dřívější části studie. On bude podobně vědět, jaká slova jsou blízká Vám. 

Vaše odměna bude záviset na jednom náhodně vybraném kole. Na konci studie se dozvíte, jaká byla ve vybraném kole Vaše role a jaký je výsledek rozhodnutí Vás a druhého účastníka.

Pro ověření pochopení úlohy odpovězte na kontrolní otázky níže."""


intstuctionsT2a = "Pro účastníka studie, s kterým jste spárován(a), jsou blízká tato slova:"


instructionsT2 = """On podobně bude vědět, jaká slova jsou blízká Vám.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Svou volbu učiňte posunutím modrých ukazatelů níže.

{}"""

endA = "<b>Nejprve se rozhodněte, kolik peněz pošlete hráči B, pokud bude náhodně vybráno, že jste hráč A.</b>"
endPrediction = "<b>Nyní uveďte pomocí ukazatele, kolik očekáváte, že Vám pošle zpět hráč B, pokud bude náhodně vybráno, že jste hráč A.</b>"
endB = "<b>Nakonec u všech možností uveďte pomocí ukazatele, kolik pošlete zpět hráči A, pokud bude náhodně vybráno, že jste hráč B.</b>"


trustControl1 = "Jaká je role hráče A a hráče B ve studii?"
trustAnswers1 = [
    "Hráč A rozhoduje, kolik vezme hráči B peněz a hráč B se rozhoduje, kolik vezme hráči A peněz na oplátku.",
    "Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči A\njakékoli množství dostupných peněz zpět.",
    "Hráči A a B se rozhodují, kolik si navzájem pošlou peněz. Transfer peněz mezi nimi je dán rozdílem poslaných peněz.",
    "Hráč A se rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí. Hráč B může vzít hráči A\njakékoli množství peněz, které hráči A zůstaly.",
]
trustFeedback1 = [
    "Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči A jakékoli množství dostupných peněz zpět.",
    "Správná odpověď.",
    "Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči A jakékoli množství dostupných peněz zpět.",
    "Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči A jakékoli množství dostupných peněz zpět.",
]


trustControl2 = "Jakou odměnu obdrží hráč A, pokud hráči B pošle 20 Kč a ten mu pošle zpět 30 Kč?"
trustAnswers2 = ["20 Kč (40 - 3 × 20 + 30)", "50 Kč (40 - 20 + 30)", "80 Kč (40 + 3 × (30 - 20))", "130 Kč (40 - 20 + 3 × 30)"]
trustFeedback2 = [
    "Chybná odpověď. Hráč A obdrží 40 Kč, z kterých 20 Kč pošle hráči B, zbyde mu tedy 20 Kč, ke kterým obdrží od hráče B 30 Kč, tj. na konec obdrží 50 Kč (40 - 20 + 30).",
    "Správná odpověď.",
    "Chybná odpověď. Hráč A obdrží 40 Kč, z kterých 20 Kč pošle hráči B, zbyde mu tedy 20 Kč, ke kterým obdrží od hráče B 30 Kč, tj. na konec obdrží 50 Kč (40 - 20 + 30).",
    "Chybná odpověď. Hráč A obdrží 40 Kč, z kterých 20 Kč pošle hráči B, zbyde mu tedy 20 Kč, ke kterým obdrží od hráče B 30 Kč, tj. na konec obdrží 50 Kč (40 - 20 + 30).",
]


trustControl3 = "Jakou odměnu obdrží hráč B, pokud hráč A pošle 20 Kč a hráč B mu pošle zpět 30 Kč?"
trustAnswers3 = ["30 Kč (40 + 20 - 30)", "70 Kč (40 + 3 × 20 - 30)", "100 Kč (40 + 3 × 30 - 20)", "130 Kč (40 + 3 × 20 + 30)"]
trustFeedback3 = [
    "Chybná odpověď. Hráč B obdrží 40 Kč, ke kterým obdrží 60 Kč od hráče A (poslaných 20 Kč se ztrojnásobí) a následně pošle hráči A 30 Kč, tj. na konec obdrží 70 Kč (40 + 3 × 20 - 30).",
    "Správná odpověď.",
    "Chybná odpověď. Hráč B obdrží 40 Kč, ke kterým obdrží 60 Kč od hráče A (poslaných 20 Kč se ztrojnásobí) a následně pošle hráči A 30 Kč, tj. na konec obdrží 70 Kč (40 + 3 × 20 - 30).",
    "Chybná odpověď. Hráč B obdrží 40 Kč, ke kterým obdrží 60 Kč od hráče A (poslaných 20 Kč se ztrojnásobí) a následně pošle hráči A 30 Kč, tj. na konec obdrží 70 Kč (40 + 3 × 20 - 30).",
]


checkButtonText3 = "Rozhodl(a) jsem se u všech možností"
checkButtonText2 = "Uvedl(a) jsem svou předpověď"
checkButtonText = "Uvedl(a) jsem své rozhodnutí"


################################################################################


class ScaleFrame(Canvas):
    def __init__(self, root, font=15, maximum=0, player="A", returned=0, endowment=TRUST_ENDOWMENT):
        super().__init__(root, background="white", highlightbackground="white", highlightcolor="white")

        self.parent = root
        self.root = root.root
        self.rounding = maximum / 5 if player == "A" else endowment / 5
        self.player = player
        self.returned = returned
        self.font = font
        self.endowment = endowment
        self.maximum = maximum

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background="white")

        self.value = ttk.Scale(self, orient=HORIZONTAL, from_=0, to=maximum, length=400, variable=self.valueVar, command=self.changedValue)
        self.value.bind("<Button-1>", self.onClick)

        self.playerText1 = "Já:" if player == "A" or player == "prediction" else "Hráč A:"
        self.playerText2 = "Hráč B:" if player == "A" or player == "prediction" else "Já:"
        self.totalText1 = "{0:3d} Kč"
        self.totalText2 = "{0:3d} Kč"

        self.valueLab = ttk.Label(self, textvariable=self.valueVar, font="helvetica {}".format(font), background="white", width=3, anchor="e")
        self.currencyLab = ttk.Label(self, text="Kč", font="helvetica {}".format(font), background="white", width=6)

        self.value.grid(column=1, row=1, padx=10)
        self.valueLab.grid(column=3, row=1)
        self.currencyLab.grid(column=4, row=1)

        fg = "white" if self.player == "prediction" else "black"

        self.playerLab1 = ttk.Label(self, text=self.playerText1, font="helvetica {}".format(font), background="white", width=6, anchor="e", foreground=fg)
        self.playerLab2 = ttk.Label(self, text=self.playerText2, font="helvetica {}".format(font), background="white", width=6, anchor="e", foreground=fg)
        self.totalLab1 = ttk.Label(self, text=self.totalText1.format(0), font="helvetica {}".format(font), background="white", width=6, anchor="e", foreground=fg)
        self.totalLab2 = ttk.Label(self, text=self.totalText2.format(0), font="helvetica {}".format(font), background="white", width=6, anchor="e", foreground=fg)
        self.spaces = ttk.Label(self, text=" ", font="helvetica {}".format(font), background="white", width=1)

        self.playerLab1.grid(column=5, row=1, padx=3)
        self.totalLab1.grid(column=6, row=1, padx=3, sticky="ew")
        self.playerLab2.grid(column=8, row=1, padx=3)
        self.totalLab2.grid(column=9, row=1, padx=3, sticky="ew")
        self.spaces.grid(column=7, row=1)

        self.changedValue(0)

    def showPrediction(self):
        self.playerLab1["foreground"] = "black"
        self.playerLab2["foreground"] = "black"
        self.totalLab1["foreground"] = "black"
        self.totalLab2["foreground"] = "black"
        self.changedValue(0)

    def onClick(self, event):
        if self.value.instate(["disabled"]):
            return
        click_position = event.x
        newValue = int((click_position / self.value.winfo_width()) * self.value['to'])
        self.changedValue(newValue)
        self.update()

    def changedValue(self, value):
        value = str(min([max([eval(str(value)), 0]), self.maximum]))
        self.valueVar.set(value)
        newval = int(round(eval(self.valueVar.get()) / self.rounding, 0) * self.rounding)
        self.valueVar.set("{0:3d}".format(newval))
        if self.player == "A":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - newval)
            self.totalLab2["text"] = self.totalText2.format(self.endowment + newval * 3)
            self.totalLab1["font"] = "helvetica {} bold".format(self.font)
            self.playerLab1["font"] = "helvetica {} bold".format(self.font)
        elif self.player == "B":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - self.returned + newval)
            self.totalLab2["text"] = self.totalText2.format(self.returned * 3 + self.endowment - newval)
            self.totalLab2["font"] = "helvetica {} bold".format(self.font)
            self.playerLab2["font"] = "helvetica {} bold".format(self.font)
        elif self.player == "prediction":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - (self.maximum - self.endowment) // 3 + newval)
            self.totalLab2["text"] = self.totalText2.format(self.maximum - newval)
            self.totalLab1["font"] = "helvetica {} bold".format(self.font)
            self.playerLab1["font"] = "helvetica {} bold".format(self.font)


class GroupsFrame(Canvas):
    def __init__(self, root, close):
        super().__init__(root, background="white", highlightbackground="white", highlightcolor="white")

        self.label = ttk.Label(self, text=intstuctionsT2a, font="helvetica 15 bold", background="white")
        self.label.grid(row=0, column=0, pady=10, sticky=W)

        self.closeText = Text(self, wrap=WORD, font="helvetica 15", height=5, width=30, background="white", relief="flat")
        self.closeText.grid(row=1, column=0, pady=10)
        self.closeText.insert("1.0", "\n".join(close))
        self.closeText.config(state=DISABLED)


class Trust(InstructionsFrame):
    def __init__(self, root):
        endowment = TRUST_ENDOWMENT
        text = instructionsT2.format(endowment, int(endowment / 5), endowment, endA)
        super().__init__(root, text=text, height=13, font=15, width=90)

        self.person = self.root.status["trust_groups_order"][self.root.status["trustblock"] - 1]
        close = self.root.status["trust_groups"][self.person]
        self.groupFrame = GroupsFrame(self, close.split("_"))

        self.labA = ttk.Label(self, text="Pokud budu hráč A", font="helvetica 15 bold", background="white")
        self.labA.grid(column=0, row=2, columnspan=3, pady=10)

        self.labR = ttk.Label(self, text="Rozdělení odměn po tomto kroku", font="helvetica 15 bold", background="white", anchor="center", width=30)
        self.labR.grid(column=1, row=2, pady=5, sticky=E)

        self.labX = ttk.Label(self, text="Finální rozdělení odměn", font="helvetica 15 bold", background="white", anchor="center", width=28)
        self.labX.grid(column=1, row=6, pady=5, sticky=E)

        self.frames = {}
        for i in range(8):
            if i < 6:
                txt = "Pokud hráč A pošle {} Kč, pošlu hráči A zpět:".format(int(i * endowment / 5))
                ttk.Label(self, text=txt, font="helvetica 15", background="white").grid(column=0, row=7 + i, pady=1, sticky=E)
                player = "B"
            elif i == 6:
                ttk.Label(self, text="Pošlu hráči B:", font="helvetica 15", background="white").grid(column=0, row=3, pady=1, sticky=E)
                player = "A"
            else:
                ttk.Label(self, text="Očekávám, že hráč B pošle zpět:", font="helvetica 15", background="white").grid(column=0, row=4, pady=1, sticky=E)
                player = "prediction"

            maximum = int(i * 3 * endowment / 5 + endowment) if i < 6 else endowment
            self.frames[i] = ScaleFrame(self, maximum=maximum, player=player, returned=int(i * endowment / 5), endowment=endowment)
            row = 7 + i if i < 6 else i - 3
            self.frames[i].grid(column=1, row=row, pady=1)
            if i != 6:
                self.frames[i].value["state"] = "disabled"

        self.labB = ttk.Label(self, text="Pokud budu hráč B", font="helvetica 15 bold", background="white")
        self.labB.grid(column=0, row=6, columnspan=3, pady=10)

        self.checkVar = BooleanVar()
        ttk.Style().configure("TCheckbutton", background="white", font="helvetica 15")
        self.checkBut = ttk.Checkbutton(self, text=checkButtonText, command=self.checkbuttoned, variable=self.checkVar, onvalue=True, offvalue=False)
        self.checkBut.grid(row=19, column=0, columnspan=3, pady=10)

        self.next.grid(column=0, row=20, columnspan=3, pady=5, sticky=N)
        self.next["state"] = "disabled"

        self.groupFrame.grid(row=0, column=0, columnspan=3, pady=5, sticky=S)
        self.text.grid(row=1, column=0, columnspan=3)

        self.trialLabel = ttk.Label(self, text="Hra {}/{}".format(self.root.status["trustblock"], TRUST_ROUNDS), font="helvetica 15", background="white")
        self.trialLabel.grid(row=0, column=1, columnspan=3, pady=15, padx=20, sticky=NE)

        self.status = "A"

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(18, weight=2)
        self.rowconfigure(20, weight=2)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=2)

    def checkbuttoned(self):
        self.next["state"] = "normal" if self.checkVar.get() else "disabled"

    def nextFun(self):
        if self.status == "A":
            for i, frame in self.frames.items():
                if i != 7:
                    frame.value["state"] = "normal" if not self.checkVar.get() else "disabled"
                else:
                    frame.value["state"] = "normal" if self.checkVar.get() else "disabled"
                    frame.maximum = TRUST_ENDOWMENT + int(self.frames[6].valueVar.get()) * 3
                    frame.value["to"] = frame.maximum
                    frame.showPrediction()
            self.status = "prediction"
            self.checkBut["text"] = checkButtonText2
            self.next["state"] = "disabled"
            self.checkVar.set(False)
            self.changeText(instructionsT2.format(TRUST_ENDOWMENT, int(TRUST_ENDOWMENT / 5), TRUST_ENDOWMENT, endPrediction))
        elif self.status == "prediction":
            for i, frame in self.frames.items():
                if i > 5:
                    frame.value["state"] = "disabled"
                else:
                    frame.value["state"] = "normal"
            self.status = "B"
            self.checkBut["text"] = checkButtonText3
            self.next["state"] = "disabled"
            self.checkVar.set(False)
            self.changeText(instructionsT2.format(TRUST_ENDOWMENT, int(TRUST_ENDOWMENT / 5), TRUST_ENDOWMENT, endB))
        else:
            self.send()
            self.write()
            super().nextFun()

    def send(self):
        block = self.root.status["trustblock"]
        sent_a = self.frames[6].valueVar.get().strip()
        sent_b_list = [self.frames[i].valueVar.get().strip() for i in range(6)]

        # Server contract: trustA<round> carries A's sent amount; trustB<round> carries
        # B's six contingency returns for A sending [0, 8, 16, 24, 32, 40].
        # Send role A decision for this round.
        data_a = {'id': self.id, 'round': "trustA" + str(block), 'offer': sent_a}
        self.sendData(data_a)

        # Send role B contingency decisions for this round (prediction excluded).
        data_b = {'id': self.id, 'round': "trustB" + str(block), 'offer': "_".join(sent_b_list)}
        self.sendData(data_b)

    def write(self):
        block = self.root.status["trustblock"]
        self.file.write("Trust\n")
        key = self.root.status["trust_groups_order"][block - 1]
        d = [self.id, str(block), key, self.root.status["trust_groups"][key]]
        self.responses = [self.frames[i].valueVar.get().strip() for i in range(8)]
        self.file.write("\t".join(map(str, d + self.responses)))
        self.file.write("\n\n")

        if "trust_decisions" not in self.root.status:
            self.root.status["trust_decisions"] = {}
        self.root.status["trust_decisions"][block] = {
            "sentA": int(self.frames[6].valueVar.get()),
            "sentB_list": [int(self.frames[i].valueVar.get()) for i in range(6)],
        }
        self.root.status["trustblock"] = block + 1

    def gothrough(self):
        # Phase A: choose how much to send as player A.
        sent_a = random.choice([0, 20, 40, 60, 80, 100])
        self.frames[6].value.set(sent_a)
        self.update()
        self.checkVar.set(True)
        self.update()
        self.checkbuttoned()
        sleep(0.05)
        self.nextFun()

        # Prediction phase.
        prediction_max = self.frames[7].maximum
        prediction = random.randint(0, prediction_max // 10) * 10
        self.frames[7].value.set(prediction)
        self.update()
        self.checkVar.set(True)
        self.update()
        self.checkbuttoned()
        sleep(0.05)
        self.nextFun()

        # Phase B: for each possible sent amount, choose return amount.
        for i in range(6):
            max_return = self.frames[i].maximum
            returned = random.randint(0, max_return // 10) * 10
            self.frames[i].value.set(returned)
            self.update()
        self.checkVar.set(True)
        self.update()
        self.checkbuttoned()
        sleep(0.05)
        self.nextFun()


class WaitGroups(Wait):
    def __init__(self, root):
        super().__init__(root, what="groups")

    def test(self):
        groups_path = os.path.join(os.getcwd(), "Stuff", "groups.txt")
        with open(groups_path, "r", encoding="utf-8") as f:
            all_groups = [line.strip() for line in f if line.strip()]
        persons = []
        ids = []
        for _ in range(TRUST_ROUNDS):
            ids.append("real{}".format(_ + 1))
            close = "_".join(random.sample(all_groups, min(5, len(all_groups))))
            persons.append(close)
        return "_".join(ids) + "!" + "~".join(persons)

    def processResponse(self, response):
        text = str(response).strip()
        if "!" in text:
            ids_part, groups_part = text.split("!", 1)
            order = [pid for pid in ids_part.split("_") if pid]
            persons = [grp for grp in groups_part.split("~") if grp]
            if len(order) != len(persons):
                order = ["real{}".format(i + 1) for i in range(len(persons))]
        else:
            persons = [grp for grp in text.split("~") if grp]
            order = ["real{}".format(i + 1) for i in range(len(persons))]
        self.root.status["trust_groups_order"] = order
        self.root.status["trust_groups"] = dict(zip(order, persons))
        self.root.status.setdefault("trustblock", 1)


controlTexts = [[trustControl1, trustAnswers1, trustFeedback1], [trustControl2, trustAnswers2, trustFeedback2], [trustControl3, trustAnswers3, trustFeedback3]]
IntroTrust = (InstructionsFrame, {"text": instructionsT0, "height": 6, "width": 80, "font": 15})
InstructionsTrust = (
    InstructionsAndUnderstanding,
    {
        "text": instructionsT1.format(TRUST_ROUNDS, TRUST_ENDOWMENT, TRUST_ENDOWMENT, TRUST_ENDOWMENT // 5, TRUST_ENDOWMENT, TRUST_ROUNDS) + "\n\n",
        "height": 22,
        "width": 100,
        "name": "Trust Control Questions",
        "randomize": False,
        "controlTexts": controlTexts,
        "fillerHeight": 300,
        "finalButton": "Pokračovat k volbě",
    },
)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    from intros import Ending
    from games import WaitResults

    GUI([
        Login,
        WaitGroups,
        IntroTrust,
        InstructionsTrust,
        *([Trust] * TRUST_ROUNDS),
        WaitResults,
        Ending,
    ])
