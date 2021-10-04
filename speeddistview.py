#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from itertools import zip_longest
from simulation import PosSpeed
from editablesim import EditableTrack
from controller import Controller
from copy import copy

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

        self._gconfig = GraphConfig()

        gridcolor = "#bbb"
        axiscolor = "#777"

        # axes of graph
        # (0, 200, 400, 200)
        self._canvas.create_line(self._gconfig.graph_seg_to_canvas(
            self._gconfig._x_range[0], self._gconfig._y_range[0],
            self._gconfig._x_range[1], self._gconfig._y_range[0]), 
            fill=axiscolor)
        # (0, 200, 0, 100)
        self._canvas.create_line(self._gconfig.graph_seg_to_canvas(
            self._gconfig._x_range[0], self._gconfig._y_range[0],
            self._gconfig._x_range[0], self._gconfig._y_range[1]), 
            fill=axiscolor)

        # tics on axes
        for i in range(self._gconfig._x_range[0], self._gconfig._x_range[1]):
            ccoords = self._gconfig.graph_seg_to_canvas(i, 
                    self._gconfig._y_range[0], i, self._gconfig._y_range[0])
            # 5 px high tic
            ccoords = (ccoords[0], ccoords[1], ccoords[2], ccoords[3]+5)
            self._canvas.create_line(ccoords, fill=axiscolor)
        for i in range(self._gconfig._y_range[0], self._gconfig._y_range[1], 5):
            ccoords = self._gconfig.graph_seg_to_canvas(
                    self._gconfig._x_range[0], i, self._gconfig._x_range[0], i)
            # 5 px wide tic
            ccoords = (ccoords[0], ccoords[1], ccoords[2]-5, ccoords[3])
            self._canvas.create_line(ccoords, fill=axiscolor)

        # grid lines (just speed for now)
        for i in range(self._gconfig._y_range[0], self._gconfig._y_range[1], 5):
            ccoords = self._gconfig.graph_seg_to_canvas(
                    self._gconfig._x_range[0], i, self._gconfig._x_range[1], i)
            self._canvas.create_line(ccoords, fill=gridcolor)

        self._segboundaries = []
        self._speedlimitsegs = []


    def make_limit_lines(self, speed_limits):
        '''For now just draw some lines--Oh cool the canvas is kind of smart'''
        #print("making or reusing speed limit lines")
        # event handler
        #def b1down_handler(event):
            #print("limit line {} clicked at {}".format(\
                    #event.widget.find_withtag('current'), event))

        #def drag_handler(event):
            #print("limit line {} dragged at {}".format(\
                    #event.widget.find_withtag('current'), event))
        '''
        self.make_or_reuse_lines(speed_limits, self._speedlimitsegs, 
                lambda prev_ps, ps: (prev_ps.pos, prev_ps.speed, ps.pos, 
                    prev_ps.speed), (self._save_mousepos, 
                        self._drag_limit_line), ("limitline",))
                        '''
        self.make_or_reuse_lines(speed_limits, self._speedlimitsegs, 
                DraggableLimit)

    def make_boundary_lines(self, speed_limits):
        '''yeah, so the vertical lines'''
        # event handler
        #def drag_handler(event):
            #print("boundary line {} clicked at {}".format(\
                    #event.widget.find_withtag('current'), event))
        #print("making or reusing segment boundary lines")
        '''self.make_or_reuse_lines(speed_limits[:-1], self._segboundaries,
                lambda prev_ps, ps: (ps.pos, prev_ps.speed, ps.pos, ps.speed),
                (self._save_mousepos, self._drag_boundary_line),
                ("boundaryline",))
        '''

        self.make_or_reuse_lines(speed_limits[:-1], self._segboundaries, 
                DraggableBoundary)

    #def make_or_reuse_lines(self, things, lines, coord_func, handlers, 
            #tagss=None):
        '''things is the list of PosSpeeds, lines is the list of line IDs,
        coord_func takes prev and current PosSpeeds and returns a 4-tuple
        in graph coordinates to represent the line'''
    def make_or_reuse_lines(self, things, lines, LineType):
        '''things is the list of PosSpeeds, lines is the list of 
        (DraggableLine-descendant) line objects, LineType is the specific 
        DraggableLine subclass'''
        #print("line ids: {}".format(lines))
        #print("len(things): {}; len(lines): {}".format(len(things), len(lines)))
        things_and_lines = zip_longest(things, lines)
        prev_ps = None
        orig_num_lines = len(lines)
        for i, (ps, l) in enumerate(things_and_lines):
            if prev_ps is not None:
                if l is None and len(things) > orig_num_lines+1:
                    # 2nd part of condition is to not make extra line when
                    # num of PosSpeeds is one more than (starting) number
                    # of lines
                    #print(str(i)+"; l is None")
                    # more speed limit segs than lines, so make new lines

                    lines.append(LineType(self._canvas, self._gconfig,
                        lines, prev_ps, ps))

                    '''
                    gcoords = coord_func(prev_ps, ps)
                    ccoords = self._gconfig.graph_seg_to_canvas(*gcoords)
                    line_id = self._canvas.create_line(ccoords, 
                            fill=self._gconfig.line_color[tagss[0]],
                            tags=tagss)
                    lines.append(line_id)'''
                elif ps is None:
                    #print(str(i)+"; ps is None")
                    # provided with fewer PosSpeeds/segs than lines that already
                    # exist, so exit loop and delete extra lines
                    break
                else:
                    #print(str(i)+"; neither l nor ps is None")
                    # re-use line
                    line_id = lines[i-1].get_id() # b/c i >= 1 by the time we
                                # get here
                    # ensure line not miscategorized if new tag provided (e.g.,
                    # can't be tagged 'boundaryline' AND 'limitline')
                    # actually this is redundant now that draggable lines
                    # are encapsulated
                    '''
                    if tagss is not None:
                        current_tags = self._canvas.gettags(line_id)
                        if not set(tagss).issubset(set(current_tags)):
                            # new tag(s) not (all) present in line's current
                            # tags (take as contradiction)
                            raise RuntimeError("New tag(s) {} conflict with"\
                                    "line's current tag(s) {}".format(tagss,
                                        current_tags))
                    '''
                    lines[i-1].set_ccoords_from_ps(prev_ps, ps)
                    '''
                    gcoords = coord_func(prev_ps, ps)
                    ccoords = self._gconfig.graph_seg_to_canvas(*gcoords)
                    self._canvas.coords(line_id, ccoords)
                    '''
            prev_ps = ps
        if len(things) < len(lines):
            num_things = len(things)
            num_lines = len(lines)
            print("#ps={} < #lines={}, so deleting lines [{}, {})".format(
                num_things, num_lines, num_things, num_lines))
            # I'm not sure if this next part is off-by-one TODO
            for i in range(num_things, num_lines):
                lines[i].delete()
            del lines[num_things:num_lines]

        #print("Lines tagged with {}[0]: {}".format(tagss,
            #self._canvas.find_withtag(tagss[0])))
        #print("Lines provided: {}".format(lines))
        
        # the all-important event binding(s)
        # just try click for now
        #self._canvas.tag_bind(tagss[0], "<Button-1>", handlers[0])
        # and also drag
        #self._canvas.tag_bind(tagss[0], "<B1-Motion>", handlers[1])

