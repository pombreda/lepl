
from bisect import bisect_left, bisect_right
from collections import deque
from operator import itemgetter
from sys import maxunicode
from traceback import format_exc

from lepl.matchers import *
from lepl.node import *
from lepl.trace import TraceResults


_CH_UPPER = maxunicode
_CH_LOWER = -1

class Character():
    '''
    A set of possible values for a character, described as a collection of 
    intervals.  Each interval is (a, b] (ie a < x <= b, where x is a character 
    code).  If a is -1 or b is sys.maxunicode then the relevant bound is 
    effectively open.
    
    The intervals are stored in a list, ordered by a, rewriting intervals as 
    necessary to ensure no overlap.
    '''
    
    def __init__(self, intervals):
        self.__intervals = deque()
        for interval in intervals:
            self.__append(interval)
        self.__intervals = list(self.__intervals)
        self.__str = self._build_str()
        self.__index = [interval[1] for interval in self.__intervals]
            
    def __append(self, interval):
        '''
        Add an interval to the existing intervals.
        
        This maintains self.__intervals in the normalized form described above.
        '''
        (a1, b1) = interval
        if a1 > b1: (a1, b1) = (b1, a1)
        intervals = deque()
        while self.__intervals:
            (a0, b0) = self.__intervals.popleft()
            if a0 <= a1:
                if b0 < a1:
                    # note that (2, 3] and (3, 4] "touch"
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append((a0, b0))
                elif b0 >= b1:
                    # old interval starts before and ends after new interval
                    # so keep old interval, discard new interval and slurp
                    intervals.append((a0, b0))
                    a1 = _CH_UPPER
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so discard old interval, extend new interval and continue
                    # (since it may overlap more intervals...)
                    (a1, b1) = (a0, b1)
            else:
                if b1 < a0:
                    # new interval starts and ends before old, so add both
                    # and slurp
                    intervals.append((a1, b1))
                    intervals.append((a0, b0))
                    a1 = _CH_UPPER
                    break
                elif b1 >= b0:
                    # new interval starts before and ends after old interval
                    # so discard old and continue (since it may overlap...)
                    pass
                else:
                    # new interval starts before old, but partially overlaps,
                    # add extended interval and slurp rest
                    intervals.append((a1, b0))
                    a1 = _CH_UPPER
                    break
        if a1 < _CH_UPPER:
            intervals.append((a1, b1))
        intervals.extend(self.__intervals) # slurp remaining
        self.__intervals = intervals
        
    def _build_str(self):
        inrange = '-\\[]'
        outrange = inrange + '*+()'
        def escape(x, chars=inrange):
            s = chr(x)
            if s in chars: s = '\\' + s
            return s
        ranges = []
        if len(self.__intervals) == 1 and \
                self.__intervals[0][0] + 1 == self.__intervals[0][1]:
            return escape(self.__intervals[0][1], outrange)
        else:
            for (a, b) in self.__intervals:
                if a + 1 == b:
                    ranges.append(escape(b))
                else:
                    ranges.append('{0!s}-{1!s}'.format(escape(a+1), escape(b)))
            return '[{0}]'.format(''.join(ranges))
        
    def __str__(self):
        return self.__str
    
    def len(self):
        return len(self.__intervals)
    
    def __getitem__(self, index):
        return self.__intervals[index]
    
    def __iter__(self):
        return iter(self.__intervals)
    
    def __contains__(self, char):
        '''
        Does char lie within the intervals?
        '''
        if self.__index:
            if type(char) is int:
                c = char
            else: 
                c = ord(char)
            index = bisect_left(self.__index, c)
            if index < len(self.__intervals):
                (a, b) = self.__intervals[index]
                return a < c <= b
        return False
    
    def __hash__(self):
        return hash(self.__str)
    
    def __eq__(self, other):
        try:
            return self.__str == other.__str
        except:
            return False
            

