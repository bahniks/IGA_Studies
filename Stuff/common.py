from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from time import time, sleep, perf_counter

import os
import sys
import ctypes
import random
import urllib.request
import urllib.parse

from constants import TESTING, URL
import re
import math


class ExperimentFrame(Canvas):
    def __init__(self, root):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")
        
        self.root = root
        self.file = self.root.file
        self.id = self.root.id

    def nextFun(self):
        if self.check():
            self.write()
            self.file.write("\n")
            self.destroy()
            self.root.nextFrame()
        else:
            self.back()

    def check(self):
        return True

    def back(self):
        pass

    def write(self):
        pass

    def gothrough(self):        
        self.nextFun()

    def sendData(self, message, pause = 0.1, trials = -1):
        if URL == "http://127.0.0.1:8000/":
            print(message)
        count = 0
        while trials != count:
            count += 1
            data = urllib.parse.urlencode(message)
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8")
                        if URL == "http://127.0.0.1:8000/":
                            print(response)
                except Exception:
                    continue
            if response == "ok":
                return
            sleep(pause)
        return





class InstructionsFrame(ExperimentFrame):
    def __init__(self, root, text, proceed = True, height = "auto", font = 15, space = False, width = 80, keys = None, 
                 update = None, wait = 2, savedata = False):
        super().__init__(root)

        self.root = root
        self.wait = wait
        self.proceedB = proceed
        self.keys = keys
        self.t0 = time()
        self.savedata = savedata
        self.height = height
        height = 12 if height == "auto" else height

        if update:
            updateTexts = []
            for i in update:
                updateTexts.append(self.root.texts[i])
            text = text.format(*updateTexts)       
                   
        self.text = Text(self, font = "helvetica {}".format(font), relief = "flat",
                         background = "white", width = width, height = height, wrap = "word",
                         highlightbackground = "white", pady = 15)
        self.text.grid(row = 1, column = 0, columnspan = 3)

        self.text.insert("1.0", text)
        if self.height == "auto":
            self.text.update_idletasks()
            num_lines = self.count_lines()
            if "</b>" in text or "</i>" in text:
                num_lines += 1
            self.text.config(height = int(num_lines))

        self.text.tag_configure("bold", font = "helvetica {} bold".format(font))
        self.text.tag_configure("italic", font = "helvetica {} italic".format(font))    
        self.text.tag_configure("courier", font = "courier {}".format(font))      
        self.text.tag_configure("center", justify="center")               
        self.text.tag_configure("blue", foreground = "blue")
        self.text.tag_configure("red", foreground = "red")
        self.text.tag_configure("green", foreground = "green")

        self.addStandardTags()

        self.text.config(state = "disabled")

        if proceed:
            ttk.Style().configure("TButton", font = "helvetica 15")
            self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun)
            self.next.grid(row = 2, column = 1)
        elif space:
            self.root.bind("<space>", lambda e: self.proceed())
        elif keys:
            for key in keys:
                if key in [str(i) for i in range(10)]:
                    self.root.bind("{}".format(key), lambda e: self.proceed())
                else:
                    self.root.bind("<{}>".format(key), lambda e: self.proceed())                
        self.keys = keys

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 3)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(2, weight = 3)
        self.rowconfigure(3, weight = 3)

    # Overload addStandardTags to handle <color: xxx>...</color>
    def addStandardTags(self):
        self.addtags("<b>", "</b>", "bold")
        self.addtags("<i>", "</i>", "italic")
        self.addtags("<c>", "</c>", "courier")
        self.addtags("<center>", "</center>", "center")
        self.addtags("<blue>", "</blue>", "blue")
        self.addtags("<red>", "</red>", "red")  
        self.addtags("<green>", "</green>", "green")
        # Handle all <color: xxx>...</color> tags
        text_content = self.text.get("1.0", "end")
        for match in re.finditer(r"<color:\s*([^>]+)\s*>", text_content):
            color = match.group(1).strip()
            starttag = f"<color: {color}>"
            self.addtags(starttag, "</color>", f"color_{color}")

    def addtags(self, starttag, endtag, tag):            
        i_index = "1.0"
        while True:
            i_index = self.text.search(starttag, i_index, regexp=False)
            if not i_index:
                break
            e_index = self.text.search(endtag, i_index, regexp=False)
            if not e_index:
                break
            # Handle <color: xxx>...</color>
            if starttag.startswith("<color:"):
                # Extract color name
                color_name = starttag[7:-1].strip()
                tag_name = f"color_{color_name}"
                # Add tag if not already present
                if not tag_name in self.text.tag_names():
                    self.text.tag_configure(tag_name, foreground=color_name)
                self.text.tag_add(tag_name, i_index, e_index)
            else:
                self.text.tag_add(tag, i_index, e_index)
            self.text.delete(e_index, f"{e_index}+{len(endtag)}c")
            self.text.delete(i_index, f"{i_index}+{len(starttag)}c")
            i_index = e_index

    def changeText(self, newtext, tags = True):
        self.text.config(state = "normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", newtext)
        if tags:
            self.addStandardTags()
        if self.height == "auto":
            self.text.update_idletasks()
            num_lines = self.count_lines()
            if "</b>" in newtext:
                num_lines += 1
            self.text.config(height = int(num_lines))
        self.text.config(state = "disabled")

    def count_lines(self) -> int:
        #val = self.text.tk.call(self.text._w, "count", "-displaylines", "1.0", "end-1c")
        val = self.text.tk.call(self.text._w, "count", "-displaylines", "1.0", "end")
        return int(val)

    def proceed(self):
        if time() - self.t0 > self.wait:
            self.nextFun()

    def nextFun(self):        
        if self.check():
            self.root.unbind("<space>")
            if self.keys:
                for key in self.keys:
                    if key in [str(i) for i in range(10)]:
                        self.root.unbind("{}".format(key))
                    else:
                        self.root.unbind("<{}>".format(key))
            if self.savedata:
                self.write()
            self.destroy()
            self.root.nextFrame()
        else:
            self.back()

    def gothrough(self):
        #self.update()
        if self.wait > 0:
            sleep(self.wait)
            
        # Safety check before attempting focus
        if self.winfo_exists():
            try:
                self.focus_force()
            except Exception as e:
                print(f"DEBUG: Focus force failed: {e}")
                
        if self.proceedB and hasattr(self, 'next') and self.next.winfo_exists():
            self.next.invoke()
        elif self.keys:
            key = self.keys[0]
            self.root.event_generate(f"<KeyPress-{key}>")


