#! /usr/bin/python3

from simulation import Simulation, Track, TrackSeg
from convunits import Pos, Speed, system_to_unit

class EditableTrackSeg(TrackSeg):
    def __init__(self, index, start, end, speed):
        TrackSeg.__init__(self, index, start, end, speed)
        # I think that's it as far as constructoring goes

    # create EditableTrackSeg from TrackSeg
    @classmethod
    def editableify(cls, seg):
        return cls(seg.get_index(), seg.get_start(), seg.get_end(),
                seg.get_speed())

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

    def set_speed(self, speed):
        if speed < 0:
            raise ValueError("speed must be non-negative")
        if (speed == 0):
            if self._start != self._end:
                raise ValueError("if start != end, speed must be > 0")
        self._speed = speed

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
        # confirm current index
        self.assertEqual(self.seg.get_index(), 14)

        # set index
        self.seg.set_index(30)
        self.assertEqual(self.seg.get_index(), 30)

        # set index < 0 (should throw)
        with self.assertRaises(IndexError):
            seg.set_index(-3)

    def test_set_start(self):
        # confirm initial seg value
        self.assertEqual(self.seg.get_start(), Pos(11.4,
                "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(13.5, 
                "mi").to_smaller_unit())

        # set start < end
        self.seg.set_start(Pos(10.8, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), 
                Pos(10.8, "mi").to_smaller_unit())

        # set start > end (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_start(Pos(15, "mi").to_smaller_unit())

        # set start so length == 0
        self.assertEqual(self.seg.get_end(), Pos(13.5, 
                "mi").to_smaller_unit())
        self.seg.set_start(Pos(13.5, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(),
                Pos(13.5, "mi").to_smaller_unit())

        # set_start should throw ValueError IFF speed is 0 and length > 0
        self.seg.set_speed(Speed(0, "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
                Speed(0, "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_start(Pos(13.4, "mi").to_smaller_unit())

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

        # set_end should throw ValueError IFF speed is 0 and length > 0
        self.seg.set_speed(Speed(0, "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
            Speed(0, "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_end(Pos(11.6, "mi").to_smaller_unit())

    def test_set_speed(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos(11.4, "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos(13.5, "mi").to_smaller_unit())

        # set speed < 0 (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_speed(Speed(-3, "mi/h").to_smaller_unit())

        # set speed to 100 mi/h
        self.seg.set_speed(Speed(100, "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(),
                Speed(100, "mi/h").to_smaller_unit())

        # set speed to 0 mi/h, while length > 0 (should throw)
        self.assertGreater(self.seg.length(), 0)
        with self.assertRaises(ValueError):
            self.seg.set_speed(Speed(0, "mi/h").to_smaller_unit())

        # set speed 0 mi/h while length == 0
        self.seg.set_end(Pos(20, "mi").to_smaller_unit())
        self.seg.set_start(Pos(20, "mi").to_smaller_unit())
        self.assertEqual(self.seg.length(), 0)
        self.seg.set_speed(Speed(0, "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 0)

        # set speed > 0 mi/h while length == 0
        self.assertEqual(self.seg.length(), 0)
        self.seg.set_speed(Speed(20, "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
                Speed(20, "mi/h").to_smaller_unit())

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
        
        # set start < end with 0 speed, should throw
        self.seg.set_speed(Speed(0, "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_start_end(Pos(8, "mi").to_smaller_unit(),
                    Pos(9.9, "mi").to_smaller_unit())


class EditableTrack(Track):
    def __init__(self, filename=None, units=None):
        if filename is None:
            # start a track from scratch
            self._track = []
            self._units = units
        else:
            # Track-style behavior and load a track
            Track.__init__(self, filename, units)
            # Make it editable
            self._editableify()
            self._units = units

    def _editableify(self):
        for i in range(0, len(self._track)):
            editable_seg = EditableTrackSeg.editableify(self._track[i])
            self._track[i] = editable_seg

    def __str__(self):
        return Track.__str__(self) + "\nEditable"

    def append_seg(self, speed, length):
        # no need to validate, EditableTrackSeg takes care of that
        pos_unit = system_to_unit(self._units, "pos", "big")
        if len(self._track) == 0:
            index = 0
            start = Pos(0, pos_unit).to_smaller_unit()
            end = length
        else:
            index = self._track[-1].get_index() + 1
            start = self._track[-1].get_end()
            end = start + length

        # append new EditableTrackSeg
        self._track.append(EditableTrackSeg(index, start, end, speed))

    # Splits track segment that mp intersects with, at mp
    # Throws if mp lies on boundary of track segment (i.e. mp == seg.get_start()
    # or mp == seg.get_end() for some segment seg)
    def split_seg(self, mp):
        # throw if there's no track
        if len(self._track) == 0:
            raise SituationError("no track segments exist")
        # throw if mp outside of range of track
        if mp < self._track[0].get_start() or mp > self._track[-1].get_end():
            raise ValueError("mp "+mp+" outside of track boundaries")
        # throw if trying to split at segment boundary
        # (this includes 0-length segments)
        if self._on_boundary(mp):
            raise ValueError("mp "+mp+" on segment boundary")

        pass

    # Checks if mp is "on boundary" of a track seg by seeing if len of tuple
    # returned by self._intersecting_segs(mp) > 1
    def _on_boundary(self, mp):
        return len(self._intersecting_segs(mp)) > 1

    # mp "intersects" any track segment where start <= mp <= end
    # hence it can intersect on boundaries and 0-length segments
    def _intersecting_segs(self, mp):
        if (mp < 0):
            raise ValueError("mp must be non-negative")
        # maybe also check if it's > final segment's end?

        # we'll have to do a search
        low_index = 0
        high_index = len(self._track) - 1
        check_index = round((low_index + high_index) / 2)

        while True:
            seg = self._track[check_index]
            if seg.get_start() <= mp and seg.get_end() >= mp:
                break
            elif seg.get_start() > mp:
                # - 1 b/c seg at check_index is NOT intersected
                high_index = check_index - 1
            elif seg.get_end() < mp:
                # + 1 b/c seg at check_index is NOT intersected
                low_index = check_index + 1
            else:
                # should never get here
                raise RuntimeError("got past if-elifs that should've exhausted"+
                    "all possibilities (i.e., you should never see this)")

            # the + 1 and - 1 ensure that low or high will always change
            # each iteration, so we can't get stuck
            # but just in case, let's make sure low <= high:
            if not (low_index <= high_index):
                raise RuntimeError("somehow low index > high index ("+
                        low_index+" > "+high_index)

            check_index = round((low_index + high_index) / 2)
            # that biases check_index to equal high_index when high_index - 
            # low_index == 1

        # check if other segs before or after check_index also intersected
        intersected = []
        the_seg = self._track[check_index]
        intersected.append(the_seg)
        # before
        i = check_index - 1
        while self._track[i].get_end() == mp:
            intersected.append(self._track[i])
            i = i - 1
        # after
        i = check_index + 1
        while self._track[i].get_start() == mp:
            intersected.append(self._track[i])
            i = i + 1


        return intersected


class TestEditableTrack(unittest.TestCase):
    def setUp(self):
        self.filetrack = EditableTrack("sprinter_maxspeeds_stations.csv",
                "imperial")
        self.buildtrack = EditableTrack(units="imperial")
        self.shorttrack = EditableTrack("short_maxspeeds.csv", "imperial")

    def test_initial_tracks(self):
        # just print it and see if it looks all right
        #print(self.filetrack)
        #print(self.buildtrack)
        pass

    #def ,kíííííííííííííííííííííííííí';[p--

    def test_append(self):
        # append first TrackSeg
        self.buildtrack.append_seg(Speed(30, "mi/h").to_smaller_unit(),
                Pos(1.1, "mi").to_smaller_unit())
        self.assertEqual(self.buildtrack._track[0], EditableTrackSeg(0,
            Pos(0, "mi").to_smaller_unit(), Pos(1.1, "mi").to_smaller_unit(),
            Speed(30, "mi/h").to_smaller_unit()))

        # append to that
        self.buildtrack.append_seg(Speed(45, "mi/h").to_smaller_unit(),
                Pos(2.1, "mi").to_smaller_unit())
        self.assertEqual(self.buildtrack._track[1], EditableTrackSeg(1,
            Pos(1.1, "mi").to_smaller_unit(), Pos(3.2, "mi").to_smaller_unit(),
            Speed(45, "mi/h").to_smaller_unit()))

        # append a third segment, but invalid
        with self.assertRaises(ValueError):
            self.buildtrack.append_seg(Speed(0, "mi/h").to_smaller_unit(),
                Pos(0.1, "mi").to_smaller_unit())

        # append a real third segment, 0mph, 0-length
        self.buildtrack.append_seg(Speed(0, "mi/h").to_smaller_unit(),
                Pos(0, "mi").to_smaller_unit())

        # print it so far
        print(self.buildtrack)

    def test_split(self):
        # just assume short track loaded correctly
        # well print it
        print(self.shorttrack)

    def test__intersecting_segs(self):
        # assume loaded track correctly

        inter = self.shorttrack._intersecting_segs(Pos(11.5, 
            "mi").to_smaller_unit())

        print("intersecting: [")
        for t in inter:
            print(str(t)+", ")
        print("]")

        inter = self.shorttrack._intersecting_segs(Pos(11.3,
            "mi").to_smaller_unit())

        self._print_intersecting_segs(inter)

    def _print_intersecting_segs(self, l):
        print("intersecting: [")
        for t in l:
            print(str(t)+", ")
        print("]")


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
