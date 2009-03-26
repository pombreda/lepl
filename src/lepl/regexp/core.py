
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
supported) and generates a finite state machines that can match them against
a stream of values.

Although simple (and slow compared to a C version), it has some advantages 
from being implemented in Python.

First, it can use a variety of alphabets - it is not restricted to strings.  
It could, for example, match lists of integers, or sequences of tokens.

Second, the NFA implementation can yield intermediate matches.

Third, it is extensible.
'''

from abc import ABCMeta, abstractmethod
from bisect import bisect_left, bisect_right
from itertools import chain
from collections import deque
from operator import itemgetter
from traceback import format_exc

from lepl.matchers import *
from lepl.node import *
from lepl.trace import TraceResults
from lepl.support import empty


class Alphabet(metaclass=ABCMeta):
    '''
    Regular expressions are generalised over alphabets, which describe the set
    of acceptable characters.
    
    The characters in an alphabet must have an order, which is defined by 
    `__lt__` on the character instances themselves (equality and inequality 
    are also assumed to be defined).  In addition, `before(c)` and `after(c)` 
    below should give the previous and subsequent characters in the ordering 
    and `min` and `max` should give the two most extreme characters.
    
    Internally, within the routines here, ranges of characters are used.
    These are encoded as pairs of values `(a, b)` which are inclusive.  
    Each pair is called an "interval".
    
    Alphabets include additional methods used for display and may also have
    methods specific to a given instance (typically named with an initial
    underscore).
    '''
    
    def __init__(self, min, max):
        self.__min = min
        self.__max = max
    
    @property
    def min(self):
        '''
        The "smallest" character.
        '''
        return self.__min

    @property
    def max(self):
        '''
        The "largest" character.
        '''
        return self.__max
    
    @abstractmethod
    def before(self, c): 
        '''
        Must return the character before c in the alphabet.  Never called with
        min (assuming input data are in range).
        ''' 

    @abstractmethod
    def after(self, c): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
    
    @abstractmethod
    def fmt_intervals(self, intervals):
        '''
        This must fully describe the data in the intervals (it is used to
        hash the data).
        '''
    
    def invert(self, intervals):
        '''
        Return a list of intervals that describes the complement of the given
        interval.  Note - the input interval must be ordered (and the result
        will be ordered too).
        '''
        if not intervals:
            return [(self.min, self.max)]
        inverted = []
        (a, last) = intervals[0]
        if a != self.min:
            inverted.append((self.min, self.before(a)))
        for (a, b) in intervals[1:]:
            inverted.append((self.after(last), self.before(a)))
            last = b
        if last != self.max:
            inverted.append((self.after(last), self.max))
        return inverted

    @abstractmethod
    def fmt_sequence(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
    
    @abstractmethod
    def fmt_repeat(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''

    @abstractmethod
    def fmt_choice(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''

    @abstractmethod
    def fmt_option(self, children):
        '''
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        
    @abstractmethod
    def join(self, chars):
        '''
        Join a list of characters into a string (or the equivalent).
        '''


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
    of ranges.  Used internally to combine transitions.
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
            self.__append(interval, character.alphabet)
        
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
        graph.terminate(final, [self.label])
        

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
        
        
class BaseGraph(LogMixin):
    '''
    Describes a collection of connected nodes.
    '''
    
    def __init__(self, alphabet):
        super(BaseGraph, self).__init__()
        self._alphabet = alphabet
        self._next_node = 0
        self._transitions = {} # map from source to (dest, edge)
        self._terminals = {} # node to label
    
    def terminate(self, node, labels):
        assert node < self._next_node
        if node not in self._terminals:
            self._terminals[node] = set()
        self._terminals[node].update(labels)
    
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
        if src not in self._transitions:
            self._transitions[src] = []
        self._transitions[src].append((dest, edge))
            
    def __iter__(self):
        '''
        An iterator over all nodes.
        '''
        return iter(range(self._next_node))
    
    def transitions(self, src):
        '''
        An iterator over all non-empty transitions from src - returns
        (dest, edge) pairs.
        '''
        return iter(self._transitions.get(src, []))
    
    def terminals(self, node):
        '''
        An iterator over the terminals for the give node.
        '''
        return iter(self._terminals.get(node, []))


class NfaGraph(BaseGraph):
    '''
    Describes a NFA with epsilon (empty) transitions.
    '''
    
    def __init__(self, alphabet):
        super(NfaGraph, self).__init__(alphabet)
        self._empty_transitions = {} # map from source to set(dest)
    
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
    
    def connected(self, nodes):
        '''
        Return all nodes connected to the given node.
        '''
        connected = set()
        stack = deque(nodes)
        while stack:
            src = stack.pop()
            connected.add(src)
            for dest in self.empty_transitions(src):
                if dest not in connected:
                    connected.add(dest)
                    stack.append(dest)
        return (frozenset(connected), 
                chain(*[self.terminals(node) for node in connected]))
    
    def terminal(self, node):
        '''
        The NFA graph has single terminal.
        '''
        terminals = list(self.terminals(node))
        if terminals:
            assert len(terminals) == 1, 'Multiple terminals in NFA'
            return terminals[0]
        else:
            return None
        
    def __str__(self):
        lines = []
        for node in self:
            edges = []
            for (dest, edge) in self.transitions(node):
                edges.append('{0}:{1}'.format(edge, dest))
            for dest in self.empty_transitions(node):
                edges.append(str(dest))
            label = '' if self.terminal(node) is None else (' ' + self.terminal(node))
            lines.append('{0}{1} {2}'.format(node, label, ';'.join(edges)))
        return ', '.join(lines)


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


