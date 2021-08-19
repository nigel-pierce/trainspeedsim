#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk

class ViewFrame(tk.Frame):
    """the widget and elements and stuff"""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        
        # temporary widgets
        self.templabel = ttk.Label(self)
        self.templabel["text"] = "TableView eventually"
        self.templabel.pack()



if __name__ == "__main__":
    root = tk.Tk()
    windo = ViewFrame(root)
    windo.mainloop()
