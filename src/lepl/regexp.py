
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
    value, making it easier to work with a variey of alphabets.
    
    The intervals are stored in a list, ordered by a, rewriting intervals as 
    necessary to ensure no overlap.
    '''
    
    def __init__(self, intervals, alphabet):
        self.__intervals = deque()
        for interval in intervals:
            self.__append(interval, alphabet)
        self.__intervals = list(self.__intervals)
        self.__str = alphabet.fmt_intervals(self.__intervals)
        self.__index = [interval[1] for interval in self.__intervals]
            
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
        
    # ------ the following methods co-operate with Sequence
        
    def complete(self):
        return False
    
    def incomplete(self):
        return True
    
    def reset(self):
        return self
    
    def transitions(self):
        yield (self, None)
        
    def options(self):
        return empty()
    

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
    

class Sequence(MutableNode):
    '''
    A sequence of Characters, etc.  This includes an index, which is internal 
    state that describes progression through the sequence.
    
    Note that a Sequence instance is static - index does not change - but it
    may be cloned with a different index value.
    '''
    
    def __init__(self, children, alphabet, index=0, fresh=True):
#        print(type(self), children)
        super(Sequence, self).__init__(children)
        self._index = index
        self._fresh = fresh
        self.alphabet = alphabet
        self.__str = self._build_str()
        
    def _build_str(self):
        return self.alphabet.fmt_sequence(self._children)
        
    def clone(self, index):
        return type(self)(self.children(), self.alphabet, index, False)
        
    def reset(self):
        return type(self)([child.reset() for child in self._children], 
                          self.alphabet, 0, True)
    
    def __str__(self):
        return self.__str
    
    def __repr__(self):
        contents = deque()
        for i in range(len(self)):
            if i == self._index: contents.append('{')
            contents.append(repr(self[i]))
            if i == self._index: contents.append('}')
        return '<{0}>({1})'.format(self._name(), ''.join(contents))
    
    def _name(self):
        return type(self).__name__
    
    def complete(self):
        '''
        Has reached a possible final match?
        '''
        complete = True
        index = self._index
        while index < len(self):
            complete = complete and self[index].complete()
            index += 1
        return complete
    
    def incomplete(self):
        '''
        More transitions available?
        '''
        return self._index + 1 < len(self) or \
              self._index + 1 == len(self) and self[self._index].incomplete()
    
    def transitions(self):
        '''
        Generate all possible transitions.  A transition a
        (Character, _Sequence) pair, which describes the possible characters
        and a sequence with an updated internal index.
        
        The algorithm here is generic; attempting to forward the responsibilty
        of generating transitions to the (embedded) sequence at the current
        index and, if that fails, calling the _next() method.
        '''
        if self._index < len(self):
            for (char, seq) in self[self._index].transitions():
                if seq and seq.incomplete():
                    # a sub-sequence has been returned, so we need to clone
                    # ourselves and then replace the old sequence with the
                    # new one.
                    clone = self.clone(self._index)
                    clone[self._index] = seq
                    # that sequence may have options, but they will be returned
                    # via the same call above
                else:
                    # we have a transition from a character, or a sequence that
                    # is now complete.  in either case we need to move on to
                    # the next child.
                    clone = self.next()
                    # we should also check to see if we have progressed to an
                    # option (ie that the next state, the one we would 
                    # transition to with char, and which will match the 
                    # character after char, is an option).  if so, we must 
                    # allow the possibility of jumping ahead.
                    for option in clone.options():
                        yield (char, option)
                yield (char, clone)
    
    def options(self):
        index = self._index
        while index + 1 < len(self) and isinstance(self[index], Option):
            yield self.clone(index + 1)
            index += 1
            
    def next(self):
        return self.clone(self._index+1)
    
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
    

class Option(Sequence):
    '''
    An optional sequence of Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_option(self._children)
    
    def complete(self):
        return True
        
    
