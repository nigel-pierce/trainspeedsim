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
        #self.templabel.pack()
        self.templabel.grid(row=0, column=0)

        # column headers
        self.boundhead = ttk.Label(self)
        self.boundhead["text"] = "MP Boundary"
        self.boundhead.grid(row=0, column=0) # hopefully packs with other label
        self.limithead = ttk.Label(self)
        self.limithead["text"] = "Speed Limit"
        self.limithead.grid(row=0, column=1)

        # pretend/mockup boundary spinboxes
        self.make_boundary_entries()
        self.make_limit_entries()

    def make_boundary_entries(self):
        self.boundary_entries = []
        temp_boundaries = ['10.1', '10.1', '10.5', '11.3', '11.8', '11.8',
                '12.5', '12.5']

        for i, b in enumerate(temp_boundaries):
            self.boundary_entries.append(ttk.Spinbox(self, increment=0.1))
            sbox = self.boundary_entries[-1]
            sbox.insert(0, b)
            sbox.grid(column=0, row=i*2+1)

    def make_limit_entries(self):
        self.limit_entries = []
        temp_limits = [0, 20, 40, 35, 0, 50, 0]

        for i, l in enumerate(temp_limits):
            self.limit_entries.append(ttk.Spinbox(self, from_=0, to=1000))
            sbox = self.limit_entries[-1]
            sbox.insert(0, l)
            sbox.grid(column=1, row=i*2+2)

if __name__ == "__main__":
    root = tk.Tk()
    windo = ViewFrame(root)
    windo.mainloop()
