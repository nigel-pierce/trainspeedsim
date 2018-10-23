
from collections import namedtuple
MaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])
TrackSeg = namedtuple("TrackSeg", ["start", "end", "length", "speed"])
# EVERYTHING is ft/sec except where noted


def mainthing():
    maxspeeds = load_maxspeeds()
    print(maxspeeds)


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
        

if __name__ == "__main__":
    mainthing()
