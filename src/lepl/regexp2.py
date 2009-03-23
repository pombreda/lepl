
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
        
    def join(self, chars):
        return ''.join(chars)


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
    
    def __init__(self, intervals, alphabet):
        self.alphabet = alphabet
        self.__intervals = deque()
        for interval in intervals:
            self.__append(interval)
        self.__intervals = list(self.__intervals)
        self.__str = alphabet.fmt_intervals(self.__intervals)
        self.__index = [interval[1] for interval in self.__intervals]
        self.state = None
        
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
    

#class _Fragments(object):
#    '''
#    Similar to Character, but each additional interval fragments the list
#    of ranges.  Used internally to combine transitions.
#    '''
#    
#    def __init__(self, characters):
#        self.alphabet = alphabet
#        self.__intervals = deque()
#        for character in characters:
#            assert type(character) is Character
#            for interval in character:
#                self.__append(interval, character.alphabet)
#            
#    def __append(self, interval, alphabet):
#        '''
#        Add an interval to the existing intervals.
#        '''
#        (a1, b1) = interval
#        if b1 < a1: (a1, b1) = (b1, a1)
#        intervals = deque()
#        done = False
#        while self.__intervals:
#            (a0, b0) = self.__intervals.popleft()
#            if a0 <= a1:
#                if b0 < a1:
#                    # old interval starts and ends before new interval
#                    # so keep old interval and continue
#                    intervals.append((a0, b0))
#                elif b1 <= b0:
#                    # old interval starts before or with and ends after or with 
#                    # new interval
#                    # so we have one, two or three new intervals
#                    if a0 < a1: intervals.append((a0, alphabet.before(a1))) # first part of old
#                    intervals.append((a1, b1)) # common to both
#                    if b1 < b0: intervals.append((alphabet.after(b1), b0)) # last part of old
#                    done = True
#                    break
#                else:
#                    # old interval starts before new, but partially overlaps
#                    # so split old and continue
#                    # (since it may overlap more intervals...)
#                    if a0 < a1: intervals.append((a0, alphabet.before(a1))) # first part of old
#                    intervals.append((a1, b0)) # common to both
#                    a1 = alphabet.after(b0)
#            else:
#                if b1 < a0:
#                    # new interval starts and ends before old
#                    intervals.append((a1, b1))
#                    intervals.append((a0, b0))
#                    done = True
#                    break
#                elif b0 <= b1:
#                    # new interval starts before and ends after or with old 
#                    # interval
#                    # so split and continue if extends (since last part may 
#                    # overlap...)
#                    intervals.append((a1, alphabet.before(a0))) # first part of new
#                    intervals.append((a0, b0)) # old
#                    if b1 > b0:
#                        a1 = alphabet.after(b0)
#                    else:
#                        done = True
#                        break
#                else:
#                    # new interval starts before old, but partially overlaps,
#                    # split and slurp rest
#                    intervals.append((a1, alphabet.before(a0))) # first part of new
#                    intervals.append((a0, b1)) # overlap
#                    intervals.append((alphabet.after(b1), b0)) # last part of old
#                    done = True
#                    break
#        if not done:
#            intervals.append((a1, b1))
#        intervals.extend(self.__intervals) # slurp remaining
#        self.__intervals = intervals
#        
#    def len(self):
#        return len(self.__intervals)
#    
#    def __getitem__(self, index):
#        return self.__intervals[index]
#    
#    def __iter__(self):
#        return iter(self.__intervals)
    

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
        
    def build(self, graph, before, after):
        '''
        Connect in sequence.
        '''
        if self._children:
            src = before
            last = self._children[-1]
            for child in self._children:
               dest = after if child is last else graph.new_node()
               child.build(graph, src, dest)
               src = dest
        else:
            graph.connect(before, after)


