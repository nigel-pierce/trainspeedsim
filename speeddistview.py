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

        # graph to pixel scaling
        self._x_scale = 20
        self._y_scale = 2

        # margin of graph, in canvas pixels
        self._x_margin = 32 # from left
        self._y_margin = 32 # from bottom

        # axes of graph
        # (0, 200, 400, 200)
        self._canvas.create_line(self.graph_seg_to_canvas(0, 0, 30, 0), 
                fill="#999")
        # (0, 200, 0, 100)
        self._canvas.create_line(self.graph_seg_to_canvas(0, 0, 0, 100), 
                fill="#999")

        self._segboundaries = []
        self._speedlimitsegs = []

    def graph_seg_to_canvas(self, x1, y1, x2, y2):
        '''Converts both points on graph to tuple of canvas points for the 
        purpose of lines'''
        return (*self.graph_pt_to_canvas(x1, y1), 
                *self.graph_pt_to_canvas(x2, y2))

    def graph_pt_to_canvas(self, x, y):
        '''Converts point on graph (origin in lower left) to point on canvas
        (origin in upper left) and scales etc.'''
        return (x*self._x_scale+self._x_margin, 
                300-self._y_margin-y*self._y_scale)

    def make_limit_lines(self, speed_limits):
        '''For now just draw some lines--Oh cool the canvas is kind of smart'''
        prev_ps = None
        colors = ['red', 'blue']
        print("num of speed limit segs: {}".format(len(speed_limits)))
        for i, ps in enumerate(speed_limits):
            if prev_ps is not None:
                #coords = (prev_ps.pos*10, 
                 #   200-prev_ps.speed, ps.pos*10, 200-prev_ps.speed)
                coords = self.graph_seg_to_canvas(prev_ps.pos, prev_ps.speed,
                        ps.pos, prev_ps.speed)
                print("coords of line:",coords)
                line_id = self._canvas.create_line(coords, fill=colors[i%2])
                self._speedlimitsegs.append(line_id)
            prev_ps = ps
        print("ids of lines created:", self._speedlimitsegs)

class SpeedDistView:
    '''The View, which controller updates, and which owns the frame containing
    the canvas on which the lines are to be drawn'''

    def __init__(self, controller, parent_frame):
        self._controller = controller
        self._viewframe = SpeedDistViewFrame(parent_frame, self._controller)
        self._viewframe.pack()

    def update(self, best_speeds, speed_limits):
        #self._viewframe.make_boundary_lines(speed_limits)
        self._viewframe.make_limit_lines(speed_limits)
        
if __name__=="__main__":
    model = EditableTrack("short_maxspeeds.csv", "imperial")
    root = tk.Tk()
    view = SpeedDistView(None, root)

    view.update([], [PosSpeed(0, 0), PosSpeed(0, 20), PosSpeed(0.9, 30), PosSpeed(1.5, 15), PosSpeed(1.8, 45), PosSpeed(4.2, 30), PosSpeed(5.1, 15), PosSpeed(5.3, 0), PosSpeed(5.3, None)])

    root.mainloop()
