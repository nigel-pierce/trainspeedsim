#! /usr/bin/python3

from simulation import Simulation, Track, TrackSeg
from convunits import Pos, Speed

class EditableTrackSeg(TrackSeg):
    def __init__(self, index, start, end, speed):
        TrackSeg.__init__(self, index, start, end, speed)
        # I think that's it as far as constructoring goes

    def set_index(self, index):
        assert index >= 0 and type(index) is int
        self._index = index

    def set_start(self, start):
        assert start <= self._end
        self._start = start

    def set_end(self, end):
        assert end >= self._start
        self._end = end

    # Convenience method
    def set_start_end(self, start, end):
        assert start <= end
        self._start = start
        self._end = end



if __name__ == "__main__":
    seg = EditableTrackSeg(3, Pos(0, "mi").to_smaller_unit(), \
            Pos(0, "mi").to_smaller_unit(), Speed(0, "mi/h").to_smaller_unit())
    print(seg)

    print("Testing invalid (Editable)TrackSegs on construction")
    try:
        seg2 = EditableTrackSeg(-2, Pos(0.2, "mi").to_smaller_unit(),
                Pos(0.3, "mi").to_smaller_unit(), Speed(100, 
                "mi/h").to_smaller_unit())
        print(seg2)
    except AssertionError as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(1, Pos(1, "mi").to_smaller_unit(),
                Pos(0.9, "mi").to_smaller_unit(), Speed(25, 
                "mi/h").to_smaller_unit())
        print(seg2)
    except AssertionError as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(10, Pos(30, "mi").to_smaller_unit(),
                Pos(30.1, "mi").to_smaller_unit(), Speed(0, 
                "mi/h").to_smaller_unit())
        # I need to make it so I don't need to call to_smaller_unit() so much
        print(seg2)
    except AssertionError as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(10, Pos(30, "mi").to_smaller_unit(),
                Pos(30, "mi").to_smaller_unit(), Speed(10, 
                "mi/h").to_smaller_unit())
        # Actually this should be OK
        print(seg2)
    except AssertionError as e:
        print(repr(e))
