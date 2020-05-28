
from fractions import Fraction

class HasUnit: # virtual/interface-ish
    # Subclasses will define the values, and units

    def __init__(self, val, unit):
        self._val = val
        self._unit = unit

    def __str__(self):
        return str(self._val)+" "+self._unit

    def val(self):
        return self._val
    
    def unit(self):
        return self._unit

    # comparison methods compatible with both HasUnits and numbers

    def _compare_to(self, other):
        if isinstance(other, HasUnit):
            assert self._unit == other._unit
            to_compare = other._val
        elif isinstance(other, (int, float)):
            to_compare = other
        else:
            raise TypeError("incomparable types")

        return to_compare

    def __eq__(self, other):
        return self._val == self._compare_to(other)

    def __lt__(self, other):
        return self._val < self._compare_to(other)

    def __le__(self, other):
        to_compare = self._compare_to(other)
        return self < to_compare or self == to_compare

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other
        
    # maths
    def __add__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val + to_math, self._unit)

    def __sub__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val - to_math, self._unit)

    def __mod__(self, other):
        to_math = self._compare_to(other)
        return Pos(self._val % to_math, self._unit)

    # formatting just defers to float
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
            print("Frontier:", frontier)
            newfrontier = {}
            for node, prev in frontier.items():
                newneighbors = {n: node for n in self._conv[node].keys() if \
                    n not in frontier and n not in visited}
                newfrontier.update(newneighbors)
                visited[node] = prev
            frontier.clear()
            frontier.update(newfrontier)
            print("New frontier:", newfrontier)
        if unit_to in frontier:
            # create the path from end to beginning
            path.append(unit_to)
            print("path:", path)
            path.append(frontier[unit_to])
            print("path:", path)
            nextnode = frontier[unit_to]
            while nextnode in visited: # will append starting node's None
                path.append(visited[nextnode])
                print("path:", path)
                nextnode = visited[nextnode]
            finalpath = list(reversed(path[:-1])) # removes the None
        else:
            raise ValueError("cannot convert to unit "+str(unit_to))

        return finalpath

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
