#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from time import perf_counter, sleep

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame
from gui import GUI
from constants import TESTING, URL



################################################################################
# TEXTS
NUMGROUPS = 5

closeText = f"""<center>Ze skupin níže vyberte kliknutím na tlačítko {NUMGROUPS} skupin, které jsou Vám nejbližší.
(Dalším kliknutím na tlačítko můžete volbu zrušit.)</center>"""

remainingText = "Zbývá vybrat skupin: {}"

introGroups = """V následující úloze bude Vaším úkolem vybrat z uvedených skupin, které jsou Vám nejbližší a následně ty, které jsou Vám nejvzdálenější."""

################################################################################



class Groups(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = closeText, height = 2, font = 15, width = 80, proceed = True)

        with open(os.path.join(os.getcwd(), "Stuff", "groups.txt"), "r", encoding="utf-8") as file:
            self.groups = [line.strip() for line in file if line.strip()]
        random.shuffle(self.groups)

        columns = 3

        self.chosen = set()

        ttk.Style().configure("Padded.TButton", padding = (2,2)) 
        
        self.groupFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.buttons = {}
        for i, group in enumerate(self.groups):
            self.buttons[group] = ttk.Button(self.groupFrame, text = group, command = lambda g = group: self.clicked(g), width = 35)
            self.buttons[group].config(style="Padded.TButton")    
            self.buttons[group].grid(row = i // columns, column = i % columns, padx = 10, pady = 10)

        self.remaining = ttk.Label(self, text = remainingText.format(NUMGROUPS), font = "helvetica 15", background = "white")

        self.groupFrame.grid(row = 2, column = 1)
        self.remaining.grid(row = 3, column = 1, sticky = N)
        self.next.grid(row = 4, column = 1)

        self.rowconfigure(0, weight = 2)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 2)

        self.next["state"] = "disabled"

        self.file.write("Groups\n")


    def nextFun(self):
        self.file.write(self.id + "\t" + "_".join(self.chosen) + "\n\n")
        data = {'id': self.id, 'round': "groups", 'offer': "_".join(self.chosen)}
        if URL != "TEST":
            self.sendData(data)
        super().nextFun()


    def clicked(self, group):
        if group in self.chosen:
            self.buttons[group].config(style="Padded.TButton")
            self.chosen.remove(group)
        else:
            if len(self.chosen) < NUMGROUPS:
                ttk.Style().configure("Clicked.TButton", background="green", foreground="blue", font=("Helvetica", 15, "underline", "bold"), padding = (2, 1))
                self.buttons[group].config(style="Clicked.TButton")
                self.chosen.add(group)
        self.remaining["text"] = remainingText.format(NUMGROUPS - len(self.chosen))
        if NUMGROUPS == len(self.chosen):
            self.next["state"] = "normal"
            for group, button in self.buttons.items():
                if group not in self.chosen:
                    button["state"] = "disabled"
        else:
            self.next["state"] = "disabled"
            for group, button in self.buttons.items():
                button["state"] = "normal"

    def gothrough(self):
        # Simulate participant clicking: select NUMGROUPS groups naturally
        for group in random.sample(self.groups, NUMGROUPS):
            if not self.winfo_exists():
                return
            if group not in self.chosen:
                self.clicked(group)
            self.update_idletasks()
            sleep(0.05)  # Brief delay between clicks, like human speed
        
        sleep(0.5)  # Wait a moment before proceeding to mimic natural pause
        self.nextFun()

        # Participant clicks Next to proceed
        #if self.winfo_exists() and self.next.winfo_exists() and str(self.next["state"]) != "disabled":
        #    self.next.invoke()
        #    self.next


InstructionsGroups = (InstructionsFrame, {"text": introGroups, "height": 5})



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([#InstructionsGroups,
         Groups,
         InstructionsGroups
         ])
