import tkinter, importlib
from tkinter import filedialog as filedialog
import whatsapp_analysis, plot_functions
importlib.reload(whatsapp_analysis)

class MainMenu(tkinter.Frame):

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master, relief=tkinter.SUNKEN, bd=2)

        self.menubar = tkinter.Menu(self)

        menu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="New")
        menu.add_command(label="Open File", command=self.OpenAnalyser)
        self.master.config(menu=self.menubar)
        tkinter.Button(self, text="asd").pack(side=tkinter.LEFT)


        self.canvas = tkinter.Canvas(self, bg="white", width=400, height=400,
                             bd=0, highlightthickness=0)
        self.canvas.pack()
        
        
    def OpenAnalyser(self):
        self.in_path = filedialog.askopenfilename()
        analyser = whatsapp_analysis.Analyser(self.in_path)
        print(analyser)
        


root = tkinter.Tk()

app = MainMenu(root)
app.pack()

root.mainloop()
