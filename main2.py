
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
    pos = 0
    for seg in maxspeeds:
        # assumes seg len in multiples of 528
        for simseg in range(0, int(seg.length), SIM_SEG):
            seg_start = pos
            pos += SIM_SEG
            speed = accel_to_target(seg.speed, 1.5, speed, SIM_SEG)
            bestspeeds.append(TrackSeg(seg_start, pos, SIM_SEG, speed))

    for seg in bestspeeds:
        print(seg.start/5280, ":", seg.speed, "fps (", seg.speed * 3600/5280, ")")


def load_maxspeeds():
    import csv
    raw_maxspeeds = [maxspeed for maxspeed in map (MaxSpeed._make, csv.reader(open("sprinter_maxspeeds2.csv", "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
    
    # generate segments from that
    maxspeedsegs = []
    for x in range(0, len(raw_maxspeeds)-1):
        maxguy = raw_maxspeeds[x]
        mp1 = maxguy.milepost * 5280
        maxguy2 = raw_maxspeeds[x+1]
        mp2 = maxguy2.milepost * 5280
        seg = TrackSeg(mp1, mp2, mp2-mp1, maxguy.speed * 3600 / 5280)
        maxspeedsegs.append(seg)

    return maxspeedsegs
        
# takes all units in feet units
def accel_to_target(v_target, acc, v_i, d):
    if v_target >= v_i:
        nacc = acc
    if v_target < v_i:
        nacc = -acc
    from math import sqrt
    t = ( -v_i + sqrt(v_i**2 - 4.0 * 0.5 * nacc * -d) ) / (2.0*0.5*nacc)
    print("sec from prev index point segment guy:", t)
    v_f = nacc * t + v_i
    return v_f

if __name__ == "__main__":
    mainthing()
