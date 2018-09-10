
from collections import namedtuple
MaxSpeed = namedtuple("MaxSpeed", ["milepost", "speed"])


def mainthing():
    raw_maxspeeds = load_maxspeeds()
    print(raw_maxspeeds)
    #maxspeeds = insert_speed_changes(raw_maxspeeds)
    maxspeeds = raw_maxspeeds
    
    segment_length = int(0.1*5280) # this stuff's in miles for some reason
    accel = 1.25; # for speeding up; braking will come later Also its f/s^2
    print("yolo")
    bestspeeds = sim_speed(maxspeeds, segment_length, accel)

    print(bestspeeds)
    print("swag")

def load_maxspeeds():
    import csv
    maxspeeds = [maxspeed for maxspeed in map (MaxSpeed._make, csv.reader(open("sprinter_maxspeeds.csv", "r"), delimiter='	', quoting=csv.QUOTE_NONNUMERIC))]
    return maxspeeds


def sim_speed(maxspeeds, seg_len, accel):
    bestspeeds = ["lololol"]
    route_len = 5280*int(maxspeeds[-1].milepost - maxspeeds[0].milepost)
    position = 0 # in ft
    for segment_point in range(0, route_len, seg_len):
        print("okisugiruuuu")
        sim_segment(bestspeeds, maxspeeds, int(segment_point/seg_len), seg_len, accel)
    
    return bestspeeds


# simulates speed at given point, taking into account prev point's speed
# and max speed at point
def sim_segment(bestspeeds, maxspeeds, index, seg_len, accel):
    if index == 0:
        len_from_prev = 0
        return
    else:
        len_from_prev = seg_len
        
    v_init = bestspeeds[index-1]
    print(type(v_init), v_init)
    v_max = lowest_current_max_speed(maxspeeds, index, seg_len, accel)
    #v_next = lowest_upcoming_max_speed(maxspeeds, index, seg_len, accel)
    v_next = 1000000 # whatever will decelerate later

    v_target = min(v_max, v_next)

    bestspeeds.append(min(v_max, accel_to_target(v_target, accel, v_init, seg_len * 5280)))


# takes all units in feet units
def accel_to_target(v_target, acc, v_i, d):
    if v_target >= v_i: # which it SHOULD be
        t = ( -v_i + sqrt(v_i**2 - 4 * (1/2) * acc * -d) ) / (2*(1/2)*acc)
        v_f = acc * t + v_i
        return v_f

def lowest_current_max_speed(maxspeeds, index, seg_len, accel):
    #candidates = []
    candidates = lowest_applicable_max_speed(maxspeeds, index * seg_len)
    return candidates # sloppy & I didn't mean to layerize this but oh well


def lowest_applicable_max_speed(maxspeeds, mile):
    # throw out all speed limits ahead of us
    maxprevs = [x for x in maxspeeds if x.milepost <= mile]
    # now last in maxprevs is the one that applies yup
    return maxprevs[-1].speed

    

if __name__ == "__main__":
    mainthing()
