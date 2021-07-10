#! /usr/bin/python3

from multidict import MultiDict
from convunits import Pos, Speed, Accel


class TrackSeg:
    def __init__(self, index, start, end, speed):
        assert index >= 0 and type(index) is int
        assert start <= end
        assert speed >= 0
        self._index = index
        self._start = start
        self._end   = end
        self._speed = speed
    
    def __str__(self):
        # want units to be in miles/km ("big" units)
        return "id: {}, {} - {} @ {}".format(self._index, self._start.to_bigger_unit(), self._end.to_bigger_unit(), self._speed)
    #.to_bigger_unit())
    
    def __repr__(self):
        return "TrackSeg(index={}, start={}, end={}, speed={})".format(self._index, self._start, self._end, self._speed)
    
    def get_index(self):
        return self._index
    
    def get_start(self):
        return self._start
    
    def get_end(self):
        return self._end
    
    def get_speed(self):
        return self._speed
    
    def length(self):
        return self._end - self._start
    
class Track:
    from collections import namedtuple
    RawMaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])

    def __init__(self, filename, units):
        # load the file into TrackSegs into
        self._track = self._load_maxspeeds(filename, units)
        # and throw if anything goes wrong
        assert len(self._track) > 0, "there must be at least one track segment"

    def __str__(self):
        out = "[\n"
        for seg in self._track:
            out += str(seg) + "\n"
        out += "]"
        return out

    def get_first_seg(self):
        return self._track[0]

    # throws IndexError and AssertionError
    def get_next_seg(self, index, direction):
        assert direction == "+" or direction == "-"
        if direction == "+": d = 1
        elif direction == "-": d = -1
        
        if index + d < 0: raise IndexError("Next segment index out of bounds")

        return self._track[index + d]

    def _load_maxspeeds(self, filename, units):
        assert units in ["imperial", "metric"]
        import csv
        raw_maxspeeds = [maxspeed for maxspeed in map (self.RawMaxSpeed._make, csv.reader(open(filename, "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
        
        if units == "imperial":
            pos_unit = "mi"
            speed_unit = "mi/h"
        elif units == "metric":
            pos_unit = "km"
            speed_unit = "km/h"
        else:
            assert False # should never get here

        # assign units
        # assumes units in file are "big units" (mi or km, mph or kph)
        # might change that later (TODO)
        # generate segments from that
        maxspeedsegs = []
        for x in range(0, len(raw_maxspeeds)-1):
            maxguy = raw_maxspeeds[x]
            mp1 = Pos(maxguy.milepost, pos_unit).to_smaller_unit()
            maxguy2 = raw_maxspeeds[x+1]
            mp2 = Pos(maxguy2.milepost, pos_unit).to_smaller_unit()
            #if maxguy2.speed != 0:
            speed1 = Speed(maxguy.speed, speed_unit).to_smaller_unit()
            seg = TrackSeg(x, mp1, mp2, speed1)
            if (x+1 == len(raw_maxspeeds)-1):
                speed2 = Speed(maxguy2.speed, speed_unit).to_smaller_unit()
                seg = TrackSeg(x, mp1, mp2, speed2)
            maxspeedsegs.append(seg)

        return maxspeedsegs
 
class Train:
    def __init__(self, track, acceleration, resolution):
        assert acceleration > 0
        assert resolution > 0 and resolution % 1 == 0 # is inty
        self._track = track
        self._acceleration = acceleration
        self._resolution = resolution
        # then the derived attributes and defaults
        self._seg = self._track.get_first_seg()
        self._speed = self._seg.get_speed() # first segment better be 0 speed
        assert self._speed == 0 # oh I can make sure of that
        self._pos = self._seg.get_start()
        self._dir = "+"
        self._finished_seg = False

    def __str__(self):
        return ("pos: {:.1f}, speed {:.2f}, dir: {}, seg: ({}), accel: {}, "+ \
            "res: {}, finished {}, track defined: {}").format(self._pos.to_bigger_unit(), self._speed.to_bigger_unit(), self._dir, self._seg, self._acceleration, self._resolution, self._finished_seg, self._track is not None)

    def get_pos(self):
        return self._pos

    def get_speed(self):
        return self._speed

    def finished_seg(self):
        return self._finished_seg

    def at_end_of_track(self):
        assert self._dir == "+" or self._dir == "-"
        if self._dir == "+":
            try:
                self._track.get_next_seg(self._seg.get_index(), self._dir)
            except IndexError:
                # we must be at last segment already
                # check if we are at the end of it
                return self._pos == self._seg.get_end()
        else:
            return self._seg == self._track.get_first_seg() and self._pos == \
                self._seg.get_start()

    def set_dir(self, direction):
        assert direction == "+" or direction == "-"
        self._dir = direction
        self._finished_seg = False

    # kind of does everything
    # travels along 1 resolution of track each call
    # automatically loads the next TrackSeg when at end of current one
    # returns false when it's finished the last resolution-length in seg
    # (i.e. self._finished_seg == True I think)
    # (except when it's at end of last seg in track, in which case it returns
    # False even though self._finished_seg is True)
    # ...
    # I need to think this through better.
    def travel_seg(self):
        if self._finished_seg == True:
            # load next seg
            try:
                self._seg = self._track.get_next_seg(\
                    self._seg.get_index(), self._dir)
                self._finished_seg = False
            except IndexError:
                # must be at one end of the track
                return False
            #return True # not sure what this one was here for
    
        if self._finished_seg == False:
            if (self._seg.length() != 0):
                self._finished_seg = self._travel_non0_seg()
            else:
                self._speed = min(self._seg.get_speed(), self._speed)
                # well I guess we're instantly finished with a 0-length seg
                self._finished_seg = True

        return self._finished_seg

    def _accelerate(self, v_target, acc, v_i, d):
        assert v_target >= 0 and v_i >= 0
        assert d >= 0
        assert acc > 0
        nacc = acc
        from math import sqrt
        t = ( -v_i + sqrt(v_i**2 - 4.0 * 0.5 * nacc * -d) ) / (2.0*0.5*nacc)
        v_f = nacc * t + v_i
        return v_f

    def _travel_non0_seg(self):
        assert self._seg.length() % self._resolution == 0

        # accelerate() over one resolution of distance? I didn't think 
        # this far ahead.
        segspeed = self._seg.get_speed()
        acc_speed = Speed(self._accelerate(segspeed.val(), self._acceleration.val(), \
            self._speed.val(), self._resolution.val()), self._speed.unit())
        self._speed = min(segspeed, acc_speed)
            

        # always travels over seg at least *once*, even if zero-length
        assert self._dir == "+" or self._dir == "-"
        if self._dir == "+":
            self._pos += self._resolution
            if self._pos == self._seg.get_end():
                self._finished_seg = True
        elif self._dir == "-":
            self._pos -= self._resolution
            if self._pos == self._seg.get_start():
                self._finished_seg = True
        return self._finished_seg

class ArgvError(Exception):
    """ An error having to do with the command-line arguments """
    pass

class Config:
    class FlagDesc:
        def __init__(self, needs_val, default_val=None):
            self.val = None
            self.needs_val = needs_val
            self.default_val = default_val

    def __init__(self, argv):
        self._flagsdict = MultiDict({("-u", "--units"): self.FlagDesc(True, \
            "imperial")})
        self._flagsdict["-b"] = self.FlagDesc(False)
        self._flagsdict.join("--boolean", "-b")
        self._flagsdict["-a"] = self.FlagDesc(True, Accel(1.25, "f/s^2"))
        self._flagsdict.join("--acceleration", "-a")
        self._flagsdict["-r"] = self.FlagDesc(True, \
            {"imperial": Pos(528, "f"), "metric": Pos(100, "m")} )
        self._flagsdict.join("--resolution", "-r")
        self._flagsdict["-h"] = self.FlagDesc(False)
        self._flagsdict.join("--help", "-h")
        
        # declare what we're configuring (just to be clear)
        self.mode = None
        self.infile = None
        self.units = None
        self.accel = None
        self.res = None

        self._parse(argv)
        self._validate_args()
    
    def _parse(self, argv):
        # input filename is just by itself, all other args are -<FLAG> val
        assert len(argv) > 1
        #for arg in argv[1:]:
        isflagval = False
        for arg in argv[1:]:
            if arg[0] == "-" and not isflagval: # it's a flag
                if arg in self._flagsdict:
                    if self._flagsdict[arg].needs_val:
                        flag = arg
                        isflagval = True # next argv entry must be a value
                    else:
                        self._flagsdict[arg].val = True
                else:
                    raise KeyError("No such flag")
            elif isflagval:
                if self._flagsdict[flag].val == None:
                    self._flagsdict[flag].val = arg
                    isflagval = False
                else:
                    raise ArgvError("Cannot define flag multiple times")
            else: # must be by itself (so probably input filename)
                if self.infile == None:
                    self.infile = arg
                else:
                    raise ArgvError("Cannot have multiple input files")
        
    def _validate_args(self):
        # make sure arguments are logical and consistent etc.
        if self._flagsdict["-h"].val == True:
            self.mode = "help"
        else:
            # default configuration or something
            self.mode = "sim"

        if self.mode == "sim":
            uflag = self._flagsdict["-u"]
            if uflag.val is not None:
                if uflag.val in ["imperial", "metric"]:
                    self.units = uflag.val
                else:
                    raise ArgvError('Value of -u flag must be "imperial" or '+\
                        '"metric"')
            else:
                self.units = uflag.default_val
            # self.units is now either "imperial" or "metric"

            if self.infile == None:
                raise ArgvError("Must specify input file")

            aflag = self._flagsdict["-a"]
            if aflag.val is not None:
                accel_unit = {"imperial": "f/s^2", "metric": "m/s^2"}
                self.accel = Accel(float(aflag.val), accel_unit[self.units])
            else: # default, in the relevant unit
                if self.units == "imperial":
                    self.accel = aflag.default_val
                elif self.units == "metric":
                    self.accel = aflag.default_val.convert_to("m/s^2")
                else:
                    # should never get here
                    raise RuntimeError("How did we get here?")

            rflag = self._flagsdict["-r"]
            if rflag.val is not None:
                dist_unit = {"imperial": "f", "metric": "m"}
                self.res = Pos(float(rflag.val), dist_unit[self.units])
            else: # default, in the relevant unit
                self.res = rflag.default_val[self.units]

        if self.mode == "help":
            pass
       
    def gen_help(self):
        # generate this automagically from self._flagsdict later
        return  "trainspeedsim [-h|--help | OPTIONS] INPUT_FILE\n" + \
                "OPTIONS:\n" + \
                "  -u|--units: imperial|metric\n" + \
                "  -a|--acceleration: decimal value (default: 1.5 ft/s^2 " + \
                "or that converted to\n    m/s^2)\n" + \
                "  -r|--resolution: integral value (default: 528 f or 100 m)"

class Simulation:
    from collections import namedtuple
    PosSpeed = namedtuple("PosSpeed", ["pos", "speed"])

    def __init__(self, filename, accel, resolution, units):
        assert accel > 0
        assert resolution > 0 and resolution % 1 == 0 # more generic than is int
        assert units in ["imperial", "metric"] # there must be a more generic way
        self._units = units
        self._resolution = resolution
        self._track = Track(filename, self._units)
        self._train = Train(self._track, accel, self._resolution)
        self._best_speeds = []

    def run(self):

        fwd_best_speeds = self._gen_best_speeds_dir("+")
        
        rev_best_speeds = self._gen_best_speeds_dir("-")

        # note: all of that up there generated duplicate PosSpeeds for 0-length 
        # segments
        # we will need to fix this when building self._best_speeds

        lastps = None
        for paired in zip(fwd_best_speeds, reversed(rev_best_speeds)):
            assert paired[0].pos == paired[1].pos
            ps = self.PosSpeed(paired[0].pos, min(paired[0].speed, \
                paired[1].speed))
            if (lastps is None or (ps.pos != lastps.pos or ps.speed != lastps.speed)):
                self._best_speeds.append(ps)
            lastps = ps
            
    def output(self):
        for point in self._best_speeds:
            # round so that e.g. 49.99999999999999 displays as 50.0
            # using HasUnit introduces rounding error, so that's compensating
            # sort of
            # on second thought, I will use fractions.Fraction for the
            # conversion
            print("{:.1f}, {}".format(point.pos.to_bigger_unit().val(), \
                point.speed.to_bigger_unit().val()))
    
    def _gen_best_speeds_dir(self, direction):
        assert direction=="+" or direction=="-"
        best = []
        self._train.set_dir(direction)
        while not self._train.at_end_of_track():
            self._train.travel_seg()
            if not self._train.at_end_of_track(): # prevents repeating last seg
                best.append(self.PosSpeed(self._train.get_pos(), \
                    self._train.get_speed()))
        return best
        

if __name__ == "__main__":

    import sys
    conf = Config(sys.argv)

    if conf.mode == "sim":
        try:
            # acceleration used to be hard-coded to 1.25 (in f/s^2)
            # resolution was hard-coded to 528 (f) as well
            # for now let's keep it hard-coded but as a Pos instead (in Conf)
            sim = Simulation(conf.infile, conf.accel, conf.res, conf.units)
        except FileNotFoundError as e:
            sys.stderr.write(str(e)+"\n")
            exit()
        sim.run()
        sim.output()
    elif conf.mode == "help":
        print(conf.gen_help())

    
