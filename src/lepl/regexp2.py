
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
A simple regular expression engine in pure Python.

This takes a set of regular expressions (only the most basic functionality is
supported) and generates a finite state machine that can match them against
a stream of values.

Although simple (and slow compared to a C version), it has some advantages 
from being implemented in Python.

First, it can use a variety of alphabets - it is not restricted to strings.  
It could, for example, match lists of integers, or sequences of tokens.

Second, it can yield intermediate matches.

Third, it is extensible.
'''


from bisect import bisect_left, bisect_right
from collections import deque
from operator import itemgetter
from sys import maxunicode
from traceback import format_exc

from lepl.matchers import *
from lepl.node import *
from lepl.trace import TraceResults
from lepl.support import empty


class UnicodeAlphabet(object):
    '''
    Various values needed to define the domain over which the regular 
    expression is applied.  Here default unicode strings are supported.
    
    Characters in the alphabet must have an ordering defined (equality,
    less than, and less than or equal to are used).
    
    nbr returns true if two characters are adjacent.  It can always return
    false, but the generated machine will be less compact. 
    '''
    
    def __init__(self):
        self.min = chr(0)
        try:
            self.max = chr(maxunicode)
        except: # Python 2.6
            self.max = unichr(maxunicode)
    
    def before(self, c): 
        '''
        Must return the character before c in the alphabet.  Never called with
        min (assuming input data are in range).
        ''' 
        return chr(ord(c)-1)
    
    def after(self, c): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return chr(ord(c)+1)
    
    def fmt_intervals(self, intervals):
        '''
        This must fully describe the data in the intervals (it is used to
        hash the data).
        '''
        inrange = '-\\[]'
        outrange = inrange + '*+()'
        def escape(c, chars=inrange):
            if c in chars: c = '\\' + c
            return c
        ranges = []
        if len(intervals) == 1 and \
                intervals[0][0] == intervals[0][1]:
            return escape(intervals[0][0], outrange)
        else:
            for (a, b) in intervals:
                if a == b:
                    ranges.append(escape(a))
                else:
                    ranges.append('{0!s}-{1!s}'.format(escape(a), escape(b)))
            return '[{0}]'.format(''.join(ranges))
        
    def fmt_sequence(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return ''.join(str(c) for c in children)
    
    def fmt_repeat(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        s = self.fmt_sequence(children)
        if len(children) == 1 and type(children[0]) in (Character, Choice):
            return s + '*'
        else:
            return '({0})*'.format(s)

    def fmt_choice(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return '({0})'.format('|'.join(self.fmt_sequence(child) 
                                       for child in children))

    def fmt_option(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        s = self.fmt_sequence(children)
        if len(children) == 1 and type(children[0]) in (Character, Choice):
            return s + '?'
        else:
            return '({0})?'.format(s)


UNICODE = UnicodeAlphabet()


class Character(object):
    '''
    A set of possible values for a character, described as a collection of 
    intervals.  Each interval is [a, b] (ie a <= x <= b, where x is a character 
    code).  We use open bounds to avoid having to specify an "out of range"
    value, making it easier to work with a variety of alphabets.
    
    The intervals are stored in a list, ordered by a, rewriting intervals as 
    necessary to ensure no overlap.
    '''
    
    def __init__(self, intervals=[], alphabet=None):
        if intervals: assert alphabet
        self.__intervals = deque()
        for interval in intervals:
            self.__append(interval, alphabet)
        self.__intervals = list(self.__intervals)
        self.__alphabet = alphabet
        if alphabet:
            self.__str = alphabet.fmt_intervals(self.__intervals)
        else:
            self.__str = '' # final state is invisible
        self.__index = [interval[1] for interval in self.__intervals]
        self.state = None
        
    def clone(self):
        return Character(self.__intervals, self.__alphabet)
        
    def number(self, state):
        self.state = state
        return self.state + 1
            
    def __append(self, interval, alphabet):
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
                if b0 < a1 and b0 != alphabet.before(a1):
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
                if b1 < a0 and b1 != alphabet.before(a0):
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
    

class _Fragments(object):
    '''
    Similar to Character, but each additional interval fragments the list
    of ranges.  Used internally to combine transitions.
    '''
    
    def __init__(self, characters, alphabet):
        self.__intervals = deque()
        for character in characters:
            assert type(character) is Character
            for interval in character:
                self.__append(interval, alphabet)
            
    def __append(self, interval, alphabet):
        '''
        Add an interval to the existing intervals.
        '''
        (a1, b1) = interval
        if b1 < a1: (a1, b1) = (b1, a1)
        intervals = deque()
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
    

class Sequence(Node):
    '''
    A sequence of Characters, etc.  This includes an index, which is internal 
    state that describes progression through the sequence.
    
    Note that a Sequence instance is static - index does not change - but it
    may be cloned with a different index value.
    '''
    
    def __init__(self, children, alphabet):
        super(Sequence, self).__init__(children)
        self.alphabet = alphabet
        self.state = None
        self.__str = self._build_str()
        
    def number(self, state):
        for child in self._children:
            state = child.number(state)
        return state
        
    def _build_str(self):
        return self.alphabet.fmt_sequence(self._children)
        
    def __str__(self):
        return self.__str
    
    def __hash__(self):
        '''
        A _Sequence is defined by the contents, the index, and the state of
        the current child.
        '''
        return hash(self.__str)
        
    def __eq__(self, other):
        try:
            return self._children == other._children
        except:
            return False
        
    def before(self, expander):
        pass
    
    def after(self, expander):
        pass
    
    def leaf(self, expander, prev, char):
        return (prev, char)
    

class Option(Sequence):
    '''
    An optional sequence of Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_option(self._children)
    

