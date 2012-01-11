#LICENCE

'''
This engine provides all functionality while staying as close to
Thompson's approach as possible (DFA incrementally constructed).

It can be used standalone, but is intended to be used as a fallback from
the simple engine, when that fails on an unsupported operation. 
'''


from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.complex.support import State
from lepl.rxpy.engine.support import Match, Fail, Groups, StreamTargetMixin
from lepl.rxpy.graph.base_compilable import compile
from lepl.stream.core import s_next, s_stream


class ComplexEngine(StreamTargetMixin, BaseMatchEngine):
    
    def __init__(self, parser_state, graph):
        super(ComplexEngine, self).__init__(parser_state, graph)
        self._program = compile(graph, self)
        self.__stack = []
        
    def run(self, stream, pos=0, search=False):
        self._initial_stream = stream
        return self._run_from(State(0, stream), stream, pos, search)
        
    def _run_from(self, start_state, stream, delta, search):
        start_state.start_group(0, delta)
        self._reset(0, stream, None)
        self._advance(delta)
        self._search = search
        self._lookaheads = (self._offset, {})
        self._states = [start_state.clone()]
        
        try:
            while self._states and self._excess < 2:
                
                known_next = set()
                next_states = []
                
                while self._states:
                    
                    self._state = self._states.pop()
                    state = self._state
                    skip = state.skip
                    
                    if not skip:
                        # advance a character (compiled actions re-call on stack
                        # until a character is consumed)
                        try:
                            state.advance(self._program[state.index]())
                            if state not in known_next:
                                next_states.append(state)
                                known_next.add(state)
                        except Fail:
                            pass
                        except Match:
                            state.skip = -1
                            if not next_states:
                                raise
                            next_states.append(state)
                            known_next.add(state)
                            
                    elif skip == -1:
                        if not next_states:
                            raise Match
                        next_states.append(state)
                        
                    else:
                        skip -= 1
                        
                        # if we have other states, or will add them via search
                        if search or next_states or self._states:
                            state.skip = skip
                            next_states.append(state)
                            known_next.add(state)
                            
                        # otherwise, we can jump directly
                        else:
                            self._advance(skip)
                            state.skip = 0
                            next_states.append(state)
                    
                # move to next character
                self._advance()
                self._states = next_states
               
                # add current position as search if necessary
                if search and start_state not in known_next:
                    new_state = start_state.clone().start_group(0, self._offset)
                    self._states.append(new_state)
                    
                self._states.reverse()
            
            while self._states:
                self._state = self._states.pop()
                if self._state.skip == -1:
                    raise Match
                
            # exhausted states with no match
            return Groups()
        
        except Match:
            return self._state.groups(self._parser_state.groups)
    
    def string(self, next, text):
        length = len(text)
        if length == 1:
            if self._current == text[0:1]:
                return True
        else:
            try:
                (advanced, _) = s_next(self._stream, length)
                if advanced == text:
                    self._state.skip = length
                    self._states.append(self._state.advance(next))
            except StopIteration:
                pass
        raise Fail

    def start_group(self, number):
        self._state.start_group(number, self._offset)
        return False
    
    def end_group(self, number):
        self._state.end_group(number, self._offset)
        return False
    
    def match(self):
        self._state.end_group(0, self._offset)
        raise Match

    def no_match(self):
        raise Fail

    def checkpoint(self, id):
        self._state.check(self._offset, id)
        
    def group_reference(self, next, number):
        try:
            text = self._state.group(number)
            if text is None:
                raise Fail
            else:
                return self.string(next, text)
        except KeyError:
            raise Fail

    # branch

    def conditional(self, next, number):
        try:
            if self._state.group(number) is not None:
                return next[1]
        except KeyError:
            pass
        return next[0]

    def split(self, next):
        for index in reversed(next):
            self._states.append(self._state.clone(index))
        # start from new states
        raise Fail

    def _push(self):
        '''
        Save current state for lookahead.
        '''
        self.__stack.append((self._offset, self._excess, self._stream,
                             self._next_stream, self._current, self._previous,
                             self._state, self._states, self._search,
                             self._lookaheads))

    def _pop(self):
        '''
        Restore current state after lookahead.
        '''
        (self._offset, self._excess, self._stream, self._next_stream,
         self._current, self._previous, self._state, self._states,
         self._search, self._lookaheads) = self.__stack.pop()

    def lookahead(self, next, equal, forwards, mutates, reads, length):
        # todo - could also cache things that read groups by state
        
        # discard old values
        if self._lookaheads[0] != self._offset:
            self._lookaheads = (self._offset, {})
        lookaheads = self._lookaheads[1]

        # approach here different from simple engine as not all
        # results can be cached
        match = False
        if next[1] in lookaheads:
            success = lookaheads[next[1]]
        else:
            # we need to match the lookahead
            search = False
            size = None if (reads and mutates) else \
                length(self._state.groups(self._parser_state.groups))
            if forwards:
                stream = self._initial_stream
                offset = self._offset
            else:
                (text, _) = s_next(self._initial_stream, self._offset)
                stream = s_stream(self._initial_stream, text)
                if size is None:
                    offset = 0
                    search = True
                else:
                    offset = self._offset - size

            if offset >= 0:
                new_state = self._state.clone(next[1], stream=stream)
                self._push()
                try:
                    match = self._run_from(new_state, stream, offset, search)
                    new_state = self._state
                finally:
                    self._pop()

            success = bool(match) == equal
            if not (mutates or reads):
                lookaheads[next[1]] = success

        # if lookahead succeeded, continue
        if success:
            if mutates and match:
                self._state.merge_groups(new_state)
            self._states.append(self._state.advance(next[0]))
        raise Fail

    def repeat(self, next, begin, end, lazy):
        # index on first loop item
        loop = next[1]
        state = self._state
        count = state.get_loop(loop)
        if count is None:
            if 0 < begin:
                # increment and loop
                state.new_loop(loop)
                return loop
            elif end is None or 0 < end:
                # can both increment and exit
                if lazy:
                    # increment on stack
                    self._states.append(state.clone(loop).new_loop(loop))
                    # exit (never started, so just continue) now
                    return next[0]
                else:
                    # exit (never started, so just continue) on stack
                    self._states.append(state.clone(next[0]))
                    # new loop now
                    state.new_loop(loop)
                    return loop
            else:
                # strange {0,0} loop so just exit
                return next[0]
        else:
            count += 1
            if count < begin:
                # increment and loop
                state.increment_inner_loop()
                return loop
            elif end is None or count < end:
                # can both increment and exit
                if lazy:
                    # increment on stack
                    self._states.append(state.clone(loop).increment_inner_loop())
                    # exit now
                    state.drop_inner_loop()
                    return next[0]
                else:
                    # exit on stack
                    self._states.append(state.clone(next[0]).drop_inner_loop())
                    # new loop now
                    state.increment_inner_loop()
                    return loop
            else:
                # equal to end so exit
                state.drop_inner_loop()
                return next[0]
    