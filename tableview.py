#! /usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from itertools import zip_longest
from simulation import PosSpeed
from editablesim import EditableTrack
from editablesim import SituationError, AmbiguousBoundaryError, \
    Adjacent0LenExistsError, Adjacent0LenPotentialError, \
    Non0LengthOf0SpeedSegPotentialError
from observer import Observer

class ViewFrame(tk.Frame):
    """the widget and elements and stuff"""

    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self._controller = controller
        #self.pack()
        
        # column headers
        self.boundhead = ttk.Label(self)
        self.boundhead["text"] = "MP Boundary"
        self.boundhead.grid(row=0, column=0) # hopefully packs with other label
        print("boundary header:  {}, its text: {}".format(repr(self.boundhead), self.boundhead["text"]))
        self.limithead = ttk.Label(self)
        self.limithead["text"] = "Speed Limit"
        self.limithead.grid(row=0, column=1)
        print("speed limit header:  {}, its text: {}".format(repr(self.limithead), self.limithead["text"]))

        
        # pretend/mockup boundary spinboxes
        #self.make_boundary_entries()
        #self.make_limit_entries()

        # where the spinboxes are stored
        # (they get re-used)
        self.boundary_entries = []
        self.limit_entries = []

    def make_boundary_entries(self, boundaries):

        self.make_or_reuse_entries(boundaries, self.boundary_entries, 0, 1, 
                0, 10000, 0.1, self._controller.shift_boundary)
        '''
        boundaries_and_entries = enumerate(zip_longest(boundaries,
            self.boundary_entries))

        #print([x for x in boundaries_and_entries])

        for i, (b, e) in boundaries_and_entries:
            print(i, b, e)
            if e is None:
                # more PosSpeed things than entries, so make new entries
                self.boundary_entries.append(ttk.Spinbox(self, from_=0,
                    to=10000, increment=0.1))
                sbox = self.boundary_entries[-1]
                sbox.insert(0, b)
                sbox.grid(column=0, row=i*2+1)
            elif b is None:
                # update provides us with fewer PosSpeed things than before
                # so leave loop and then delete the extra entries/spinboxes
                break
            else:
                # re-use entry
                sbox = self.boundary_entries[i]
                sbox.delete(0, len(sbox.get()))
                sbox.insert(0, b)

        if len(boundaries) < len(self.boundary_entries):
            # excess spinbox widgets; destroy unneeded ones
            num_boundaries = len(boundaries)
            num_entries = len(self.boundary_entries)
            for i in range(num_boundaries, num_entries):
                self.boundary_entries[i].destroy()
            del self.boundary_entries[num_boundaries:num_entries]
        '''

    def print_args(*args, **kwargs):
        print(args, kwargs)

    def make_or_reuse_entries(self, things, entries, col, row_offset, fromm, 
            too, inc, controller_command):
        things_and_entries = zip_longest(things, entries)
        for i, (t, e) in enumerate(things_and_entries):
            if e is None:
                # more PosSpeed things than entries, so make new entries
                entries.append(ValidatableSpinbox(self, t, fromm,
                    too, inc, controller_command))
                sbox = entries[-1]
                sbox.spinbox.grid(column=col, row=i*2+row_offset)
                #sbox
            elif t is None:
                # update provides us with fewer PosSpeed things than before
                # so leave loop and then delete the extra entries/spinboxes
                break
            else:
                # re-use entry
                sbox = entries[i]
                sbox.replace_val(t)
        if len(things) < len(entries):
            # excess spinbox widgets; destroy unneeded ones
            num_things = len(things)
            num_entries = len(entries)
            for i in range(num_things, num_entries):
                entries[i].destroy()
            del entries[num_things:num_entries]


    def make_limit_entries(self, limits):
        temp_limits = [0, 20, 40, 35, 0, 50, 0]

        self.make_or_reuse_entries(limits[:-1], self.limit_entries, 1, 2, 0,
                1000, 1, lambda x, y: None) # TODO make the model and controller
                                            # shift_speed_limit() method
        '''
        for i, l in enumerate(limits):
            self.limit_entries.append(ttk.Spinbox(self, from_=0, to=1000))
            sbox = self.limit_entries[-1]
            sbox.insert(0, l)
            sbox.grid(column=1, row=i*2+2)
        '''

