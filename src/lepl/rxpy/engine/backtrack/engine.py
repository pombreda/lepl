#LICENCE

'''
A matcher implementation using a simple interpreter-based approach.  State is
encapsulated in `State` while program flow uses trampolining to avoid
exhausting the Python stack.  In addition, to further reduce the use of the
(non-Python) stack, simple repetition is "run length" compressed (this
addresses ".*" matching against long strings, for example).
'''                                    

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.support import Groups, Loops, Fail, Match, StreamTargetMixin
from lepl.rxpy.graph.base_compilable import compile
from lepl.stream.core import s_next, s_stream


class State(StreamTargetMixin):
    '''
    State for a particular position moment / graph position / text offset.
    '''
    
    def __init__(self, parser_state, stream, groups, pos=None,
                 previous=None, offset=0, loops=None, checkpoints=None):
        self._parser_state = parser_state
        self._reset(offset, stream, previous)
        if pos is not None:
            self._advance(pos)
        self.__groups = groups
        self.__loops = loops if loops else Loops()
        self.__checkpoints = checkpoints

    def clone(self, offset=None, groups=None):
        '''
        Duplicate this state.  If offset is specified, it must be greater than
        or equal the existing offset; then the text and offset of the clone
        will be consistent with the new value.  If groups is given it replaces
        the previous groups.
        '''
        if groups is None:
            groups = self.__groups.clone()
        previous = self._previous
        if offset is None or offset == self._offset:
            offset = self._offset
            stream = self._stream
        else:
            delta = offset - self._offset
            (advanced, stream) = s_next(self._stream, delta)
            previous = advanced[-1:]
        checkpoints = set(self.__checkpoints) if self.__checkpoints else None
        return State(self._parser_state, stream, groups,
                     previous=previous, offset=offset,
                     loops=self.__loops.clone(), checkpoints=checkpoints)
        
    def search_forwards(self):
        if self._current is not None:
            self._advance()
            self.__groups.start_group(0, self._offset)
            return True
        else:
            return False

    def _advance(self, delta=1):
        if delta:
            self.__checkpoints = None
        return super(State, self)._advance(delta)
        
    def increment(self, index):
        return self.__loops.increment(index)

    # below are methods that correspond roughly to opcodes in the graph.
    # these are called from the engine.
        
    def string(self, next, text):
        length = len(text)
        if length == 1:
            if self._current == text[0:1]:
                self._advance()
                return True
        else:
            try:
                (advanced, _) = s_next(self._stream, length)
                if advanced == text:
                    self._advance(length)
                    return True
            except StopIteration:
                pass
        raise Fail

    def start_group(self, number):
        self.__groups.start_group(number, self._offset)

    def end_group(self, number):
        self.__groups.end_group(number, self._offset)

    def drop(self, node):
        self.__loops.drop(node)
        return self

    def similar(self, other):
        '''
        Is this state similar to the one given?  In particular, are the
        groups and loops values identical (so we only differ by offset)?
        '''
        return self.__groups == other.__groups and self.__loops == other.__loops
    
    def checkpoint(self, token):
        if self.__checkpoints is None:
            self.__checkpoints = {token}
        else:
            if token in self.__checkpoints:
                raise Fail
        return False

    @property
    def groups(self):
        return self.__groups
    

