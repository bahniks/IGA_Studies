from tkinter import *
from tkinter import ttk
from time import sleep
import random
import os
import re

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding
from gui import GUI
from constants import TESTING, MARKET_ROUNDS, MARKET_ENDOWMENT, MARKET_WIN, MARKET_LOSS
from login import Login


################################################################################
# TEXTS

meIntro0 = """Nyní začíná další úloha.

Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři.

Pozorně si přečtěte pokyny na další obrazovce, abyste porozuměl(a) úloze a své roli v ní."""

meIntro1 = """Tato úloha se skládá z {} kol.

V rámci každého kola této úlohy nejprve vyplníte krátký kvíz sestávající z 5 odhadovacích otázek, kde za správnou odpověď bude považována taková, která spadá do rozmezí ±10 % od skutečné hodnoty.  

V každém kole budete náhodně spárován(a) s dalším účastníkem a budete volit mezi možnostmi: <i>"Vstoupit na trh"</i> nebo <i>"Nevstoupit"</i>

<b>Výplaty:</b>
• Pokud oba účastníci nevstoupí, každý obdrží {} Kč
• Pokud jeden vstoupí a druhý nevstoupí, vstupující obdrží {} Kč a druhý {} Kč
• Pokud vstoupí oba, účastník s vyšším počtem správně zodpovězených otázek v kvízu obdrží {} Kč a druhý {} Kč. V případě shody bude vítěz vybrán náhodně. 

Vaše výsledky v kvízu budou tedy použity při určování výsledků v následné rozhodovací úloze. 

O Vaší odměně za tuto část studie rozhodne jedno náhodně vybrané kolo. Výsledek se dozvíte na konci studie. Výsledky za jednotlivá kola neuvidíte."""

meIntro2 = """Odpovězte prosím na následující otázky. U každé otázky uveďte svůj nejlepší číselný odhad. Odpovědi, které jsou v rozmezí ±10 % od skutečné hodnoty, budou považovány za správné."""

meGameText = """Nyní učiníte své rozhodnutí pro kolo {} z {}.

V tomto kole budete náhodně spárován(a) s dalším účastníkem. Oba se rozhodnete, zda vstoupíte na trh, nebo nevstoupíte.

<b>Připomenutí výplaty:</b>
•  Oba nevstoupí: každý {} Kč
•  Jeden vstoupí, jeden nevstoupí: vstupující {} Kč, druhý {} Kč
•  Oba vstoupí: ten s vyšším počtem správně zodpovězených otázek v kvízu získá {} Kč, ten s nižším {} Kč; v případě shody bude vítěz vybrán náhodně."""

meConfidenceText = "Kolik z právě zodpovězených {} otázek si myslíte, že jste zodpověděl(a) správně?"

# Control questions
meControl1 = "Co se stane, pokud oba účastníci nevstoupí na trh?"
meAnswers1 = ["Oba dostanou {} Kč".format(MARKET_ENDOWMENT),
			  "Oba dostanou 0 Kč",
			  "Oba dostanou {} Kč".format(MARKET_WIN)]
meFeedback1 = ["Správně.",
			   "Nesprávně. Pokud oba nevstoupí, oba obdrží {} Kč.".format(MARKET_ENDOWMENT),
			   "Nesprávně. Pokud oba nevstoupí, oba obdrží {} Kč.".format(MARKET_ENDOWMENT)]

meControl2 = "Co se stane, pokud oba účastníci vstoupí na trh?"
meAnswers2 = ["Výsledek bude záviset na počtu správně zodpovězených otázek v kvízu",
			  "Oba dostanou {} Kč".format(MARKET_WIN),
			  "Oba dostanou {} Kč".format(MARKET_ENDOWMENT)]
meFeedback2 = ["Správně. Účastník s vyšším počtem správně zodpovězených otázek v kvízu získá {} Kč.".format(MARKET_WIN),
			   "Nesprávně. Výsledek bude záviset na počtu správně zodpovězených otázek v kvízu. Účastník s vyšším skóre v kvízu získá {} Kč.".format(MARKET_WIN),
			   "Nesprávně. Výsledek bude záviset na počtu správně zodpovězených otázek v kvízu. Účastník s vyšším skóre v kvízu získá {} Kč.".format(MARKET_WIN)]


