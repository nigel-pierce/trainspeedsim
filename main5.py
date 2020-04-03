
class ArgumentError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class TrackSeg:
    def __init__(self, index, start, end, speed):
        self._index = index
        self._start = int(start)
        self._end   = int(end)
        self._speed = speed
    
    def __str__(self):
        return "id: {}, {} mi - {} mi @ {:.1f} mph".format(self._index, self._start/5280, self._end/5280, self._speed*3600/5280)
    
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
    MaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])

    def __init__(self, filename):
        # load the file into TrackSegs into
        self._track = self._load_maxspeeds(filename)
        # and throw if anything goes wrong

    def __str__(self):
        out = "[\n"
        for seg in self._track:
            out += str(seg) + "\n"
        out += "]"
        return out

    def get_first_seg(self):
        return self._track[0]

    # throws IndexError and ArgumentError
    def get_next_seg(self, index, direction):
        if direction == "+": d = 1
        elif direction == "-": d = -1
        else: # raise something something I should probably use an enum
            raise ArgumentError('Direction can be only "+" or "-"')
        
        if index + d < 0: raise IndexError("Next segment index out of bounds")

        return self._track[index + d]

    def _load_maxspeeds(self, filename):
        import csv
        raw_maxspeeds = [maxspeed for maxspeed in map (self.MaxSpeed._make, csv.reader(open(filename, "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
        
        # generate segments from that
        maxspeedsegs = []
        for x in range(0, len(raw_maxspeeds)-1):
            maxguy = raw_maxspeeds[x]
            mp1 = maxguy.milepost * 5280
            maxguy2 = raw_maxspeeds[x+1]
            mp2 = maxguy2.milepost * 5280
            #if maxguy2.speed != 0:
            seg = TrackSeg(x, mp1, mp2, maxguy.speed * 5280 / 3600)
            if (x+1 == len(raw_maxspeeds)-1):
                seg = TrackSeg(x, mp1, mp2, maxguy2.speed * 5280/3600)
            maxspeedsegs.append(seg)

        return maxspeedsegs
 
class Train:
    def __init__(self, track, acceleration, resolution):
        self._track = track
        self._acceleration = acceleration
        self._resolution = resolution
        # then the derived attributes and defaults
        self._speed = 0
        self._seg = self._track.get_first_seg()
        self._pos = self._seg.get_start()
        self._dir = "+"
        self._finished_seg = False

    def __str__(self):
        return ("pos: {:.1f} mi, speed {:.2f} mph, dir: {}, seg: ({}), accel: {}, "+ \
            "res: {}, finished {}, track defined: {}").format(self._pos/5280, self._speed*3600/5280, self._dir, self._seg, self._acceleration, self._resolution, self._finished_seg, self._track is not None)

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

    # takes all units in feet units
    def _accelerate(self, v_target, acc, v_i, d):
        nacc = acc
        from math import sqrt
        t = ( -v_i + sqrt(v_i**2 - 4.0 * 0.5 * nacc * -d) ) / (2.0*0.5*nacc)
        #print("sec from prev index point segment guy:", t)
        #print("target speed", v_target, "fps (",(v_target*3600/5280.0),"mph)")
        v_f = nacc * t + v_i
        return v_f

    def _travel_non0_seg(self):
        assert self._seg.length() % self._resolution == 0

        # accelerate() over one resolution of distance? I didn't think 
        # this far ahead.
        segspeed = self._seg.get_speed()
        self._speed = min(segspeed, self._accelerate(segspeed, self._acceleration, self._speed, self._resolution))

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

class Simulation:
    from collections import namedtuple
    PosSpeed = namedtuple("PosSpeed", ["pos", "speed"])

    def __init__(self, filename, accel, resolution):
        self._resolution = resolution
        self._track = Track(filename)
        self._train = Train(self._track, accel, self._resolution)
        self._best_speeds = []

    def run(self):

        #print(self._train)
        #print("The train is leaving the station!")
        fwd_best_speeds = []
        while not self._train.at_end_of_track():
            self._train.travel_seg()
            #print(self._train)
            if not self._train.at_end_of_track(): # prevents repeating last seg
                fwd_best_speeds.append(self.PosSpeed(self._train.get_pos(), \
                    self._train.get_speed()))
        #print("And finally...", self._train)
        self._train.set_dir("-")
        #print("--------- REVERSING COURSE ----------")
        rev_best_speeds = []
        while not self._train.at_end_of_track():
            self._train.travel_seg()
            #print(self._train)
            if not self._train.at_end_of_track():
                rev_best_speeds.append(self.PosSpeed(self._train.get_pos(), \
                    self._train.get_speed()))
        #print("And finally...", self._train)

        # note: all of that up there generated duplicate PosSpeeds for 0mph or 
        # 0-length (not sure which is important) segments
        # we will need to fix this when building self._best_speeds

        lastps = None
        for paired in zip(fwd_best_speeds, reversed(rev_best_speeds)):
            #print(paired[0].pos/5280, "vs", paired[1].pos/5280)
            assert paired[0].pos == paired[1].pos
            ps = self.PosSpeed(paired[0].pos, min(paired[0].speed, \
                paired[1].speed))
            if (lastps is not None and (ps.pos != lastps.pos and ps.speed != lastps.speed)):
                self._best_speeds.append(ps)
            lastps = ps
            
    def output(self):
        #print("-----------OUTPUT-------------")
        for point in self._best_speeds:
            print("{:.1f}, {}".format(point.pos/5280, point.speed*3600/5280))
    

if __name__ == "__main__":
    sim = Simulation("sprinter_maxspeeds4.csv", 1.25, 528)

    sim.run()

    sim.output()
