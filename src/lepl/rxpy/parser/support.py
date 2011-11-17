#LICENCE

'''
Support classes for parsing.
'''

from string import digits, ascii_letters

from lepl.rxpy.graph.post import resolve_group_names, post_process, set_lookahead_properties
from lepl.rxpy.parser.error import SimpleGroupError
from lepl.rxpy.support import _FLAGS, RxpyError, refuse_flags


OCTAL = '01234567'
ALPHANUMERIC = digits + ascii_letters


class ParserState(object):
    '''
    Encapsulate state needed by the parser.  This includes information
    about flags (which may change during processing and is related to
    alphabets) and groups.
    '''

    (I, M, S, U, X, A, _L, _C, _E, _U, _G, _B,
     IGNORECASE, MULTILINE, DOT_ALL, UNICODE, VERBOSE, ASCII,
     _LOOP_UNROLL, _CHARS, _EMPTY, _UNSAFE, _GROUPS, _LOOKBACK) = _FLAGS

    def __init__(self, alphabet, flags=0, require=0, refuse=0):
        '''
        `alphabet` - alphabet to use

        `flags` - initial flags set by user (bits as int)

        `require` - flags required by the engine

        `refuse` - flags refused by the engine
        '''

        flags = flags | require
        # check contradictions
        if (flags & ParserState.ASCII) and (flags & ParserState.UNICODE):
            raise ValueError('Cannot specify Unicode and ASCII together')
        refuse_flags(flags & refuse)

        self.__flags = flags
        self.__alphabet = alphabet
        self.__require = require
        self.__refuse = refuse

        self.__new_flags = 0
        self.groups = GroupState()
        self.__comment = False  # used to track comments with extended syntax
        self.__unwind_credit = 10

    def deep_eq(self, other):
        '''
        Used only for testing.
        '''
        def same_type(a, b):
            '''Test for same type'''
            return a == b == None or (a and b and type(a) == type(b))
        return self.__new_flags == other.__new_flags and \
            self.__require == other.__require and \
            self.__refuse == other.__refuse and \
            same_type(self.__alphabet, other.__alphabet) and \
            self.__flags == other.__flags and \
            self.groups == other.groups and \
            self.__comment == other.__comment and \
            self.__unwind_credit == other.__unwind_credit

    @property
    def has_new_flags(self):
        '''
        Have flags change during parsing (possible when flags are embedded in
        the regular expression)?

        We also return True of neither ASCII nor UNICODE was set - this lets
        us set UNICODE as the default for the second parse.
        '''
        return (self.__new_flags & ~self.__flags) or \
               not ((self.__new_flags | self.__flags) &
                    (ParserState.ASCII | ParserState.UNICODE))

    def clone_with_new_flags(self, expression):
        '''
        This discards group information because the expression will be parsed
        again with new flags.
        '''
        flags = self.__flags | self.__new_flags
        if not (flags & (ParserState.ASCII | ParserState.UNICODE)):
            if is_bytes(expression):
                flags |= ParserState.ASCII
            else:
                flags |= ParserState.UNICODE
        return ParserState(alphabet=self.__alphabet, flags=flags,
                           require=self.__require, refuse=self.__refuse)

    def next_group_index(self, name=None):
        '''
        Get the index number for the next group, possibly associating it with
        a name.
        '''
        return self.groups.new_index(name, self.flags & self._GROUPS)

    def index_for_name_or_count(self, name):
        '''
        Given a group name or index (as text), return the group index (as int).
        First, we parse as an integer, then we try as a name.
        '''
        return self.groups.index_for_name_or_count(name)

    def new_flag(self, flag):
        '''
        Add a new flag (called by the parser for embedded flags).
        '''
        self.__new_flags |= flag

    def significant(self, character):
        '''
        Returns false if character should be ignored (extended syntax).
        '''
        char_str = self.__alphabet.expression_to_str(character)
        if self.__flags & self.VERBOSE:
            if char_str == '#':
                self.__comment = True
                return False
            elif self.__comment:
                self.__comment = char_str != '\n'
                return False
            elif self.__alphabet.space(character, self.__flags):
                return False
            else:
                return True
        else:
            return True

    def unwind(self, count):
        '''
        Allow limited unwinding of loops.  This is to limit unwinding in case
        of nested repeats.  Unfortunately, because the parser is L to R, it
        will be applied to the outer loop (although this is not for direct
        speed as much as letting the simple engine work, so that may not be
        a serious issue).
        '''
        if count <= self.__unwind_credit:
            self.__unwind_credit -= count
            return True
        else:
            return False

    @property
    def alphabet(self):
        '''
        The alphabet to be used.
        '''
        return self.__alphabet

    @property
    def flags(self):
        '''
        Current flags (this does not change as new flags are added; instead
        the entire expression must be re-parsed if `has_new_flags` is True.
        '''
        return self.__flags


