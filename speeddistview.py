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
        super().__init__(master)
        self.master = master
        self._controller = controller
        # all that stuff should be in a more generic ViewFrame class
        # (not to be confused with the tableview.py ViewFrame)

