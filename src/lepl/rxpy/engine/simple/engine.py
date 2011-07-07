#LICENCE

'''
An engine with a simple compiled transition table that does not support 
groups or stateful loops (so state is the current offset in the table,
the start index, and a skip/matched flag).
'''

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.support import UnsupportedOperation, _LOOP_UNROLL
from lepl.rxpy.engine.support import Match, Fail, Groups, StreamTargetMixin
from lepl.rxpy.graph.base_compilable import compile
from lepl.stream.core import s_next, s_stream


class SimpleEngine(StreamTargetMixin, BaseMatchEngine):
    
    REQUIRE = _LOOP_UNROLL
    
    def __init__(self, parser_state, graph):
        super(SimpleEngine, self).__init__(parser_state, graph)
        self._program = compile(graph, self)
        self.__stack = []
        
    def run(self, stream, pos=0, search=False, fail_on_groups=True):

        self._initial_stream = stream

        # TODO - add explicit search if expression starts with constant
        
        self.group_defined = False
        result = self._run_from(0, stream, pos, search)
        if self.group_defined and fail_on_groups:
            raise UnsupportedOperation('groups')
        else:
            return result
        
    def _run_from(self, start_index, stream, delta, search):
        self._reset(0, stream, None)
        self._advance(delta)
        self._search = search
        self._checkpoints = {}
        self._lookaheads = (self._offset, {})
        search = self._search # read only, dereference optimisation

        # states are ordered by group start, which explains a lot of
        # the otherwise rather opaque logic below.
        self._states = [(start_index, self._offset, 0)]
        
        try:

            while self._states and self._excess < 2:

                known_next = set()
                next_states = []

                while self._states:

                    # unpack state
                    (index, self._start, skip) = self._states.pop()
                    try:

                        if not skip:
                            # process the current character
                            index = self._program[index]()
                            if index not in known_next:
                                next_states.append((index, self._start, 0))
                                known_next.add(index)

                        elif skip == -1:
                            raise Match

                        else:
                            skip -= 1

                            # if we have other states, or will add them via search
                            if search or next_states or self._states:
                                if (index, skip) not in known_next:
                                    next_states.append((index, self._start, skip))
                                    known_next.add((index, skip))

                            # otherwise, we can jump directly
                            else:
                                self._advance(skip)
                                next_states.append((index, self._start, 0))

                    except Fail:
                        pass

                    except Match:
                        # no groups starting earlier?
                        if not next_states:
                            raise
                        # some other, pending, earlier starting, state may
                        # still give a match
                        next_states.append((index, self._start, -1))
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
                (index, self._start, skip) = self._states.pop()
                if skip == -1:
                    raise Match

            # exhausted states with no match
            return Groups()

        except Match:
            groups = Groups(group_state=self._parser_state.groups,
                            stream=self._initial_stream)
            groups.start_group(0, self._start)
            groups.end_group(0, self._offset)
            return groups

    def string(self, next, text):
        length = len(text)
        if length == 1:
            if self._current == text[0:1]:
                return True
        else:
            try:
                (advanced, _) = s_next(self._stream, length)
                if advanced == text:
                    self._states.append((next, self._start, length))
            except StopIteration:
                pass
        raise Fail

    #noinspection PyUnusedLocal
    def start_group(self, number):
        return False

    #noinspection PyUnusedLocal
    def end_group(self, number):
        self.group_defined = True
        return False
    
    def match(self):
        raise Match

    def no_match(self):
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
            self._states.append((index, self._start, 0))
        # start from new states
        raise Fail

    def _push(self):
        '''
        Save current state for lookahead.
        '''
        self.__stack.append((self._offset, self._excess, self._stream,
                             self._next_stream, self._current, self._previous,
                             self._states, self._start, self._search,
                             self._checkpoints, self._lookaheads))

    def _pop(self):
        '''
        Restore current state after lookahead.
        '''
        (self._offset, self._excess, self._stream, self._next_stream,
         self._current, self._previous, self._states, self._start,
         self._search, self._checkpoints, self._lookaheads) = self.__stack.pop()

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
            self._push()
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
                if pos >= 0:
                    result = bool(self._run_from(next[1], stream, pos, search)) == equal
                else:
                    result = not equal
            finally:
                self._pop()
            lookaheads[next[1]] = result

        if lookaheads[next[1]]:
            return next[0]
        else:
            raise Fail

    #noinspection PyUnusedLocal
    def repeat(self, next, begin, end, lazy):
        raise UnsupportedOperation('repeat')
