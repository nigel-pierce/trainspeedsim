
from fractions import Fraction
from decimal import Decimal
import decimal

# TODO add accel
def system_to_unit(units, unit_type, size):
    systems = ("imperial", "metric")
    types = ("pos", "speed")
    sizes = ("big", "small")

    # validate
    if units not in systems:
        raise ValueError("units '"+units+"' must be in systems "+systems)
    if unit_type not in types:
        raise ValueError("unit type '"+unit_type+"' must be one of "+types)
    if size not in sizes:
        raise ValueError("size '"+size+"' must be one of "+sizes)

    #everything = {
            #systems[0]: {
            #types[0]: {
            #sizes[0]: 

    sys_to_unit = {
            "imperial": {
                "pos": {
                    "big": "mi",
                    "small": "f" },
                "speed": {
                    "big":  "mi/h",
                    "small":"f/s" } },
            "metric": {
                "pos": {
                    "big":   "km",
                    "small": "m" },
                "speed": {
                    "big":   "km/h",
                    "small": "m/s" } }
            }
    
    return sys_to_unit[units][unit_type][size]

class HasUnit: # virtual/interface-ish
    # Subclasses will define the values, and units

    # decorator b/c needs its own decimal context
    def preservecontext(f):
        def preserver(*args, **kwargs):
            oldcontext = decimal.getcontext()
            decimal.setcontext(decimal.ExtendedContext)
            result = f(*args, **kwargs)
            decimal.setcontext(oldcontext)
            return result
        return preserver

    def __init__(self, val, unit):
        if isinstance(val, str):
            self._val = Decimal(val)
        else:
            self._val = val
        self._unit = unit

    @preservecontext
    def __str__(self):
        return str(self._val)+" "+self._unit

    def __repr__(self):
        #return str(self)
        return "{}({}, '{}')".format(type(self).__name__, self._val, self._unit)

    def val(self):
        return self._val
    
    def unit(self):
        return self._unit

    # comparison methods compatible with both HasUnits and numbers

    def _compare_to(self, other):
        if isinstance(other, HasUnit):
            assert self._unit == other._unit
            to_compare = other._val
        elif isinstance(other, (int, float, Decimal)):
            to_compare = other
        else:
            raise TypeError("incomparable types "+str(type(self))+", " \
                    +str(type(other)))

        return to_compare

    @preservecontext
    def __eq__(self, other):
        return self._val == self._compare_to(other)

    @preservecontext
    def __lt__(self, other):
        return self._val < self._compare_to(other)

    @preservecontext
    def __le__(self, other):
        to_compare = self._compare_to(other)
        return self < to_compare or self == to_compare

    @preservecontext
    def __gt__(self, other):
        return not self <= other

    @preservecontext
    def __ge__(self, other):
        return not self < other
        
    # maths
    @preservecontext
    def __add__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val + to_math, self._unit)

    @preservecontext
    def __sub__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val - to_math, self._unit)

    @preservecontext
    def __mod__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val % to_math, self._unit)

    # formatting just defers to float
    @preservecontext
    def __format__(self, format_spec):
        return format(self._val, format_spec) + " " + self._unit

class ConvertibleUnit(HasUnit):
    # subclasses will define values, units, and their conversions
    
    def __init__(self, val, unit):
        HasUnit.__init__(self, val, unit)

    def to_bigger_unit(self):
        assert self._unit in self._bigger, "cannot bigify" # keys are the small units
        return self.convert_to(self._bigger[self._unit])

    def to_smaller_unit(self):
        assert self._unit in self._smaller, "cannot smallify" # keys are the big units
        return self.convert_to(self._smaller[self._unit])

    # These next two make my life easier
    def to_bg(self):
        return self.to_bigger_unit()

    def to_sm(self):
        return self.to_smaller_unit()


    @HasUnit.preservecontext
    def convert_to(self, unit):
        # find path from self._unit to unit
        # the graph is stored as a dict where each key is a node and value is a 
        # dict where each key is a node (unit) connected (convertible) to.
        # to make it "undirected", include the reverse direction yeah.


        unit_from = self._unit
        unit_to = unit

        if unit_to == self._unit:
            return type(self)(self._val, self._unit)

        conv_path = self._dijkstra(unit_from, unit_to)

        result = self._conv_calc(conv_path)

        return type(self)(result, unit)

    def _dijkstra(self, unit_from, unit_to):
        path = []
        visited = {} # ones we have examined all edges from and the value is 
            # the previous node
        frontier = {unit_from: None} # neighbors to nodes in visited that we 
            # haven't examined outgoing edges yet
        
        while unit_to not in frontier and len(frontier) > 0:
            #print("Frontier:", frontier)
            newfrontier = {}
            for node, prev in frontier.items():
                newneighbors = {n: node for n in self._conv[node].keys() if \
                    n not in frontier and n not in visited}
                newfrontier.update(newneighbors)
                visited[node] = prev
            frontier.clear()
            frontier.update(newfrontier)
            #print("New frontier:", newfrontier)
        if unit_to in frontier:
            # create the path from end to beginning
            path.append(unit_to)
            #print("path:", path)
            path.append(frontier[unit_to])
            #print("path:", path)
            nextnode = frontier[unit_to]
            while nextnode in visited: # will append starting node's None
                path.append(visited[nextnode])
                #print("path:", path)
                nextnode = visited[nextnode]
            finalpath = list(reversed(path[:-1])) # removes the None
        else:
            raise ValueError("cannot convert to unit "+str(unit_to))

        return finalpath

    @HasUnit.preservecontext
    def _conv_calc(self, finalpath):
        result = self._val
        unit_from = finalpath[0]
        for unit_to in finalpath[1:]:
            convd = self._conv[unit_from]
            ratio = convd[unit_to]
            result = result * ratio.numerator / ratio.denominator
            unit_from = unit_to
        return result

