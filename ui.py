from tkinter.ttk import Progressbar, Separator
from tkinter import filedialog, messagebox
from tkinter import *

import langEN as lang
import scraper as sc
import subprocess
import threading
import ctypes
import queue
import os

class ScrapeThread(threading.Thread):
    def __init__(self, queue, wordCheckButtonState, htmlCheckButtonState, textCheckButtonState, linkEntry, path, pathToImportedFile = None, isFileImport = False):
        super().__init__()
        self.queue = queue
        self.wordCheckButtonState = wordCheckButtonState
        self.htmlCheckButtonState = htmlCheckButtonState
        self.textCheckButtonState = textCheckButtonState
        self.isFileImport = isFileImport
        self.url = linkEntry.get()
        self.path = path
        if pathToImportedFile is not None:
            self.pathToImportedFile = pathToImportedFile
    
    def run(self):
        if not self.isFileImport:
            url = self.url

            check = sc.checkUrl(url)
            if check["value"]:
                page = sc.getPage(url)
                parsedPage = sc.removeJunk(sc.parsePage(page.content, check["host"]))
                soup = sc.bs(page.content, "html.parser")
                title = sc.getTitle(soup)

                if self.wordCheckButtonState.get():
                    sc.writeToWord(parsedPage, title, self.path)
            
                if self.htmlCheckButtonState.get():
                    sc.writeToHtml(parsedPage, title, self.path)

                if self.textCheckButtonState.get():
                    sc.writeToText(parsedPage, title, self.path)

                self.queue.put("scrape finished")
                pathToOpen = os.path.join(self.path.replace("/", "\\"), title)
                subprocess.Popen('explorer "' + pathToOpen + '"')

            else:
                messagebox.showerror(lang.msgboxError, check["reason"])
                self.queue.put("scrape finished")
        else:
            with open(self.pathToImportedFile.name, encoding="utf8") as importedFile:
                page = importedFile.read()
                parsedPage = sc.removeJunk(sc.parsePage(page))
                soup = sc.bs(page, "html.parser")
                title = sc.getTitle(soup)
                print(title)
                if self.wordCheckButtonState.get():
                    sc.writeToWord(parsedPage, title, self.path)
            
                if self.htmlCheckButtonState.get():
                    sc.writeToHtml(parsedPage, title, self.path)

                if self.textCheckButtonState.get():
                    sc.writeToText(parsedPage, title, self.path)
                self.queue.put("scrape finished")