class Option(Sequence):
    '''
    An optional sequence of Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_option(self._children)
    
    def build(self, graph, before, after):
        '''
        Connect as sequence and also directly from start to end
        '''
        super(Option, self).build(graph, before, after)
        graph.connect(before, after)
    

class Repeat(Sequence):
    '''
    A sequence of Characters (or sequences) that can repeat 0 or more times.
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_repeat(self._children)            
    
    def build(self, graph, before, after):
        '''
        Connect in loop from before to before, and also directly from
        start to end.
        '''
        super(Repeat, self).build(graph, before, before)
        graph.connect(before, after) 
    
    
class Choice(Sequence):
    '''
    A set of alternative Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_choice(self._children)
    
    def build(self, graph, before, after):
        '''
        Connect in parallel from start to end, but add extra nodes so that
        the sequence is tried in order (because evaluation tries empty
        transitions last).
        '''
        if self._children:
            last = self._children[-1]
        for child in self._children:
            child.build(graph, before, after)
            if child is not last:
                node = graph.new_node()
                graph.connect(before, node)
                before = node
    
        
class Labelled(Sequence):
    '''
    A labelled sequence.  Within our limited implementation these are 
    restricted to (1) being children of Regexp and (2) not being followed
    by any other sequence.  Their termination defines terminal nodes.
    '''
    
    def __init__(self, label, children, alphabet):
        super(Labelled, self).__init__(children, alphabet)
        self.label = label
        
    def build(self, graph, before):
        '''
        A sequence, but with an extra final empty transition to force
        any loops before termination.
        '''
        after = graph.new_node()
        final = graph.new_node()
        super(Labelled, self).build(graph, before, after)
        graph.connect(after, final)
        graph.terminate(final, self.label)
        

class Regexp(Choice):
    '''
    A collection of Labelled instances.
    '''
    
    def __init__(self, children, alphabet):
        for child in children:
            assert isinstance(child, Labelled)
        super(Regexp, self).__init__(children, alphabet)
        
    def _build_str(self):
        return self.alphabet.fmt_sequence(self._children)

    def build(self, graph):
        '''
        Each Labelled is an independent sequence.  We use empty transitions 
        to order the choices.
        '''
        if self._children:
            before = graph.new_node()
            last = self._children[-1]
            src = before
            for child in self._children:
                child.build(graph, src)
                if child is not last:
                    src = graph.new_node()
                    graph.connect(before, src)
                    
    def nfa(self):
        graph = NfaGraph(self.alphabet)
        self.build(graph)
        return NfaCompiler(graph, self.alphabet).matcher
        
        
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
    parser = expr.string_parser()
    return lambda text: parser(text)

__compiled_unicode_parser = _make_unicode_parser()
'''
Cache the parser to allow efficient re-use.
'''

def unicode_single_parser(label, text):
    '''
    Parse a Unicode regular expression, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)], 
                  UNICODE)