class Wait(InstructionsFrame):
    def __init__(self, root, what):
        super().__init__(
            root,
            text="Čekejte na data od ostatních účastníků studie",
            height=3,
            font=15,
            proceed=False,
            width=45,
        )
        self.progressBar = ttk.Progressbar(self, orient=HORIZONTAL, length=400, mode='indeterminate')
        self.progressBar.grid(row=2, column=1, sticky=N)

        self.what = what

    def checkUpdate(self):
        t0 = perf_counter() - 4
        while True:
            self.update()
            if perf_counter() - t0 > 5:
                t0 = perf_counter()
                if URL == "TEST":
                    response = self.test()
                else:
                    try:
                        data = urllib.parse.urlencode({'id': self.id, 'round': "wait", 'offer': self.what})
                        data = data.encode('ascii')
                        with urllib.request.urlopen(URL, data=data) as f:
                            response = f.read().decode("utf-8")
                            if URL == "http://127.0.0.1:8000/":
                                print(response)
                    except Exception:
                        continue
                if response:
                    self.processResponse(response)
                    self.write(response)
                    self.progressBar.stop()
                    self.nextFun()
                    return

    def run(self):
        self.progressBar.start()
        self.checkUpdate()

    def test(self):
        pass

    def processResponse(self, response):
        pass

    def gothrough(self):
        self.run()

    def write(self, response):
        self.file.write(self.what.capitalize() + " Results" + "\n")
        self.file.write(self.id + "\t" + response.replace("_", "\t") + "\n\n")


