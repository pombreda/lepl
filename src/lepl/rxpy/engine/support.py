#LICENCE

'''
Support classes shared by various engines.
'''                 

from operator import xor
from functools import reduce

from lepl.rxpy.parser.support import GroupState
from lepl.stream.core import s_next, s_empty, s_len
from lepl.support.lib import unimplemented


class Fail(Exception):
    '''
    Raised on failure.
    '''
    pass


class Match(Exception):
    '''
    Raised on success
    '''
    pass


class Loops(object):
    '''
    The state needed to track explicit repeats.  This assumes that loops are 
    nested (as they must be).
    '''
    
    def __init__(self, counts=None, order=None):
        # counts for loops in nested order
        self.__counts = counts if counts else []
        # map from node to position in counts list
        self.__order = order if order else {}
        
    def increment(self, node):
        if node not in self.__order:
            order = len(self.__counts)
            self.__order[node] = order
            self.__counts.append(0)
        else:
            order = self.__order[node]
            self.__counts = self.__counts[0:order+1]
            self.__counts[order] += 1
        return self.__counts[order]
    
    def drop(self, node):
        self.__counts = self.__counts[0:self.__order[node]]
        del self.__order[node]
        
    def clone(self):
        return Loops(list(self.__counts), dict(self.__order))
    
    def __eq__(self, other):
        return self.__counts == other.__counts and self.__order == other.__order
    
    def __hash__(self):
        return reduce(xor, map(hash, self.__counts), 0) ^ \
                      reduce(xor, [hash(node) ^ hash(self.__order[node])
                                   for node in self.__order], 0)

class Groups(object):
    
    def __init__(self, group_state=None, stream=None,
                 groups=None, offsets=None, last_index=None):
        '''
        `group_state` - The group definitions (GroupState)
        
        `text` - The text being matched
        
        Other arguments are internal for cloning.
        '''
        self.__state = group_state if group_state else GroupState()
        self.__stream = stream
        # map from index to (text, start, end)
        self.__groups = groups if groups else {}
        # map from index to start for pending groups
        self.__offsets = offsets if offsets else {}
        # last index matched
        self.__last_index = last_index
        # cache for str
        self.__str = None
        
    def start_group(self, number, offset):
        assert isinstance(number, int)
        self.__str = None
        self.__offsets[number] = offset
        
    def end_group(self, number, offset):
        assert isinstance(number, int)
        assert number in self.__offsets, 'Unopened group: ' + str(number)
        self.__str = None
        (_, stream) = s_next(self.__stream, self.__offsets[number])
        (text, _) = s_next(stream, offset - self.__offsets[number])
        self.__groups[number] = (text, self.__offsets[number], offset)
        del self.__offsets[number]
        if number: # avoid group 0
            self.__last_index = number

    def __len__(self):
        return self.__state.count
    
    def __bool__(self):
        return bool(self.__groups)
    
    def __nonzero__(self):
        return self.__bool__()
    
    def __eq__(self, other):
        '''
        Ignores values from context (so does not work for comparison across 
        matches).
        '''
        return type(self) == type(other) and str(self) == str(other)
            
    def __hash__(self):
        '''
        Ignores values from context (so does not work for comparison across 
        matches).
        '''
        return hash(self.__str__())
    
    def __str__(self):
        '''
        Unique representation, used for eq and hash.  Ignores values from 
        context (so does not work for comparison across matches).
        '''
        if not self.__str:
            def fmt_group(index):
                group = self.__groups[index]
                return str(group[1]) + ':' + str(group[2]) + ':' + repr(group[0])
            self.__str = ';'.join(str(index) + '=' + fmt_group(index)
                            for index in sorted(self.__groups.keys())) + ' ' + \
                         ';'.join(str(index) + ':' + str(self.__offsets[index])
                            for index in sorted(self.__offsets.keys()))
        return self.__str

    def clone(self):
        return Groups(group_state=self.__state, stream=self.__stream,
                      groups=dict(self.__groups),  offsets=dict(self.__offsets), 
                      last_index=self.__last_index)
    
    def data(self, number):
        if number in self.__state.names:
            index = self.__state.names[number]
        else:
            index = number
        try:
            return self.__groups[index]
        except KeyError:
            if isinstance(index, int) and index <= self.__state.count:
                return [None, -1, -1]
            else:
                raise IndexError(number)
            
    def group(self, number, default=None):
        group = self.data(number)[0]
        return default if group is None else group
        
    def start(self, number):
        return self.data(number)[1]
    
    def end(self, number):
        return self.data(number)[2]

    @property
    def last_index(self):
        return self.__last_index
    
    @property
    def last_group(self):
        return self.__state.indices.get(self.__last_index, None)
    
    @property
    def indices(self):
        return self.__state.indices.keys()
    
    @property
    def groups(self):
        return self.__groups


