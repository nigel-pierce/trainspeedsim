
from collections import namedtuple
MaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])
MaxSpeedF = namedtuple("MaxSpeedF", ["footpost", "speed"])
TrackSeg = namedtuple("TrackSeg", ["start", "end", "length", "speed"])
# EVERYTHING is ft/sec except where noted


def mainthing():
    maxspeeds = load_maxspeeds()
    print(maxspeeds)

    SIM_SEG = 528 # feet
    
    bestspeeds = []
    #bestspeeds.append(MaxSpeedF(maxspeeds[0].start, maxspeeds[0].speed)
    speed = 0
    pos = maxspeeds[0].start
    for seg in maxspeeds:
        # assumes seg len in multiples of 528
        # +1 b/c range(0,0) == []
        if int(seg.length) == 0:
            bestspeeds.append(TrackSeg(seg.start, seg.start, 0, seg.speed))
        for simseg in range(0, int(seg.length), SIM_SEG):
            pos += SIM_SEG
            speed = min(seg.speed, accel(seg.speed, 1.25, speed, SIM_SEG))
            bestspeeds.append(TrackSeg(seg.start, pos, SIM_SEG, speed))

    bestspeeds_rev = []
    maxspeeds_rev = reversed(maxspeeds)
    speed = 0
    for seg in maxspeeds_rev:
        # assumes seg len in multiples of 528
        if int(seg.length) == 0:
            bestspeeds_rev.append(TrackSeg(seg.end, seg.end, 0, seg.speed))
        for simseg in range(0, int(seg.length), SIM_SEG):
            seg_start = pos
            pos -= SIM_SEG
            speed = min(seg.speed, accel(seg.speed, 1.25, speed, SIM_SEG))
            bestspeeds_rev.append(TrackSeg(seg_start, pos, SIM_SEG, speed))

    final_bestspeeds = []
    for paired in zip(bestspeeds, reversed(bestspeeds_rev)):
        lower_speed = min(paired[0].speed, paired[1].speed)
        seg = paired[0]
        final_bestspeeds.append(TrackSeg(seg.start, seg.end, SIM_SEG, lower_speed))

    for seg in final_bestspeeds:
        print(seg.end/5280.0, " ", seg.speed * 3600/5280)


def load_maxspeeds():
    import csv
    raw_maxspeeds = [maxspeed for maxspeed in map (MaxSpeed._make, csv.reader(open("sprinter_maxspeeds3.csv", "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
    
    # generate segments from that
    maxspeedsegs = []
    #lastmp = 0
    for x in range(0, len(raw_maxspeeds)-1):
        maxguy = raw_maxspeeds[x]
        mp1 = maxguy.milepost * 5280
        maxguy2 = raw_maxspeeds[x+1]
        mp2 = maxguy2.milepost * 5280
        seg = TrackSeg(mp1, mp2, mp2-mp1, maxguy.speed * 5280 / 3600)
        maxspeedsegs.append(seg)
        #lastmp = mp2

    # we really do need a 0 mph segment at the end
    #maxspeedsegs.append(TrackSeg(lastmp, lastmp, 0, 0))
    # NOT I just changed sprinter speeds csv to have symmetrical ends
    # and changed filename to sprinter_maxspeeds3.csv

    return maxspeedsegs
        
# takes all units in feet units
def accel(v_target, acc, v_i, d):
    nacc = acc
    from math import sqrt
    t = ( -v_i + sqrt(v_i**2 - 4.0 * 0.5 * nacc * -d) ) / (2.0*0.5*nacc)
    #print("sec from prev index point segment guy:", t)
    print("target speed", v_target, "fps (",(v_target*3600/5280.0),"mph)")
    v_f = nacc * t + v_i
    return v_f

if __name__ == "__main__":
    mainthing()