class GraphConfig:
    '''Graph configuration information like line colors, margins, conversion
    between graph coordinates and canvas coordinates, etc.'''
    
    def __init__(self):
        self.line_color = {'limitline': 'black', 'boundaryline': 'black'}

        # graph to pixel scaling
        self._x_scale = 30 # mult of 10 so tenths of miles/km are unambiguous
        self._y_scale = 4 # mult of 1 :I

        # ranges of graph
        self._x_range = (5, 15)
        self._y_range = (0, 60)

        # margin of graph, in canvas pixels
        self._x_margin = 32 # from left
        self._y_margin = 32 # from bottom

        # TODO add and incorporate other colors and settings
    
    def graph_seg_to_canvas(self, x1, y1, x2, y2):
        '''Converts both points on graph to tuple of canvas points for the 
        purpose of lines'''
        return (*self.graph_pt_to_canvas(x1, y1), 
                *self.graph_pt_to_canvas(x2, y2))

    def graph_pt_to_canvas(self, x, y):
        '''Converts point on graph (origin in lower left) to point on canvas
        (origin in upper left) and scales etc.'''
        return ((x-self._x_range[0])*self._x_scale+self._x_margin, 
                300-self._y_margin-(y-self._y_range[0])*self._y_scale)
    

class DraggableLine:
    '''Draggable line values/logic abstract class'''

    def __init__(self, canvas, gconfig, peers, prev_ps, ps, line_type):
        self._canvas = canvas
        self._gconfig = gconfig
        self._peers = peers
        self._value = self._val_from_ps(prev_ps, ps)
        gcoords = self._gcoords_from_ps(prev_ps, ps)
        ccoords = self._gconfig.graph_seg_to_canvas(*gcoords)
        self._id = self._canvas.create_line(ccoords, 
                fill=self._gconfig.line_color[line_type], tags=(line_type,))
        # the all-important event binding(s)
        # click
        self._canvas.tag_bind(self._id, "<Button-1>", self._save_mousepos)
        # and also drag
        self._canvas.tag_bind(self._id, "<B1-Motion>", self._drag_line)

    def get_id(self):
        return copy(self._id)

    def set_ccoords_from_ps(self, prev_ps, ps):
        '''Move the line to new position based on PosSpeeds'''
        self._canvas.coords(self._id, self._gconfig.graph_seg_to_canvas(
            *self._gcoords_from_ps(prev_ps, ps)))

    def _val_from_ps(self, prev_ps, ps):
        '''Pure virtual. Subclasses return value based on given PosSpeeds'''
        raise NotImplementedError

    def _gcoords_from_ps(self, prev_ps, ps):
        '''Also pure virtual. Subclass returns tuple of graph coordinates 
        (startx, starty, endx, endy) based on given PosSpeeds'''
        raise NotImplementedError

    def _drag_line_specific(self, event):
        '''Pure virtual. Subclass handles drag appropriately (up/down,
        left/right, ... I think I need this.'''
        raise NotImplementedError

    def _drag_line(self, event):
        '''mouse has moved, try to move speed limit line to follow'''
        # identify line segment being dragged
        line_id = event.widget.find_withtag('current')[0]
        # this should match self._id
        if line_id != self._id:
            raise RuntimeError("line IDs do not match: self._id={}, found "\
                    "id={}".format(self._id, line_id))

        self._drag_line_specific(event)

    def _save_mousepos(self, event):
        '''Saves start/previous location of click & drag'''
        self._lastx, self._lasty = event.x, event.y
        print("last mouse pos now {}".format((self._lastx, self._lasty)))


