
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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

 * It can use a variety of alphabets - it is not restricted to strings.  
   It could, for example, match lists of integers, or sequences of tokens.

 * The NFA implementation can yield intermediate matches.

 * It is extensible.

The classes here form a layered series of representations for regular 
expressions.

The first layer contains the classes `Sequence`, `Option`, `Repeat`, `Choice`,
`Labelled` and `Regexp`.  These are a high level representation that will
typically be constructed by an alphabet-specific parser.

The second layer encodes the regular expression as a non-deterministic 
finite automaton (NFA) with empty transitions.  This is a "natural" 
representation of the transitions that can be generated by the first layer.

The third layer encodes the regular expression as a deterministic finite
automaton (DFA).  This is a more "machine friendly" representation that allows 
for more efficient matching.  It is generated by transforming a representation
from the second layer.
'''

from abc import ABCMeta, abstractmethod
from collections import deque
from itertools import chain
from logging import getLogger
from traceback import format_exc

from lepl.node import Node
from lepl.regexp.interval import Character, TaggedFragments, IntervalMap
from lepl.support import LogMixin


# pylint: disable-msg=C0103
# Python 2.6
#class Alphabet(metaclass=ABCMeta):
_Alphabet = ABCMeta('_Alphabet', (object, ), {})


# pylint: disable-msg=E1002
# pylint can't find ABCs
class Alphabet(_Alphabet):

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
    
    def __init__(self, min_, max_):
        self.__min = min_
        self.__max = max_
        super(Alphabet, self).__init__()
    
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
        
    @abstractmethod
    def parse(self, regexp):
        '''
        Generate a Sequence from the given regexp text.
        '''


class Sequence(Node):
    '''
    A sequence of Characters, etc.
    '''
    
    def __init__(self, children, alphabet):
        # pylint: disable-msg=W0142
        super(Sequence, self).__init__(*children)
        self.alphabet = alphabet
        self.state = None
        self.__str = self._build_str()
        
    def _build_str(self):
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_sequence(self)
        
    def __str__(self):
        return self.__str
    
    def __hash__(self):
        return hash(self.__str)
        
    def build(self, graph, before, after):
        '''
        Connect in sequence.
        '''
        if self:
            src = before
            last = self[-1]
            for child in self:
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
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_option(self)
    
    def build(self, graph, before, after):
        '''
        Connect as sequence and also directly from start to end
        '''
        super(Option, self).build(graph, before, after)
        graph.connect(before, after)
    

class Empty(Sequence):
    '''
    Matches an empty sequence.
    '''
    
    def __init__(self, alphabet):
        super(Empty, self).__init__([], alphabet)
    
    def _build_str(self):
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_sequence([])
    
    def build(self, graph, before, after):
        '''
        Connect directly from start to end.
        '''
        graph.connect(before, after)
    

class Repeat(Sequence):
    '''
    A sequence of Characters (or sequences) that can repeat 0 or more times.
    '''
    
    def _build_str(self):
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_repeat(self)            
    
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
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_choice(self)
    
    def build(self, graph, before, after):
        '''
        Connect in parallel from start to end, but add extra nodes so that
        the sequence is tried in order (because evaluation tries empty
        transitions last).
        '''
        if self:
            last = self[-1]
        for child in self:
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
        
    def build(self, graph, before, _after=None):
        '''
        A sequence, but with an extra final empty transition to force
        any loops before termination.
        '''
        assert not _after
        after = graph.new_node()
        final = graph.new_node()
        super(Labelled, self).build(graph, before, after)
        graph.connect(after, final)
        graph.terminate(final, [self.label])
        

class RegexpError(Exception):
    '''
    An error associated with (problems in) the regexp implementation.
    '''
    pass


class Regexp(Choice):
    '''
    A collection of Labelled instances.
    '''
    
    def __init__(self, children, alphabet):
        for child in children:
            assert isinstance(child, Labelled)
        super(Regexp, self).__init__(children, alphabet)
        
    def _build_str(self):
        '''
        Construct a string representation of self.
        '''
        return self.alphabet.fmt_sequence(self)

    def build(self, graph, _before=None, _after=None):
        '''
        Each Labelled is an independent sequence.  We use empty transitions 
        to order the choices.
        '''
        assert not _before
        assert not _after
        if self:
            before = graph.new_node()
            last = self[-1]
            src = before
            for child in self:
                child.build(graph, src)
                if child is not last:
                    src = graph.new_node()
                    graph.connect(before, src)
                    
    def nfa(self):
        '''
        Generate a NFA-based matcher.
        '''
        graph = NfaGraph(self.alphabet)
        self.build(graph)
        return NfaCompiler(graph, self.alphabet)
        
    def dfa(self):
        '''
        Generate a DFA-based matcher (faster than NFA, but returns only a
        single, greedy match).
        '''
        ngraph = NfaGraph(self.alphabet)
        self.build(ngraph)
        dgraph = NfaToDfa(ngraph, self.alphabet).dfa
        return DfaCompiler(dgraph, self.alphabet)
    
    @staticmethod
    def _coerce(regexp, alphabet):
        '''
        Coerce to a regexp.
        '''
        if isinstance(regexp, str):
            coerced = alphabet.parse(regexp)
            if not coerced:
                raise RegexpError('Cannot parse regexp {0!r} using {1}'
                                  .format(regexp, alphabet))
        else:
            coerced = [regexp]
        return coerced
        
    
    @staticmethod
    def single(alphabet, regexp, label='label'):
        '''
        Generate an instance for a single expression or sequence.
        '''
        return Regexp([Labelled(label, Regexp._coerce(regexp, alphabet), 
                                alphabet)], alphabet)
    
    @staticmethod
    def multiple(alphabet, regexps):
        '''
        Generate an instance for several expressions.
        '''
        return Regexp([Labelled(label,  Regexp._coerce(regexp, alphabet), 
                                alphabet) for (label, regexp) in regexps], 
                      alphabet)
        

        
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
        '''
        Indicate that the node terminates with the given labels.
        '''
        assert node < self._next_node
        if node not in self._terminals:
            self._terminals[node] = set()
        self._terminals[node].update(labels)
    
    def new_node(self):
        '''
        Get a new node.
        '''
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
    
    def __len__(self):
        return self._next_node


class NfaGraph(BaseGraph):
    '''
    Describes a NFA with epsilon (empty) transitions.
    '''
    
    def __init__(self, alphabet):
        super(NfaGraph, self).__init__(alphabet)
        self._empty_transitions = {} # map from source to set(dest)
    
    def new_node(self):
        '''
        Get a new (unconnected) node.
        '''
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
            label = '' if self.terminal(node) is None \
                       else (' ' + self.terminal(node))
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
            # construct an interval map of possible destinations and terminals
            # given a character
            fragments = TaggedFragments(self.__alphabet)
            for (dest, char) in self.__graph.transitions(src):
                fragments.append(char, (dest, self.__graph.terminal(dest)))
            map_ = IntervalMap()
            for (interval, dts) in fragments:
                map_[interval] = dts
            # collect empty transitions
            empties = [(dest, self.__graph.terminal(dest))
                       # ordering here is reverse of what is required, which
                       # is ok because we use empties[-1] below
                       for dest in sorted(self.__graph.empty_transitions(src))]
            self.__table[src] = (map_, empties)
    
    def match(self, stream):
        '''
        Create a matcher from the table.
        
        The stack holds the current state, which is consumed from left to
        right.  The state is:
        
          - map_ - a map from character to [(dest state, terminals)]

          - matched - the [(dest state, terminals)] generated by the map for
            a given character

          - empties - empty transitions for this state

          - match - the current match, as a list of tokens consumed from the stream

          - stream - the current stream

        map_ and matched are not both necessary (they are exclusive), but it 
        simplifies the algorithm to separate them.
        '''
        self._debug(str(self.__table))
        stack = deque()
        (map_, empties) = self.__table[0]
        stack.append((map_, None, empties, [], stream))
        while stack:
            #self._debug(str(stack))
            (map_, matched, empties, match, stream) = stack.pop()
            if not map_ and not matched and not empties:
                # if we have no more transitions, drop
                pass
            elif map_:
                # re-add empties with old match
                stack.append((None, [], empties, match, stream))
                # and try matching a character
                if stream:
                    matched = map_[stream[0]]
                    if matched:
                        stack.append((None, matched, None,
                                      match + [stream[0]], stream[1:]))
            elif matched:
                (dest, terminal) = matched[-1]
                # add back reduced matched
                if len(matched) > 1: # avoid discard iteration
                    stack.append((map_, matched[:-1], empties, match, stream))
               # and expand this destination
                (map_, empties) = self.__table[dest]
                stack.append((map_, None, empties, match, stream))
                # this doesn't happen with current nfa
                if terminal:
                    yield (terminal, self.__alphabet.join(match), stream)
            else:
                # we must have an empty transition
                (dest, terminal) = empties[-1]
                # add back reduced empties
                if len(empties) > 1: # avoid discard iteration
                    stack.append((map_, matched, empties[:-1], match, stream))
                # and expand this destination
                (map_, empties) = self.__table[dest]
                stack.append((map_, None, empties, match, stream))
                if terminal:
                    yield (terminal, self.__alphabet.join(match), stream)


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
            labels = ' ' + '/'.join(str(label) for label in labels) \
                     if labels else ''
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
        '''
        This is the driver for the "usual" superset algorithm - we find
        all states that correspond to a DFA state, then look at transitions
        to other states.  This repeats until we have covered all the 
        different combinations of NFA states that could occur.
        '''
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
            groups = self.__group_fragments(fragments)
            self.__add_groups(src, groups, stack)
    
    def __fragment_transitions(self, nfa_nodes):
        '''
        From the given nodes we can accumulate the destination nodes and
        terminals associated with each transition (edge/character).
        At the same time we separate the character matches into non-overlapping 
        fragments.
        '''
        fragments = TaggedFragments(self.__alphabet)
        for nfa_node in nfa_nodes:
            for (dest, edge) in self.__nfa.transitions(nfa_node):
                (nodes, terminals) = self.__nfa.connected([dest])
                fragments.append(edge, (nodes, list(terminals)))
        return fragments
    
    def __group_fragments(self, fragments):
        '''
        For each fragment, we for the complete set of possible destinations
        and associated terminals.  Since it is possible that more than one 
        fragment will lead to the same set of target nodes we group all
        related fragments together.
        '''
        # map from set(nfa nodes) to (set(intervals), set(terminals))
        groups = {} 
        for (interval, nts) in fragments:
            if len(nts) > 1:
                # collect all nodes and terminals for fragment
                (nodes, terminals) = (set(), set()) 
                for (n, t) in nts:
                    nodes.update(n)
                    terminals.update(t)
                nodes = frozenset(nodes)
            else:
                (nodes, terminals) = nts[0]
            if nodes not in groups:
                groups[nodes] = (set(), set())
            groups[nodes][0].add(interval)
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
#            self._debug('new: {0}, nodes:{1}'.format(new, nfa_nodes))
            self.dfa.connect(src, dest, char)
            if new:
                stack.append((dest, nfa_nodes, terminals))


class DfaCompiler(object):
    '''
    Create a lookup table for a DFA and a matcher to evaluate it.
    '''
    
    def __init__(self, graph, alphabet):
        super(DfaCompiler, self).__init__()
        self.__graph = graph
        self.__alphabet = alphabet
        self.__table = [None] * len(graph)
        self.__empty_labels = list(graph.terminals(0))
        self.__build_table()
        
    def __build_table(self):
        '''
        Construct a transition table.
        '''
        for src in self.__graph:
            row = IntervalMap()
            for (dest, char) in self.__graph.transitions(src):
                labels = list(self.__graph.terminals(dest))
                for interval in char:
                    row[interval] = (dest, labels)
            self.__table[src] = row
            
    def match(self, stream_in):
        '''
        Match against the stream.
        '''
        try:
            (terminals, size, stream_out) = self.size_match(stream_in)
            return (terminals, stream_in[0:size], stream_out)
        except TypeError:
            getLogger('lepl.regexp.DfaCompiler.match').debug(format_exc())
            return None
        
    def size_match(self, stream):
        '''
        Match against the stream, but return the length of the match.
        '''
        state = 0
        size = 0
        longest = (self.__empty_labels, 0, stream) \
                    if self.__empty_labels else None
        while stream:
            future = self.__table[state][stream[0]]
            if future is None:
                break
            # update state
            (state, terminals) = future
            size += 1
            # it might be faster to use size as an index here  - it's a
            # trade-odd depending on line length.  probably worth measuring.
            stream = stream[1:]
            # match is strictly increasing, so storing the length is enough
            # (no need to make an expensive copy)
            if terminals:
                longest = (terminals, size, stream)
        return longest
    