class Question(Canvas):
    def __init__(self, root, text, conditional = None, condtype = None, condtext = "", width = 80,
                 label = True, answer = "yesno", condition = "yes", where = "below"):
        super().__init__(root)
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        self.root = root

        self.yesno = answer == "yesno"
        self.condition = condition

        self.answer = StringVar()
        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 13")

        if label:
            self.label = ttk.Label(self, text = text, background = "white", font = "helvetica 15",
                                   width = width)
        else:
            self.label = Text(self, width = width, wrap = "word", font = "helvetica 15",
                              relief = "flat", height = 5, cursor = "arrow",
                              selectbackground = "white", selectforeground = "black")
            self.label.insert("1.0", text)
            self.label.config(state = "disabled")

        if answer == "yesno":
            self.yes = ttk.Radiobutton(self, text = "Ano", variable = self.answer, value = "yes",
                                       command = self.answered)
            self.no = ttk.Radiobutton(self, text = "Ne", variable = self.answer, value = "no",
                                       command = self.answered)
            self.yes.grid(column = 0, row = 1, sticky = "w", padx = 5)
            self.no.grid(column = 0, row = 2, sticky = "w", padx = 5)
        else:
            self.field = answer[0](self, textvariable = self.answer, **answer[1])
            if where == "below":
                self.field.grid(column = 0, row = 1, sticky = "w", padx = 5)
            elif where == "next":
                self.field.grid(column = 5, row = 0, sticky = "w", padx = 5)

        self.condtype = condtype
        if conditional:
            self.condvar = StringVar()
            if condtype in ("combo", "entry"):
                self.cond = conditional[0](self, textvariable = self.condvar, **conditional[1])
            else:
                self.cond = conditional[0](self, variable = self.condvar, **conditional[1])
            if condtype == "combo":
                self.cond.config(state = "readonly")
            self.cond.grid(column = 2, row = 1, sticky = "w")
            self.condtext = ttk.Label(self, text = condtext, background = "white",
                                      font = "helvetica 13")
            self.condtext.grid(column = 1, row = 1, sticky = "w", padx = 20)
            self.condtext.grid_forget()
            self.cond.grid_forget()
                        
        self.label.grid(column = 0, row = 0, columnspan = 4, sticky = "w", pady = 10)

        self.columnconfigure(3, weight = 1)


    def answered(self):
        if self.condtype:
            if self.answer.get() == self.condition:
                row = 1 if self.condition == "yes" else 2
                self.condtext.grid(column = 1, row = row, sticky = "w", padx = 20)
                self.cond.grid(column = 2, row = row, sticky = "w")
            else:
                self.condtext.grid_forget()
                self.cond.grid_forget()

    def check(self):
        return self.answer.get() and (not self.condtype or self.condvar.get()
                                      or self.answer.get() != self.condition)

    def write(self, newline = True):
        self.root.file.write(self.answer.get())
        if self.condtype and self.condvar.get():
            self.root.file.write("\t" + self.condvar.get())
        if newline:
            self.root.file.write("\n")

    def disable(self):
        if self.yesno: 
            self.yes.config(state = "disabled")
            self.no.config(state = "disabled")
        else:
            self.field.config(state = "disabled")
        if self.condtype:
            self.cond.config(state = "disabled")


class TextFrame(ExperimentFrame):
    def __init__(self, root, text, width = 80, qlines = 2, alines = 5, name = "", timeDisabled_s = 0, requiredLength = 0):
        super().__init__(root)

        self.timeDisabled_s = timeDisabled_s
        self.requiredLength = requiredLength

        self.file.write(name + "\n")
        self.textarea = TextArea(self, text, width, qlines, alines, on_text_change = lambda e: self.checkEnabling())
        self.textarea.grid(row = 1, column = 1)

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun)
        self.next.grid(column = 1, row = 2) 

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)

        self.time0 = perf_counter()

        if timeDisabled_s or requiredLength:            
            self.next.config(state = "disabled")
            self.after(timeDisabled_s * 1000, self.checkEnabling)

    def write(self):
        self.file.write(self.id + "\t")
        self.textarea.write()
        
    def checkEnabling(self):
        if len(self.textarea.check()) >= self.requiredLength and perf_counter() - self.time0 >= self.timeDisabled_s:
            self.next.config(state = "normal")
        else:
            self.next.config(state = "disabled")


class TextArea(Canvas):
    def __init__(self, root, text, width = 80, qlines = 2, alines = 5, on_text_change = None):
        super().__init__(root)
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        self.on_text_change = on_text_change if on_text_change else lambda x: None

        self.root = root

        self.answer = StringVar()

        self.label = Text(self, width = width, wrap = "word", font = "helvetica 15",
                          relief = "flat", height = qlines, cursor = "arrow",
                          selectbackground = "white", selectforeground = "black")
        self.label.insert("1.0", text)
        self.label.config(state = "disabled")
        self.label.grid(column = 0, row = 0)

        self.field = Text(self, width = width, wrap = "word", font = "helvetica 15",
                  height = alines, relief = "solid")
        self.field.bind("<KeyRelease>", self.on_text_change)

        self.field.grid(column = 0, row = 1, pady = 6)

        self.columnconfigure(0, weight = 1)

    def check(self):
        return self.field.get("1.0", "end").strip()

    def write(self, newline = True):
        self.root.file.write(self.field.get("1.0", "end").replace("\n", "  ").replace("\t", " "))
        if newline:
            self.root.file.write("\n")

    def disable(self):
        self.field.config(state = "disabled")


