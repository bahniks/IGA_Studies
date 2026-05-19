from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import localtime, strftime, time, sleep
from collections import defaultdict
from uuid import uuid4

import urllib.request
import urllib.parse
import os
import json
import sys
import traceback

from constants import TESTING, URL, GOTHROUGH, PARTICIPATION_FEE, SCREEN
from common import change_keyboard_layout


class DurableAppendFile:
    """Small file-like wrapper that appends each write immediately to disk."""

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.closed = False

        if mode == "w":
            # Start a fresh session file while keeping append semantics for subsequent writes.
            with open(self.path, mode="w", encoding="utf-8"):
                pass

    def write(self, text):
        if self.closed:
            raise ValueError("I/O operation on closed file")

        with open(self.path, mode="a", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())

    def close(self):
        self.closed = True


class GUI(Tk):
    @staticmethod
    def _intify_mapping_keys(mapping):
        if not isinstance(mapping, dict):
            return mapping

        normalized = {}
        for key, value in mapping.items():
            if isinstance(key, str) and key.isdigit():
                normalized[int(key)] = value
            else:
                normalized[key] = value
        return normalized

    def _normalize_loaded_state(self):
        if not isinstance(self.status, dict):
            return

        # temp.json stores object keys as strings; restore numeric round/trial keys
        # for structures that are indexed with integers throughout the codebase.
        for status_key in ("co_roles", "me_decisions", "me_quiz_scores", "trust_decisions"):
            if status_key in self.status:
                self.status[status_key] = self._intify_mapping_keys(self.status[status_key])

        for status_key in ("co_decisions", "co_results"):
            if status_key in self.status:
                top = self._intify_mapping_keys(self.status[status_key])
                if isinstance(top, dict):
                    for block_key, block_value in list(top.items()):
                        top[block_key] = self._intify_mapping_keys(block_value)
                self.status[status_key] = top

    def __init__(self, frames, load = False):
        super().__init__()
        self.restart_requested = False
        self.is_closing = False
        
        self.title("Experiment")
        self.config(bg = "white")
        windowed = TESTING or URL == "http://127.0.0.1:8000/"
        if windowed:
            self.geometry("{}x{}".format(SCREEN[0], SCREEN[1]))
        self.attributes("-fullscreen", not windowed)
        self.attributes("-topmost", not windowed)
        self.overrideredirect(not windowed)
        self.protocol("WM_DELETE_WINDOW", lambda: self.closeFun())

        self.screenwidth = SCREEN[0]
        self.screenheight = SCREEN[1]

        # Ensure we're in the project root directory
        # Try to find the project root by looking for experiment.pyw
        current_dir = os.getcwd()
        if not os.path.exists(os.path.join(current_dir, "experiment.pyw")):
            # We're likely in the Stuff directory, go up one level
            parent_dir = os.path.dirname(current_dir)
            if os.path.exists(os.path.join(parent_dir, "experiment.pyw")):
                os.chdir(parent_dir)
                current_dir = parent_dir
        
        print(f"GUI working directory set to: {os.getcwd()}")
        
        filepath = os.path.join(os.getcwd(), "Data")
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        
        writeTime = localtime()
        self.id = str(uuid4())
        self.outputfile = os.path.join("Data", strftime("%y_%m_%d_%H%M%S", writeTime) + "_" + self.id + ".txt")

        self.bind("<Escape>", self.closeFun)
        # Emergency restart hotkey for operator use when UI becomes unstable.
        #self.bind_all("<Control-Shift-KeyPress-R>", self._manual_restart_request)
        #self.bind_all("<Control-Shift-KeyPress-r>", self._manual_restart_request)

        self.order = frames
        self._frame_aliases = self._build_frame_aliases()

        self.texts = defaultdict(str)        
        self.status = defaultdict(str)
        self.status["logged"] = False
        self.status["reward"] = PARTICIPATION_FEE
        self.status["results"] = []

        self.count = -1

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        if load and URL != "TEST":            
            if os.path.exists("temp.json"):
                ans = messagebox.askyesno(
                    message="Má se načíst započatý experiment?",
                    icon="question",
                    parent=self,
                    title="Pokračovat v experimentu?"
                )
                if ans:
                    with open('temp.json') as f:
                        data = json.load(f)            
                    message = urllib.parse.urlencode({"id": data["id"], "round": data["count"], "offer": "continue"})
                    message = message.encode('ascii')
                    with urllib.request.urlopen(URL, data = message) as f:
                        response = f.read().decode("utf-8")                
                    if response == "continue":
                        for key, value in data.items():
                            setattr(self, key, value)  
                        self._normalize_loaded_state()
                    else:
                        load = False  
                else:
                    load = False
                self.focus_force()

        if TESTING:
            self.title("TEST " + self.id)
        else:
            try:
                change_keyboard_layout("00000405") # Change to Czech layout
            except Exception as e:
                print(f"Error changing keyboard layout: {e}")

        mode = "a" if load else "w"
        self.file = DurableAppendFile(self.outputfile, mode)
        if load:
            self.file.write("resume: " + str(time()) + f"\t{self.count}\tfrom_temp_json" + "\n")
        self.nextFrame()
        self.after(100, self.frame.focus_force)
        self.mainloop()
            

    def destroy(self):
        self.is_closing = True
        #self.unbind_all("<Control-Shift-KeyPress-R>")
        #self.unbind_all("<Control-Shift-KeyPress-r>")
        self.file.close()
        if URL != "TEST":
            self.uploadResults()        
        super().destroy()


    def removeJson(self):
        try:
            if os.path.exists("temp.json"):
                os.remove("temp.json")
        except Exception as e:
            if TESTING:
                print("Could not remove temp.json:", e)


    def _write_temp_snapshot(self, count_override = None):
        snapshot_count = self.count if count_override is None else count_override
        self.removeJson()
        with open("temp.json", mode = "w") as f:
            json.dump({"id": self.id,
                    "outputfile": self.outputfile,
                    "texts": self.texts,
                    "status": self.status,
                    "count": snapshot_count},
                    f)


    # def report_callback_exception(self, exc, val, tb):
    #     """Tkinter hook: catch unhandled callback exceptions and relaunch safely."""
    #     traceback_text = "".join(traceback.format_exception(exc, val, tb))
    #     print("Unhandled Tk callback exception:")
    #     print(traceback_text)
    #     try:
    #         self.file.write("gui_exception\t" + str(time()) + "\t" + traceback_text.replace("\n", " | ") + "\n")
    #     except Exception:
    #         pass
    #     if self.is_closing:
    #         # During shutdown, late callbacks from destroyed widgets can raise harmlessly.
    #         return
    #     self._restart_process("tk_callback_exception")


    # def _manual_restart_request(self, event = None):
    #     if self.restart_requested:
    #         return "break"

    #     # Unbind immediately to avoid duplicate invocation from key-repeat/double press.
    #     #self.unbind_all("<Control-Shift-KeyPress-R>")
    #     #self.unbind_all("<Control-Shift-KeyPress-r>")

    #     ans = messagebox.askyesno(
    #         message="Aplikace se restartuje a bude nabídnuto pokračování z uloženého stavu. Pokračovat?",
    #         icon="question",
    #         parent=self,
    #         title="Nouzový restart"
    #     )
    #     if ans:
    #         self._restart_process("manual_hotkey")
    #     else:
    #         self.bind_all("<Control-Shift-KeyPress-R>", self._manual_restart_request)
    #         self.bind_all("<Control-Shift-KeyPress-r>", self._manual_restart_request)
    #     return "break"


    # def _restart_process(self, reason):
    #     if self.restart_requested:
    #         return

    #     self.restart_requested = True
    #     self.is_closing = True
    #     try:
    #         self.file.write("restart: " + str(time()) + "\t" + str(self.count) + "\t" + reason + "\n")
    #     except Exception:
    #         pass

    #     try:
    #         # Preserve the currently visible frame after restart.
    #         self._write_temp_snapshot(count_override = max(-1, self.count - 1))
    #     except Exception:
    #         pass

    #     try:
    #         self.file.close()
    #     except Exception:
    #         pass

    #     try:
    #         args = sys.argv[:] if sys.argv else [os.path.join(os.getcwd(), "experiment.py")]
    #         os.execv(sys.executable, [sys.executable] + args)
    #     except Exception:
    #         traceback.print_exc()
    #         self.restart_requested = False
    #         try:
    #             messagebox.showerror(
    #                 title="Restart selhal",
    #                 message="Automatický restart selhal. Zavřete prosím okno a spusťte experiment znovu.",
    #                 parent=self,
    #             )
    #         except Exception:
    #             pass


    def nextFrame(self):
        if not GOTHROUGH:
            self._write_temp_snapshot()

        self.count += 1       
        
        if self.count < len(self.order):
            frame_entry = self.order[self.count]
            framename = self._frame_display_name(frame_entry)
        else:
            framename = "end"
        self.file.write("time: " + str(time()) + f"\t{self.count}\t{framename}" + "\n")

        if self.count >= len(self.order):
            if not GOTHROUGH:
                self.removeJson()
            self.destroy()
        else:
            nxt = self.order[self.count]
            if isinstance(nxt, tuple):
                self.frame = nxt[0](self, **nxt[1])
            else:
                self.frame = nxt(self)
            self.frame.grid(row = 0, column = 0, sticky = (N, S, E, W))     
            if self.status["logged"]:
                self.frame.sendData({'id': self.id, 'round': self.count, 'offer': "progress"}, pause = 0.01, trials = 5)

            if GOTHROUGH and GOTHROUGH != type(self.frame).__name__ and (type(GOTHROUGH) is not int or GOTHROUGH < self.count):
                self.update()
                sleep(0.5)
                self.frame.gothrough()
            elif hasattr(self.frame, "run"):
                self.update()
                self.frame.run()

    def _build_frame_aliases(self):
        aliases = {}
        main_module = sys.modules.get("__main__")
        if main_module is None:
            return aliases

        for name, value in vars(main_module).items():
            if name.startswith("_"):
                continue
            if value in self.order:
                aliases[id(value)] = name
        return aliases

    def _frame_display_name(self, frame_entry):
        if isinstance(frame_entry, tuple):
            return self._frame_aliases.get(id(frame_entry), frame_entry[0].__name__)
        return frame_entry.__name__


    def closeFun(self, event = ""):
        if TESTING:
            self.destroy()
            return
        
        message = "Jste si jistí, že chcete studii předčasně ukončit? "
        ans = messagebox.askyesno(message = message, icon = "question", parent = self,
                                  title = "Ukončit studii?")
        if ans:
            self.destroy()


    def uploadResults(self):
        for i in range(20):
            # Set the URL of the Django app that handles file uploads
            url = URL + "results/"

            # Open the file and read its contents
            with open(self.outputfile, "rb") as f:
                file_contents = f.read()

            # Encode the file contents as multipart/form-data
            boundary = b"----WebKitFormBoundary7MA4YWxkTrZu0gW"
            data = b""
            data += b"--" + boundary + b"\r\n"
            filename = os.path.basename(self.outputfile)
            data += bytes('Content-Disposition: form-data; name="results"; filename="{}"\r\n'.format(filename), 'UTF-8')
            data += b"Content-Type: text/plain\r\n\r\n"
            data += file_contents + b"\r\n"
            data += b"--" + boundary + b"--\r\n"

            # Set the headers and data for the request
            headers = {
                "Content-Type": "multipart/form-data; boundary=" + boundary.decode(),
                "Content-Length": str(len(data)),
            }
            request_data = urllib.request.Request(url, data, headers)
            
            try:
                # Send the file to the Django app
                response = urllib.request.urlopen(request_data)
                # Print the response from the Django app
                if response.read().decode() == "ok":
                    break
            except Exception:
                sleep(0.5)