class Repeat(Option):
    '''
    A sequence of Characters (or sequences) that can repeat 0 or more times.
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_repeat(self._children)

    def clone(self, index):
        if index < len(self):
            return super(Repeat, self).clone(index)
        else:
            return self.reset()
        
    def complete(self):
        return self._fresh
    
    def incomplete(self):
        return True
    
    
class Choice(Sequence):
    '''
    A set of alternative Characters (or sequences).
    '''
    
    def _build_str(self):
        return self.alphabet.fmt_choice(self._children)
            
    def transitions(self):
        '''
        Either generate all choices, or do normal sequential processing of
        current choice.
        '''
        if self._fresh:
            for index in range(len(self)):
                for (char, seq) in self[index].transitions():
                    if seq:
                        clone = self.clone(index)
                        clone[index] = seq
                    else:
                        clone = self.next()
                    yield (char, clone)
                    for option in clone.options():
                        yield (char, option)
        else:
            for (char, seq) in super(Choice, self).transitions():
                yield (char, seq)
                
    def incomplete(self):
        return self._index < len(self) and self[self._index].incomplete() 
                
    def next(self):
        return self.clone(len(self))
    
        
class Regexp(Sequence):
    '''
    A labelled sequence of Characters and Repeats.
    '''
    
    def __init__(self, label, children, alphabet, index=0):
        super(Regexp, self).__init__(children, alphabet, index)
        self.label = label

    def clone(self, index):
        return type(self)(self.label, self.children(), self.alphabet, index)

    def _name(self):
        return type(self).__name__ + ' ' + str(self.label)
    
       
class State(LogMixin):
    '''
    A single node in a FSM.  This is used to construct the FSM, but plays no
    part in the final matching (which is done via a simple table).
    
    A state provides a list of transitions which describe how to get to
    neighbouring states.  Duplicate instances (with the same internal
    state) will hash and equate identically.
    '''
    
    def __init__(self, regexps, alphabet):
        super(State, self).__init__()
        self.__regexps = frozenset(regexps)
        self.__alphabet = alphabet
        
    def transitions(self):
        '''
        A sequence of (Character, State) pairs.
        '''
        fragments = self.__split(list(self.__raw_transitions()))
        joined = self.__join(fragments)
        self._debug('Transitions from ' + repr(self))
        for regexps in joined:
            char = Character(joined[regexps], self.__alphabet)
            state = State(regexps, self.__alphabet)
            self._debug(repr(char) + ' -> ' + repr(state))
            yield (char, state)
        
    def __raw_transitions(self):
        for regexp in self.__regexps:
            if regexp.incomplete():
                for (char, regexp) in regexp.transitions():
                    self._debug('Raw: ' + repr(char) + ' -> ' + repr(regexp))
                    yield (char, regexp)
                    
    def __split(self, raw):
        '''
        Generate a set of mutually exclusive character ranges so that we can
        divide the transitions cleanly.
        '''
        fragments = {} # from char range to regexps
        for (fa, fb) in _Fragments((chars for (chars, _seq) in raw), 
                                   self.__alphabet):
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
        
    def __repr__(self):
        return '<State>({0}) {1}'.format(','.join(repr(regexp) 
                                                  for regexp in self.__regexps),
                                         list(self.terminals()))
                                        
        

class Fsm(LogMixin):
    '''
    Given a set of regular expressions, this compiles the state machine and
    provides the transition table to sub-classes.  To use this in a subclass
    simply start at state 0 and iterate over the input data, supplying each
    value to self._transition[state] to get the next state (state is None 
    when no further transitions are available).
    
    For any state, self._terminals[state] lists the labels that may terminate.
    '''
    
    def __init__(self, regexps, alphabet):
        super(Fsm, self).__init__()
        self.__alphabet = alphabet
        self._terminals = []
        self._transitions = []
        index = self.__expand(regexps)
        self.__compile(index)

    def __expand(self, regexps):
        '''
        Expand the entire set of states, noting all transitions and terminals.
        '''
        known = set()
        state_to_index = {}
        stack = deque()
        stack.append(State(regexps, self.__alphabet))
        while stack:
            state = stack.pop()
            if state not in known:
                index = len(known)
                state_to_index[state] = index
                known.add(state)
                self._terminals.append(list(state.terminals()))
                transitions = list(state.transitions())
                self._transitions.append(transitions)
                for (char, state) in transitions:
#                    self._debug('Raw: ' + repr(char) + ' -> ' + repr(state))
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
        for start in range(len(self._transitions)):
            # construct a list of (a, b, index) triples, where a and b are the
            # usual interval values (a < c <= b)
            triples = []
            for (chars, state) in self._transitions[start]:
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
                    if a <= c <= b:
                        return end
                return None
            self._transitions[start] = lookup
            

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


class SimpleFsm(Fsm):
    '''
    A simple implementation of the matcher, mainly for testing.
    '''
    
    def __init__(self, regexps, alphabet):
        super(SimpleFsm, self).__init__(regexps, alphabet)
            
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
        transitions = self._transitions
        terminals = self._terminals
        while state is not None:
            for label in terminals[state]:
#                self._debug('terminal ' + str(label))
                yield (label, result)
            char = next(characters)
            result.append(char)
            state2 = transitions[state](char)
            self._debug(str(state) + '/' + char + ' -> ' + str(state2))
            state = state2
    
    def all_for_string(self, string):
        '''
        A simplified but less efficient interface.  Yields values in 
        increasing size.
        '''
        for (label, result) in self.generator(iter(string)):
            yield (label, ''.join(result))
