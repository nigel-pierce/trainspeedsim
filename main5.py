
class ArgumentError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

from collections import namedtuple
MaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])

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
        return self._track(index + direction)

    def _load_maxspeeds(self, filename):
        import csv
        raw_maxspeeds = [maxspeed for maxspeed in map (MaxSpeed._make, csv.reader(open(filename, "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
        
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
 


if __name__ == "__main__":
    seg = TrackSeg(0, 0, 0.1*5280, 25*5280/3600)
    print("seg: ", seg)
    print("seg: ", str(seg))
    print("seg: ", repr(seg))
    seg1 = eval(repr(seg))
    print("seg1:", seg1)
    
    print("seg.length(): expect 528", seg.length())
    print("seg.get_index(): expect 0", seg.get_index())
    print("seg.get_start(): expect 0", seg.get_start())
    print("seg.get_end(): expect 528", seg.get_end())
    print("seg.get_speed(): expect", 25*5280/3600, seg.get_speed())

    track = Track("sprinter_maxspeeds4.csv")

    print(track)
    print(track.get_first_seg())
    print(track.get_next_seg(0, "?"))