class Repeat(Option):
    '''
    A sequence of Characters (or sequences) that can repeat 0 or more times.
    '''
    
    def __init__(self, children, alphabet):
        super(Repeat, self).__init__(children, alphabet)
        self.entry = None
    
    def _build_str(self):
        return self.alphabet.fmt_repeat(self._children)
    
    def before(self, expander):
        assert expander.states
        (prev, stack) = expander.states[-1]
        self.entry = prev
        assert stack
        (index, this) = stack[-1]
        assert this is self
        clone = deque(stack)
        clone.pop()
        clone.append((AFTER, self))
        print('clone', prev, clone)
        expander.push(prev, clone)
        
    def leaf(self, expander, prev, char):
        # this won't work - need to somehow intercept last transition from 
        # within repeat
        if char == self[-1]:
            char = char.clone()
            char.number(self.entry)
            
    
    
class Choice(Sequence):
    '''
    A set of alternative Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_choice(self._children)
    
        
_FINAL = Character()

class Regexp(Sequence):
    '''
    A labelled sequence of Characters and Repeats.
    '''
    
    def __init__(self, label, children, alphabet):
        children.append(_FINAL)
        super(Regexp, self).__init__(children, alphabet)
        self._info(children)
        self.label = label
        self.final = self.number(1)


def _make_unicode_parser():
    '''
    Construct a parser for Unicode based expressions.
    '''
    
    dup = lambda x: (x, x)
    sequence = lambda x: Sequence(x, UNICODE)
    repeat = lambda x: Repeat(x, UNICODE)
    option = lambda x: Option(x, UNICODE)
    choice = lambda x: Choice(x, UNICODE)
    character = lambda x: Character(x, UNICODE)
    
    escaped  = Drop('\\') + Any()
    raw      = ~Lookahead('\\') + AnyBut("[]*()-?")
    single   = escaped | raw
    
    pair     = single & Drop('-') & single                      > tuple
    letter   = single                                           >> dup
    
    interval = pair | letter
    brackets = Drop('[') & interval[1:] & Drop(']')
    char     = brackets | letter                                > character

    item     = Delayed()
    
    seq      = (char | item)[1:]                                > sequence
    group    = Drop('(') & seq & Drop(')')
    alts     = Drop('(') & seq[2:, Drop('|')] & Drop(')')       > choice
    star     = (alts | group | char) & Drop('*')                > repeat
    opt      = (alts | group | char) & Drop('?')                > option
    
    item    += alts | group | star | opt
    
    expr     = (char | item)[:] & Drop(Eos())
    parser = expr.string_parser(#Configuration(monitors=[TraceResults(False)]))
                                )
    return lambda text: parser(text)

__compiled_unicode_parser = _make_unicode_parser()
'''
Cache the parser to allow efficient re-use.
'''

def unicode_parser(label, text):
    '''
    Parse a Unicode regular expression, returning the associated Regexp.
    '''
    return Regexp(label, __compiled_unicode_parser(text), UNICODE)


BEFORE = 'BEFORE'
AFTER = 'AFTER'

class TreeIndex(LogMixin):
    '''
    This gives in-order traversal for children and both pre- and post-order
    (via BEFORE and AFTER) traversal of nodes.
    
    This requires indexing of nodes (which isn't directly supported by any
    of the classes above) and len().
    
    It is distinct from the earlier traversal code in that it has a stack of
    indexes.  No assumptions are made about the persistence of self.indexes 
    between calls to self.action.
    '''
    
    def __init__(self, root, type_):
        super(TreeIndex, self).__init__()
        self.root = root
        self.__type = type_
        
    def run(self):
        self.indexes = deque()
        self.push()
        self.__enter(self.root)
        
        while self.indexes:
            
            (prev, index) = self.indexes[-1]
            print(len(self.indexes), prev, index)
            
            if index:
                (posn, node) = index[-1]
                self._debug('Previous state was {0}'.format(prev))
                self._debug('Current position is {0}[{1}]'.format(node, posn))
                
                if posn is AFTER:
                    # if we are about to end and have an initial state of 0
                    # then have an empty transition to the final state
                    print(prev, len(index), '***')
                    if prev == 0 and len(index) == 1:
                        empty = Character()
                        empty.number(index[0].final)
                        self.__visit(empty)
                    # drop current node and repeat loop
                    index.pop()
                    
                else:
                    # if next position is in current node, find index
                    next_posn = None
                    if posn is BEFORE and len(node) > 0:
                        next_posn = 0
                    elif posn is not BEFORE and posn + 1 < len(node):
                        next_posn = posn + 1
                        
                    # advance to next position if found
                    if index is not None:
                        # update existing state on stack
                        index.pop()
                        index.append((next_posn, node))
                        # and extend
                        child = node[next_posn]
                        if isinstance(child, self.__type):
                            self.__enter(child)
                        else:
                            self.__visit(child)
                    else:
                        # otherwise, we are leaving this node
                        self.__leave()
            
            else:
                # if the current state is now empty, discard it
                self.indexes.pop()
                
        
    def __enter(self, node):
        self.indexes[-1][1].append((BEFORE, node))
        self.before(node)
        
    def __leave(self):
        (_index, node) = self.indexes[-1][1].pop()
        self.indexes[-1][1].append((AFTER, node))
        self.after(node)

    def __visit(self, child):
        # replace previous state
        (prev, index) = self.indexes.pop()
        (_posn, node) = index[-1]
        self.indexes.append((child.state, index))
        self._debug('Visiting {0} at {1}'.format(child, child.state))
        self.leaf(node, prev, child)

    def push(self, prev=0, index=None):
        self.indexes.append((prev, deque() if index is None else index))
        
        
class Expander(TreeIndex):
    
    def __init__(self, regexp):
        super(Expander, self).__init__(regexp, Node)
        self.__known_states = set()
        self.transitions = set()
        self.terminals = set()
        self.run()

    def leaf(self, node, prev, char):
        (prev, char) = node.leaf(self, prev, char)
        if char is _FINAL:
            self._debug('So {0} is a terminal'.format(prev))
            self.terminals.add(prev)
        else:
            transition = (prev, char)
            if transition in self.transitions:
                self._debug('Already known; discarding')
                self.indexes.pop()
            else:
                self._debug('New transition {0}/{1}'.format(transition, char.state))
                self.transitions.add(transition)
    
    def before(self, node):
        node.before(self)
        
    def after(self, node):
        node.after(self)