class _Fragments():
    '''
    Similar to Character, but each additional interval fragments the list
    of ranges.  Used internally to combine transitions.
    '''
    
    def __init__(self, characters):
        self.__intervals = deque()
        for character in characters:
            assert type(character) is Character
            for interval in character:
                self.__append(interval)
            
    def __append(self, interval):
        '''
        Add an interval to the existing intervals.
        '''
        (a1, b1) = interval
        if a1 > b1: (a1, b1) = (b1, a1)
        intervals = deque()
        while self.__intervals:
            (a0, b0) = self.__intervals.popleft()
            if a0 <= a1:
                if b0 <= a1:
                    # old interval starts and ends before new interval
                    # so keep old interval and continue
                    intervals.append((a0, b0))
                elif b0 >= b1:
                    # old interval starts before or with and ends after or with 
                    # new interval
                    # so we have one, two or three new intervals
                    if a0 < a1: intervals.append((a0, a1)) # first part of old
                    intervals.append((a1, b1)) # common to both
                    if b0 > b1: intervals.append((b1, b0)) # last part of old
                    a1 = _CH_UPPER
                    break
                else:
                    # old interval starts before new, but partially overlaps
                    # so split old and continue
                    # (since it may overlap more intervals...)
                    if a0 < a1: intervals.append((a0, a1)) # first part of old
                    intervals.append((a1, b0)) # common to both
                    (a1, b1) = (b0, b1)
            else:
                if b1 <= a0:
                    # new interval starts and ends before old, so add both
                    # and slurp
                    intervals.append((a1, b1))
                    intervals.append((a0, b0))
                    a1 = _CH_UPPER
                    break
                elif b1 >= b0:
                    # new interval starts before and ends after or with old 
                    # interval
                    # so split and continue if extends (since last part may 
                    # overlap...)
                    intervals.append((a1, a0)) # first part of new
                    intervals.append((a0, b0)) # old
                    if b1 > b0:
                        (a1, b1) = (b0, b1)
                    else:
                        a1 = _CH_UPPER
                        break
                else:
                    # new interval starts before old, but partially overlaps,
                    # split and slurp rest
                    intervals.append((a1, a0)) # first part of new
                    intervals.append((a0, b1)) # overlap
                    intervals.append((b1, b0)) # last part of old
                    a1 = _CH_UPPER
                    break
        if a1 < _CH_UPPER:
            intervals.append((a1, b1))
        intervals.extend(self.__intervals) # slurp remaining
        self.__intervals = intervals
        
    def len(self):
        return len(self.__intervals)
    
    def __getitem__(self, index):
        return self.__intervals[index]
    
    def __iter__(self):
        return iter(self.__intervals)
    

class _Sequence(MutableNode):
    '''
    Common support for sequences of Characters, etc.  This includes an index,
    which is internal state that describes progression through the sequence.
    
    Note that a _Sequence instance is static - index does not change - but it
    may be cloned with a different index value.
    '''
    
    def __init__(self, children, index=0):
        super(_Sequence, self).__init__(children)
        self.__str = self._build_str()
        self._index = index
        
    def clone(self, index):
        return type(self)(self.children(), index)
        
    def _build_str(self):
        return ''.join(str(c) for c in self.children())
    
    def __str__(self):
        return self.__str
    
    def complete(self):
        '''
        Has reached a possible final match?
        '''
        try:
            return self[self._index].complete()
        except:
            return self._index == len(self)
    
    def incomplete(self):
        '''
        More transitions available?
        '''
        return self._index < len(self)
    
    def transitions(self):
        '''
        Generate all possible transitions.  A transition a
        (Character, _Sequence) pair, which describes the possible characters
        and a sequence with an updated internal index.
        
        The algorithm here is generic; attempting to forward the responsibilty
        of generating transitions to the (embedded) sequence at the current
        index and, if that fails, calling the _next() method.
        '''
        try:
            for (chars, seq) in self[self._index].transitions():
                    # construct the new sequence
                    clone = self.clone(self._index)
                    clone[self._index] = seq
                    yield (chars, clone)
        except:
            for transition in self._transitions():
                yield transition
                
    def _transitions(self):
        '''
        Generate transitions from the current position.  This is called if 
        forwarding to the the embedded sequence at the current index has
        failed.
        '''
        if self._index < len(self):
            yield (self[self._index], self.clone(self._index + 1))
    
    def __contains__(self, char):
        return self.incomplete() and char in self[self._index]
    
    def __hash__(self):
        '''
        A _Sequence is defined by the contents, the index, and the state of
        the current child.
        '''
        value = hash(self.__str) ^ self._index
        if self.incomplete(): value ^= hash(self[self._index])
        return value
        
    def __eq__(self, other):
        try:
            return self._children == other._children \
                and self._index == other._index
        except:
            return False
    

class Repeat(_Sequence):
    '''
    A sequence of Characters that can repeat 0 or more times.
    '''
    
    def _build_str(self):
        s = super(Repeat, self)._build_str()
        if len(self) == 1:
            return s + '*'
        else:
            return '({0})*'.format(s)
        
    def _transitions(self):
        yield (self[self._index], self.clone((self._index + 1) % len(self)))
            
    def complete(self):
        return self._index == 0
    
    def incomplete(self):
        return True
            
        
class Regexp(_Sequence):
    '''
    A labelled sequence of Characters and Repeats.
    '''
    
    def __init__(self, label, children, index=0):
        super(Regexp, self).__init__(children, index)
        self.label = label

    def clone(self, index):
        return type(self)(self.label, self.children(), index)
        

def _make_parser():
    
    mktuple1 = lambda x: (ord(x)-1, ord(x))
    mktuple2 = lambda xy: (ord(xy[0])-1, ord(xy[1]))
    
    char     = Drop('\\')+Any() | ~Lookahead('\\')+Any()
    pair     = char & Drop('-') & char
    interval = (pair > mktuple2) | (char >> mktuple1)
    brackets = (Drop('[') & interval[1:] & Drop(']')) > Character
    letter   = (char >> mktuple1) > Character
    nested   = Drop('(') & (brackets | letter)[1:] & Drop(')')
    star     = (nested | brackets | letter) & Drop('*') > Repeat
    expr     = (star | brackets | letter)[:] & Drop(Eos())
    parser = expr.string_parser()
