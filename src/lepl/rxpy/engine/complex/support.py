#LICENCE


from lepl.rxpy.engine.support import Fail, Groups
from lepl.stream.core import s_next


class State(object):
    '''
    This is heavily optimized to (1) cache a valid hash and (2) avoid creating
    new objects (copy on write for slowly changing structures).
    '''
    
    def __init__(self, index, stream, groups=None, loops=None, checks=None,
                 last_number=None, hash=0):
        self.__index = index
        self.__stream = stream
        # map from index to (text, start, end) where text and end may be None
        # - copy on write
        self.__groups = groups if groups else {}
        # a list of (index, count) - copy on write
        self.__loops = loops if loops else []
        # (offset, set(index)) - copy on write
        self.__checks = checks if checks else (0, set())
        self.__last_number = last_number
        # this is updated in parallel with the above
        self.__hash = hash
        # number of characters to skip or -1 if matched
        # never cloned on non-zero
        self.__skip = 0
        
    def clone(self, index=None, stream=None):
        hash = self.__hash
        if index is not None:
            hash = hash ^ self.__index ^ index
        else:
            index = self.index
        if stream is None:
            stream = self.__stream
        # don't clone contents - they are copy on write
        return State(index, stream, groups=self.__groups,
                     loops=self.__loops, checks=self.__checks, 
                     last_number=self.__last_number, hash=hash)
        
    def __eq__(self, other):
        # don't include checks - they are not needed
        return other.index == self.index and \
                other.__groups == self.__groups and \
                other.__loops == self.__loops
    
    def __hash__(self):
        return self.__hash
    
    def start_group(self, number, offset):
        # copy (for write)
        groups = dict(self.__groups)
        self.__groups = groups
        old_triple = groups.get(number, None)
        if old_triple is None:
            # add key to hash (shift to avoid clashes with index)
            self.__hash ^= number << 8
        else:
            (_text, start, end) = old_triple
            if start is not None: self.__hash ^= start << 16
            if end is not None: self.__hash ^= end << 24
        new_triple = (None, offset, None)
        # add new value to hash
        self.__hash ^= offset << 16
        # and store
        groups[number] = new_triple
        # allows chaining on creating a new state
        return self
        
    def end_group(self, number, offset):
        # copy (for write)
        groups = dict(self.__groups)
        self.__groups = groups
        # we know key is present, so can ignore that
        old_triple = groups[number]
        (_text, start, end) = old_triple
        # remove old value from hash
        if end is not None: self.__hash ^= end << 24
        # TODO - maybe this should be postponed
        (_, stream) = s_next(self.__stream, start)
        (text, _) = s_next(stream, offset - start)
        new_triple = (text, start, offset)
        # add new value to hash
        self.__hash ^= offset << 24
        # and store
        groups[number] = new_triple
        if number != 0:
            self.__last_number = number
            
    def merge_groups(self, other):
        # copy (for write)
        groups = dict(self.__groups)
        self.__groups = groups
        for number in other.__groups:
            if number:
                new = other.__groups[number]
                old = groups.get(number, None)
                if new != old:
                    if old:
                        (_text, start, end) = old
                        self.__hash ^= start << 16
                        self.__hash ^= end << 24
                    (_text, start, end) = new
                    self.__hash ^= start << 16
                    self.__hash ^= end << 24
                    groups[number] = new
            
    def get_loop(self, index):
        loops = self.__loops
        if loops and loops[-1][0] == index:
            return loops[-1][1]
        else:
            return None
        
    def new_loop(self, index):
        # copy on write
        loops = list(self.__loops)
        self.__loops = loops
        next = (index, 0)
        # add to loops and hash
        loops.append(next)
        self.__hash ^= hash(next)
        return self
    
    def increment_inner_loop(self):
        # copy on write
        loops = list(self.__loops)
        self.__loops = loops
        prev = loops.pop()
        # drop from hash (added back later on increment)
        self.__hash ^= hash(prev)
        (index, count) = prev
        # increment
        count += 1
        next = (index, count)
        # add to loops and hash
        loops.append(next)
        self.__hash ^= hash(next)
        return self
    
    def drop_inner_loop(self):
        # copy on write
        loops = list(self.__loops)
        self.__loops = loops
        # drop from loops and hash
        prev = loops.pop()
        self.__hash ^= hash(prev)
        return self

    def check(self, offset, index):
        if offset != self.__checks[0]:
            self.__checks = (offset, set([index]))
        elif index in  self.__checks[1]:
            raise Fail
        else:
            self.__checks = (offset, self.__checks[1].union([index]))

    @property
    def index(self):
        return self.__index
    
    def advance(self, index, stream=None):
        self.__hash ^= index ^ self.__index
        self.__index = index
        if stream is not None:
            self.__stream = stream
        return self

    def groups(self, group_state):
        return Groups(group_state, self.__stream, self.__groups, None,
                      self.__last_number)
        
    def group(self, number):
        return self.__groups.get(number, (None, None, None))[0]
    
    @property
    def skip(self):
        return self.__skip
    
    @skip.setter
    def skip(self, skip):
        self.__hash ^= self.__skip ^ skip
        self.__skip = skip
        