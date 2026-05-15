#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from collections import deque
from time import perf_counter, sleep
from math import ceil
import re

import random
import os

from common import ExperimentFrame, InstructionsFrame, Question, Measure, read_all
from gui import GUI
from constants import TESTING, AUTOFILL, ATTENTION_BONUS


################################################################################
# TEXTS questionnaire

questintro = """V následující části studie budete řešit krátké číselné úlohy a odpovídat na otázky o sobě."""

questintro2 = """V následující části studie budete odpovídat na otázky o sobě, Vašich postojích a názorech."""

attentiontext = "Chcete-li prokázat, že zadání věnujete pozornost, vyberte možnost "

bonusGained = "Protože jste odpověděl(a) správně na {}, získáváte dalších {} Kč."
bonusNotGained = "Protože jste neodpověděl(a) správně na vžádnou kontrolní otázku, nezískáváte žádnou další odměnu."
oneCheck = "jednu kontrolní otázku"
twoChecks = "obě kontrolní otázky"

intro = "Označte, do jaké míry souhlasíte s následujícími tvrzeními, na poskytnuté škále."

uppsIntro = """Přečtěte si prosím každé tvrzení a označte, nakolik s ním souhlasíte."""
samsIntro = """Všechny následující položky se vztahují k otázce: <b>"Proč se vzděláváte?"</b>
Ohodnoťte, do jaké míry nakolik každá položka odpovídá Vaší situaci."""
sciIntro1 = "<b>Když se zamyslíte nad typickou nocí v posledním měsíci…</b>"
sciIntro2 = "\nKdyž se zamyslíte nad uplynulým měsícem, do jaké míry špatný spánek"
sciIntro3 = "\nNakonec…"
mindsetIntro = "Do jaké míry souhlasíte nebo nesouhlasíte s těmito tvrzeními?"

narcissismIntro = "Uveďte prosím, do jaké míry je pro Vás každé z následujících tvrzení typické. Použijte uvedenou škálu."

transactionValueIntro = """Níže jsou uvedena tvrzení týkající se cenových nabídek. U každého tvrzení označte, nakolik s ním souhlasíte."""

numeracyIntro = """Na této obrazovce budete řešit několik krátkých početních úloh.
Odpovězte prosím na následující otázky."""

salesPronenessIntro = """Níže jsou uvedena tvrzení týkající se cenových nabídek produktů. U každého tvrzení označte, nakolik s ním souhlasíte."""

NUMERACY_ITEMS = [
    {
        "id": "1",
        "text": "V malém městě je z 1 000 obyvatel 500 členy pěveckého sboru. Z těchto 500 členů sboru je 100 mužů. Z 500 obyvatel, kteří členy sboru nejsou, je 300 mužů. Jaká je pravděpodobnost, že náhodně vybraný muž je členem sboru? Uveďte prosím pravděpodobnost v procentech.",
        "unit": "%",
    },
    {
        "id": "2",
        "text": "Představte si, že padesátkrát hodíme pětistěnnou kostkou. Kolikrát by tato kostka v průměru z těchto 50 hodů ukázala liché číslo (1, 3 nebo 5)?",
        "unit": "z 50 hodů",
    },
    {
        "id": "3",
        "text": "Představte si, že házíme nevyváženou kostkou (se 6 stranami). Pravděpodobnost, že padne číslo 6, je dvakrát vyšší než pravděpodobnost každého z ostatních čísel. Kolikrát by v průměru z těchto 70 hodů padlo číslo 6?",
        "unit": "z 70 hodů",
    },
    {
        "id": "4",
        "text": "V lese je 20 % hub červených, 50 % hnědých a 30 % bílých. Pravděpodobnost, že červená houba je jedovatá, je 20 %. Pravděpodobnost, že houba, která není červená, je jedovatá, je 5 %. Jaká je pravděpodobnost, že jedovatá houba v lese je červená?",
        "unit": "%",
    },
]

################################################################################





