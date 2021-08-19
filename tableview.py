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

        # pretend/mockup boundary spinboxes
        self.make_boundary_entries()

    def make_boundary_entries(self):
        self.boundary_entries = []
        temp_boundaries = ['10.1', '10.1', '10.5', '11.3', '11.8', '11.8',
                '12.5', '12.5']

        for i, b in enumerate(temp_boundaries):
            self.boundary_entries.append(ttk.Spinbox(self, increment=0.1))
            sbox = self.boundary_entries[-1]
            sbox.insert(0, b)
            sbox.grid(column=0, row=i*2+1)


if __name__ == "__main__":
    root = tk.Tk()
    windo = ViewFrame(root)
    windo.mainloop()