class StreamTargetMixin(object):
    '''
    Some common operations from `BaseMatchTarget` that are common across
    multiple engines (not necessarily in the engine class itself).

    Assumes self._parser_state is present in subclass.
    '''

    def __init__(self, *args, **kargs):
        super(StreamTargetMixin, self).__init__(*args, **kargs)

    def _reset(self, offset, stream, previous):
        self._previous = previous
        self._stream = stream
        self._offset = offset
        self._excess = 0
        self._advance(0)

    def _advance(self, delta=1):
        '''
        Move forwards in the stream.

        The following conventions are followed:
        - `offset` is the offset from the initial input
        - `stream` is the stream starting at the current location
        - `current` is the character at the current location
        - `previous` is the character just before the current location
        - `final` is True if the current character is the last
        - `excess` is the amount by which we advanced past the end
        '''
        if delta:
            if delta == 1:
                self._previous = self._current
            else:
                self._previous = None
            self._offset += delta

        old_stream = self._stream
        self._current = None
        self._final = False
        try:
            (advanced, self._stream) = s_next(old_stream, delta)
            if advanced:
                self._previous = advanced[-1:]
            try:
                (self._current, next) = s_next(self._stream)
                self._final = s_empty(next)
            except StopIteration:
                self._excess = 1
        except StopIteration:
            if old_stream:
                self._excess = delta - s_len(old_stream) + 1
            else:
                self._excess += delta
            self._stream = None

    def string(self, next, text):
        length = len(text)
        if length == 1:
            if self._current == text[0:1]:
                return True
            else:
                raise Fail
        else:
            try:
                (advanced, _) = s_next(self._stream, length)
                if advanced == text:
                    return self._string_advance(next, length)
            except StopIteration:
                pass
            raise Fail

    #noinspection PyUnusedLocal
    @unimplemented
    def _string_advance(self, next, length):
        '''Called by `string()` above if match over multiple characters'''

    def character(self, charset):
        if self._current is not None and self._current in charset:
            return True
        else:
            raise Fail

    def dot(self, multiline):
        current_str = self._parser_state.alphabet.letter_to_str(self._current)
        if self._current is not None and (multiline or current_str != '\\n'):
            return True
        else:
            raise Fail

    def start_of_line(self, multiline):
        previous_str = self._parser_state.alphabet.letter_to_str(self._previous)
        if self._offset == 0 or (multiline and previous_str == '\\n'):
            return False
        else:
            raise Fail

    def end_of_line(self, multiline):
        if self._current is None:
            return False
        current_str = self._parser_state.alphabet.letter_to_str(self._current)
        if ((multiline or self._final) and current_str == '\\n'):
            return False
        raise Fail

    def word_boundary(self, inverted):
        word = self._parser_state.alphabet.word
        flags = self._parser_state.flags
        boundary = word(self._current, flags) != word(self._previous, flags)
        if boundary != inverted:
            return False
        else:
            raise Fail

    def digit(self, inverted):
        if self._current is not None and \
                self._parser_state.alphabet.digit(self._current,
                            self._parser_state.flags) != inverted:
            return True
        else:
            raise Fail

    def space(self, inverted):
        if self._current is not None and \
                self._parser_state.alphabet.space(self._current,
                            self._parser_state.flags) != inverted:
            return True
        else:
            raise Fail

    def word(self, inverted):
        if self._current is not None and \
                self._parser_state.alphabet.word(self._current,
                            self._parser_state.flags) != inverted:
            return True
        else:
            raise Fail
