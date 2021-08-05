#! /usr/bin/python3

from simulation import Simulation, Track, TrackSeg
from convunits import Pos, Speed, system_to_unit

# For when an edit operation is impossible due to the circumstances and 
# there's no valid value (so it's not ValueError)
# e.g., can't edit the track because there are no track segments
class SituationError(RuntimeError):
    pass

# For when trying to move/shift boundary of 0-length seg
class AmbiguousBoundaryError(SituationError):
    pass

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
        if self._speed == 0 and start != end:
            raise ValueError("start and end must be equal if speed is 0")
        self._start = start
        self._end = end



import unittest

class TestEditableTrackSegMethods(unittest.TestCase):
    def setUp(self):
        self.seg = EditableTrackSeg(14, Pos('11.4', "mi").to_smaller_unit(),
                Pos('13.5', "mi").to_smaller_unit(), Speed('25',
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
        self.assertEqual(self.seg.get_start(), Pos('11.4',
                "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('13.5', 
                "mi").to_smaller_unit())

        # set start < end
        self.seg.set_start(Pos('10.8', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), 
                Pos('10.8', "mi").to_smaller_unit())

        # set start > end (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_start(Pos('15', "mi").to_smaller_unit())

        # set start so length == 0
        self.assertEqual(self.seg.get_end(), Pos('13.5', 
                "mi").to_smaller_unit())
        self.seg.set_start(Pos('13.5', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(),
                Pos('13.5', "mi").to_smaller_unit())

        # set_start should throw ValueError IFF speed is 0 and length > 0
        self.seg.set_speed(Speed('0', "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
                Speed('0', "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_start(Pos('13.4', "mi").to_smaller_unit())

    def test_set_end(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos('11.4', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('13.5', "mi").to_smaller_unit())

        # set end farther to 14 miles and check
        self.seg.set_end(Pos('14', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('14', "mi").to_smaller_unit())
        
        # set end to earlier than start (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_end(Pos('10', "mi").to_smaller_unit())

        # set end to equal start and check
        self.seg.set_end(Pos('11.4', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(),
            Pos('11.4', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), self.seg.get_end())

        # set_end should throw ValueError IFF speed is 0 and length > 0
        self.seg.set_speed(Speed('0', "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
            Speed('0', "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_end(Pos('11.6', "mi").to_smaller_unit())

    def test_set_speed(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos('11.4', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('13.5', "mi").to_smaller_unit())

        # set speed < 0 (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_speed(Speed('-3', "mi/h").to_smaller_unit())

        # set speed to 100 mi/h
        self.seg.set_speed(Speed('100', "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(),
                Speed('100', "mi/h").to_smaller_unit())

        # set speed to 0 mi/h, while length > 0 (should throw)
        self.assertGreater(self.seg.length(), 0)
        with self.assertRaises(ValueError):
            self.seg.set_speed(Speed('0', "mi/h").to_smaller_unit())

        # set speed 0 mi/h while length == 0
        self.seg.set_end(Pos('20', "mi").to_smaller_unit())
        self.seg.set_start(Pos('20', "mi").to_smaller_unit())
        self.assertEqual(self.seg.length(), 0)
        self.seg.set_speed(Speed('0', "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 0)

        # set speed > 0 mi/h while length == 0
        self.assertEqual(self.seg.length(), 0)
        self.seg.set_speed(Speed('20', "mi/h").to_smaller_unit())
        self.assertEqual(self.seg.get_speed(), 
                Speed('20', "mi/h").to_smaller_unit())

    def test_set_start_end(self):
        # check initial start & end values
        self.assertEqual(self.seg.get_start(),
                Pos('11.4', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('13.5', "mi").to_smaller_unit())

        # set start and end to > current end
        self.seg.set_start_end(Pos('14', "mi").to_smaller_unit(),
                Pos('15', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), Pos('14', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_end(), Pos('15', "mi").to_smaller_unit())

        # set start > end (should throw)
        with self.assertRaises(ValueError):
            self.seg.set_start_end(Pos('16', "mi").to_smaller_unit(),
                    Pos('10', "mi").to_smaller_unit())

        # set start == end
        self.seg.set_start_end(Pos('9.5', "mi").to_smaller_unit(),
                Pos('9.5', "mi").to_smaller_unit())
        self.assertEqual(self.seg.get_start(), self.seg.get_end())
        
        # set start < end with 0 speed, should throw
        self.seg.set_speed(Speed('0', "mi/h").to_smaller_unit())
        with self.assertRaises(ValueError):
            self.seg.set_start_end(Pos('8', "mi").to_smaller_unit(),
                    Pos('9.9', "mi").to_smaller_unit())


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
            start = Pos(0, pos_unit).to_smaller_unit() # DON'T make 0 a str!
            end = length
        else:
            # throw if trying to append 0-len seg to another 0-len seg
            if self._track[-1].length() == 0 and length == 0:
                raise ValueError("0-length segments cannot be adjacent")
            index = self._track[-1].get_index() + 1
            start = self._track[-1].get_end()
            end = start + length

        # append new EditableTrackSeg
        self._track.append(EditableTrackSeg(index, start, end, speed))

    # Splits track segment that mp intersects with, at mp, into 2 new segs
    # and updates subsequent segs' indexes accordingly
    # Throws if mp lies on boundary of track segment (i.e. mp == seg.get_start()
    # or mp == seg.get_end() for some segment seg)
    def split_seg(self, mp):
        # throw if there's no track
        if len(self._track) == 0:
            raise SituationError("no track segments exist")
        # throw if mp outside of range of track
        if mp < self._track[0].get_start() or mp > self._track[-1].get_end():
            raise ValueError("mp "+str(mp)+" outside of track boundaries")
        # throw if trying to split at segment boundary
        # (this includes 0-length segments)
        if self._on_boundary(mp):
            raise ValueError("mp "+str(mp)+" on segment boundary")

        # checks up there ^^^ guarantee there's exactly 1 seg in question
        seg_to_split = self._intersecting_segs(mp)[0]

        # make seg_to_split's end be mp, and make new seg whose start is mp
        # and end is seg_to_split's old end
        old_end = seg_to_split.get_end()
        seg_to_split.set_end(mp)
        import copy
        new_seg = EditableTrackSeg(seg_to_split.get_index() + 1, copy.copy(mp), 
                old_end, seg_to_split.get_speed())

        # insert new_seg
        new_seg_i = seg_to_split.get_index() + 1
        self._track.insert(new_seg_i, new_seg)

        # update subsequent segs' index members
        for i in range(new_seg_i+1, len(self._track)):
            self._track[i].set_index(i)


        # that should do it

    # Joins all segments that share a boundary
    # mp must be on a segment boundary, or ValueError will be thrown
    # Newly-joined TrackSeg will have speed of highest-speed of the TrackSegs
    # that get joined. This makes it unambiguous and allows joining of 0-length
    # segments.
    # Also the newly-joined seg will have the LOWEST index of the merged segs
    # and all subsequent segs' indices will be decremented appropriately
    def join_segs(self, mp):
        if len(self._track) == 0:
            raise SituationError("no track segments exist")
        if len(self._track) == 1:
            raise SituationError("only 1 track segment exists (need >= 2)")
        if (mp < self._track[0].get_start()):
            raise ValueError("{} outside bounds of track (< start)".format(mp))
        if (mp > self._track[-1].get_end()):
            raise ValueError("{} outside track bounds (> end)".format(mp))

        intersecting = self._intersecting_segs(mp)

        # more checks
        if (len(intersecting) == 1):
            raise ValueError("{} not on a boundary between track segments" \
                "".format(mp))
        if (len(intersecting) == 0):
            raise RuntimeError("{} doesn't intersect with any track segment..."\
                    " Previous checks should have stopped this".format(mp))

        # It occurs to me that having one TrackSeg's _end refer to the same
        # object as next TrackSeg's _start would be desirable...
        # TODO

        #import math
        #min_index = math.inf
        #for s in intersecting:
            #min_index = min(min_index
        min_index = min(intersecting, key=lambda x: x.get_index()).get_index()

        max_index = max(intersecting, key=lambda x: x.get_index()).get_index()
        
        max_end = max(intersecting, key=lambda x: x.get_end()).get_end()

        max_speed = max(intersecting, key=lambda x: x.get_speed()).get_speed()

        print("*********", mp.to_bigger_unit(), min_index, max_index, max_end.to_bigger_unit(), max_speed, "*************")

        # Toss unneeded segments into the ether
        for i in range(min_index+1, max_index+1):
            self._track.pop(i)

        # modify segment at min_index to have correct properties
        self._track[min_index].set_end(max_end)
        self._track[min_index].set_speed(max_speed)

        # adjust subsequent segments' indexes
        for s in self._track[min_index+1:]:
            old_i = s.get_index()
            s.set_index(old_i - (max_index - min_index))

        print("track with segments joined at", mp.to_bigger_unit(),":", self)
        pass

    # Shifts a boundary of a track seg and of its neighbor if applicable
    # Affects at most 2 track segs
    # Throws if requested shift would cross another boundary
    # A seg affected by this can be reduced to 0-length
    # Shifting boundary of 0-length seg:
    # * any shift on 0-speed seg: NOT OK
    # * shift to left shifts start only
    # * shift to right shifts end only
    def shift_boundary(self, mp, dist):
        if len(self._track) == 0:
            raise SituationError("no track segments exist")
        if len(self._track) == 1:
            raise SituationError("only 1 track segment exists (need >= 2)")
        if (mp < self._track[0].get_start()):
            raise ValueError("{} outside bounds of track (< start)".format(mp))
        if (mp > self._track[-1].get_end()):
            raise ValueError("{} outside track bounds (> end)".format(mp))

        intersecting = self._intersecting_segs(mp)

        # more checks
        if (len(intersecting) == 0):
            raise RuntimeError("{} doesn't intersect with any track segment..."\
                    " Previous checks should have stopped this".format(mp))

        # NOW to the mean & potatoes
        # I mean meat

        if len(intersecting) == 2:
            # either on boundary between 2 non-zero-length segments
            # or on boundary between zero-length seg and non-zero, at start
            # or end of track.
            self._shift_2_boundary(intersecting, dist)
        elif len(intersecting) == 3:
            # on boundary representing non0-length,0-length,non0 segments
            # make sure of that
            #if intersecting[0].length() !
            # !ABC v A!BC v AB!C
            # (shorten to X v Y v Z)
            # by le whoever's law is equivalent to
            # !(!X ^ !Y ^ !Z)
            # ???
            # oh just make a function
            # if self._only_one_is_0_length(intersecting):
            # Actually better yet just make _intersecting_segs() return them
            # in index order
            if not (intersecting[0].length() > 0 and intersecting[1].length() \
                    == 0 and intersecting[2].length() > 0):
                raise RuntimeError("3 segs intersected by "+str(mp)+" but not"\
                        " following non0-length,0-length,non0-length pattern")
            raise NotImplementedError
        else:
            # somehow we have multiple adjacent 0-length segments
            raise Adjacent0LenError("Multiple adjacent 0-length segs at "+\
                    str(mp))
        pass

    def _shift_2_boundary(self, intersecting, dist):
        """shifts boundary between 2 non-0-length segments or one non-0-length
        and one 0-length segment"""
        # also a quick check
        if intersecting[0].length() == 0 and intersecting[1].length() == 0:
            raise Adjacent0LenError("Multiple 0-length segments at "+str(mp))
        elif intersecting[0].length() == 0:
            raise NotImplementedError
        elif intersecting[1].length() == 0:
            raise NotImplementedError
        else:
            # both non-0-length
            # shift end of [0] and start of [1]
            if dist > 0:
                # trying to shift right
                if intersecting[1].get_start()+dist > intersecting[1].get_end():
                    raise ValueError("moving boundary at {} by {} moves beyond"\
                            "segment end {}".format(intersecting[1].get_start(),
                            dist, intersecting[1].get_end()))
            elif dist < 0:
                # trying to shift left
                if intersecting[0].get_end()+dist < intersecting[0].get_start():
                    raise ValueError("moving boundary at {} by {} moves beyond"\
                            "segment start {}".format(intersecting[0].get_end(),
                            dist, intersecting[0].get_start()))

            # do the actual work
            intersecting[0].set_end(intersecting[0].get_end()+dist)
            intersecting[1].set_start(intersecting[1].get_start()+dist)

            # invariant
            if intersecting[0].get_end() != intersecting[1].get_start():
                raise RuntimeError("Track seg {} end {} != seg {} start {}"\
                        .format(intersecting[0].get_index(),
                            intersecting[0].get_end(),
                            intersecting[1].get_index(),
                            intersecting[1].get_start()))

    # Checks if mp is "on boundary" of a track seg by seeing if len of tuple
    # returned by self._intersecting_segs(mp) > 1
    def _on_boundary(self, mp):
        return len(self._intersecting_segs(mp)) > 1

    # mp "intersects" any track segment where start <= mp <= end
    # hence it can intersect on boundaries and 0-length segments
    # returns list of intersecting segs IN INDEX ORDER
    def _intersecting_segs(self, mp):
        if (mp < 0):
            raise ValueError("mp must be non-negative")
        if mp < self._track[0].get_start():
            raise ValueError("mp {} < min mp {}".format(mp,
                self._track[0].get_start()))
        # maybe also check if it's > final segment's end?
        if mp > self._track[-1].get_end():
            raise ValueError("mp {} > max mp {}".format(mp, 
                self._track[-1].get_end()))

        # we'll have to do a search
        low_index = 0
        high_index = len(self._track) - 1
        check_index = round((low_index + high_index) / 2)

        #print("mp:", mp)

        while True:
            seg = self._track[check_index]

            #print("low_index:", low_index, " check_index:", check_index,
            #    " high_index:", high_index)
            #print("seg:", seg)
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

            #print("NEW: low_index:", low_index, " high_index:", high_index)
            #print("---------------")

            # the + 1 and - 1 ensure that low or high will always change
            # each iteration, so we can't get stuck
            # but just in case, let's make sure low <= high:
            if not (low_index <= high_index):
                raise RuntimeError("somehow low index > high index ("+
                        str(low_index)+" > "+str(high_index)+")")

            check_index = round((low_index + high_index) / 2)
            # that biases check_index to equal high_index when high_index - 
            # low_index == 1

        # check if other segs before or after check_index also intersected
        intersected = []
        # before
        low_i = check_index
        while low_i-1 >= 0 and self._track[low_i-1].get_end() == mp:
            low_i = low_i - 1
        # after
        hi_i = check_index
        while hi_i+1 < len(self._track) \
                and self._track[hi_i+1].get_start() == mp:
            hi_i = hi_i + 1

        return self._track[low_i:hi_i+1]


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


        # append another 0-len seg (should throw)
        with self.assertRaises(ValueError):
            self.buildtrack.append_seg(Speed(10, "mi/h").to_smaller_unit(),
                    Pos(0, "mi").to_smaller_unit())

        # print it so far
        print(self.buildtrack)

    def test_split(self):
        # SituationError on 0-seg track
        with self.assertRaises(SituationError):
            self.buildtrack.split_seg(Pos(0, "mi").to_smaller_unit())

        # just assume short track loaded correctly
        # well print it
        print(self.shorttrack)

        # should split seg 5 into id 5 11.8-12mi @ 50mph and id 6 12-12.5mi
        # @ 50 mph (and shift subsequent ones id's to old id + 1)
        twelvemiles = Pos(12.0, "mi").to_smaller_unit()
        self.shorttrack.split_seg(twelvemiles)

        self.assertEqual(len(self.shorttrack._track), 8)
        self.assertEqual(self.shorttrack._track[5], EditableTrackSeg(5,
            Pos(11.8, "mi").to_smaller_unit(), twelvemiles, 
            Speed(50, "mi/h").to_smaller_unit()))
        self.assertEqual(self.shorttrack._track[6], TrackSeg(6, twelvemiles,
            Pos(12.5, "mi").to_smaller_unit(), 
            Speed(50, "mi/h").to_smaller_unit()))
        self.assertEqual(self.shorttrack._track[7].get_index(), 7)

        print("Split seg of ",self.shorttrack)

        # try to split 0-length seg (should throw)
        with self.assertRaises(ValueError):
            self.shorttrack.split_seg(Pos(11.8, "mi").to_smaller_unit())

        # try to split on seg boundary (should throw)
        with self.assertRaises(ValueError):
            self.shorttrack.split_seg(Pos(10.5, "mi").to_smaller_unit())

    def test__intersecting_segs(self):
        # assume loaded track correctly

        # intersect in middle of seg
        inter = self.shorttrack._intersecting_segs(Pos(11.5, 
            "mi").to_smaller_unit())
        self._print_intersecting_segs(inter)
        track1 = EditableTrackSeg(3, Pos(11.3, "mi").to_smaller_unit(),
                Pos(11.8, "mi").to_smaller_unit(), Speed(35, 
                "mi/h").to_smaller_unit())
        self.assertIn(track1, inter)
        # Gawd writing that takes forever
        # maybe I'll just index shorttrack._track in the future
        self.assertEqual(len(inter), 1)

        # intersect boundary of 2 segs
        inter = self.shorttrack._intersecting_segs(Pos(11.3,
            "mi").to_smaller_unit())
        self._print_intersecting_segs(inter)
        self.assertEqual(len(inter), 2)
        self.assertIn(self.shorttrack._track[2], inter)
        self.assertIn(self.shorttrack._track[3], inter)

        # intersect 0-length seg
        inter = self.shorttrack._intersecting_segs(Pos(11.8,
            "mi").to_smaller_unit())
        self._print_intersecting_segs(inter)
        self.assertEqual(len(inter), 3)
        self.assertIn(self.shorttrack._track[3], inter)
        self.assertIn(self.shorttrack._track[4], inter)
        self.assertIn(self.shorttrack._track[5], inter)

        # intersect outside of range (throws)
        with self.assertRaises(ValueError):
            inter = self.shorttrack._intersecting_segs(Pos(0,
                "mi").to_smaller_unit())

        # intersect very start of track
        inter = self.shorttrack._intersecting_segs(Pos(10.1,
            "mi").to_smaller_unit())
        self._print_intersecting_segs(inter)
        self.assertEqual(len(inter), 2)
        self.assertIn(self.shorttrack._track[0], inter)
        self.assertIn(self.shorttrack._track[1], inter)

        # intersect very end of track
        inter = self.shorttrack._intersecting_segs(Pos(12.5,
            "mi").to_smaller_unit())
        self._print_intersecting_segs(inter)
        self.assertEqual(len(inter), 2)
        self.assertIn(self.shorttrack._track[5], inter)
        self.assertIn(self.shorttrack._track[6], inter)

    def _print_intersecting_segs(self, l):
        print("intersecting: [")
        for t in l:
            print(str(t)+", ")
        print("]")

    def test_join(self):
        # use shorttrack
        
        # test error situations
        # out of bounds: before start
        with self.assertRaises(ValueError):
            self.shorttrack.join_segs(Pos(9.5, "mi").to_smaller_unit())
        # out of bounds: after end
        with self.assertRaises(ValueError):
            self.shorttrack.join_segs(Pos(13.6, "mi").to_smaller_unit())
        # in bounds, but not on a boundary
        with self.assertRaises(ValueError):
            self.shorttrack.join_segs(Pos(11.4, "mi").to_smaller_unit())

        import copy
        orig_seg0 = copy.deepcopy(self.shorttrack._track[0])
        # join at 10.5 miles
        self.shorttrack.join_segs(Pos(10.5, "mi").to_smaller_unit())
        # there should now be 6 segments
        self.assertEqual(len(self.shorttrack._track), 6)
        # _track[0] should be the same as ever
        self.assertEqual(orig_seg0, self.shorttrack._track[0])
        # _track[1] should be 10.1 mi - 11.3 mi at 58.666666etc. f/s
        self.assertEqual(self.shorttrack._track[1],
            TrackSeg(1, Pos(10.1, "mi").to_smaller_unit(),
                Pos(11.3, "mi").to_smaller_unit(),
                Speed(40, "mi/h").to_smaller_unit()))
        # _track[2] should be 11.3-11.8 mi @ 35 mph
        self.assertEqual(self.shorttrack._track[2],
            TrackSeg(2, Pos(11.3, "mi").to_smaller_unit(),
                Pos(11.8, "mi").to_smaller_unit(),
                Speed(35, "mi/h").to_smaller_unit()))
        # I'll assume the rest are good
        # because there is TOO MUCH TYPING
        # (as in, of the keyboard)

    def test_shift_boundary(self):
        # use shorttrack

        # shift 10.5 mi boundary to 10.3 mi
        self.shorttrack.shift_boundary(Pos(10.5, "mi").to_smaller_unit(),
                Pos(-0.2, "mi").to_smaller_unit())
        self.assertEqual(self.shorttrack._track[1].get_end(),
                Pos(10.3, "mi").to_smaller_unit())
        self.assertEqual(self.shorttrack._track[2].get_start(),
                Pos(10.3, "mi").to_smaller_unit())

        # shift 11.3 mi boundary to 11.8 mi (as far as it'll go)
        # (though that will result in 2 adjacent 0-length segments, with
        # differing speeds at that, and I'm not sure how the sim will handle
        # that.)
        # (so let's throw for that)
        with self.assertRaises(Adjacent0LenError):
            self.shorttrack.shift_boundary(Pos(11.3, "mi").to_smaller_unit(),
                    Pos(0.5, "mi").to_smaller_unit())

        # shift 10.1 mi boundary to 10.0 (should throw)
        # (or maybe shouldn't? It wouldn't if it shifted both boundaries
        # of the 0-speed/0-length segment)
        # (but if it did shift both boundaries, could result in a 0-length
        # seg pileup, which would be bad)
        # (well I'll say as long as it DOESN'T result in a 0-length pileup,
        # it's valid)
        # SO this SHOULDN'T throw
        # No... even if it doesn't result in a pileup, it's ambiguous as to
        # whether to move both boundaries or just one or the other...
        # so it SHOULD throw, maybe a SituationError
        # or how about this: an AmbiguousBoundaryError, a subclass of
        # SituationError
        # WELL if I compare this situation to the one of a seg that's only 1 
        # sim-seg long, I am free to move its start to the left, but not to
        # the right, and I am free to move its end to the right, but not to
        # the left. Well actually I am but that's not the point. The point is,
        # I'm largely allowed to move its start to the left, but only 1 sim-
        # seg to the right, and to move its end to the right, but only 1 sim-
        # seg to the left. So by extension, the start of a 0-length seg can
        # be moved to the left but not the right, and the end can be moved
        # to the right but not to the left. Yes.
        # so this SHOULDN'T throw simply for the reason of an "ambiguous" 
        # boundary.
        # ... but it should throw because it's trying to increase length of a
        # 0-speed seg ;)
        with self.assertRaises(NonzeroLengthOfZeroSpeedSegError):
            self.shorttrack.shift_boundary(Pos(10.1, "mi").to_sm(), 
                    Pos(-0.1, "mi").to_sm())

        # shift 10.3 mi boundary to 9.8 (should throw)
        pass

if __name__ == "__main__":
    seg = EditableTrackSeg(3, Pos('0', "mi").to_smaller_unit(), \
            Pos('0', "mi").to_smaller_unit(), Speed('0', 
                "mi/h").to_smaller_unit())
    print(seg)

    print("Testing invalid (Editable)TrackSegs on construction")
    try:
        seg2 = EditableTrackSeg(-2, Pos('0.2', "mi").to_smaller_unit(),
                Pos('0.3', "mi").to_smaller_unit(), Speed('100', 
                "mi/h").to_smaller_unit())
        print(seg2)
    except Exception as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(1, Pos('1', "mi").to_smaller_unit(),
                Pos('0.9', "mi").to_smaller_unit(), Speed('25', 
                "mi/h").to_smaller_unit())
        print(seg2)
    except Exception as e:
        print(repr(e))
    try:
        seg2 = EditableTrackSeg(10, Pos('30', "mi").to_smaller_unit(),
                Pos('30.1', "mi").to_smaller_unit(), Speed('0', 
                "mi/h").to_smaller_unit())
        # I need to make it so I don't need to call to_smaller_unit() so much
        print(seg2)
    except Exception as e:
        print(repr(e))

    print("Testing valid speed > 0 when TrackSeg length == 0")
    try:
        seg2 = EditableTrackSeg(10, Pos('30', "mi").to_smaller_unit(),
                Pos('30', "mi").to_smaller_unit(), Speed('10', 
                "mi/h").to_smaller_unit())
        # Actually this should be OK
        print(seg2)
    except Exception as e:
        print(repr(e))

    print("Testing setting methods")
    unittest.main()