class ValidatableSpinbox:
    '''Stores "old" value alongside Spinbox and validates new values,
    calls controller to do that and commit change if valid. THIS IS NOW AN
    ABSTRACT CLASS, due to differences between boundary and speed limit 
    spinbox value storange needs'''

    def __init__(self, parent_frame, init_val, fromm, too,
            inc, controller_command):
        # method of controller that this spinbox calls when modified
        self._controller_command = controller_command
        # spinbox is public
        self.spinbox = ttk.Spinbox(parent_frame, from_=fromm,
                    to=too, increment=inc)
        self.replace_val(init_val)
        # event-ish handler for arrows pressed
        self.spinbox["command"] = self._try_commit
        # TODO assign focus, key enter event handlers
        self._value = init_val

    def replace_val(self, new_val):
        '''New val had better be valid, because this doesn't check'''
        self._value = new_val
        self.spinbox.delete(0, len(self.spinbox.get()))
        self.spinbox.insert(0, self._value)

    def destroy(self):
        self.spinbox.destroy()

    def _try_commit(self):
        '''User has modified value in spinbox, try to commit the change
        or if invalid revert displayed value and display error message'''
        from decimal import Decimal
        new_val = Decimal(self.spinbox.get())

        try:
            self._controller_command(self._value, new_val-self._value)
            #self._value = new_val
        except (ValueError, Non0LengthOf0SpeedSegPotentialError, Adjacent0LenPotentialError) as e:
            print(e.args)
            self.replace_val(self._value)

    pass

class TableView:
    def __init__(self, controller, parent_frame):
        self.controller = controller
        self.frame = ViewFrame(parent_frame, self.controller)
        self.frame.pack()

    def update(self, best_speeds, speed_limits):
        self.frame.make_boundary_entries([ps.pos for ps in speed_limits])
        self.frame.make_limit_entries([ps.speed for ps in speed_limits])
        # do best_speeds later

class TableController(Observer):
    def __init__(self, model, parent_frame):
        self._model = model
        self._view = TableView(self, parent_frame)
        self._update_view()
        # do this last since modifying (registering with) model shouldn't
        # happen until all else has been successful
        Observer.__init__(self, self._model)

    def notify(self, observable, message, arg=None):
        if message not in ("ChangeSuccess", "ChangeFail", "NoChange"):
            raise ValueError("Message "+str(message)+" is not known")

        if observable is self._model:
            if message == "ChangeSuccess":
                print("Change success")
                self._update_view()
            elif message == "ChangeFail":
                # arg should be an exception
                print("Error: "+str(arg.args))
                # update view anyway (easiest way to set correct view)
                self._update_view()
            elif message == "NoChange":
                print("No change")
            else:
                # shouldn't get here
                raise RuntimeError("should not get here (message and arg: "\
                        "'{}'; '{}')".format(message, arg))
        else:
            raise ValueError("{} is not the model ({})".format(observable,
                self._model))

    def shift_boundary(self, mp, dist):
        '''No need for exception checking because errors are notified back
        to controller'''
        from convunits import Pos, Speed
        self._model.shift_boundary(Pos(mp, 'mi').to_sm(), 
                Pos(dist, 'mi').to_sm())

    def _update_view(self):
        self._view.update([], self._model.get_limits())


class TempTableController:
    '''Quick & dirty controller that owns model (EditableTrack) and view.
    It's exploratory.'''
    def __init__(self, filename, units_, parent_frame):
        self._model = EditableTrack(filename, units=units_)
        self._view = TableView(self, parent_frame)
        self._update_view()
        
    def _update_view(self):
        self._view.update([], self._model.get_limits())
        print(self._model)

    def shift_boundary(self, mp, dist):
        '''model uses feet, so have to convert mp and dist (unitless, but in 
        miles) to Pos with miles '''
        from convunits import Pos, Speed
        try:
            self._model.shift_boundary(Pos(mp, 'mi').to_sm(), 
                Pos(dist, 'mi').to_sm())
        finally:
            print("about to _update_view()")
            self._update_view()

if __name__ == "__main__":
    '''root = tk.Tk()
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

    # again, but provide only 3 dudes (not sure what will happen)
    temp_boundrs3 = ['100', '100', '104']
    temp_ps3 = [PosSpeed(b, 1) for b in temp_boundrs3]
    tableview.update([], temp_ps3)

    # use temp_boundaries along with speed limits from short_maxspeeds.csv
    temp_limits = ['0', '20', '40', '35', '0', '50', '50', '0']
    temp_ps4 = [PosSpeed(b, l) for b, l in zip_longest(temp_boundaries,
        temp_limits)]
    tableview.update([], temp_ps4)

    windo.mainloop()'''

    model = EditableTrack("short_maxspeeds.csv", "imperial") 
    root2 = tk.Tk()
    controller = TableController(model, root2)

    root2.mainloop()
