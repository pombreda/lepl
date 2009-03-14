
from sys import maxunicode

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
        self.__intervals = []
        for interval in intervals:
            self.__append(interval)
        self.__str = self._build_str()
            
    def __append(self, interval):
        '''
        Add an interval to the existing intervals.
        
        This maintains self.__intervals in the normalized form described above.
        '''
        (a1, b1) = interval
        if a1 > b1: (a1, b1) = (b1, a1)
        intervals = []
        while self.__intervals:
            (a0, b0) = self.__intervals.pop()
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
    
    def complete(self):
        '''
        In a sequence this has no internal state, so is always complete.
        '''
        return True
    

class _Sequence(MutableNode):
    '''
    Common support for sequences of characters, etc.  This includes an index,
    which is internal state that describes progression through the sequence.
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
        return self.__index == len(self)
    
    def incomplete(self):
        '''
        More transitions available?
        '''
        return not self.complete()
    
    def transitions(self):
        '''
        Generate all possible transitions.  A transition a
        (Character, _Sequence) pair, which describes the possible characters
        and a sequence with an updated internal index.
        
        The algorithm here is generic; attempting to forward the responsibilty
        of generating transitions to the (embedded) sequence at the current
        index and, if that fails, calling the _next() method.
        '''
        if self[self._index].complete():
            for transition in self._next():
                yield transition
        else:
            for transition in self[self._index].transitions():
                    # construct the new sequence
                    clone = self.clone()
                    clone[self.__index] = transition[1]
                    yield (transition[0], clone)
                
    def _next(self):
        '''
        Generate transitions from the current position.  This is called if 
        forwarding to the the embedded sequence at the current index has
        failed.
        '''
        if not self.complete():
            yield (self[self._index], self.clone(self._index + 1))
    

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
        
    def _next(self):
        if self._index+1 < len(self):
            yield (self[self._index], self.clone(self._index + 1))
        else:
            yield (self[self._index], self.clone(0)) # restart
            
    def complete(self):
        return self.__index == 0
    
    def incomplete(self):
        return True
            
        
class Regexp(_Sequence):
    '''
    A sequence of Characters and Repeats.
    '''


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
    expr     = (star | brackets | letter)[:] & Drop(Eos()) > Regexp
    parser = expr.string_parser()
#    print(parser.matcher)
    return lambda text: parser(text)[0]

_parser = _make_parser()


class State():
    
    def __init__(self, regexps):
        self.__regexps = regexps
        
    def __raw_transitions(self):
        for regexp in self.__regexps:
            if regexp.incomplete():
                for transition in regexp.transitions():
                    yield transition
                    
    def complete(self):
        '''
        '''
                
        