def unicode_parser(*regexps):
    '''
    Parse a set of Unicode regular expressions, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)
                   for (label, text) in regexps], UNICODE)


class DfaGraph(LogMixin):
    '''
    Describes a DFA.
    '''
    
    def __init__(self, alphabet):
        super(DfaGraph, self).__init__()
        self._alphabet = alphabet
        self._next_node = 0
        self._transitions = {} # map from source to (dest, edge)
        self._terminals = {} # node to label
    
    def terminate(self, node, label):
        assert node < self._next_node
        assert node not in self._terminals, 'Node already has terminal'
        assert node not in self._transitions, 'Terminal node has transition'
        assert label is not None, 'Label cannot be None'
        self._terminals[node] = label
    
    def new_node(self):
        node = self._next_node
        self._next_node += 1
        return node
    
    def connect(self, src, dest, edge):
        '''
        Define a connection between src and dest, with an edge
        value (a character).
        '''
        assert src < self._next_node
        assert dest < self._next_node
        assert src not in self._terminals, 'Source is terminal'
        assert src not in self._transitions, 'Node already has transition'
        self._transitions[src] = [(dest, edge)]
            
    def __iter__(self):
        '''
        An iterator over all nodes.
        '''
        return iter(range(self._next_node))
    
    def transitions(self, src):
        '''
        An iterator over all non-empty transitions from src.
        '''
        return iter(self._transitions.get(src, []))
    
    def terminal(self, node):
        '''
        The terminal for the give node, or None.
        '''
        return self._terminals.get(node, None)


class NfaGraph(DfaGraph):
    '''
    Describes a NFA with epsilon (empty) transitions.
    '''
    
    def __init__(self, alphabet):
        super(NfaGraph, self).__init__(alphabet)
        self._empty_transitions = {} # map from source to set(dest)
    
    def terminate(self, node, label):
        assert not self._empty_transitions[node], 'Terminal node has empty transition'
        super(NfaGraph, self).terminate(node, label)
    
    def new_node(self):
        node = super(NfaGraph, self).new_node()
        self._empty_transitions[node] = set()
        return node
    
    def connect(self, src, dest, edge=None):
        '''
        Define a connection between src and dest, with an optional edge
        value (a character).
        '''
        if edge:
            super(NfaGraph, self).connect(src, dest, edge)
        else:
            assert src < self._next_node
            assert dest < self._next_node
            assert src not in self._terminals, 'Source is terminal'
            self._empty_transitions[src].add(dest)
            
    def empty_transitions(self, src):
        '''
        An iterator over all empty transitions from src.
        '''
        return iter(self._empty_transitions.get(src, []))
    

class NfaCompiler(LogMixin):
    '''
    Given a graph this constructs a transition table and an associated
    matcher.  The matcher attempts to find longest matches but does not
    guarantee termination (if a possible empty match is repeated).
    
    Note that the matcher returns a triple, including label.  This is not
    the same interface as the matchers used in recursive descent parsing.
    
    Evaluation order for transition:
    - Transition with character, if defined
    - Empty transition to largest numbered node 
    these ensure we do deepest match first.
    '''
    
    def __init__(self, graph, alphabet):
        super(NfaCompiler, self).__init__()
        self.__graph = graph
        self.__alphabet = alphabet
        self.__table = {}
        self.__build_table()
        
    def __build_table(self):
        '''
        Rewrite the graph as a transition table, with appropriate ordering.
        '''
        for src in self.__graph:
            self.__table[src] = []
            for (dest, char) in self.__graph.transitions(src):
                self.__table[src].append((char, dest, 
                                          self.__graph.terminal(dest)))
            for dest in sorted(self.__graph.empty_transitions(src), reverse=True):
                self.__table[src].append((None, dest, 
                                          self.__graph.terminal(dest)))
    
    def matcher(self, stream):
        '''
        Create a matcher from the table.
        '''
        self._debug(str(self.__table))
        stack = deque()
        stack.append((deque(self.__table[0]), [], stream))
        while stack:
            self._debug(str(stack))
            (transitions, match, stream) = stack[-1]
            if not transitions:
                self._debug('Discard empty transitions')
                # if we have no more transitions, drop
                stack.pop()
            else:
                self._debug(transitions)
                (char, dest, label) = transitions.popleft()
                if char is None:
                    # empty edge
                    stack.append((deque(self.__table[dest]), match, stream))
                    if label: 
                        yield (label, self.__alphabet.join(self.__alphabet.join(match)), stream)
                else:
                    if stream and stream[0] in char:
                        self._debug('Test for {0} in {1}'.format(stream[0], char))
                        match = list(match)
                        match.append(stream[0])
                        stream = stream[1:]
                        stack.append((deque(self.__table[dest]), match, stream))
                        # this never happens?
                        if label:
                            yield (label, self.__alphabet.join(match), stream)


class DfaCompiler(LogMixin):
    
    def __init__(self, graph, alphabet):
        self.__nfa = graph
        self.__alphabet = alphabet
        self.__dfa = Graph()
    