class Stack(object):
    '''
    A stack of states.  This extends a simple stack with the ability to 
    compress repeated states (which is useful to avoid filling the stack
    with backtracking when something like ".*" is used to match a large 
    string).
    
    The compression is quite simple: if a state and group are pushed to
    the stack which are identical, apart from offset, with the existing top
    of the stack, then the stack is not extended.  Instead, the new offset
    and increment are appended to the existing entry.  The same occurs for
    further pushes that have the same increment.
    
    On popping we create a new state, and adjust the offset as necessary.
    
    For this to work correctly we must also be careful to preserve the
    original state, since that is the one that contains the most text.
    Later states have less text and so cannot be cloned "back" to having
    an earlier offset.
    '''
    
    def __init__(self):
        self.__stack = []
        self.max_depth = 0  # for tests
        
    def push(self, index, state):
        if self.__stack:
            (p_index, p_state, p_repeat) = self.__stack[-1]
            # is compressed repetition possible?
            if p_state.similar(state) and p_index == index:
                # do we have an existing repeat?
                if p_repeat:
                    (end, step) = p_repeat
                    # and this new state has the expected increment
                    if state._offset == end + step:
                        self.__stack.pop()
                        self.__stack.append((index, p_state,
                                             (state._offset, step)))
                        return
                # otherwise, start a new repeat block
                elif p_state._offset < state._offset:
                    self.__stack.pop()
                    self.__stack.append((index, p_state,
                                         (state._offset,
                                          state._offset - p_state._offset)))
                    return
        # above returns on success, so here default to a "normal" push
        self.__stack.append((index, state, None))
        self.max_depth = max(self.max_depth, len(self.__stack))

    def pop(self):
        (index, state, repeat) = self.__stack.pop()
        if repeat:
            (end, step) = repeat
            # if the repeat has not expired
            if state._offset != end:
                # add back one step down
                self.__stack.append((index, state, (end-step, step)))
                state = state.clone(end)
        return (index, state)


    def __bool__(self):
        return bool(self.__stack)

    def __nonzero__(self):
        return self.__bool__()


