



if __name__ == "main":
    raw_maxspeeds = load_maxspeeds()
    maxspeeds = insert_speed_changes(raw_maxspeeds)
    
    segment_length = 0.1 # this stuff's in miles for some reason
    accel = 1.25; # for speeding up; braking will come later Also its f/s^2

    bestspeeds = sim_speed(maxspeeds, segment_length)

    print(bestspeeds)


def sim_speed(maxspeeds, seg_len, accel):
    bestspeeds = []
    route_len = 5280 * (maxspeeds[-1].milepost - maxspeeds[0].milepost)
    position = 0 # in ft
    for segment_point in range(0, route_len, seg_len):
        sim_segment(bestspeeds, maxspeeds, position, seg_len, accel)
    
    return bestspeeds


# simulates speed at given point, taking into account prev point's speed
# and max speed at point
def sim_segment(bestspeeds, maxspeeds, index, seg_len, accel):
    if segment_point == 0:
        len_from_prev = 0
        return
    else:
        len_from_prev = segment_length
        
    v_init = bestspeeds[index-1]
    v_max = lowest_current_max_speed(maxspeeds, index, seg_len, accel)
    v_next = lowest_upcoming_max_speed(maxspeeds, index, seg_len, accel)

    v_target = min(v_max, v_next)

def lowest_current_max_speed(maxspeeds, index, seg_len, accel)
    candidates = []
    candidates = lowest_applicable_max_speed(maxspeeds, index * seg_len)



def lowest_applicable_max_speed(maxspeeds, mile):
    # throw out all speed limits ahead of us
    maxprevs = [x for x in maxspeeds if x.milepost <= mile]
    # sort by speed, then dist from mile
    closest = sorted(sorted(maxspeeds, key = lambda speedlimit: speedlimit.speed), key=lambda speedlimit: abs(mile - speedlimit.milepost)
    # if on change of speed, lower one is the one
    if mile == closest[0].milepost:
        # first one should be closest & lowest speed, yeah
        return closest[0]
    # if between changes of speed, higher one is the one
    else:
        

    
