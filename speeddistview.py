#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from itertools import zip_longest
from simulation import PosSpeed
from editablesim import EditableTrack
from controller import Controller

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
        self.make_or_reuse_lines(speed_limits, self._speedlimitsegs, 
                lambda prev_ps, ps: (prev_ps.pos, prev_ps.speed, ps.pos, 
                    prev_ps.speed))

    def make_boundary_lines(self, speed_limits):
        '''yeah, so the vertical lines'''
        self.make_or_reuse_lines(speed_limits[:-1], self._segboundaries,
                lambda prev_ps, ps: (ps.pos, prev_ps.speed, ps.pos, ps.speed))

    def make_or_reuse_lines(self, things, lines, coord_func):
        '''things is the list of PosSpeeds, lines is the list of line IDs,
        coord_func takes prev and current PosSpeeds and returns a 4-tuple
        in graph coordinates to represent the line'''
        things_and_lines = zip_longest(things, lines)
        prev_ps = None
        for i, (ps, l) in enumerate(things_and_lines):
            if prev_ps is not None:
                if l is None:
                    # more speed limit segs than lines, so make new lines
                    gcoords = coord_func(prev_ps, ps)
                    ccoords = self.graph_seg_to_canvas(*gcoords)
                    line_id = self._canvas.create_line(ccoords, fill='black')
                    lines.append(line_id)
                elif ps is None:
                    # provided with fewer PosSpeeds/segs than lines that already
                    # exist, so exit loop and delete extra lines
                    break
                else:
                    # re-use line
                    line_id = lines[i-1] # b/c i >= 1 by the time we get here
                    gcoords = coord_func(prev_ps, ps)
                    ccoords = self.graph_seg_to_canvas(*gcoords)
                    self._canvas.coords(line_id, ccoords)
            prev_ps = ps
        if len(things) < len(lines):
            num_things = len(things)
            num_lines = len(lines)
            # I'm not sure if this next part is off-by-one TODO
            for i in range(num_things, num_lines):
                lines[i].delete()
            del lines[num_things:num_lines]


class SpeedDistView:
    '''The View, which controller updates, and which owns the frame containing
    the canvas on which the lines are to be drawn'''

    def __init__(self, controller, parent_frame):
        self._controller = controller
        self._viewframe = SpeedDistViewFrame(parent_frame, self._controller)
        self._viewframe.pack()

    def update(self, best_speeds, speed_limits):
        self._viewframe.make_boundary_lines(speed_limits)
        self._viewframe.make_limit_lines(speed_limits)
        
class SpeedDistController(Controller):
    '''Controller for interaction between SpeedDistView and sim model'''

    def __init__(self, model, parent_frame):
        self._view = SpeedDistView(self, parent_frame)
        super().__init__(model)

    def _update_view(self):
        self._view.update([], self._model.get_limits())

if __name__=="__main__":
    model = EditableTrack("short_maxspeeds.csv", "imperial")
    root = tk.Tk()
    view = SpeedDistView(None, root)

    view.update([], [PosSpeed(0, 0), PosSpeed(0, 20), PosSpeed(0.9, 30), PosSpeed(1.5, 15), PosSpeed(1.8, 45), PosSpeed(4.2, 30), PosSpeed(5.1, 15), PosSpeed(5.3, 0), PosSpeed(5.3, None)])

    root.mainloop()

    root2 = tk.Tk()
    controller = SpeedDistController(model, root2)

    root2.mainloop()