class Pos(ConvertibleUnit):
    # conversions
    # should be sufficient to convert between any of these in any direction
    _conv = {"f":  {"mi": Fraction(1,5280),  \
                   "m":  Fraction(0.3048),  \
                   "in": Fraction(12)     }, # just to spice things up\
            "mi": {"f":  Fraction(5280)   },\
            "m":  {"f":  Fraction(3.2808399), \
                    "cm": Fraction(100),    \
                    "km": Fraction(1, 1000) },  \
            "in": {"f":  Fraction(1, 12) }, \
            "cm": {"m": Fraction(1, 100) }, \
            "km": {"m":  Fraction(1000) }\
           }
    _bigger = {     \
        "f": "mi",  \
        "m": "km"   \
    }
    _smaller = {    \
        "mi": "f",  \
        "km": "m",  \
    }

    def __init__(self, val, unit):
        assert unit in self._conv
        ConvertibleUnit.__init__(self, val, unit)

class Speed(ConvertibleUnit):
    _conv = { \
        "f/s": {"mi/h": Fraction(3600,5280), \
                "m/s": Fraction(0.3048) }, \
        "mi/h":{"f/s": Fraction(5280, 3600) }, \
        "m/s": {"km/h": Fraction(3600,1000), \
                "f/s": Fraction(3.2808399) }, \
        "km/h":{"m/s": Fraction(1000,3600) } \
    }

    _bigger = {         \
        "f/s": "mi/h",  \
        "m/s": "km/h"   \
    }

    _smaller = {        \
        "mi/h": "f/s",  \
        "km/h": "m/s"   \
    }

    def __init__(self, val, unit):
        assert unit in self._conv
        ConvertibleUnit.__init__(self, val, unit)
    
class Accel(ConvertibleUnit):
    _conv = {\
        "f/s^2": {"m/s^2": Fraction(0.3048) },\
        "m/s^2": {"f/s^2": Fraction(3.2808399) } \
    }

    _bigger = {}

    _smaller = {}

    def __init__(self, val, unit):
        assert unit in self._conv
        ConvertibleUnit.__init__(self, val, unit)

if __name__ == "__main__":

    pos = Pos(1, "f")
    in_m = pos.convert_to("m")
    print(pos, "is" , in_m)
    pos_bigger = pos.to_bigger_unit()
    print(pos, "biggers to", pos_bigger)
    try:
        pos_smaller = pos.to_smaller_unit()
        print(pos, "smallers to", pos_smaller)
    except AssertionError as e:
        print(repr(e))
    pos_bigger_smaller = pos_bigger.to_smaller_unit()
    print(pos_bigger, "smallers to", pos_bigger_smaller)
    
    mi = Pos(1, "mi")
    in_km = mi.convert_to("km")
    print(mi, "is", in_km)

    in_mi = mi.convert_to("mi")
    print(mi, "is", in_mi)

    two_mi = Pos(2, "mi")
    in_m = two_mi.convert_to("m")
    print(two_mi, "is", in_m)

    speed = Speed(1, "f/s")
    in_mps = speed.convert_to("m/s")
    print(speed, "is", in_mps)

    accel = Accel(1.5, "f/s^2")
    in_mps2 = accel.convert_to("m/s^2")
    print(accel, "is", in_mps2)

    mps = Accel(2, "m/s^2")
    in_fps2 = mps.convert_to("f/s^2")
    print(mps, "is", in_fps2)

    try:
        acc_big = accel.to_bigger_unit()
        print(accel, "is", acc_big)
    except AssertionError as e:
        print(repr(e))

    try:
        acc_small = accel.to_smaller_unit()
        print(accel, "is", acc_small)
    except AssertionError as e:
        print(repr(e))

    try:
        acc = Accel(3, "m/s^2")
        invalid_acc = acc.convert_to("f/h^2")
        print(invalid_acc)
    except ValueError as e:
        print(repr(e))

    dfoot = Pos('1', 'f')
    print(dfoot)

    d1pt1foot = Pos('1.1', 'f')
    print(d1pt1foot)

    print("...compared to float-based...")
    f1pt1foot = Pos(1.1, 'f')
    print(repr(f1pt1foot))
    print("OK I cheated in HasUnit by rounding val on repr/str, let's access _val directly")
    print(f1pt1foot._val)
    print("I swear this  shouldn't be working, let's try some math")
    print("2.2 f = 1.1 f + 1.1 f:", Pos(1.1, 'f')+Pos(1.1,'f'))
    print("WHY ISN'T THIS WORKING BY NOT WORKING")

    s = "Pos(0.1, 'f')"+"+Pos(0.1, 'f')"*8
    point1_9times = eval(s)
    print("Let's try 0.9 f as 0.1 f + itself 9 times (so effectively 9*0.1):", 
        point1_9times)
    print("AH-HA There it is!")
    
    s = "Pos('0.1', 'f')"+"+Pos('0.1', 'f')"*8
    dpoint1_9times = eval(s)
    print("Now let's try with Decimal (with Pos('0.1', 'f') etc.):",
            dpoint1_9times)
    
    print("See? Drop-in replacement.")

    print("Convert decimalized 0.9 f to m:", dpoint1_9times.convert_to('m'))

    dsum1 = dpoint1_9times+Pos('0.1', 'f')
    print("'0.9' f + '0.1' f:",dsum1)
    print("that, to m:", dsum1.convert_to('m'))
    
