
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
    bestspeeds = []
    route_len = 5280*int(maxspeeds[-1].milepost - maxspeeds[0].milepost)
    position = 0 # in ft
    for segment_point in range(0, route_len, seg_len):
    #    print("okisugiruuuu")
        bestspeeds.append(sim_segment(bestspeeds, maxspeeds, int(segment_point/seg_len), seg_len, accel))
    
    # "reverse" of that for braking
    bestspeeds_rev = []
    maxspeeds_rev = reverse_maxspeeds(maxspeeds) # can't just reverse maxspeeds
    for segment_point in range(0, route_len, seg_len):
        bestspeeds_rev.append(sim_segment(bestspeeds_rev, maxspeeds_rev, int(segment_point/seg_len), seg_len, accel))
    
    bestspeeds_rev = [x * 3600/5280 for x in bestspeeds_rev]
    print(bestspeeds_rev)

    bestspeeds = [x * 3600/5280 for x in bestspeeds]
    return bestspeeds


# simulates speed at given point, taking into account prev point's speed
# and max speed at point
def sim_segment(bestspeeds, maxspeeds, index, seg_len, accel):
    if index == 0:
        len_from_prev = 0
        #bestspeeds.append(0)
        return 0
    else:
        len_from_prev = seg_len
        
    v_init = bestspeeds[index-1]
    #print("for index", index, "v_init is", v_init)
    v_max = lowest_current_max_speed(maxspeeds, index, seg_len, accel) * 5280/3600
    #print(v_max)
    #v_next = lowest_upcoming_max_speed(maxspeeds, index, seg_len, accel)
    v_next = 1000000 # whatever will decelerate later

    v_target = min(v_max, v_next) * 5280 / 3600 # needs to be in fps

    unbounded_v = accel_to_target(v_target, accel, v_init, seg_len)
    #print("for index", index, "unbounded speed is", unbounded_v, 'f/s')
    bounded_v = min(v_max, unbounded_v)
    #print("for index", index, "bounded speed is  ", bounded_v, "f/s")
    return bounded_v


# takes all units in feet units
def accel_to_target(v_target, acc, v_i, d):
    #if v_target >= v_i: # which it SHOULD be? nah don't be conditional
        from math import sqrt
        t = ( -v_i + sqrt(v_i**2 - 4.0 * 0.5 * acc * -d) ) / (2.0*0.5*acc)
        #print("sec from prev index point segment guy:", t)
        v_f = acc * t + v_i
        return v_f

def lowest_current_max_speed(maxspeeds, index, seg_len, accel):
    #candidates = []
    start_mile = maxspeeds[0].milepost
    candidates = lowest_applicable_max_speed(maxspeeds, start_mile + index * seg_len / 5280) # uhh in miles i guess?
    return candidates # sloppy & I didn't mean to layerize this but oh well


def lowest_applicable_max_speed(maxspeeds, mile):
    # throw out all speed limits ahead of us
    maxprevs = [x for x in maxspeeds if x.milepost <= mile]
    # now last in maxprevs is the one that applies yup
    #print("maxprevs[-1] (expect a speed thing): ", maxprevs[-1])
    return maxprevs[-1].speed

    
def reverse_maxspeeds(maxspeeds):
    # maxspeed has a structure like this: (mp, speed) ... <- implied 
    # until ... (mp later, speed) ... <- implied until ... etc.
    # so simply reversing it and using it would imply: implied -> ... (mp, 
    # speed) ... implied -> ... (mp earlier, speed) ... etc.
    # which is incorrect.
    # we need (mp, speed=0) ... <- implied until... (mp earlier, speed) ...
    # <- implied until ... etc.

    # basically we need to reverse maxspeeds, separate mp and speed into 
    # parallel lists, & shift speed to next-earlier speed change place
    # bah let me just do the code

    maxspeeds_rev = [dude for dude in reversed(maxspeeds)]

    mp_rev = [dude.milepost for dude in maxspeeds_rev]
    spd_rev = [dude.speed for dude in maxspeeds_rev]
    
    maxspeeds_rev = [] # we will rebuild it
    #for dude in mp_rev:
        #maxspeeds_rev.append(dude, 
    # hey let's use map() uh oh
    maxspeeds_rev = list(map(lambda x,y: MaxSpeed(x,y), mp_rev[:-1], spd_rev[1:]))
    # [:-1] there so same length. Not sure if problem to ignore last mp_rev guy.
    return maxspeeds_rev

if __name__ == "__main__":
    mainthing()