class Measure(Canvas):
    def __init__(self, root, text, values, left, right, shortText = "", function = None,
                 questionPosition = "next", labelPosition = "above", middle = "",
                 funconce = False, filler = 0, center = False):
        super().__init__(root)

        self.root = root
        self.text = shortText
        self.answer = StringVar()
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")

        if text:        
            if questionPosition == "next":
                self.question = ttk.Label(self, text = text, background = "white", anchor = "e", font = "helvetica 15")
                self.question.grid(column = 0, row = 2, sticky = E, padx = 5)
            elif questionPosition == "above":
                self.question = ttk.Label(self, text = text, background = "white", anchor = "center",
                                          font = "helvetica 15")
                self.question.grid(column = 0, row = 0, columnspan = 4, pady = 5)

        if labelPosition != "none":
            self.left = ttk.Label(self, text = "{:>15}".format(left), background = "white", font = "helvetica 15")
            self.right = ttk.Label(self, text = "{:<15}".format(right), background = "white", font = "helvetica 15")
        if labelPosition == "above":
            self.left.grid(column = 1, row = 1, sticky = W)
            self.right.grid(column = 2, row = 1, sticky = E)
        elif labelPosition == "next":
            self.left.grid(column = 0, row = 2, sticky = E)
            self.right.grid(column = 3, row = 2, sticky = W)
            self.root.update_idletasks()
            if center:
                width = max(self.left.winfo_width(), self.right.winfo_width())
                self.leftFiller = Canvas(self, background = "white", width = width, height = 1,
                                 highlightbackground = "white", highlightcolor = "white")
                self.leftFiller.grid(row = 1, column = 0)
                self.rightFiller = Canvas(self, background = "white", width = width, height = 1,
                                 highlightbackground = "white", highlightcolor = "white")
                self.rightFiller.grid(row = 1, column = 3)

        if middle:
            self.middle = ttk.Label(self, text = middle, background = "white", font = "helvetica 15")
            self.middle.grid(column = 1, row = 1, columnspan = 2)
            self.question["font"] = "helvetica 15"

        self.scale = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.scale.grid(column = 1, row = 2, sticky = EW, columnspan = 2, padx = 40)        

        self.radios = []
        for col, value in enumerate(values):
            padx = 4 if not middle else 18
            self.radios.append(ttk.Radiobutton(self.scale, text = str(value), value = value,
                                               command = self.func, variable = self.answer))
            self.radios[col].grid(row = 0, column = col, padx = padx)
            self.scale.columnconfigure(col, weight = 1)
        if filler:
            self.filler = Canvas(self.scale, background = "white", width = filler, height = 1,
                                 highlightbackground = "white", highlightcolor = "white")
            self.filler.grid(column = 0, row = 1, columnspan = len(values), sticky = EW)
            
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(3, weight = 1)

        self.function = function            
        self.functionProcessed = False
        self.funconce = funconce

    def enable(self):
        for radio in self.radios:
            radio["state"] = "normal"

    def disable(self): 
        for radio in self.radios:
            radio["state"] = "disabled"

    def func(self):
        if not self.funconce or not self.functionProcessed:
            if self.function:
                self.function()
                self.functionProcessed = True

    def write(self):
        if self.text:
            ans = "{}\t{}".format(self.text, self.answer.get())
        else:
            ans = self.answer.get()
        self.root.file.write(ans)

    def check(self):
        return self.answer.get()


