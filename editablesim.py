#! /usr/bin/python3

from simulation import Simulation, Track, TrackSeg
from convunits import Pos, Speed

class EditableTrackSeg(TrackSeg):
    def __init__(self, index, start, end, speed):
        TrackSeg.__init__(self, index, start, end, speed)
        # I think that's it as far as constructoring goes

    def set_index(self, index):
        if not isinstance(index, int):
            raise TypeError("index must be int-derived")
        if index < 0:
            raise IndexError("index must be non-negative")

        self._index = index

    def set_start(self, start):
        if start > self._end:
            raise ValueError("start must be <= end")
        if self._speed == 0 and start != self._end:
            raise ValueError("start and end must be equal if speed is 0")
        self._start = start

    def set_end(self, end):
        if self._start > end:
            raise ValueError("start must be <= end")
        if self._speed == 0 and self._start != end:
            raise ValueError("start and end must be equal if speed is 0")
        self._end = end

    # Convenience method
    def set_start_end(self, start, end):
        if start > end:
            raise ValueError("start must be <= end")
        if self._speed == 0 and self._start != end:
            raise ValueError("start and end must be equal if speed is 0")
        self._start = start
        self._end = end



import unittest

class TestEditableTrackSegMethods(unittest.TestCase):
    def setUp(self):
        self.seg = EditableTrackSeg(14, Pos(11.4, "mi").to_smaller_unit(),
                Pos(13.5, "mi").to_smaller_unit(), Speed(25,
                "mi/h").to_smaller_unit())

    def test_set_index(self):
        self.assertEqual(self.seg.get_index(), 14)
        self.seg.set_index(30)
        self.assertEqual(self.seg.get_index(), 30)
        with self.assertRaises(IndexError):
            seg.set_index(-3)

    def test_set_start(self):
        self.assertEqual(self.seg.get_start(), Pos(11.4,
                "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(13.5, 
                "mi").to_smaller_unit())
        self.seg.set_start(Pos(10.8, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), 
                Pos(10.8, "mi").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_start(Pos(15, "mi").to_smaller_unit())
        self.seg.set_start(Pos(13.5, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(),
                Pos(13.5, "mi").to_smaller_unit())

    def test_set_end(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos(11.4, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(13.5, "mi").to_smaller_unit())
        # set end farther to 14 miles and check
        self.seg.set_end(Pos(14, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(14, "mi").to_smaller_unit())
        # set end to earlier than start (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_end(Pos(10, "mi").to_smaller_unit())
        # set end to equal start and check
        self.seg.set_end(Pos(11.4, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(),
            Pos(11.4, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), self.seg.get_end())

    def test_set_start_end(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos(11.4, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(13.5, "mi").to_smaller_unit())
        # set start and end to > current end
        self.seg.set_start_end(Pos(14, "mi").to_smaller_unit(),
                Pos(15, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), Pos(14, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(15, "mi").to_smaller_unit())
        # set start > end (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_start_end(Pos(16, "mi").to_smaller_unit(),
                    Pos(10, "mi").to_smaller_unit())
        # set start == end
        self.seg.set_start_end(Pos(9.5, "mi").to_smaller_unit(),
                Pos(9.5, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), self.seg.get_end())
        


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
    except Exception as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(1, Pos(1, "mi").to_smaller_unit(),
                Pos(0.9, "mi").to_smaller_unit(), Speed(25, 
                "mi/h").to_smaller_unit())
        print(seg2)
    except Exception as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(10, Pos(30, "mi").to_smaller_unit(),
                Pos(30.1, "mi").to_smaller_unit(), Speed(0, 
                "mi/h").to_smaller_unit())
        # I need to make it so I don't need to call to_smaller_unit() so much
        print(seg2)
    except Exception as e:
        print(repr(e))

    print("Testing valid speed > 0 when TrackSeg length == 0")
    try:
        seg2 = EditableTrackSeg(10, Pos(30, "mi").to_smaller_unit(),
                Pos(30, "mi").to_smaller_unit(), Speed(10, 
                "mi/h").to_smaller_unit())
        # Actually this should be OK
        print(seg2)
    except Exception as e:
        print(repr(e))

    print("Testing setting methods")
    unittest.main()