class DraggableLimit(DraggableLine):
    def __init__(self, canvas, gconfig, peers, prev_ps, ps):
        super().__init__(canvas, gconfig, peers, prev_ps, ps, "limitline")

    def _val_from_ps(self, prev_ps, ps):
        '''return value based on given PosSpeeds'''
        return prev_ps.speed

    def _gcoords_from_ps(self, prev_ps, ps):
        '''returns tuple of graph coordinates (startx, starty, endx, endy)
        based on given PosSpeeds'''
        return (prev_ps.pos, prev_ps.speed, ps.pos, prev_ps.speed)

    def _drag_line_specific(self, event):
        print("limit line {} dragged from {} to {}".format(self._id, 
            (self._lastx, self._lasty), (event.x, event.y)))

        self._save_mousepos(event)

class DraggableBoundary(DraggableLine):
    def __init__(self, canvas, gconfig, peers, prev_ps, ps):
        super().__init__(canvas, gconfig, peers, prev_ps, ps, "boundaryline")

    def _val_from_ps(self, prev_ps, ps):
        '''return value based on given PosSpeeds'''
        return ps.pos

    def _gcoords_from_ps(self, prev_ps, ps):
        '''returns tuple of graph coordinates (startx, starty, endx, endy)
        based on given PosSpeeds'''
        return (ps.pos, prev_ps.speed, ps.pos, ps.speed)

    def _drag_line_specific(self, event):
        '''mouse has moved, try to move boundary line to follow'''
        print("boundary line {} dragged from {} to {}".format(self._id, 
            (self._lastx, self._lasty), (event.x, event.y)))

        # try to shift line, see if it's successful
        # (...)
        # only save position if it was successful (i.e. actually moves line)

        self._save_mousepos(event)

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

    def shift_speed_limit(self, mp, speed_diff):
        '''Requests model to shift speed limit seg intersecting mp by 
        speed_diff. Returns whether request resulted in a shift (True) or no
        change (False)'''
        from convunits import Pos, Speed
        return self._model.shift_speed_limit(Pos(mp, 'mi').to_sm(),
                Speed(speed_diff, 'mi/h').to_sm())

if __name__=="__main__":
    model = EditableTrack("short_maxspeeds.csv", "imperial")
    root = tk.Tk()
    view = SpeedDistView(None, root)

    view.update([], [PosSpeed(0, 0), PosSpeed(0, 20), PosSpeed(0.9, 30), PosSpeed(1.5, 15), PosSpeed(1.8, 45), PosSpeed(4.2, 30), PosSpeed(5.1, 15), PosSpeed(5.3, 0), PosSpeed(5.3, None)])

    root.mainloop()

    root2 = tk.Tk()
    controller = SpeedDistController(model, root2)

    root2.mainloop()
