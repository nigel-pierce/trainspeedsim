#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from simulation import PosSpeed
from editablesim import EditableTrack
from observer import Observer

class SpeedDistViewFrame(tk.Frame):
    '''Frame containing the canvas and whatever I decide to use for the
    graph elements'''

    def __init__(self, master, controller):
        super().__init__(master, width=400, height=300)
        self.master = master
        self._controller = controller
        # all that stuff should be in a more generic ViewFrame class
        # (not to be confused with the tableview.py ViewFrame)

        self._canvas = tk.Canvas(self, bg="white", width=400, height=300)
        self._canvas.pack(expand=True, fill=tk.BOTH)

        self._segboundaries = []
        self._speedlimitsegs = []


class SpeedDistView:
    '''The View, which controller updates, and which owns the frame containing
    the canvas on which the lines are to be drawn'''

    def __init__(self, controller, parent_frame):
        self._controller = controller
        self._frame = SpeedDistViewFrame(root, self._controller)
        self._frame.pack()


if __name__=="__main__":
    model = EditableTrack("short_maxspeeds.csv", "imperial")
    root = tk.Tk()
    view = SpeedDistView(None, root)

    root.mainloop()