class DfaGraph(BaseGraph):
    '''
    Describes a DFA where each node is a collection of NFA nodes.
    '''
    
    def __init__(self, alphabet):
        super(DfaGraph, self).__init__(alphabet)
        self._dfa_to_nfa = {} # map from dfa node to set(nfa nodes)
        self._nfa_to_dfa = {} # map from set(nfa nodes) to dfa nodes
        
    def node(self, nfa_nodes):
        '''
        Add a node, defined as a set of nfa nodes.  If the set already exists,
        (False, old node) is returned, with the existing DFA node.
        Otherwise (True, new node) is returned.
        '''
        new = nfa_nodes not in self._nfa_to_dfa
        if new:
            dfa_node = self.new_node()
            self._nfa_to_dfa[nfa_nodes] = dfa_node
            self._dfa_to_nfa[dfa_node] = nfa_nodes
        return (new, self._nfa_to_dfa[nfa_nodes])
    
    def nfa_nodes(self, node):
        '''
        An iterator over NFA nodes associated with the given DFA node.
        '''
        return iter(self._dfa_to_nfa[node]) 
    
    def __str__(self):
        lines = []
        for node in self:
            edges = []
            for (dest, edge) in self.transitions(node):
                edges.append('{0}:{1}'.format(edge, dest))
            nodes = [n for n in self.nfa_nodes(node)]
            edges = ' ' + ';'.join(edges) if edges else ''
            labels = list(self.terminals(node))
            labels = ' ' + '/'.join(str(label) for label in labels) if labels else ''
            lines.append('{0} {1}{2}{3}'.format(node, nodes, edges, labels))
        return ', '.join(lines)


class NfaToDfa(LogMixin):
    '''
    Convert a NFA graph to a DFA graph (uses the usual superset approach but
    does combination of states in a way that seems to fit better with the idea 
    of character ranges).
    '''
    
    def __init__(self, nfa, alphabet):
        super(NfaToDfa, self).__init__()
        self.__nfa = nfa
        self.__alphabet = alphabet
        self.dfa = DfaGraph(alphabet)
        self.__build_graph()
    
    def __build_graph(self):
        stack = deque() # (dfa node, set(nfa nodes), set(terminals))
        # start with initial node
        (nfa_nodes, terminals) = self.__nfa.connected([0])
        (_, src) = self.dfa.node(nfa_nodes)
        stack.append((src, nfa_nodes, terminals))
        # continue until all states covered
        while stack:
            (src, nfa_nodes, terminals) = stack.pop()
            self.dfa.terminate(src, terminals)
            fragments = self.__fragment_transitions(nfa_nodes)
            groups = self.__group_fragments(nfa_nodes, fragments)
            self.__add_groups(src, groups, stack)
    
    def __fragment_transitions(self, nfa_nodes):
        '''
        From the given nodes we can accumulate all the transitions.  These
        are associated with character matches (edges).  We separate the
        character matches into non-overlapping fragments.
        '''
        fragments = Fragments(self.__alphabet)
        for nfa_node in nfa_nodes:
            for (_dest, edge) in self.__nfa.transitions(nfa_node):
                fragments.append(edge)
        return fragments
    
    def __group_fragments(self, nfa_nodes, fragments):
        '''
        It's possible that more than one fragment will lead to the same
        set of target nodes.  So we group fragments (intervals) by target
        nodes.  Each group will be a dfa node.  At the same time we can
        accumulate terminals.
        '''
        groups = {} # map from set(nfa nodes) to ([intervals], set(terminals))
        # this doesn't look very efficient
        for interval in fragments:
            nodes = set()
            terminals = set()
            for nfa_node in nfa_nodes:
                for (dest, edge) in self.__nfa.transitions(nfa_node):
                    if interval[0] in edge:
                        (nodes_, terminals_) = self.__nfa.connected([dest])
                        nodes.update(nodes_)
                        terminals.update(terminals_)
            nodes = frozenset(nodes)
            if nodes not in groups:
                groups[nodes] = ([], set())
            groups[nodes][0].append(interval)
            groups[nodes][1].update(terminals)
        return groups

    def __add_groups(self, src, groups, stack):
        '''
        The target nfa nodes identified above are now used to create dfa
        nodes. 
        '''
        for nfa_nodes in groups:
            (intervals, terminals) = groups[nfa_nodes]
            char = Character(intervals, self.__alphabet)
            (new, dest) = self.dfa.node(nfa_nodes)
            self._debug('new: {0}, nodes:{1}'.format(new, nfa_nodes))
            self.dfa.connect(src, dest, char)
            if new:
                stack.append((dest, nfa_nodes, terminals))
    