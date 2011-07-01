#LICENCE

'''
A matcher implementation using a simple interpreter-based approach with the
`Visitor` interface.  State is encapsulated in `State` while program flow 
uses trampolining to avoid exhausting the Python stack.  In addition, to
further reduce the use of the (non-Python) stack, simple repetition is
"run length" compressed (this addresses ".*" matching against long strings, 
for example). 
'''                                    

from lepl.rxpy.engine.base import BaseMatchEngine
from lepl.rxpy.engine.support import Groups, lookahead_logic, Loops, Fail, Match
from lepl.rxpy.graph.base_compilable import compile


class State(object):
    '''
    State for a particular position moment / graph position / text offset.
    '''
    
    def __init__(self, text, groups, previous=None, offset=0, loops=None,
                 checkpoints=None):
        self.__text = text
        self.__groups = groups
        self.__previous = previous
        self.__offset = offset
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
        previous = self.__previous
        if offset is None:
            offset = self.__offset
            text = self.__text
        else:
            delta = offset - self.__offset
            if delta:
                previous = self.__text[delta-1:delta]
            text = self.__text[delta:]
        checkpoints = set(self.__checkpoints) if self.__checkpoints else None
        return State(text, groups, previous=previous, offset=offset, 
                     loops=self.__loops.clone(), checkpoints=checkpoints)
        
    def advance(self):
        '''
        Used in search to increment start point.
        '''
        if self.__text:
            self.__increment()
            self.__groups.start_group(0, self.__offset)
            return True
        else:
            return False
        
    def __increment(self, length=1):
        '''
        Increment offset during match.
        '''
        if length:
            self.__checkpoints = None
            self.__previous = self.__text[length-1:length]
            self.__text = self.__text[length:]
            self.__offset += length
        if not self.__previous: raise IndexError
    
    def increment(self, node):
        return self.__loops.increment(node)

    # below are methods that correspond roughly to opcodes in the graph.
    # these are called from the engine.
        
    def string(self, text):
        l = len(text)
        if self.__text[0:l] == text:
            self.__increment(l)
            return self
        raise Fail
    
    def character(self, charset):
        if self.__text[0:1] in charset:
            self.__increment()
            return self
        raise Fail
    
    def start_group(self, number):
        self.__groups.start_group(number, self.__offset)
        return self
        
    def end_group(self, number):
        self.__groups.end_group(number, self.__offset)
        return self
    
    def drop(self, node):
        self.__loops.drop(node)
        return self

    def dot(self, multiline=True):
        try:
            if multiline or self.__text[0] != '\n':
                self.__increment()
                return self
        except IndexError:
            pass
        raise Fail
        
    def start_of_line(self, multiline):
        if self.__offset == 0 or (multiline and self.__previous == '\n'):
            return self
        else:
            raise Fail
            
    def end_of_line(self, multiline):
        if ((not self.__text or (multiline and self.__text[0] == '\n'))
                # also before \n at end of text
                or (self.__text and self.__text[0] == '\n' and
                    not self.__text[1:])):
            return self
        else:
            raise Fail
        
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
        return self

    @property
    def groups(self):
        return self.__groups
    
    @property
    def offset(self):
        return self.__offset

    @property
    def text(self):
        return self.__text

    @property
    def previous(self):
        return self.__previous
    
    
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
        
    def push(self, pointer, state):
        if self.__stack:
            (p_pointer, p_state, p_repeat) = self.__stack[-1]
            # is compressed repetition possible?
            if p_state.similar(state) and p_pointer == pointer:
                # do we have an existing repeat?
                if p_repeat:
                    (end, step) = p_repeat
                    # and this new state has the expected increment
                    if state.offset == end + step:
                        self.__stack.pop()
                        self.__stack.append((pointer, p_state,
                                             (state.offset, step)))
                        return
                # otherwise, start a new repeat block
                elif p_state.offset < state.offset:
                    self.__stack.pop()
                    self.__stack.append((pointer, p_state,
                                         (state.offset, state.offset - p_state.offset)))
                    return
        # above returns on success, so here default to a "normal" push
        self.__stack.append((pointer, state, None))
        self.max_depth = max(self.max_depth, len(self.__stack))
        
    def pop(self):
        (pointer, state, repeat) = self.__stack.pop()
        if repeat:
            (end, step) = repeat
            # if the repeat has not expired
            if state.offset != end:
                # add back one step down
                self.__stack.append((pointer, state, (end-step, step)))
                state = state.clone(end)
        return (pointer, state)


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

    def run(self, text, pos=0, search=False):
        '''
        Execute a search.
        '''
        self.__text = text
        self.__pos = pos
        
        state = State(text[pos:],
                      Groups(group_state=self._parser_state.groups, text=text),
                      offset=pos, previous=text[pos-1:pos] if pos else None)

        # for testing optimizations
        self.ticks = 0
        self.max_depth = 0
        
        self.__stack = None
        self.__stacks = []
        self.__lookaheads = {} # map from node to set of known ok states
        
        state.start_group(0)
        (match, state) = self.__run(0, state, search=search)
        if match:
            state.end_group(0)
            return state.groups
        else:
            return Groups()
            
    def __run(self, pointer, state, search=False):
        '''
        Run a sub-search.  We support multiple searches (stacks) so that we
        can invoke the same interpreter for lookaheads etc.
        
        This is a simple trampoline - it stores state on a stack and invokes
        the the compiled program.  Callbacks return the new program pointer,
        raise `Fail` on failure, or `Match` on success.
        '''
        self.__stacks.append(self.__stack)
        self.__stack = Stack()
        self.__state = state
        save_pointer = False
        try:
            try:
                # search loop
                while True:
                    # if searching, save state for restart
                    if search:
                        (save_state, save_pointer) = (self.__state.clone(), pointer)
                    # trampoline loop
                    while True:
                        self.ticks += 1
                        try:
                            pointer = self._program[pointer]()
                        # backtrack if stack exists
                        except Fail:
                            if self.__stack:
                                (pointer, self.__state) = self.__stack.pop()
                            else:
                                break
                    # nudge search forwards and try again, or exit
                    if search:
                        if save_state.advance():
                            (self.__state, pointer) = (save_state, save_pointer)
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
            self.__stack = self.__stacks.pop()
            self.__match = False
            
    # below are the engine methods - these implement the different opcodes
    # TODO - can we return False sometimes?

    def string(self, next, text, length):
        self.__state = self.__state.string(text)
        return True
    
    def character(self, charset):
        self.__state = self.__state.character(charset)
        return True

    def start_group(self, number):
        self.__state = self.__state.start_group(number)
        return True

    def end_group(self, number):
        self.__state = self.__state.end_group(number)
        return True

    def group_reference(self, next, number):
        try:
            text = self.__state.groups.group(number)
            if text is None:
                raise Fail
            else:
                return self.string(next, text, len(text))
        except KeyError:
            raise Fail

    def conditional(self, next, number):
        try:
            if self.__state.groups.group(number):
                return 1
        except KeyError:
            pass
        return 0

    def split(self, next):
        for (index, _node) in reversed(next):
            clone = self.__state.clone()
            self.__stack.push(index, clone)
        # start from new states
        raise Fail

    def match(self):
        raise Match

    def no_match(self):
        raise Fail

    def dot(self, multiline):
        self.__state = self.__state.dot(multiline)
        return True

    def start_of_line(self, multiline):
        self.__state = self.__state.start_of_line(multiline)
        return True
        
    def end_of_line(self, multiline):
        self.__state = self.__state.end_of_line(multiline)
        return True

    def lookahead(self, next, equal, forwards):
        node = next[1]
        if node not in self.__lookaheads:
            self.__lookaheads[node] = {}
        if self.__state.offset in self.__lookaheads[node]:
            reads, mutates = False, False
            success = self.__lookaheads[node][self.__state.offset]
        else:
            (reads, mutates, size) = \
                lookahead_logic(next[1], forwards, self.__state.groups)
            search = False
            if forwards:
                clone = State(self.__state.text, self.__state.groups.clone())
            else:
                if size is not None and size > self.__state.offset and equal:
                    raise Fail
                elif size is None or size > self.__state.offset:
                    subtext = self.__text[0:self.__state.offset]
                    previous = None
                    search = True
                else:
                    offset = self.__state.offset - size
                    subtext = self.__text[offset:self.__state.offset]
                    if offset:
                        previous = self.__text[offset-1:offset]
                    else:
                        previous = None
                clone = State(subtext, self.__state.groups.clone(), previous=previous)
            (match, clone) = self.__run(next[1], clone, search=search)
            success = match == equal
            if not (reads or mutates):
                self.__lookaheads[node][self.__state.offset] = success
        # if lookahead succeeded, continue
        if success:
            if mutates:
                self.__state = self.__state.clone(groups=clone.groups)
            return True
        else:
            raise Fail

    def repeat(self, next, begin, end, lazy):
        node = next[1]
        count = self.__state.increment(node)
        # if we haven't yet reached the point where we can continue, loop
        if count < begin:
            return 1
        # stack logic depends on laziness
        if lazy:
            # we can continue from here, but if that fails we want to restart 
            # with another loop, unless we've exceeded the count or there's
            # no text left
            # this is well-behaved with stack space
            if (end is None and self.__state.text) \
                    or (end is not None and count < end):
                self.__stack.push(next[1], self.__state.clone())
            if end is None or count <= end:
                self.__state.drop(node)
                return 0
            else:
                raise Fail
        else:
            if end is None or count < end:
                # add a fallback so that if a higher loop fails, we can continue
                self.__stack.push(next[0], self.__state.clone().drop(node))
            if count == end:
                # if last possible loop, continue
                self.__state.drop(node)
                return 0
            else:
                # otherwise, do another loop
                return 1
    
    def word_boundary(self, inverted):
        previous = self.__state.previous
        current = self.__state.text[0:1]
        word = self._parser_state.alphabet.word
        boundary = word(current) != word(previous)
        if boundary != inverted:
            return True
        else:
            raise Fail

    def digit(self, inverted):
        if self._parser_state.alphabet.digit(self.__state.text[0:1]) != inverted:
            self.__state = self.__state.dot()
            return True
        raise Fail
    
    def space(self, inverted):
        if self._parser_state.alphabet.space(self.__state.text[0:1]) != inverted:
            self.__state = self.__state.dot()
            return True
        raise Fail
    
    def word(self, inverted):
        if self._parser_state.alphabet.word(self.__state.text[0:1]) != inverted:
            self.__state = self.__state.dot()
            return True
        raise Fail

    def checkpoint(self, token):
        self.__state = self.__state.checkpoint(token)
        return True