class BacktrackingEngine(BaseMatchEngine):
    '''
    The interpreter.
    '''

    def __init__(self, parser_state, graph):
        super(BacktrackingEngine, self).__init__(parser_state, graph)
        self._program = compile(graph, self)

    def run(self, stream, pos=0, search=False):
        '''
        Execute a search.
        '''
        self.__stream = stream
        self.__pos = pos

        state = State(self._parser_state, stream,
                      Groups(group_state=self._parser_state.groups, stream=stream),
                      pos=pos)

        # for testing optimizations
        self.ticks = 0
        self.max_depth = 0

        self.__stack = None
        self.__state = None
        self.__stacks = []
        self.__lookaheads = {} # map from node to set of known ok states

        state.start_group(0)
        (match, state) = self.__run(0, state, search=search)
        if match:
            state.end_group(0)
            return state.groups
        else:
            return Groups()

    def __run(self, index, state, search=False):
        '''
        Run a sub-search.  We support multiple searches (stacks) so that we
        can invoke the same interpreter for lookaheads etc.

        This is a simple trampoline - it stores state on a stack and invokes
        the the compiled program.  Callbacks return the new program index,
        raise `Fail` on failure, or `Match` on success.
        '''
        self.__stacks.append((self.__stack, self.__state))
        self.__stack = Stack()
        self.__state = state
        save_index = None
        try:
            try:
                # search loop
                while True:
                    # if searching, save state for restart
                    if search:
                        (save_state, save_index) = (self.__state.clone(), index)
                    # backtrack loop
                    while True:
                        try:
                            # can't loop completely inside program as we exceed
                            # stack depth
                            index = self._program[index]()
                        # backtrack if stack exists
                        except Fail:
                            if self.__stack:
                                (index, self.__state) = self.__stack.pop()
                            else:
                                break
                    # nudge search forwards and try again, or exit
                    if search:
                        if save_state.search_forwards():
                            (self.__state, index) = (save_state, save_index)
                        else:
                            break
                    # match (not search), so exit with failure
                    else:
                        break
                return (False, self.__state)
            except Match:
                return (True, self.__state)
        finally:
            # restore state so that another run can resume
            self.max_depth = max(self.max_depth, self.__stack.max_depth)
            self.__stack, self.__state = self.__stacks.pop()
            self.__match = False
            
    # below are the engine methods - these implement the different opcodes

    def string(self, next, text):
        self.ticks += 1
        return self.__state.string(next, text)

    def character(self, charset):
        self.ticks += 1
        return self.__state.character(charset) and self.__state._advance()

    def dot(self, multiline):
        self.ticks += 1
        return self.__state.dot(multiline) and self.__state._advance()

    def start_group(self, number):
        self.ticks += 1
        return self.__state.start_group(number)

    def end_group(self, number):
        self.ticks += 1
        return self.__state.end_group(number)

    def group_reference(self, next, number):
        self.ticks += 1
        try:
            text = self.__state.groups.group(number)
            if text is None:
                raise Fail
            else:
                return self.__state.string(next, text)
        except KeyError:
            raise Fail

    def conditional(self, next, number):
        self.ticks += 1
        try:
            if self.__state.groups.group(number):
                return next[1]
        except KeyError:
            pass
        return next[0]

    def split(self, next):
        self.ticks += 1
        for index in reversed(next[1:]):
            clone = self.__state.clone()
            self.__stack.push(index, clone)
        return next[0]

    def match(self):
        self.ticks += 1
        raise Match

    def no_match(self):
        self.ticks += 1
        raise Fail

    def start_of_line(self, multiline):
        self.ticks += 1
        return self.__state.start_of_line(multiline)

    def end_of_line(self, multiline):
        self.ticks += 1
        return self.__state.end_of_line(multiline)

    def lookahead(self, next, equal, forwards, mutates, reads, length):
        self.ticks += 1
        alternate = next[1]
        if alternate not in self.__lookaheads:
            self.__lookaheads[alternate] = {}
        if self.__state._offset in self.__lookaheads[alternate]:
            success = self.__lookaheads[alternate[self.__state._offset]]
        else:
            size = None if (reads and mutates) else length(self.__state.groups)
            search = False
            if forwards:
                clone = State(self.__state._parser_state, self.__state._stream,
                              self.__state.groups.clone())
            else:
                if size is not None and size > self.__state._offset and equal:
                    raise Fail
                (text, _) = s_next(self.__stream, self.__state._offset)
                stream = s_stream(self.__stream, text)
                if size is None or size > self.__state._offset:
                    search = True
                    pos = None
                else:
                    pos = self.__state._offset - size
                clone = State(self.__state._parser_state, stream,
                              self.__state.groups.clone(), pos=pos)
            (match, clone) = self.__run(alternate, clone, search=search)
            success = match == equal
            if not (reads or mutates):
                self.__lookaheads[alternate][self.__state._offset] = success
        # if lookahead succeeded, continue
        if success:
            if mutates:
                self.__state = self.__state.clone(groups=clone.groups)
            return next[0]
        else:
            raise Fail

    def repeat(self, next, begin, end, lazy):
        self.ticks += 1
        loop = next[1]
        count = self.__state.increment(loop)
        # if we haven't yet reached the point where we can continue, loop
        if count < begin:
            return loop
        # stack logic depends on laziness
        if lazy:
            # we can continue from here, but if that fails we want to restart 
            # with another loop, unless we've exceeded the count or there's
            # no text left
            # this is well-behaved with stack space
            if (end is None and self.__state._current is not None) \
                    or (end is not None and count < end):
                self.__stack.push(loop, self.__state.clone())
            if end is None or count <= end:
                self.__state.drop(loop)
                return next[0]
            else:
                raise Fail
        else:
            if end is None or count < end:
                # add a fallback so that if a higher loop fails, we can continue
                self.__stack.push(next[0], self.__state.clone().drop(loop))
            if count == end:
                # if last possible loop, continue
                self.__state.drop(loop)
                return next[0]
            else:
                # otherwise, do another loop
                return loop
    
    def word_boundary(self, inverted):
        self.ticks += 1
        return self.__state.word_boundary(inverted)

    def digit(self, inverted):
        self.ticks += 1
        return self.__state.digit(inverted) and self.__state._advance()

    def space(self, inverted):
        self.ticks += 1
        return self.__state.space(inverted) and self.__state._advance()

    def word(self, inverted):
        self.ticks += 1
        return self.__state.word(inverted) and self.__state._advance()

    def checkpoint(self, token):
        self.ticks += 1
        return self.__state.checkpoint(token)
