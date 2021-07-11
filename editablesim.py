#! /usr/bin/python3

from simulation import Simulation, Track, TrackSeg

class EditableTrackSeg(TrackSeg):
    def __init__(self, index, start, end, speed):
        TrackSeg.__init__(index, start, end, speed)
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