class MultipleChoice(Canvas):
    def __init__(self, root, text, answers, feedback, randomize = True, callback = False):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.root = root
        self.answer = StringVar()
        self.feedbackTexts = feedback
        self.answers = answers
        self.callback = callback
        
        self.question = ttk.Label(self, text = text, background = "white", anchor = "center", font = "helvetica 15 bold", wraplength = 950)
        self.question.grid(column = 0, row = 0, pady = 5, sticky = W)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
        self.radios = []
        self.order = [i for i in range(len(answers))]
        if randomize:
            random.shuffle(self.order)
        answer_font = tkfont.Font(family="helvetica", size=15)
        max_answer_width_px = 900
        for i in range(len(answers)):            
            wrapped_answer = self._wrap_text_to_width(answers[self.order[i]], answer_font, max_answer_width_px)
            self.radios.append(ttk.Radiobutton(self, text = wrapped_answer, value = i + 1,
                                               command = self.answerFunction, variable = self.answer))
            self.radios[i].grid(row = i+ 1, column = 0, pady = 3, sticky = W)

        self.filler = ttk.Label(self, text = " "*150 + "\n ", background = "white", anchor = "center",
                                          font = "helvetica 15", wraplength = 1000)
        self.filler.grid(column = 0, row = len(answers) + 1, pady = 5, sticky = NW)
        self.feedback = ttk.Label(self, text = " \n ", background = "white", anchor = "center",
                                          font = "helvetica 15", wraplength = 950)
        self.feedback.grid(column = 0, row = len(answers) + 1, pady = 5, sticky = NW)
        self.rowconfigure(len(answers) + 1, weight = 1)

    @staticmethod
    def _wrap_text_to_width(text, font, max_width_px):
        words = text.split()
        if not words:
            return text

        lines = []
        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if font.measure(candidate) <= max_width_px:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return "\n".join(lines)

    def getAnswer(self):
        return self.answers[self.order[int(self.answer.get()) - 1]].replace("\n", "  ").replace("\t", " ") 

    def answerFunction(self):
        if hasattr(self.root.master, "next"):
            self.root.master.next["state"] = "normal"
        elif hasattr(self.root, "next"):
            self.root.next["state"] = "normal"
        if self.callback:
            self.callback()
        
    def showFeedback(self):
        self.feedback["text"] = self.feedbackTexts[self.order[int(self.answer.get()) - 1]]
        for radio in self.radios:
            radio["state"] = "disabled"
        
        