meControlTexts = [
	[meControl1, meAnswers1, meFeedback1],
	[meControl2, meAnswers2, meFeedback2],
]

# Quiz question sets: one set per round.
# Each question: (display text, true value for scoring)
# Scoring: answer within 10 % of the true value counts as correct.
ME_QUIZ_QUESTIONS = [

    [
		("Jaká je vzdušná vzdálenost mezi Berlínem a Vídní v kilometrech?", 524),
		("Jaký je počet obyvatel Berlína?", 3600000),
		("Jaký je počet obyvatel Norska?", 5400000),
		("Jaká je výška nejvyšší hory v Evropě v metrech?", 5642),
		("Kolik zemí Evropské unie oficiálně používá euro jako svou měnu?", 21),
    ],

    [
		("Jaký je počet obyvatel Vídně?", 2000000),
		("Jaká je vzdušná vzdálenost mezi Paříží a Berlínem v kilometrech?", 878),
		("Jaká je rozloha Slovinska v kilometrech čtverečních?", 20273),
		("Jaký je počet obyvatel Finska?", 5600000),
		("Jaká je výška Eiffelovy věže v metrech?", 330),
    ],

    [
		("Jaká je oficiální cílová míra inflace Evropské centrální banky v procentech?", 2),
		("Jaká je celková délka řeky Dunaj v kilometrech?", 2850),
		("Jaký je počet obyvatel Rakouska?", 9100000),
		("Jaká je výška London Eye v metrech?", 135),
		("Kolik let trvá oficiální funkční období prezidenta Evropské centrální banky?", 8),
    ],
]


understandingPrompt = "<b>Odpovězte prosím na následující kontrolní otázky, abyste si ověřil(a), že pokynům rozumíte.</b>"

################################################################################


