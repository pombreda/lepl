#LICENCE

'''
An engine with a simple compiled transition table that does not support 
groups or stateful loops (so state is simply the current offset in the table
plus the earliest start index and a matched flag).
'''

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.support import UnsupportedOperation, _LOOP_UNROLL
from lepl.rxpy.engine.support import Match, Fail, Groups
from lepl.rxpy.graph.base_compilable import compile
from lepl.stream.core import s_next, s_empty, s_stream, s_len


class SimpleEngine(BaseMatchEngine):
    
    REQUIRE = _LOOP_UNROLL
    
    def __init__(self, parser_state, graph):
        super(SimpleEngine, self).__init__(parser_state, graph)
        self._program = compile(graph, self)
        self.__stack = []
        
    def push(self):
        # group_defined purposefully excluded
        self.__stack.append((self._offset, self._excess, self._stream,
                             self._search, self._current, self._previous,
                             self._states, self._group_start,
                             self._checkpoints, self._lookaheads))
        
    def pop(self):
        # group_defined purposefully excluded
        (self._offset, self._excess, self._stream, self._search,
         self._current, self._previous, self._states, 
         self._group_start, self._checkpoints, 
         self._lookaheads) = self.__stack.pop()
        
    def _advance(self, delta=1):
        '''
        Move forwards in the stream.

        The following conventions are followed:
        - `offset` is the offset from the initial input
        - `stream` is the stream starting at the current location
        - `current` is the character at the current location
        - `previous` is the character just before the current location
        '''
        self._offset += delta
        old_stream = self._stream
        try:
            (advanced, self._stream) = s_next(old_stream, delta)
            if advanced:
                self._previous = advanced[-1:]
            try:
                (self._current, _) = s_next(self._stream)
            except StopIteration:
                self._current = None
        except StopIteration:
            if old_stream:
                self._excess = delta - s_len(old_stream)
            else:
                self._excess += delta
            self._stream = None
            self._current = None

    def run(self, stream, pos=0, search=False):

        self._initial_stream = stream

        # TODO - add explicit search if expression starts with constant
        
        self._group_defined = False
        result = self._run_from(0, stream, pos, search)
        if self._group_defined:
            raise UnsupportedOperation('groups')
        else:
            return result
        
    def _run_from(self, start_index, stream, delta, search):
        self._previous = None
        self._offset = 0
        self._excess = 0
        self._stream = stream
        self._advance(delta)
        self._search = search
        self._checkpoints = {}
        self._lookaheads = (self._offset, {})
        search = self._search # read only, dereference optimisation

        # states are ordered by group start, which explains a lot of
        # the otherwise rather opaque logic below.
        self._states = [(start_index, self._offset, 0)]
        
        try:
            # TODO - looks like we may not need excess
            while self._states and not self._excess:

                known_next = set()
                next_states = []

                while self._states:

                    # unpack state
                    (index, self._group_start, skip) = self._states.pop()
                    try:

                        if not skip:
                            # process the current character
                            index = self._program[index]()
                            if index not in known_next:
                                next_states.append((index, self._group_start, 0))
                                known_next.add(index)

                        elif skip == -1:
                            raise Match

                        else:
                            skip -= 1

                            # if we have other states, or will add them via search
                            if search or next_states or self._states:
                                next_states.append((index, self._group_start, skip))
                                # block this same "future state"
                                known_next.add((index, skip))

                            # otherwise, we can jump directly
                            else:
                                self._advance(skip)
                                next_states.append((index, self._group_start, 0))

                    except Fail:
                        pass

                    except Match:
                        # no groups starting earlier?
                        if not next_states:
                            raise
                        # some other, pending, earlier starting, state may
                        # still give a match
                        next_states.append((index, self._group_start, -1))
                        known_next.add(index)
                        # but we can discard anything that starts later
                        self._states = []
                        search = False

                # move to next character
                self._advance()
                self._states = next_states

                # add current position as search if necessary
                if search and start_index not in known_next:
                    self._states.append((start_index, self._offset, 0))

                self._states.reverse()

            # pick first matched state, if any
            while self._states:
                (index, self._group_start, skip) = self._states.pop()
                if skip == -1:
                    raise Match

            # exhausted states with no match
            return Groups()

        except Match:
            groups = Groups(group_state=self._parser_state.groups,
                            stream=self._initial_stream)
            groups.start_group(0, self._group_start)
            groups.end_group(0, self._offset - self._excess)
            return groups

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
                    self._states.append((next, self._group_start, length))
            except StopIteration:
                pass
            raise Fail

    def character(self, charset):
        if self._current is not None and self._current in charset:
            return True
        else:
            raise Fail

    #noinspection PyUnusedLocal
    def start_group(self, number):
        return False

    #noinspection PyUnusedLocal
    def end_group(self, number):
        self._group_defined = True
        return False
    
    def match(self):
        raise Match

    def no_match(self):
        raise Fail

    def dot(self, multiline):
        if self._current and (multiline or self._current != '\n'):
            return True
        else:
            raise Fail
    
    def start_of_line(self, multiline):
        if self._offset == 0 or (multiline and self._previous == '\n'):
            return False
        else:
            raise Fail
    
    def end_of_line(self, multiline):
        current_str = self._parser_state.alphabet.letter_to_str(self._current)
        if multiline and current_str == '\\n':
            return False
        try:
            # at end of stream?
            (_, next) = s_next(self._stream)
            if current_str == '\\n': s_next(next)
        except StopIteration:
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
        # current here tests whether we have finished
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
        
    def checkpoint(self, id):
        if id not in self._checkpoints or self._offset != self._checkpoints[id]:
            self._checkpoints[id] = self._offset
            return False
        else:
            raise Fail
        
    # branch

    #noinspection PyUnusedLocal
    def group_reference(self, next, number):
        raise UnsupportedOperation('group_reference')

    #noinspection PyUnusedLocal
    def conditional(self, next, number):
        raise UnsupportedOperation('conditional')

    def split(self, next):
        for index in reversed(next):
            self._states.append((index, self._group_start, False))
        # start from new states
        raise Fail

    def lookahead(self, next, equal, forwards, mutates, reads, length):

        # discard old values
        if self._lookaheads[0] != self._offset:
            self._lookaheads = (self._offset, {})
        lookaheads = self._lookaheads[1]

        if next[1] not in lookaheads:

            # requires complex engine
            if reads:
                raise UnsupportedOperation('lookahead')
            size = None if (reads and mutates) else length(None)

            # invoke simple engine and cache
            self.push()
            try:
                if forwards:
                    stream = self._initial_stream
                    pos = self._offset
                    search = False
                else:
                    (text, _) = s_next(self._initial_stream, self._offset)
                    stream = s_stream(self._initial_stream, text)
                    if size is None:
                        pos = 0
                        search = True
                    else:
                        pos = self._offset - size
                        search = False
                result = bool(self._run_from(next[1], stream, pos, search)) == equal
            finally:
                self.pop()
            lookaheads[next[1]] = result

        if lookaheads[next[1]]:
            return next[0]
        else:
            raise Fail

    #noinspection PyUnusedLocal
    def repeat(self, next, begin, end, lazy):
        raise UnsupportedOperation('repeat')