class InstallThread(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        super().__init__()

    def run(self):
        sc.installPandoc()
        
        cwd = os.getcwd()
        for filename in os.listdir(cwd):
            if filename.startswith("pandoc"):
                os.remove(os.path.join(cwd, filename))

        self.queue.put("install finished")

class GUI:   
    def createLoadingWindow(self, title, description):
        self.top = Toplevel(self.root)
        self.top.title(title)
        self.top.resizable(width=False, height=False)
        
        #Put loading bar in center of main window
        # x = self.root.winfo_x()
        # y = self.root.winfo_y()
        # dy = self.top.winfo_height() / 4
        # self.top.geometry("+%d+%d" %(x+10,y+dy))

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        self.top.geometry("+%d+%d" %(screen_width / 3, screen_height / 3))

        self.label = Label(self.top, text=description).pack()

        self.progbar = Progressbar(self.top, orient="horizontal", length=250, mode="indeterminate")
        self.progbar.pack(expand=True)
        self.progbar.start()
        self.top.update_idletasks()


    def processQueue(self):
        try:
            msg = self.queue.get_nowait()
            self.top.destroy()
            self.root.deiconify()
        except queue.Empty:
            self.root.after(100, self.processQueue)

    def startScrapeThread(self):
        if len(self.linkEntry.get()):
            if self.wordCheckButtonState.get() or self.htmlCheckButtonState.get() or self.textCheckButtonState.get():
                self.queue = queue.Queue()
                path = filedialog.askdirectory(initialdir="F:\School")
                if path != "":
                    ScrapeThread(self.queue, self.wordCheckButtonState, self.htmlCheckButtonState, self.textCheckButtonState, self.linkEntry, path).start()
                    self.createLoadingWindow(lang.scrapingTitle, lang.scrapingDescription)
                    self.root.after(100, self.processQueue)
            else:
                messagebox.showerror(lang.noOutputTitle, lang.noOutputDescription)
        else:
            messagebox.showerror(lang.noLinkTitle, lang.noLinkDescription)

    def importFromFile(self):
        pathToFile = filedialog.askopenfile(title=lang.fileToImport)
        pathToSave = filedialog.askdirectory(title=lang.saveTo)
        if self.wordCheckButtonState.get() or self.htmlCheckButtonState.get() or self.textCheckButtonState.get():
            self.queue = queue.Queue()
            if pathToSave != "":
                ScrapeThread(
                        self.queue, 
                        self.wordCheckButtonState,
                        self.htmlCheckButtonState,
                        self.textCheckButtonState,
                        self.linkEntry,
                        pathToSave,
                        isFileImport=True,
                        pathToImportedFile=pathToFile
                    ).start()
                self.createLoadingWindow(lang.convertTitle, lang.convertDescription)
                self.root.after(100, self.processQueue)
            else:
                messagebox.showerror(lang.noOutputTitle, lang.noOutputDescription)
    
    def setup(self):
        if not sc.isPandocInstalled():
            self.queue = queue.Queue()
            InstallThread(self.queue).start()
            self.createLoadingWindow(lang.setupTitle, lang.setupDescription)
            self.root.after(100, self.processQueue)
        else:
            self.root.deiconify()

    def __init__(self, root):
        self.root = root
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("+%d+%d" %(screen_width / 3, screen_height / 3))

        self.root.withdraw()
        self.setup()

        self.frame = Frame(root, padx=5, pady=5)
        self.frame.pack(fill="both", expand=True)

        self.linkLabel = Label(self.frame, text=lang.urlLabel)
        self.linkLabel.grid(column=0, row=0, padx=5, sticky="w")

        self.linkEntry = Entry(self.frame)
        self.linkEntry.grid(column=1, row=0)

        self.br = Separator(self.frame, orient="horizontal")
        self.br.grid(column=0, row=1, columnspan=2, pady=5, sticky="ew")


        self.wordCheckButtonState = BooleanVar()
        self.wordCheckButton = Checkbutton(self.frame, text=lang.wordCheck, onvalue=True, offvalue=False, variable=self.wordCheckButtonState)
        self.wordCheckButton.grid(column=0, row=2, sticky="w")

        self.htmlCheckButtonState = BooleanVar()
        self.htmlCheckButton = Checkbutton(self.frame, text=lang.htmlCheck, onvalue=True, offvalue=False, variable=self.htmlCheckButtonState)
        self.htmlCheckButton.grid(column=0, row=3, sticky="w")

        self.textCheckButtonState = BooleanVar()
        self.textCheckButton = Checkbutton(self.frame, text=lang.textCheck, onvalue=True, offvalue=False, variable=self.textCheckButtonState)
        self.textCheckButton.grid(column=0, row=4, sticky="w")

        self.br2 = Separator(self.frame, orient="horizontal")
        self.br2.grid(column=0, row=5, columnspan=2, pady=5, sticky="ew")

        self.scrapeButton = Button(self.frame, text=lang.scrape, command=self.startScrapeThread)
        self.scrapeButton.grid(column=0, row=6, sticky="ew")

        self.importButton = Button(self.frame, text=lang.importButton, command=self.importFromFile)
        self.importButton.grid(column=1, row=6, sticky="ew")

def start():
    root = Tk()
    root.title(lang.title)
    root.resizable(height=False, width=False)
    main_ui = GUI(root)
    root.mainloop()

def errorMessage(title, description):
    ctypes.windll.user32.MessageBoxW(0, description, title, 0)

if sc.checkInternetConnection():
    start()
else:
    errorMessage(lang.noInternetTitle, lang.noInternetDescription)