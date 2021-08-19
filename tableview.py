#! /usr/bin/python3

import tkinter as tk

class ViewFrame(tk.Frame):
    """the widget and elements and stuff"""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        
        # temporary widgets
        self.templabel = tk.Label(self)
        self.templabel["text"] = "TableView eventually"
        self.templabel.pack()