class GroupState(object):

    def __init__(self):
        self.__name_to_index = {}
        self.__index_to_name = {}

    def index_for_name_or_count(self, name):
        '''
        Given a group name or index (as text), return the group index (as int).
        First, we parse as an integer, then we try as a name.
        '''
        try:
            index = int(name)
            if index not in self.__index_to_name:
                raise RxpyError('Unknown index ' + str(name))
            else:
                return index
        except ValueError:
            if name not in self.__name_to_index:
                raise RxpyError('Unknown name ' + str(name))
            else:
                return self.__name_to_index[name]

    def new_index(self, name=None, extended=False):

        def next_index():
            index = 1
            while index in self.__index_to_name:
                index += 1
            return index

        if extended:
            # allow aliasing and numbers as names
            if not name:
                name = str(next_index())
            try:
                index = self.index_for_name_or_count(name)
            except RxpyError:
                try:
                    index = int(name)
                except ValueError:
                    index = next_index()
            else:
                return index
        else:
            # names are not numbers and cannot repeat
            index = next_index()
            if name:
                try:
                    int(name)
                    raise SimpleGroupError('Invalid group name ' + name)
                except ValueError:
                    if name in self.__name_to_index:
                        raise SimpleGroupError('Repeated group name ' + name)
            else:
                name = str(index)

        self.__index_to_name[index] = name
        self.__name_to_index[name] = index
        return index

    def __eq__(self, other):
        return isinstance(other, GroupState) and \
            self.__index_to_name == other.__index_to_name

    @property
    def count(self):
        return len(self.__index_to_name)

    @property
    def names(self):
        '''
        Map from group names to index.  Warning - for efficiency, exposed raw.
        '''
        return self.__name_to_index

    @property
    def indices(self):
        '''
        Map from group index to name.  Warning - for efficiency, exposed raw.
        '''
        return self.__index_to_name


class Builder(object):
    '''
    Base class for states in the parser (called Builder rather than State
    to avoid confusion with the parser state).

    The parser can be though of as a state machine, implemented via a separate
    loop (`parse()`) that repeatedly calls `.append_character()` on the current
    state, using whatever is returned as the next state.

    The graph is assembled within the states, which either assemble locally
    or extend the state in a "parent" state (so states may reference parent
    states, but the evaluation process remains just a single level deep).

    It is also possible for one state to delegate to the append_character
    method of another state (escapes are handled in this way, for example).

    After all characters have been parsed, `None` is used as a final character
    to flush any state that is waiting for lookahead.
    '''

    def __init__(self, parser_state):
        self._parser_state = parser_state

    def append_character(self, character, escaped=False):
        '''
        Accept the given character, returning a new builder.  A value of
        None is passed at the end of the input, allowing cleanup.

        If escaped is true then the value is always treated as a literal.
        '''


def parse(text, parser_state, class_, mutable_flags=True):
    '''
    Parse the text using the given builder.

    If the expression sets flags then it is parsed again.  If it changes flags
    on the second parse then an error is raised.
    '''
    graph = None
    try:
        graph = class_(parser_state).parse(text)
    except RxpyError:
        # suppress error if we will parse again
        if not (mutable_flags and parser_state.has_new_flags):
            raise
    if mutable_flags and parser_state.has_new_flags:
        parser_state = parser_state.clone_with_new_flags(text)
        graph = class_(parser_state).parse(text)
    parser_state.alphabet.validate_expression(text, parser_state.flags)
    actions = resolve_group_names(parser_state)
    actions.append(set_lookahead_properties())
    graph = post_process(graph, actions)
    if parser_state.has_new_flags:
        raise RxpyError('Inconsistent flags')
    return parser_state, graph


def is_bytes(text):
    # experimented here with avoiding strings in 2.7, but was inconsistent
    return isinstance(text, bytes)


def default_alphabet(alphabet, text):
    from lepl.rxpy.alphabet.bytes import Bytes
    from lepl.rxpy.alphabet.ucode import String
    if not alphabet:
        if is_bytes(text):
            alphabet = Bytes()
        else:
            alphabet = String()
    return alphabet

