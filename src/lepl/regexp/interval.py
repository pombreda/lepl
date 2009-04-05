
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Support for managing sets of intervals (not all used).  
An interval is an open range implemented as a tuple pair.  For example (2,5) 
is an interval that represents the integers 2,3,4 and 5.
'''

from bisect import bisect_left
from collections import deque


class Character(object):
    '''
    A set of possible values for a character, described as a collection of 
    intervals.  Each interval is [a, b] (ie a <= x <= b, where x is a character 
    code).  We use open bounds to avoid having to specify an "out of range"
    value, making it easier to work with a variety of alphabets.
    
    The intervals are stored in a list, ordered by a, joining overlapping 
    intervals as necessary.
    '''
    
    def __init__(self, intervals, alphabet):
        self.alphabet = alphabet
        self.__intervals = deque()
        for interval in intervals:
            self.__append(interval)
        self.__intervals = list(self.__intervals)
        self.__str = alphabet.fmt_intervals(self.__intervals)
        self.__build_index()
        self.state = None
        
    def append(self, interval):
        self.__append(interval)
        self.__build_index()
        
    def __build_index(self):
        self.__index = [interval[1] for interval in self.__intervals]
        
    def __append(self, interval):
        '''
        Add an interval to the existing intervals.
        
        This maintains self.__intervals in the normalized form described above.
        '''
        (a1, b1) = interval
        if b1 < a1: (a1, b1) = (b1, a1)
        intervals = deque()
        done = False
        while self.__intervals:
            (a0, b0) = self.__intervals.popleft()
            if a0 <= a1:
                if b0 < a1 and b0 != self.alphabet.before(a1):
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append((a0, b0))
                elif b1 <= b0:
                    # old interval starts before and ends after new interval
                    # so keep old interval, discard new interval and slurp
                    intervals.append((a0, b0))
                    done = True
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so discard old interval, extend new interval and continue
                    # (since it may overlap more intervals...)
                    (a1, b1) = (a0, b1)
            else:
                if b1 < a0 and b1 != self.alphabet.before(a0):
                    # new interval starts and ends before old, so add both
                    # and slurp
                    intervals.append((a1, b1))
                    intervals.append((a0, b0))
                    done = True
                    break
                elif b0 <= b1:
                    # new interval starts before and ends after old interval
                    # so discard old and continue (since it may overlap...)
                    pass
                else:
                    # new interval starts before old, but partially overlaps,
                    # add extended interval and slurp rest
                    intervals.append((a1, b0))
                    done = True
                    break
        if not done:
            intervals.append((a1, b1))
        intervals.extend(self.__intervals) # slurp remaining
        self.__intervals = intervals
        
    def __str__(self):
        return self.__str
    
    def __repr__(self):
        return self.__str
    
    def len(self):
        return len(self.__intervals)
    
    def __getitem__(self, index):
        return self.__intervals[index]
    
    def __iter__(self):
        return iter(self.__intervals)
    
    def __contains__(self, c):
        '''
        Does the value lie within the intervals?
        '''
        if self.__index:
            index = bisect_left(self.__index, c)
            if index < len(self.__intervals):
                (a, b) = self.__intervals[index]
                return a <= c <= b
        return False
    
    def __hash__(self):
        return hash(self.__str)
    
    def __eq__(self, other):
        try:
            return self.__str == other.__str
        except:
            return False
        
    def build(self, graph, src, dest):
        '''
        Insert within an NFA graph (although at this level, it's not clear it's
        NFA).
        '''
        graph.connect(src, dest, self)
    

class Fragments(object):
    '''
    Similar to Character, but each additional interval fragments the list
    of intervals, instead of creating a new merged interval.  For example,
    if (3,5) is added to (1,4) and (7,8) then the result will be the
    intervals (1,2), (3,4), (5,5) and (7,8) - the interval (3,4) is the
    overlap between (1,4) and (3,5).   
    
    Used internally to combine transitions.
    '''
    
    def __init__(self, alphabet, characters=None):
        self.alphabet = alphabet
        self.__intervals = deque()
        if characters:
            for character in characters:
                self.append(character)
                
    def append(self, character):
        assert type(character) is Character
        for interval in character:
            self.__append(interval)
        
    def __append(self, interval):
        '''
        Add an interval to the existing intervals.
        '''
        (a1, b1) = interval
        if b1 < a1: (a1, b1) = (b1, a1)
        intervals = deque()
        alphabet = self.alphabet
        done = False
        while self.__intervals:
            (a0, b0) = self.__intervals.popleft()
            if a0 <= a1:
                if b0 < a1:
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append((a0, b0))
                elif b1 <= b0:
                    # old interval starts before or with and ends after or with 
                    # new interval
                    # so we have one, two or three new intervals
                    if a0 < a1: intervals.append((a0, alphabet.before(a1))) # first part of old
                    intervals.append((a1, b1)) # common to both
                    if b1 < b0: intervals.append((alphabet.after(b1), b0)) # last part of old
                    done = True
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so split old and continue
                    # (since it may overlap more intervals...)
                    if a0 < a1: intervals.append((a0, alphabet.before(a1))) # first part of old
                    intervals.append((a1, b0)) # common to both
                    a1 = alphabet.after(b0)
            else:
                if b1 < a0:
                    # new interval starts and ends before old
                    intervals.append((a1, b1))
                    intervals.append((a0, b0))
                    done = True
                    break
                elif b0 <= b1:
                    # new interval starts before and ends after or with old 
                    # interval
                    # so split and continue if extends (since last part may 
                    # overlap...)
                    intervals.append((a1, alphabet.before(a0))) # first part of new
                    intervals.append((a0, b0)) # old
                    if b1 > b0:
                        a1 = alphabet.after(b0)
                    else:
                        done = True
                        break
                else:
                    # new interval starts before old, but partially overlaps,
                    # split and slurp rest
                    intervals.append((a1, alphabet.before(a0))) # first part of new
                    intervals.append((a0, b1)) # overlap
                    intervals.append((alphabet.after(b1), b0)) # last part of old
                    done = True
                    break
        if not done:
            intervals.append((a1, b1))
        intervals.extend(self.__intervals) # slurp remaining
        self.__intervals = intervals
        
    def len(self):
        return len(self.__intervals)
    
    def __getitem__(self, index):
        return self.__intervals[index]
    
    def __iter__(self):
        return iter(self.__intervals)
    
    
class IntervalMap(dict):
    '''
    Map from intervals to values.
    
    Note - this is for open intervals!  This means it will not work as
    expected for continuous variables (which will overlap when two intervals
    share a single boundary value).  In other words, you cannot store 
    (1,2) and (2,3) together because both contain 2.
    '''
    
    def __init__(self):
        # None is used as a flag to indicate that a new index is needed
        self.__index = None
        
    def index(self):
        '''
        Build the internal indices.  Called automatically when necessary.
        '''
        second = lambda x: x[1]
        self.__intervals = list(sorted(self.keys(), key=second))
        self.__index = list(map(second, self.__intervals))
    
    def __setitem__(self, interval, value):
        # these are rather inefficient, but perhaps useful during development
#        assert None == self[interval[0]], 'Overlap'
#        assert None == self[interval[1]], 'Overlap'
        self.__index = None
        super(IntervalMap, self).__setitem__(interval, value)
        
    def __getitem__(self, point):
        '''
        The argument here is a single value, not an interval.
        '''
        if self.__index is None:
            self.index()
        if self.__index:
            index = bisect_left(self.__index, point)
            if index < len(self.__index):
                # keep interval for identity on retrieval, just in case
                (a, b) = interval = self.__intervals[index]
                if a <= point <= b:
                    return super(IntervalMap, self).__getitem__(interval)
        return None
    
    def __delitem__(self, interval):
        self.__index = None
        super(IntervalMap, self).__delitem__(interval)

    def __contains__(self, interval):
        (a, b) = interval
        return self[a] is not None or self[b] is not None
    

class TaggedFragments(object):
    '''
    Similar to Fragments, but associates a value with each initial interval;
    on retrieval returns a list of all values associated with fragment. 
    '''
    
    def __init__(self, alphabet):
        self.alphabet = alphabet
        self.__intervals = deque()
                
    def append(self, character, value):
        assert type(character) is Character
        for interval in character:
            self.__append(interval, [value])
        
    def __append(self, interval, v1):
        '''
        Add an interval to the existing intervals.
        '''
        (a1, b1) = interval
        if b1 < a1: (a1, b1) = (b1, a1)
        intervals = deque()
        alphabet = self.alphabet
        done = False
        while self.__intervals:
            ((a0, b0), v0) = self.__intervals.popleft()
            if a0 <= a1:
                if b0 < a1:
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append(((a0, b0), v0))
                elif b1 <= b0:
                    # old interval starts before or with and ends after or with 
                    # new interval
                    # so we have one, two or three new intervals
                    if a0 < a1: intervals.append(((a0, alphabet.before(a1)), v0)) # first part of old
                    intervals.append(((a1, b1), v0+v1)) # common to both
                    if b1 < b0: intervals.append(((alphabet.after(b1), b0), v0)) # last part of old
                    done = True
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so split old and continue
                    # (since new may overlap more intervals...)
                    if a0 < a1: intervals.append(((a0, alphabet.before(a1)), v0)) # first part of old
                    intervals.append(((a1, b0), v0+v1)) # common to both
                    a1 = alphabet.after(b0)
            else:
                if b1 < a0:
                    # new interval starts and ends before old
                    intervals.append(((a1, b1), v1))
                    intervals.append(((a0, b0), v0))
                    done = True
                    break
                elif b0 <= b1:
                    # new interval starts before and ends after or with old 
                    # interval
                    # so split and continue if extends (since last part may 
                    # overlap...)
                    intervals.append(((a1, alphabet.before(a0)), v1)) # first part of new
                    intervals.append(((a0, b0), v0+v1)) # old
                    if b1 > b0:
                        a1 = alphabet.after(b0)
                    else:
                        done = True
                        break
                else:
                    # new interval starts before old, but partially overlaps,
                    # split and slurp rest
                    intervals.append(((a1, alphabet.before(a0)), v1)) # first part of new
                    intervals.append(((a0, b1), v0+v1)) # overlap
                    intervals.append(((alphabet.after(b1), b0), v0)) # last part of old
                    done = True
                    break
        if not done:
            intervals.append(((a1, b1), v1))
        intervals.extend(self.__intervals) # slurp remaining
        self.__intervals = intervals
        
    def len(self):
        return len(self.__intervals)
    
    def __getitem__(self, index):
        return self.__intervals[index]
    
    def __iter__(self):
        return iter(self.__intervals)
    
    
