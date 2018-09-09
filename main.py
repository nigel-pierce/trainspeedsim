



if __name__ == "main":
    raw_maxspeeds = load_maxspeeds()
    maxspeeds = insert_speed_changes(raw_maxspeeds)
    
    segment_length = 0.1 * 5280 # working in f/s
    accel = 1.25; # for speeding up; braking will come later Also its f/s^2

    bestspeeds = sim_speed()

    print(bestspeeds)


def sim_speed(maxspeeds, seg_len, accel):
    bestspeeds = []
    route_len = 5280 * (maxspeeds[-1].milepost - maxspeeds[0].milepost)
    position = 0 # in ft
    for segment_point in range(0, route_len, seg_len):
        sim_segment(bestspeeds, maxspeeds, position, seg_len)
        if segment_point == 0:
            len_from_prev = 0
            continue
        else:
            len_from_prev = segment_length
        