class MarketEntryQuiz(ExperimentFrame):
	"""Two-phase frame: (1) 5 estimation questions, (2) confidence about correct count."""

	def __init__(self, root):
		super().__init__(root)
		if "me_block" not in self.root.status:
			self.root.status["me_block"] = 1

		self.block = self.root.status["me_block"]
		idx = min(self.block - 1, len(ME_QUIZ_QUESTIONS) - 1)
		self.question_set = ME_QUIZ_QUESTIONS[idx]
		self.quiz_raw = []
		self.phase = 1
		self._build_quiz()

	def _validate_numeric_input(self, value):
		"""Allow digits with optional decimal separator (comma or dot)."""
		if value == "":
			return True
		return bool(re.fullmatch(r"\d*([\.,]\d*)?", value))

	def _normalize_numeric_string(self, value):
		"""Normalize user numeric input for parsing (comma decimal -> dot)."""
		return value.replace(",", ".").replace("\u00a0", "").replace(" ", "")

	def _all_quiz_answers_valid(self):
		if not hasattr(self, "entry_vars"):
			return False
		for var in self.entry_vars:
			value = var.get().strip()
			if not value or not self._validate_numeric_input(value):
				return False
		return True

	def _update_quiz_next_state(self, *args):
		if hasattr(self, "next"):
			self.next["state"] = "normal" if self._all_quiz_answers_valid() else "disabled"

	def _build_quiz(self):
		header = ttk.Label(self,
					   text="Kvíz \u2013 kolo {}/{}".format(self.block, MARKET_ROUNDS),
						   font="helvetica 15 bold", background="white")
		header.grid(row=0, column=0, columnspan=3, pady=15)

		intro = Text(self, font="helvetica 15", relief="flat", background="white",
					 width=80, height=3, wrap="word", highlightbackground="white",
					 highlightcolor="white")
		intro.insert("1.0", meIntro2)
		intro.config(state="disabled")
		intro.grid(row=1, column=0, columnspan=3, pady=5)

		self.entry_vars = []
		vcmd = (self.register(self._validate_numeric_input), "%P")
		for i, (q_text, _) in enumerate(self.question_set):
			ttk.Label(self, text=q_text, font="helvetica 15", background="white",
					  wraplength=580, anchor="w", justify="left").grid(
				row=2 + i, column=0, sticky=W, padx=60, pady=4)
			var = StringVar()
			var.trace_add("write", self._update_quiz_next_state)
			ent = ttk.Entry(self, textvariable=var, width=14, font="helvetica 15",
							validate="key", validatecommand=vcmd)
			ent.grid(row=2 + i, column=1, sticky=W, padx=10, pady=4)
			self.entry_vars.append(var)

		ttk.Style().configure("TButton", font="helvetica 15")
		self.next = ttk.Button(self, text="Pokračovat", command=self.nextFun)
		self.next.grid(row=2 + len(self.question_set), column=0, columnspan=3, pady=20)
		self.next["state"] = "disabled"

		self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=2)
		self.rowconfigure(2 + len(self.question_set), weight=2)

	def _build_confidence(self):
		for widget in self.winfo_children():
			widget.destroy()

		ttk.Label(self, text=meConfidenceText.format(len(self.question_set)),
				  font="helvetica 15", background="white",
				  wraplength=700).grid(row=1, column=0, columnspan=3, pady=15)

		self.confidence_var = StringVar()
		ttk.Style().configure("TRadiobutton", background="white", font="helvetica 15")
		conf_frame = Canvas(self, background="white",
							highlightbackground="white", highlightcolor="white")
		conf_frame.grid(row=2, column=0, columnspan=3, pady=10)
		for j in range(len(self.question_set) + 1):
			ttk.Radiobutton(conf_frame, text=str(j), variable=self.confidence_var,
							value=str(j), command=self._enable_next).grid(
				row=0, column=j, padx=8)

		ttk.Style().configure("TButton", font="helvetica 15")
		self.next = ttk.Button(self, text="Pokračovat", command=self.nextFun,
							   state="disabled")
		self.next.grid(row=3, column=0, columnspan=3, pady=20)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=2)
		self.rowconfigure(3, weight=2)

	def _enable_next(self):
		self.next["state"] = "normal"

	def _score_quiz(self):
		"""Count questions answered within 10 % of the true value."""
		score = 0
		for i, (_, correct) in enumerate(self.question_set):
			try:
				raw = self._normalize_numeric_string(self.quiz_raw[i])
				ans = float(raw)
				if correct > 0 and abs(ans - correct) / correct <= 0.10:
					score += 1
			except (ValueError, IndexError):
				pass
		return score

	def nextFun(self):
		if self.phase == 1:
			if not all(v.get().strip() for v in self.entry_vars):
				return
			self.quiz_raw = [v.get().strip() for v in self.entry_vars]
			self.phase = 2
			self._build_confidence()
		else:
			self.send()
			self.write()
			self.destroy()
			self.root.nextFrame()

	def send(self):
		print("Scoring quiz answers:", self.quiz_raw)
		score = self._score_quiz()
		data = {'id': self.id, 'round': "market_entry_quiz" + str(self.block), 'offer': "{}".format(score)}
		self.sendData(data)

	def write(self):
		score = self._score_quiz()
		if "me_quiz_scores" not in self.root.status:
			self.root.status["me_quiz_scores"] = {}
		self.root.status["me_quiz_scores"][self.block] = score

		self.file.write("MarketEntryQuiz\n")
		self.file.write("\t".join(
			[self.id, str(self.block)] + self.quiz_raw + [str(score), self.confidence_var.get()]
		))
		self.file.write("\n\n")

	def gothrough(self):
		sleep(0.1)
		if self.phase == 1:
			for var in self.entry_vars:
				var.set("1000")
			self.quiz_raw = ["1000"] * len(self.entry_vars)
			if hasattr(self, "next"):
				self.next.invoke()
		if self.phase == 2:
			self.confidence_var.set(str(len(self.question_set) // 2))
			self._enable_next()
			sleep(0.1)
			if hasattr(self, "next"):
				self.next.invoke()

################################################################################


class MarketEntryGame(InstructionsFrame):
	"""Decision screen: Enter the market or Stay out."""

	def __init__(self, root):
		block = root.status.get("me_block", 1)
		text = meGameText.format(block, MARKET_ROUNDS,
								 MARKET_ENDOWMENT, MARKET_WIN, MARKET_ENDOWMENT,
								 MARKET_WIN, MARKET_LOSS)
		super().__init__(root, text=text, height=12, font=15, width=80)

		self.block = block
		self.decision_var = StringVar()
		ttk.Style().configure("TButton", background="white", font="helvetica 15")

		choice_frame = Canvas(self, background="white",
							  highlightbackground="white", highlightcolor="white")
		self.enter_button = ttk.Button(choice_frame, text="Vstoupit na trh",
							   width=20,
							   command=lambda: self._choose("enter"))
		self.enter_button.grid(row=0, column=0, padx=30, pady=10, sticky=E)
		self.stayout_button = ttk.Button(choice_frame, text="Nevstoupit",
							   width=20,
							   command=lambda: self._choose("stayout"))
		self.stayout_button.grid(row=0, column=1, padx=30, pady=10, sticky=W)
		choice_frame.grid(row=2, column=0, columnspan=3, pady=15)

		self.trialLabel = ttk.Label(self,
									text="Kolo {}/{}".format(block, MARKET_ROUNDS),
									font="helvetica 15", background="white")
		self.trialLabel.grid(row=0, column=2, pady=15, padx=20, sticky=NE)

		self.rowconfigure(0, weight=2)
		self.rowconfigure(4, weight=2)
		self.columnconfigure(0, weight=2)
		self.columnconfigure(2, weight=2)

	def _choose(self, decision):
		self.decision_var.set(decision)
		self.nextFun()

	def nextFun(self):
		if not self.decision_var.get():
			return
		self.send()
		self.write()
		self.destroy()
		self.root.nextFrame()

	def send(self):
		decision = self.decision_var.get()
		data = {'id': self.id, 'round': "market_entry" + str(self.block), 'offer': "{}".format(decision)}
		self.sendData(data)

	def write(self):
		decision = self.decision_var.get()
		if "me_decisions" not in self.root.status:
			self.root.status["me_decisions"] = {}
		self.root.status["me_decisions"][self.block] = decision
		self.root.status["me_block"] = self.block + 1
		self.file.write("MarketEntryGame\n")
		self.file.write(self.id + "\t" + str(self.block) + "\t" + decision + "\n\n")

	def gothrough(self):
		sleep(0.1)
		if hasattr(self, "enter_button"):
			if random.random() < 0.5:
				self.enter_button.invoke()
			else:
				self.stayout_button.invoke()
		else:
			if random.random() < 0.5:
				self.decision_var.set("enter")
			else:
				self.decision_var.set("stayout")
		sleep(0.1)


################################################################################
# Tuples for use in frame lists

IntroMarketEntry = (InstructionsFrame, {
	"text": meIntro0,
	"height": "auto",
	"width": 80,
	"font": 15,
})

InstructionsMarketEntry = (InstructionsAndUnderstanding, {
	"text": meIntro1.format(MARKET_ROUNDS,
							MARKET_ENDOWMENT,
							MARKET_WIN, MARKET_ENDOWMENT,
							MARKET_WIN, MARKET_LOSS) + "\n\n",
	"height": "auto",
	"width": 90,
	"name": "Kontrolní otázky k úloze vstupu na trh",
	"randomize": False,
	"controlTexts": meControlTexts,
	"fillerHeight": 150,
	"finalButton": "Pokračovat k úloze",
	"prompt": understandingPrompt,
})


################################################################################

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.getcwd()))
	from intros import Ending
	from games import WaitResults
	GUI([Login,
		 #IntroMarketEntry,
		 #InstructionsMarketEntry,
		 *([MarketEntryQuiz, MarketEntryGame] * MARKET_ROUNDS),
		 WaitResults,
		 Ending
		 ])