class InstructionsAndUnderstanding(InstructionsFrame):
    def __init__(self, root, controlTexts, name, showFeedback = True, randomize = True, fillerHeight = 255, finalButton = None, prompt = None, **kwargs):        
        
        original_text = kwargs.get("text", "")
        self.original_text = original_text
        if prompt and kwargs.get("height", "auto") == "auto":
            kwargs["text"] = original_text + "\n\n" + prompt

        super().__init__(root, **kwargs)

        if prompt and kwargs.get("height", "auto") == "auto":
            self.text.config(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", original_text)
            self.addStandardTags()
            self.text.config(state="disabled")

        if type(controlTexts) == str:
            self.controlTexts = self.root.texts[controlTexts]
        else:
            self.controlTexts = controlTexts
        self.randomize = randomize
        self.showFeedback = showFeedback
        self.finalButton = finalButton
        self.prompt = prompt

        self.controlFrame = Canvas(self, background = "white", highlightbackground = "white",
                                 highlightcolor = "white")
        self.controlFrame.grid_propagate(False)

        self.control_frame_width, self.control_frame_height = self._measure_max_control_area()
        self.control_frame_height = max(self.control_frame_height, fillerHeight)
        self.controlFrame.configure(width = self.control_frame_width, height = self.control_frame_height)

        self.controlFrame.grid(row = 2, column = 1, sticky = W)
        self.next.grid(row = 3, column = 1)

        self.controlNum = 0
        if not self.prompt:
            self.createQuestion()
        self.file.write(name + "\n")

    def createQuestion(self):
        if self.controlNum:
            self.controlQuestion.grid_forget()
        self.next["state"] = "disabled"
        texts = self.controlTexts[self.controlNum]
        self.controlQuestion = MultipleChoice(self.controlFrame, text = texts[0], answers = texts[1], feedback = texts[2], randomize = self.randomize)
        self.controlQuestion.grid(row = 0, column = 0)
        self.controlNum += 1
        self.controlstate = "answer"

    def _measure_max_control_area(self):
        max_width = 1
        max_height = 1

        for texts in self.controlTexts:
            probe = MultipleChoice(self.controlFrame, text = texts[0], answers = texts[1], feedback = texts[2], randomize = False)
            probe.grid(row = 99, column = 0)
            self.update_idletasks()

            max_width = max(max_width, probe.winfo_reqwidth())
            max_height = max(max_height, probe.winfo_reqheight())

            for fb_text in texts[2]:
                probe.feedback["text"] = fb_text
                self.update_idletasks()
                max_width = max(max_width, probe.winfo_reqwidth())
                max_height = max(max_height, probe.winfo_reqheight())

            probe.destroy()

        return max_width, max_height
        
    def nextFun(self):        
        if self.prompt and not self.controlNum:
            self.changeText(self.original_text + "\n\n" + self.prompt)
            self.createQuestion()
            return
        if self.controlstate == "feedback" or not self.showFeedback:
            self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlQuestion.getAnswer() + "\n")
            if self.controlNum == len(self.controlTexts):
                self.file.write("\n")
                super().nextFun()   
            else:
                self.createQuestion()                
        else:            
            self.controlQuestion.showFeedback()
            self.controlstate = "feedback"     
            if self.controlNum == len(self.controlTexts) and self.finalButton:         
                self.next["text"] = self.finalButton

    def gothrough(self):
        # If there's a prompt, handle the initial prompt display first
        if self.prompt and not self.controlNum:
            sleep(0.1)
            self.update()
            if self.winfo_exists():
                try:
                    self.focus_force()
                except Exception as e:
                    print(f"DEBUG: Focus force failed in prompt display: {e}")
            if hasattr(self, 'next') and self.next.winfo_exists():
                self.next.invoke()
                self.update()
                sleep(0.1)
        
        # Now iterate through all control questions
        for i in range(len(self.controlTexts)):
            sleep(0.1)
            self.update()
            
            # Safety check before attempting focus
            if self.winfo_exists():
                try:
                    self.focus_force()
                except Exception as e:
                    print(f"DEBUG: Focus force failed in control questions: {e}")
                    
            num_options = len(self.controlTexts[i][1])
            option = random.randint(0, num_options - 1)
            self.update()
            # invoke the selected radio for the current question
            self.controlQuestion.radios[option].invoke()
            self.update()
            sleep(0.1)
            
            # Safety check before attempting focus
            if self.winfo_exists():
                try:
                    self.focus_force()
                except Exception as e:
                    print(f"DEBUG: Focus force failed in control questions: {e}")
                    
            # first click: show feedback (if enabled) or proceed immediately if not
            if hasattr(self, 'next') and self.next.winfo_exists():
                self.next.invoke()
                self.update()
                sleep(0.1)
                # if feedback is shown, click Next again to advance to the next question
                if self.showFeedback:
                    self.next.invoke()
                    self.update()
                    sleep(0.05)


class OneFrame(Canvas):
    def __init__(self, root, question, items, scale, wrap = 480):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.root = root
        self.file = self.root.file

        self.answers = scale
        
        self.lab1 = ttk.Label(self, text = question, font = "helvetica 15", background = "white")
        self.lab1.grid(row = 2, column = 1, pady = 10, columnspan = 2)
        self.measures = []
        for count, word in enumerate(items):
            self.measures.append(Measure(self, word, self.answers, "", "", function = self.root.check,
                                         labelPosition = "none"))
            self.measures[count].grid(row = count + 3, column = 1, columnspan = 2, sticky = E)
            self.measures[count].question["wraplength"] = wrap
            self.measures[count].question["justify"] = "right"

    def check(self):
        for measure in self.measures:
            if not measure.answer.get():
                return False
        else:
            return True             

    def write(self):
        for num, measure in enumerate(self.measures):
            self.file.write(str(self.answers.index(measure.answer.get()) + 1))
            if num != len(self.measures) - 1:
                self.file.write("\t")


def read_all(file, encoding = "utf-8", comments = False):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), file), encoding = encoding) as f:
        for line in f:
            if comments and line.startswith("#"):
                continue
            if comments and "#" in line:
                line = line[:line.find("#")]
            text += line.rstrip(" \t")
    return text


# Load and activate keyboard layout
# Language IDs: "00000405" = Czech, "00000409" = English US
def change_keyboard_layout(language_id):
    user32 = ctypes.windll.user32
    layout = user32.LoadKeyboardLayoutW(language_id, 1)  # 1 = KLF_ACTIVATE
    if layout:
        user32.ActivateKeyboardLayout(layout, 0)