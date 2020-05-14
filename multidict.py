
class MultiDict:
    def __init__(self, d={}):
        self._layer1 = {} # outer keys to "canonical" keys
        self._layer2 = {} # "canonical" keys to values
        self._reverse = {} # keys are the "canonical" ones
        # Expects input in the form {(k1a, k1b): v1, (k2a): v2} (a dictionary
        # of tuples-to-values)
        # For that matter a dict of lists-to-values works too
        # The basic idea is that it maps all members of a given key to the 
        # first element of that key, which is used as the key to the second
        # mapping which actually contains the values.
        # The fundamental operations on this object will be these:
        #  1. multidict[k] = v
        #     Sets key group containing k to value v.
        #     If key belongs to no key group, create a new key group containing
        #     only k and set its value to v.
        #  2. multidict.join(k1, k2) joins k1 to the key group containing k2.
        #     That is all it does; even if k1 originally belongs to (k1, k3),
        #     k3 is unaffected besides k1 being removed from its group.
        # Construction of this object will be considered like so:
        #  1. A key tuple-or-list of the form (k1a, k1b, ...): v1 will be 
        #     treated as:
        #     if a key group already contains k1a:
        #       multidict[k1a] = v1
        #     else if no key group already contains k1a:
        #       multidict[k1a] = v1
        #     Oh I guess multidict[k] takes care of this already.
        #     Anyway the rest would be:
        #     multidict.join(k1b, k1a)
        #     multidict.join(..., k1a or k1b or any other key in that key group 
        #       it doesn't matter)
        # For example: {(k1a, k1b): v1, (k1b): v2} would create self._layer1 
        # and _layer2 as follows:
        #  1. Key is (k1a, k1b). Value is v1.
        #     This should create a new key group containing k1a and then join
        #     k1b to it.
        #     md[k1a] = v1:
        #     self._layer1 = {k1a: k1a}
        #     self._layer2 = {k1a: v1}
        #     md.join(k1b, k1a):
        #     self._layer1 = {k1a: k1a, k1b: k1a}
        #  2. Key is (k1b). Value is v2.
        #     This should set key group containing k1b to the value v2.
        #     md[k1b] = v2:
        #     self._layer1 = {k1a: k1a, k1b: k1a} (no change)
        #     self._layer2 = {k1a: v2}
        for k in d:
            for i in range(len(k)):
                subkey = k[i]
                if i==0:
                    # become the "root node" of this key-set
                    rootkey = subkey
                    self.__setitem__(subkey, d[k])
                else:
                    self.join(subkey, rootkey)

    def __repr__(self):
        # TODO iterator for MultiDict
        # YIKES I have to build these darn things in reverse
        # I mean seriously if the number of keys is N and the number of values/
        # groups is M this is going to take O(N*M) time.
        diclist = {}
        for rootkey in self._layer2:
            val = self._layer2[rootkey]
            for key in self._layer1:
                if self._layer1[key] == rootkey:
                    if val in diclist:
                        diclist[val].append(key)
                    else:
                        diclist[val] = [key]

        out = "old code: {"
        for val in diclist:
            out = out + str(tuple(diclist[val]))
            out = out + ": " + repr(val) + ", "
        out = out + "}\nnew code: {"

        for canonical_key, val in self._layer2.items():
            out = out + str(tuple(self._reverse[canonical_key]))
            out = out + ": " + repr(val) + ", "
        out = out + "}"
        
        return out

    def __setitem__(self, key, value):
        if key not in self._layer1:
            self._layer1[key] = key
            self._add_to_reverse(key, key)
        key2 = self._layer1[key]
        self._layer2[key2] = value
        
                
    def __getitem__(self, key):
        if key in self._layer1:
            return self._layer2[self._layer1[key]]
        else:
            raise KeyError()

    def __contains__(self, key):
        return key in self._layer1

    #def
    # TODO do __delitem__ and __keys__ and stuff later

    def join(self, key_wanting_to_join, key_dest):
        # can't move key from one group to another or otherwise join groups
        # (might change that later)
        assert key_wanting_to_join not in self._layer1

        canonical_key = self._layer1[key_dest]
        self._layer1[key_wanting_to_join] = canonical_key
        self._add_to_reverse(key_wanting_to_join, canonical_key)
        # TODO do something if a key group no longer has members

    # DON'T CALL if to_add already is in val list of _reverse
    # (otherwise it puts duplicate entry in that list)
    # The only way to avoid that purely in _add_to_reverse would be to search
    # all of _reverse's value lists for to_add, which would take O(N*M) time.
    def _add_to_reverse(self, to_add, canonical_key):
        if canonical_key in self._reverse:
            self._reverse[canonical_key].append(to_add)
        else:
            self._reverse[canonical_key] = [to_add]
        

if __name__ == "__main__":

    md = MultiDict({('1a','1b','1c'):1, ('2a','2b'):2})
    print(md,"\n--")
    md.join('1d','1b')
    print(md,"\n--")
    md['3a'] = 3
    print(md,"\n--")
    md['2b'] = 20
    print(md)
    md.join('4b','4a')