class Questionnaire(ExperimentFrame):
    def __init__(self, root, words, question = "", labels = None, blocksize = 4, values = 7, text = True,
                 filetext = "", fontsize = 15, labelwidth = None, wraplength = 0, pady = 0, fixedlines = 0, randomize = False, perpage = 0, questionnaireHeight = "auto", labelFontsize = "auto"):
        super().__init__(root)

        self.fontsize = fontsize
        self.blocksize = blocksize
        self.values = values
        self.text = text
        self.fixedlines = fixedlines
        self.labelwidth = labelwidth
        self.wraplength = wraplength
        self.pady = pady
        self.question = question
        self.answers = labels
        self.perpage = perpage
        self.labelFontsize = labelFontsize if labelFontsize != "auto" else self.fontsize

        if filetext:
            self.file.write(filetext + "\n")

        if type(words) == str and os.path.exists(os.path.join(os.path.dirname(__file__), words)):
            self.allwords = read_all(os.path.join(os.path.dirname(__file__), words)).split("\n")
        else:
            self.allwords = words
        if randomize:
            random.shuffle(self.allwords)
        if perpage and len(self.allwords) > perpage:
            self.screen = 1                      
            self.words = self.allwords[:perpage]
        else:
            self.words = self.allwords

        self.buttons = {}
        self.variables = {}
        self.labels = {}

        self.frame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.frame.grid(column = 1, row = 1, sticky = NSEW, pady = 10)
        self.createWidgets()
        if questionnaireHeight != "auto":
            self.filler = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white", height = questionnaireHeight, width = 1)
            self.filler.grid(column = 0, row = 1, sticky = NSEW)

        self.question = ttk.Label(self, text = self.question, background = "white", font = "helvetica 15")
        self.question.grid(column = 1, row = 0, sticky = S, pady = 10)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 2)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 2)
        self.rowconfigure(3, weight = 1)

    def createWidgets(self):
        maxwidth = max(map(len, self.words))

        for count, word in enumerate(self.words, 1):
            self.variables[word] = StringVar()
            #if AUTOFILL:
            #    self.variables[word].set(random.randint(1, self.values))
            for i in range(1, self.values+1):
                if word not in self.buttons:
                    self.buttons[word] = {}
                valuetext = str(i) if self.text else ""
                self.buttons[word][i] = ttk.Radiobutton(self.frame, text = valuetext, value = i,
                                                        command = self.clicked,
                                                        variable = self.variables[word])
                self.buttons[word][i].grid(column = i+1, row = count + (count-1)//self.blocksize, padx = 15)

            if self.fixedlines:
                fillerlabel = ttk.Label(self.frame, text = "l" + "\nl"*int(self.fixedlines - 1), background = "white", foreground = "white", font = "helvetica {}".format(self.fontsize))
                fillerlabel.grid(column = 0, row = count + (count-1)//self.blocksize, pady = self.pady)

            self.labels[word] = ttk.Label(self.frame, text = word, background = "white",
                                          font = "helvetica {}".format(self.fontsize), justify = "left",
                                          width = maxwidth/1.2, wraplength = self.wraplength)
            self.labels[word].grid(column = 1, row = count + (count-1)//self.blocksize, padx = 15, sticky = W, pady = self.pady)
            if not count % self.blocksize:
                self.frame.rowconfigure(count + count//self.blocksize, weight = 1)

        avg_char_width = tkfont.Font(family="helvetica", size=self.fontsize).measure("s")
        if self.wraplength:
            fillerSize = min([int(ceil(maxwidth/(1+maxwidth/1000))), self.wraplength//avg_char_width])
        else:
            fillerSize = int(ceil(maxwidth/(1+maxwidth/1000)))
        fillerLabel = ttk.Label(self.frame, text = "s"*fillerSize, background = "white", font = "helvetica {}".format(self.fontsize+1), foreground = "white", justify = "left", width = maxwidth/1.2, wraplength = self.wraplength)
        fillerLabel.grid(column = 1, padx = 15, sticky = W, row = count + 1 + (count-1)//self.blocksize)

        self.texts = []
        if not self.answers:
            self.answers = [""]*self.values
        elif len(self.answers) != self.values:
            self.answers = [self.answers[0]] + [""]*(self.values - 2) + [self.answers[-1]]

        for count, label in enumerate(self.answers):
            _lw = self.labelwidth * tkfont.Font(family="helvetica", size=self.labelFontsize, weight="normal").measure("0") if self.labelwidth else 0
            self.texts.append(ttk.Label(self.frame, text = label, background = "white",
                                        font = "helvetica {}".format(self.labelFontsize), anchor = "center",
                                        justify = "center", wraplength = _lw))
            if self.labelwidth:
               self.texts[count]["width"] = self.labelwidth,
            self.texts[count].grid(column = count+2, row = 0, sticky = W, pady = 4, padx = 3)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica {}".format(self.fontsize))

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun, state = "disabled")
        self.next.grid(column = 1, row = 2)

    def nextFun(self):
        if self.perpage and len(self.allwords) > self.screen * self.perpage:
            self.write()
            self.screen += 1
            self.words = self.allwords[(self.screen-1)*self.perpage:self.screen*self.perpage]
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.buttons = {}
            self.variables = {}
            self.labels = {}
            self.createWidgets()
            return
        return super().nextFun()

    def clicked(self):
        end = True
        for word in self.words:
            if not self.variables[word].get():
                end = False
            else:
                self.labels[word]["foreground"] = "grey"
        if end:
            self.next["state"] = "!disabled"

    def write(self):
        for word in self.words:
            self.file.write(self.id + "\t" + word + "\t" + self.variables[word].get() + "\n")

    def gothrough(self):
        for i in range(ceil(len(self.allwords)/self.perpage)):
            for word in self.words:
                choice = random.randint(1, self.values)
                self.buttons[word][choice].invoke()
            self.update()
            sleep(0.5)
            self.next.invoke()


class MeasureQuestionnaire(InstructionsFrame):
    def __init__(self, root, text, questions, options, filetext = "", **kwargs):
        super().__init__(root, text = text, proceed = True, savedata = True)

        self.root = root
        self.questions = self.load_questions(questions)
        self.options = self.load_options(options, len(self.questions))
        self.filetext = filetext
        self.measures = []

        left = kwargs.pop("left", "")
        right = kwargs.pop("right", "")

        for count, question in enumerate(self.questions, start = 2):
            measure = Measure(self, text = question, values = self.options[count - 2], left = left, right = right, function = self.enable, **kwargs)
            measure.grid(row = count, column = 1, sticky = EW)
            self.measures.append(measure)

        self.next.grid(row = len(self.measures) + 2, column = 1)

        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 1)
        for row in range(2, len(self.measures) + 2):
            self.rowconfigure(row, weight = 1)
        self.rowconfigure(len(self.measures) + 2, weight = 2)
        self.rowconfigure(len(self.measures) + 3, weight = 3)

        self.next["state"] = "disabled"

    @staticmethod
    def load_questions(questions):
        if isinstance(questions, str) and os.path.exists(os.path.join(os.path.dirname(__file__), questions)):
            return [line for line in read_all(questions).split("\n") if line]
        return list(questions)

    @staticmethod
    def load_options(options, question_count):
        if isinstance(options, str) and os.path.exists(os.path.join(os.path.dirname(__file__), options)):
            option_sets = [line.split("\t") for line in read_all(options).split("\n") if line]
        else:
            option_sets = list(options)

        if option_sets and isinstance(option_sets[0], (list, tuple)):
            if len(option_sets) == 1:
                return [list(option_sets[0]) for _ in range(question_count)]
            if len(option_sets) != question_count:
                raise ValueError("Options count must match questions count or contain exactly one shared option set.")
            return [list(option_set) for option_set in option_sets]

        return [list(option_sets) for _ in range(question_count)]

    def enable(self):
        if all(measure.answer.get() for measure in self.measures):
            self.next["state"] = "normal"
        else:
            self.next["state"] = "disabled"

    def write(self):
        if self.filetext:
            self.file.write(self.filetext + "\n")
        self.file.write(self.id + "\t" + "\t".join(measure.answer.get() for measure in self.measures) + "\n\n")

    def gothrough(self):
        for measure in self.measures:
            random.choice(measure.radios).invoke()
        self.update()
        sleep(0.5)
        self.next.invoke()


class Numeracy(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        self.file.write("Numeracy\n")

        self.vars = []
        self.entries = []
        self.vcmd = (self.register(self._validate_number), "%P")

        self.instructions = ttk.Label(
            self,
            text = numeracyIntro,
            background = "white",
            font = "helvetica 15",
            justify = "center",
            wraplength = 1100,
        )
        self.instructions.grid(row = 0, column = 1, pady = (10, 20))

        self.form = Frame(self, background = "white")
        self.form.grid(row = 1, column = 1, sticky = NSEW)

        for idx, item in enumerate(NUMERACY_ITEMS, start = 1):
            question = ttk.Label(
                self.form,
                text = f"{item['id']}. {item['text']}",
                background = "white",
                font = "helvetica 15",
                justify = "left",
                wraplength = 1030,
            )
            question.grid(row = (idx - 1) * 2, column = 0, columnspan = 3, sticky = W, pady = (35, 2))

            var = StringVar()
            var.trace_add("write", self._on_change)
            self.vars.append(var)

            entry = ttk.Entry(
                self.form,
                textvariable = var,
                width = 14,
                font = "helvetica 15",
                justify = "center",
                validate = "key",
                validatecommand = self.vcmd,
            )
            entry.grid(row = (idx - 1) * 2 + 1, column = 0, sticky = W, padx = (10, 8), pady = (2, 0))
            self.entries.append(entry)

            unit_label = ttk.Label(self.form, text = item["unit"], background = "white", font = "helvetica 15")
            unit_label.grid(row = (idx - 1) * 2 + 1, column = 1, sticky = W, pady = (2, 0))

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun, state = "disabled")
        self.next.grid(row = 2, column = 1, pady = 10)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 2)  # space above + instructions
        self.rowconfigure(1, weight = 3)  # form area
        self.rowconfigure(2, weight = 1)  # button
        self.rowconfigure(3, weight = 2)  # space below

        self.form.columnconfigure(2, weight = 1)
        # distribute vertical space evenly between entry rows inside the form
        for _entry_row in range(1, len(NUMERACY_ITEMS) * 2, 2):
            self.form.rowconfigure(_entry_row, weight = 1)

    @staticmethod
    def _validate_number(proposed):
        if proposed == "":
            return True
        normalized = proposed.replace(",", ".")
        return bool(re.fullmatch(r"[0-9]*\.?[0-9]*", normalized)) and normalized.count(".") <= 1

    @staticmethod
    def _normalize_number(value):
        return value.strip().replace(",", ".")

    def _is_complete(self):
        for var in self.vars:
            value = self._normalize_number(var.get())
            if not value or value == ".":
                return False
            try:
                float(value)
            except ValueError:
                return False
        return True

    def _on_change(self, *_):
        self.next["state"] = "normal" if self._is_complete() else "disabled"

    def write(self):
        for item, var in zip(NUMERACY_ITEMS, self.vars):
            answer = self._normalize_number(var.get())
            self.file.write(self.id + "\t" + item["id"] + "\t" + answer + "\n")
        self.file.write("\n")

    def check(self):
        return self._is_complete()

    def gothrough(self):
        autofill_values = ["25", "30", "20", "50"]
        for var, value in zip(self.vars, autofill_values):
            var.set(value)
        self.update()
        sleep(0.5)
        self.next.invoke()


class BlockQuestionnaire(InstructionsFrame):
    def __init__(self, root, perpage, file, name, left, right, options = 5, shuffle = True,
                 instructions = "", height = 3, width = 80, center = False, checks = 0, endChecks = False,
                 wraplength = "auto"):
        super().__init__(root, text = instructions, proceed = False, height = height, width = width)

        self.perpage = perpage
        self.left = left
        self.right = right
        self.options = options
        self.checks = checks != 0
        self.checksNumber = checks
        self.endChecks = endChecks
        self.name = name
        self.wraplength = wraplength

        self.file.write("{}\n".format(name))

        if center:
            self.text.config(state = "normal")
            self.text.tag_add("center", "1.0", "end")
            self.text.config(state = "disabled")

        self.questions = [i for i in read_all(file, comments = True).split("\n")]
        # with open(os.path.join("Stuff", file), encoding = "utf-8") as f:
        #     for line in f:
        #         self.questions.append(line.strip())

        if shuffle:
            random.shuffle(self.questions)

        if checks:
            if checks > 1:
                spread = len(self.questions)//checks
                positions = [random.randint(self.perpage//2 + spread*i, spread*(i+1) - self.perpage//2) for i in range(checks)]                
            else:
                positions = [random.randint(2, len(self.questions))]
            for i in range(checks):
                self.questions.insert(positions[i], attentiontext + str(random.randint(1, options)) + ".")

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun, state = "disabled")
        self.next.grid(row = self.perpage*2 + 4, column = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 2)
        for i in range(2, self.perpage*2 + 4):
            self.rowconfigure(i, weight = 0)
        self.rowconfigure(self.perpage*2 + 4, weight = 1)
        self.rowconfigure(self.perpage*2 + 5, weight = 3)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)

        self.mnumber = 0
        
        self.createQuestions()

    def createQuestions(self):
        self.measures = []
        for i in range(self.perpage):
            m = Likert(self, self.questions[self.mnumber], shortText = str(self.mnumber + 1),
                       left = self.left, right = self.right, options = self.options, wraplength=self.wraplength)
            m.grid(column = 0, columnspan = 3, row = i*2 + 3)
            self.rowconfigure(i*2 + 4, weight = 1)
            self.mnumber += 1
            self.measures.append(m)
            if self.mnumber == len(self.questions):
                break

    def nextFun(self):
        for measure in self.measures:
            measure.write()
            measure.grid_forget()
        if self.mnumber == len(self.questions):
            self.file.write("\n")
            if self.endChecks:
                self.file.write("Attention checks\n")
                correct_checks = str(self.root.status["attention_checks"])
                self.file.write(self.id + "\t" + self.name + "\t" + correct_checks + "\n\n")
                if int(correct_checks) > 0:
                    self.root.status["results"] += [bonusGained.format(oneCheck if int(correct_checks) == 1 else twoChecks, int(correct_checks) * ATTENTION_BONUS)]
                    self.root.status["reward"] += int(correct_checks) * ATTENTION_BONUS
                else:
                    self.root.status["results"] += [bonusNotGained]
            self.destroy()
            self.root.nextFrame()
        else:
            self.next["state"] = "disabled"
            self.createQuestions()

    def check(self):
        for m in self.measures:
            if not m.answer.get():
                return
        else:
            self.next["state"] = "!disabled"

    def gothrough(self):
        if not hasattr(self, 'goingThrough'):
            self.goingThrough = True
            
        # Safety check: ensure widget still exists
        if not self.winfo_exists():
            return
            
        # Only proceed if we're still in the going-through state
        if not self.goingThrough:
            return
            
        print(f"DEBUG: BlockQuestionnaire gothrough - page {self.mnumber}/{len(self.questions)}, measures: {len(self.measures)}")
            
        for m in self.measures:
            choice = random.randint(1, self.options)
            m.answer.set(str(choice))
            
        # Safety check before accessing button
        if self.winfo_exists() and hasattr(self, 'next') and self.next.winfo_exists():
            self.next["state"] = "!disabled"
            self.update()
            sleep(0.5)
            
            # Check if we need to continue to next page BEFORE invoking next
            has_more_questions = self.mnumber < len(self.questions)
            
            # Click next to advance to next page (or finish questionnaire)
            self.next.invoke()
            
            # If there are more questions, schedule gothrough for the new page after a delay
            if has_more_questions and self.goingThrough:
                print("DEBUG: BlockQuestionnaire scheduling gothrough for next page")
                # Delay the recursive call to allow the new page to fully initialize
                self.after(100, self._continue_gothrough)
            else:
                # End the gothrough process cleanly
                print("DEBUG: BlockQuestionnaire gothrough completed")
                self.goingThrough = False

    def _continue_gothrough(self):
        """Continue gothrough on the next page after initialization delay"""
        if self.goingThrough and self.winfo_exists():
            print("DEBUG: BlockQuestionnaire continuing gothrough on new page")
            self.gothrough()
        else:
            print("DEBUG: BlockQuestionnaire gothrough cancelled or widget destroyed")
            self.goingThrough = False




class Likert(Canvas):
    def __init__(self, root, text, options = 5, shortText = "", left = "strongly disagree", right = "strongly agree", wraplength = "auto"):
        super().__init__(root)

        if wraplength == "auto":
            if hasattr(root.root, "screenwidth"):
                wraplength = root.root.screenwidth * 0.9
            elif hasattr(root, "screenwidth"):
                root.screenwidth * 0.9
            else:
                wraplength = 900

        self.root = root
        self.text = text
        self.short = shortText
        self.answer = StringVar()
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")

        self.question = ttk.Label(self, text = text, background = "white", anchor = "center", font = "helvetica 15", wraplength=wraplength)
        self.question.grid(column = 0, row = 0, columnspan = options + 2, sticky = S)

        self.left = ttk.Label(self, text = left, background = "white", font = "helvetica 14")
        self.right = ttk.Label(self, text = right, background = "white", font = "helvetica 14")
        self.left.grid(column = 0, row = 1, sticky = E, padx = 5)
        self.right.grid(column = options + 1, row = 1, sticky = W, padx = 5)           

        for value in range(1, options + 1):
            ttk.Radiobutton(self, text = str(value), value = value, variable = self.answer,
                            command = self.check).grid(row = 1, column = value, padx = 4)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(options + 1, weight = 1)
        self.rowconfigure(0, weight = 1)


    def write(self):
        if attentiontext in self.text:
            if not "attention_checks" in self.root.root.status:
                self.root.root.status["attention_checks"] = 0
            if self.answer.get() == self.text[-2]:
                self.root.root.status["attention_checks"] += 1
        else:
            ans = "{}\t{}\t{}\n".format(self.short, self.answer.get(), self.text.replace("\t", " "))
            self.root.file.write(self.root.id + "\t" + ans)


    def check(self):
        self.root.check()


Narcissism = (Questionnaire,
              {"words": "bpni.txt",
               "question": narcissismIntro,
               "labels": ["Vůbec se mi\nnepodobá", "Velmi se mi\npodobá"],
               "values": 6,
               "randomize": True,
               "perpage": 7,
               "blocksize": 7,
               "wraplength": 620,
               "labelwidth": 8,
               "fixedlines": 2,
               "filetext": "Narcissism"})




TransactionValue = (MeasureQuestionnaire,
                {"text": transactionValueIntro,
                    "questions": "transactionValue.txt",
                    "options": [1, 2, 3, 4, 5, 6, 7],
                    "filetext": "TransactionValue",
                    "left": "Rozhodně souhlasím",
                    "right": "Rozhodně nesouhlasím",
                    "questionPosition": "above",
                    "labelPosition": "next",
                    "filler": 300})


SalesProneness = (MeasureQuestionnaire,
                {"text": salesPronenessIntro,
                    "questions": "salesProneness.txt",
                    "options": [1, 2, 3, 4, 5, 6, 7],
                    "filetext": "SalesProneness",
                    "left": "Rozhodně nesouhlasím",
                    "right": "Rozhodně souhlasím",
                    "questionPosition": "above",
                    "labelPosition": "next",
                    "filler": 430})


# class Hexaco(BlockQuestionnaire):
#     def __init__(self, root):
#         super().__init__(root, 9, "hexaco.txt", "Hexaco", instructions = hexacoinstructions, width = 85,
#                          left = "silně nesouhlasím", right = "silně souhlasím",
#                          height = 3, options = 5, center = True, checks = 3)


QuestInstructions = (InstructionsFrame, {"text": questintro, "height": 15})
QuestInstructions2 = (InstructionsFrame, {"text": questintro2, "height": 15})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([SalesProneness, Narcissism, TransactionValue, Numeracy])