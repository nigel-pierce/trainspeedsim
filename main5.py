
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
    

if __name__ == "__main__":
    seg = TrackSeg(0, 0, 0.1*5280, 25*5280/3600)
    print("seg: ", seg)
    print("seg: ", str(seg))
    print("seg: ", repr(seg))
    seg1 = eval(repr(seg))
    print("seg1:", seg1)
    
    print("seg.length(): expect 528", seg.length())
