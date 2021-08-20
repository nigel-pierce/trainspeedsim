#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from itertools import zip_longest
from simulation import PosSpeed

class ViewFrame(tk.Frame):
    """the widget and elements and stuff"""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        
        # column headers
        self.boundhead = ttk.Label(self)
        self.boundhead["text"] = "MP Boundary"
        self.boundhead.grid(row=0, column=0) # hopefully packs with other label
        self.limithead = ttk.Label(self)
        self.limithead["text"] = "Speed Limit"
        self.limithead.grid(row=0, column=1)

        # pretend/mockup boundary spinboxes
        #self.make_boundary_entries()
        #self.make_limit_entries()

        # where the spinboxes are stored
        # (they get re-used)
        self.boundary_entries = []
        self.limit_entries = []

    def make_boundary_entries(self, boundaries):

        boundaries_and_entries = enumerate(zip_longest(boundaries,
            self.boundary_entries))

        #print([x for x in boundaries_and_entries])

        for i, (b, e) in boundaries_and_entries:
            print(i, b, e)
            if e is None:
                self.boundary_entries.append(ttk.Spinbox(self, from_=0,
                    to=10000, increment=0.1))
                sbox = self.boundary_entries[-1]
                sbox.insert(0, b)
                sbox.grid(column=0, row=i*2+1)
            else:
                sbox = self.boundary_entries[i]
                sbox.delete(0, len(sbox.get()))
                sbox.insert(0, b)

    def make_limit_entries(self, limits):
        temp_limits = [0, 20, 40, 35, 0, 50, 0]

        for i, l in enumerate(limits):
            self.limit_entries.append(ttk.Spinbox(self, from_=0, to=1000))
            sbox = self.limit_entries[-1]
            sbox.insert(0, l)
            sbox.grid(column=1, row=i*2+2)

class TableView:
    def __init__(self, controller, frame):
        self.controller = controller
        self.frame = frame

    def update(self, best_speeds, speed_limits):
        self.frame.make_boundary_entries([ps.pos for ps in speed_limits])
        self.frame.make_limit_entries([ps.speed for ps in speed_limits])
        # do best_speeds later

if __name__ == "__main__":
    root = tk.Tk()
    windo = ViewFrame(root)
    tableview = TableView(None, windo)
    temp_boundaries = ['10.1', '10.1', '10.5', '11.3', '11.8', '11.8',
        '12.5', '12.5']
    temp_ps = [PosSpeed(b, 1) for b in temp_boundaries]
    tableview.update([], temp_ps)

    # update again to see if spinbox/entry re-use works (all 8 entries)
    temp_boundrs2 = ['90', '90', '92.4', '94.3', '96.2', '96.5', '96.7', '97']
    temp_ps2 = [PosSpeed(b, 1) for b in temp_boundrs2]
    tableview.update([], temp_ps2)

    windo.mainloop()