#    print(parser.matcher)
    return lambda text: parser(text)

__compiled_parser = _make_parser()

def parser(label, text):
    return Regexp(label, __compiled_parser(text))


class State():
    '''
    A single node in a FSM.
    '''
    
    def __init__(self, regexps):
        self.__regexps = frozenset(regexps)
        
    def transitions(self):
        '''
        A sequence of (Character, State) pairs.
        '''
        fragments = self.__split(list(self.__raw_transitions()))
        joined = self.__join(fragments)
        for regexps in joined:
            yield (Character(joined[regexps]), State(regexps))
        
    def __raw_transitions(self):
        for regexp in self.__regexps:
            if regexp.incomplete():
                for transition in regexp.transitions():
                    yield transition
                    
    def __split(self, raw):
        '''
        Generate a set of mutually exclusive character ranges so that we can
        divide the transitions cleanly.
        '''
        fragments = {} # from char range to regexps
        for (fa, fb) in _Fragments(chars for (chars, _seq) in raw):
            # we have constructed fragments so that chars will always be
            # within the chars for a transition
            for (chars, regexp) in raw:
                if fb in chars:
                    if (fa, fb) not in fragments:
                        fragments[(fa, fb)] = []
                    fragments[(fa, fb)].append(regexp)
        return fragments

    def __join(self, fragments):
        '''
        Collect together all character ranges for identical groups of regexps.
        '''
        joined = {} # from regexps to char ranges
        for chars in fragments:
            regexps = frozenset(fragments[chars])
            if regexps not in joined:
                joined[regexps] = []
            joined[regexps].append(chars)
        return joined
    
    def __eq__(self, other):
        try:
            return self.__regexps == other.__regexps
        except:
            return False

    def __len__(self):
        return len(self.__regexps)
    
    def terminals(self):
        '''
        A sequence of labels for regexps that can be considered complete at
        this node.
        '''
        for regexp in self.__regexps:
            if regexp.complete():
                yield regexp.label
                
    def __hash__(self):
        '''
        A State is described completely by the state of the Regexps it contains.
        '''
        return hash(self.__regexps)
    
    def __eq__(self, other):
        '''
        A State is described completely by the state of the Regexps it contains.
        '''
        try:
            return self.__regexps == other.__regexps
        except:
            return False
        

class Fsm():
    
    def __init__(self, regexps):
        self.__terminals = []
        self.__transitions = []
        index = self.__expand(regexps)
        self.__compile(index)

    def __expand(self, regexps):
        '''
        Expand the entire set of states, noting all transitions and terminals.
        '''
        known = set()
        state_to_index = {}
        stack = deque()
        stack.append(State(regexps))
        while stack:
            state = stack.pop()
            if state not in known:
                index = len(known)
                state_to_index[state] = index
                known.add(state)
                self.__terminals.append(list(state.terminals()))
                transitions = list(state.transitions())
                self.__transitions.append(transitions)
                for (_, state) in transitions:
                    stack.append(state)
        return state_to_index
    
    def __compile(self, state_to_index):
        '''
        After __expand the transitions array contains, at each index, a list 
        of (Character, State) pairs.  We need to convert the States into 
        indices and the Characters into maps from character to index.
        
        Note that the Characters for a particular entry, by construction in 
        State, will not overlap.
        '''
        for start in range(len(self.__transitions)):
            # construct a list of (a, b, index) triples, where a and b are the
            # usual interval values (a < c <= b)
            triples = []
            for (chars, state) in self.__transitions[start]:
                end = state_to_index[state]
                for (a, b) in chars:
                    triples.append((a, b, end))
            triples.sort(key=itemgetter(0))
            index = [b for (_a, b, _end) in triples]
            l = len(index)
            def lookup(c, l=l, index=index, triples=triples):
                triple = bisect_left(index, c)
                if triple < l:
                    (a, b, end) = triples[triple]
                    if a < c <= b:
                        return end
                return None
            self.__transitions[start] = lookup
            
    def generator(self, characters):
        '''
        This is the most basic way of calling the matcher.  It will yield
        all values matched, in increasing size.  Note that (1) the characters
        must be a sequence (eg iter("some string")) and (2) the result returned,
        if needed, must be converted immediately via, for example, 
        ''.join(result), because it will be extended on the next call.
        '''
        state = 0
        result = deque()
        transitions = self.__transitions
        terminals = self.__terminals
        while state is not None:
            for label in terminals[state]:
                yield (label, result)
            char = next(characters)
            result.append(char)
            c = ord(char)
            state = transitions[state](c)
    
    def all_for_string(self, string):
        '''
        A simplified but less efficient interface.  Yields values in 
        increasing size.
        '''
        for (label, result) in self.generator(iter(string)):
            yield (label, ''.join(result))
