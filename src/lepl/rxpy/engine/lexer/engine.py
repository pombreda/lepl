#LICENCE

'''
An engine that is based on the simple engine but which assumes:
 - the pattern matched will be a series of alternative groups
 - no lookback
 - no search
Plus all the assumptions in the simple engine (eg, no group
references).

It then returns sufficient group information to indicate which
group matched.  This allows use within a lexer that has ordered tokens.

The state is (index, x) where x is skip if non-negative or the
last non-zero group matched.
'''

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.support import StreamTargetMixin, Match, Fail, Groups
from lepl.rxpy.graph.base_compilable import compile
from lepl.rxpy.support import UnsupportedOperation, _LOOP_UNROLL
from lepl.stream.core import s_next


class LexerEngine(StreamTargetMixin, BaseMatchEngine):

    REQUIRE = _LOOP_UNROLL

    def __init__(self, parser_state, graph):
        super(LexerEngine, self).__init__(parser_state, graph)
        self._program = compile(graph, self)

    def run(self, stream, pos=0, search=False):
        if pos or search:
            raise UnsupportedOperation('Search')
        self._initial_stream = stream
        self._reset(0, stream, None)
        self._checkpoints = {}
        self._last_group = None

        self._states = [(0, 0)]

        try:

            while self._states and self._excess < 2:

                known_next = set()
                next_states = []

                while self._states:

                    # unpack state
                    (index, skip) = self._states.pop()
                    try:

                        if not skip:
                            # process the current character
                            index = self._program[index]()
                            if index not in known_next:
                                next_states.append((index, 0))
                                known_next.add(index)

                        elif skip == -1:
                            raise Match

                        else:
                            skip -= 1

                            # if we have other states
                            if next_states or self._states:
                                if (index, skip) not in known_next:
                                    next_states.append((index, skip))
                                    known_next.add((index, skip))

                            # otherwise, we can jump directly
                            else:
                                self._advance(skip)
                                next_states.append((index, 0))

                    except Fail:
                        pass

                    except Match:
                        # no groups starting earlier?
                        if not next_states:
                            raise
                        # some other, pending, earlier starting, state may
                        # still give a match
                        if index not in known_next:
                            next_states.append((index, self._last_group))
                            known_next.add(index)
                        # but we can discard anything that starts later
                        self._states = []

                # move to next character
                self._advance()
                self._states = next_states
                self._states.reverse()

            # pick first matched state, if any
            while self._states:
                (index, skip) = self._states.pop()
                if skip < 0:
                    raise Match

            # exhausted states with no match
            return Groups()

        except Match:
            groups = Groups(group_state=self._parser_state.groups,
                            stream=self._initial_stream)
            groups.start_group(0, 0)
            groups.end_group(0, self._offset)
            groups.start_group(-skip, 0)
            groups.end_group(-skip, self._offset)
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
                    self._states.append((next, length))
            except StopIteration:
                pass
        raise Fail

    #noinspection PyUnusedLocal
    def start_group(self, number):
        return False

    #noinspection PyUnusedLocal
    def end_group(self, number):
        if number:
            self._last_group = -number
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
            self._states.append((index, 0))
        # start from new states
        raise Fail

    def lookahead(self, next, equal, forwards, mutates, reads, length):
        raise UnsupportedOperation('lookahead')

    #noinspection PyUnusedLocal
    def repeat(self, next, begin, end, lazy):
        raise UnsupportedOperation('repeat')
