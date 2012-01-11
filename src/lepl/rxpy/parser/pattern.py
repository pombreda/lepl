#LICENCE

'''
An ad-hoc parser for regular expressions.  I think it's best to consider this
as recursive descent with hand-written trampolining, but you can also consider
the matchers as states in a state machine.  Whatever it is, it works quite
nicely, and exploits inheritance well.  I call the matchers/states "builders".

Note: This doesn't use Lepl as a parser because it was initially a separate,
standalone package.  At some point it should be replaced by a Lepl parser.

Builders have references to their callers and construct the graph through
those references (ultimately accumulating the graph nodes in the root
`SequenceBuilder`).
'''

from string import digits, ascii_letters

from lepl.rxpy.graph.container import Alternatives, Sequence, Optional, Loop, \
    CountedLoop
from lepl.rxpy.graph.opcode import Match, Dot, StartOfLine, EndOfLine, \
    Character, String, StartGroup, EndGroup, Lookahead, Conditional, \
    GroupReference, WordBoundary, Digit, Word, Space
from lepl.rxpy.parser.error import ParseError, EmptyError
from lepl.rxpy.parser.support import Builder, ParserState, OCTAL, parse
from lepl.rxpy.support import RxpyError


class SequenceBuilder(Builder):
    '''
    Parse a sequence (this is the main entry point for parsing, but users
    will normally call `parse_pattern`).
    '''

    def __init__(self, parser_state):
        super(SequenceBuilder, self).__init__(parser_state)
        self._alternatives = Alternatives()
        self._sequence = Sequence()

    def parse(self, text):
        '''Parse a regular expression.'''
        builder, index = self, None
        try:
            for (index, character) in enumerate(text):
                builder = builder.append_character(character)
            builder = builder.append_character(None)
        except ParseError as e:
            e.update(text, index)
            raise
        if self != builder:
            raise RxpyError('Incomplete expression')
        return self.to_sequence().join(Match(), self._parser_state)

    def parse_group(self, text):
        '''Parse a set of groups for `Scanner`.'''
        builder = GroupBuilder(self._parser_state, self)
        if self._sequence:
            self.__start_new_alternative()
        for character in text:
            builder = builder.append_character(character)
        try:
            builder = builder.append_character(')')
            assert builder == self
        except:
            raise RxpyError('Incomplete group')

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if not escaped and char_str == '\\':
            return ComplexEscapeBuilder(self._parser_state, self)
        elif not escaped and char_str == '{':
            return CountBuilder(self._parser_state, self, character)
        elif not escaped and char_str == '(':
            return GroupEscapeBuilder(self._parser_state, self)
        elif not escaped and char_str == '[':
            return CharacterBuilder(self._parser_state, self)
        elif not escaped and char_str == '.':
            self._sequence.append(Dot(self._parser_state.flags & ParserState.DOT_ALL))
        elif not escaped and char_str == '^':
            self._sequence.append(StartOfLine(self._parser_state.flags & ParserState.MULTILINE))
        elif not escaped and char_str == '$':
            self._sequence.append(EndOfLine(self._parser_state.flags & ParserState.MULTILINE))
        elif not escaped and char_str == '|':
            self.__start_new_alternative()
        elif character is not None and self._sequence and (
                not escaped and char_str in '+?*'):
            return RepeatBuilder(self._parser_state, self, self._sequence.pop(), character)
        elif character is not None and (
                escaped or self._parser_state.significant(character)):
            (is_pair, value) = \
                self._parser_state.alphabet.expression_to_charset(character,
                                                     self._parser_state.flags)
            if is_pair:
                self._sequence.append(Character([(value[0], value[0]),
                                             (value[1], value[1])],
                                             self._parser_state.alphabet))
            else:
                self._sequence.append(String(value))
        return self

    def __start_new_alternative(self):
        self._alternatives.append(self._sequence)
        self._sequence = Sequence()

    def to_sequence(self):
        '''Retrieve contents as a sequence.'''
        if not self._alternatives:
            return self._sequence
        else:
            self.__start_new_alternative()
            return Sequence([self._alternatives])

    def __bool__(self):
        return bool(self._sequence)


class RepeatBuilder(Builder):
    '''
    Parse simple repetition expressions (*, + and ?).
    '''

    def __init__(self, parser_state, parent, latest, character):
        super(RepeatBuilder, self).__init__(parser_state)
        self._parent = parent
        self._latest = latest
        self._initial_char_str = self._parser_state.alphabet.expression_to_str(character)

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''

        char_str = self._parser_state.alphabet.expression_to_str(character)

        lazy = char_str == '?'

        if character is not None and char_str in '+*':
            raise RxpyError('Compound repeat: ' +
                                 self._initial_char_str + char_str)
        elif self._initial_char_str == '?':
            self.build_optional(self._parent, self._latest, lazy)
        elif self._initial_char_str == '+':
            self.build_plus(self._parent, self._latest, lazy,
                            self._parser_state)
        elif self._initial_char_str == '*':
            self.build_star(self._parent, self._latest, lazy, self._parser_state)
        else:
            raise RxpyError('Bad initial character for RepeatBuilder')

        if lazy:
            return self._parent
        else:
            return self._parent.append_character(character)

    @staticmethod
    def assert_consumer(latest, parser_state):
        '''Helper to check that a sequence is a consumer of input.'''
        if not latest.consumer(True) and not (parser_state.flags & ParserState._EMPTY):
            raise EmptyError

    @staticmethod
    def build_optional(parent, latest, lazy):
        '''Helper to build an optional sub-matcher.'''
        optional = Optional([latest], lazy=lazy,
                            label='...?' + ('?' if lazy else ''))
        parent._sequence.append(optional)

    @staticmethod
    def build_plus(parent, latest, lazy, parser_state):
        '''Helper to build a repeated (1 or more) sub-matcher.'''
        RepeatBuilder.assert_consumer(latest, parser_state)
        loop = Loop([latest], parser_state=parser_state, lazy=lazy, once=True,
                    label='...+' + ('?' if lazy else ''))
        parent._sequence.append(loop)

    @staticmethod
    def build_star(parent, latest, lazy, parser_state):
        '''Helper to build a repeated (0 or more) sub-matcher.'''
        RepeatBuilder.assert_consumer(latest, parser_state)
        loop = Loop([latest], parser_state=parser_state, lazy=lazy, once=False,
                    label='...*' + ('?' if lazy else ''))
        parent._sequence.append(loop)


class GroupEscapeBuilder(Builder):
    '''
    Parse "group escapes" - expressions of the form (?X...).
    '''

    def __init__(self, parser_state, parent):
        super(GroupEscapeBuilder, self).__init__(parser_state)
        self._parent = parent
        self._count = 0

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        self._count += 1
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if self._count == 1:
            if char_str == '?':
                return self
            else:
                builder = GroupBuilder(self._parser_state, self._parent)
                return builder.append_character(character)
        else:
            if char_str == ':':
                return GroupBuilder(self._parser_state, self._parent,
                                    binding=False)
            elif char_str in ParserStateBuilder.INITIAL:
                return ParserStateBuilder(self._parser_state, self._parent).append_character(character)
            elif char_str == 'P':
                return NamedGroupBuilder(self._parser_state, self._parent)
            elif char_str == '#':
                return CommentGroupBuilder(self._parser_state, self._parent)
            elif char_str == '=':
                return LookaheadBuilder(
                            self._parser_state, self._parent, True, True)
            elif char_str == '!':
                return LookaheadBuilder(
                            self._parser_state, self._parent, False, True)
            elif char_str == '<':
                return LookbackBuilder(self._parser_state, self._parent)
            elif char_str == '(':
                return ConditionalBuilder(self._parser_state, self._parent)
            else:
                raise RxpyError(
                    'Unexpected qualifier after (? - ' + char_str)


class ParserStateBuilder(Builder):
    '''
    Parse embedded flags - expressions of the form (?i), (?m) etc.
    '''

    INITIAL = 'iLmsuxa_'

    def __init__(self, parser_state, parent):
        super(ParserStateBuilder, self).__init__(parser_state)
        self.__parent = parent
        self.__escape = False
        self.__table = {'i': ParserState.I,
                        'm': ParserState.M,
                        's': ParserState.S,
                        'u': ParserState.U,
                        'x': ParserState.X,
                        'a': ParserState.A,
                        '_l': ParserState._L,
                        '_c': ParserState._C,
                        '_e': ParserState._E,
                        '_u': ParserState._U,
                        '_g': ParserState._G}

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if not self.__escape and char_str == '_':
            self.__escape = True
            return self
        elif self.__escape and char_str in 'lceug':
            self._parser_state.new_flag(self.__table['_' + char_str])
            self.__escape = False
            return self
        elif not self.__escape and char_str == 'L':
            raise RxpyError('Locale based classes unsupported')
        elif not self.__escape and char_str in self.__table:
            self._parser_state.new_flag(self.__table[char_str])
            return self
        elif not self.__escape and char_str == ')':
            return self.__parent
        elif self.__escape:
            raise RxpyError('Unexpected characters after (? - _' + char_str)
        else:
            raise RxpyError('Unexpected character after (? - ' + char_str)


class BaseGroupBuilder(SequenceBuilder):
    '''
    Support for parsing groups.
    '''

    # This must subclass SequenceBuilder rather than contain an instance
    # because that may itself return child builders.

    def __init__(self, parser_state, parent):
        super(BaseGroupBuilder, self).__init__(parser_state)
        self._parent = parent

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if not escaped and char_str == ')':
            return self._build_group()
        else:
            # this allows further child groups to be opened, etc
            return super(BaseGroupBuilder, self).append_character(character, escaped)

    def _build_group(self):
        pass


class GroupBuilder(BaseGroupBuilder):
    '''
    Parse groups - expressions of the form (...) containing sub-expressions,
    like (ab[c-e]*).
    '''

    def __init__(self, parser_state, parent, binding=True, name=None):
        super(GroupBuilder, self).__init__(parser_state, parent)
        if binding:
            self.__start = StartGroup(self._parser_state.next_group_index(name))
        else:
            self.__start = None

    def _build_group(self):
        if self.__start:
            group = Sequence()
            group.append(self.__start)
            group.append(self.to_sequence())
            group.append(EndGroup(self.__start.number))
            self._parent._sequence.append(group)
        else:
            self._parent._sequence.append(self.to_sequence())
        return self._parent


class LookbackBuilder(Builder):
    '''
    Parse lookback expressions of the form (?<...).
    This delegates most of the work to `LookaheadBuilder`.
    '''

    def __init__(self, parser_state, parent):
        super(LookbackBuilder, self).__init__(parser_state)
        self._parent = parent

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if char_str == '=':
            return LookaheadBuilder(self._parser_state, self._parent, True, False)
        elif char_str == '!':
            self._parser_state.new_flag(ParserState._LOOKBACK)
            return LookaheadBuilder(self._parser_state, self._parent, False, False)
        else:
            raise RxpyError(
                'Unexpected qualifier after (?< - ' + char_str)


class LookaheadBuilder(BaseGroupBuilder):
    '''
    Parse lookahead expressions of the form (?=...) and (?!...), along with
    lookback expressions (via `LookbackBuilder`).

    If it's a reverse lookup we add an end of string matcher, but no prefix,
    so the matcher must be used to "search" if the start is not known.
    '''

    def __init__(self, parser_state, parent, equal, forwards):
        super(LookaheadBuilder, self).__init__(parser_state, parent)
        self._equal = equal
        self._forwards = forwards

    def _build_group(self):
        lookahead = Lookahead(self._equal, self._forwards)
        if not self._forwards:
            self._sequence.append(EndOfLine(False))
        lookahead.next = [self.to_sequence().join(Match(), self._parser_state)]
        self._parent._sequence.append(lookahead)
        return self._parent


class ConditionalBuilder(Builder):
    '''
    Parse (?(id/name)yes-pattern|no-pattern) expressions.  Either
    sub-expression is optional (this isn't documented, but is required by
    the tests).
    '''

    def __init__(self, parser_state, parent):
        super(ConditionalBuilder, self).__init__(parser_state)
        self.__parent = parent
        self.__name = ''
        self.__yes = None

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if not escaped and char_str == ')':
            return YesNoBuilder(self, self._parser_state, self.__parent, '|)')
        elif not escaped and char_str == '\\':
            return SimpleEscapeBuilder(self._parser_state, self)
        else:
            self.__name += char_str
            return self

    def callback(self, yes_no, terminal):
        '''Callback used by `yesNoBuilder` to accumulate data.'''

        # first callback - have 'yes', possibly terminated by '|'
        if self.__yes is None:
            (self.__yes, yes_no) = (yes_no, None)
            # collect second alternative
            if terminal == '|':
                return YesNoBuilder(self, self._parser_state, self.__parent, ')')

        # final callback - build yes and no (if present)
        yes = self.__yes.to_sequence()
        no = yes_no.to_sequence() if yes_no else Sequence()
        label = ('...' if yes else '') + ('|...' if no else '')
        if not label:
            label = '|'
        split = lambda label: Conditional(self.__name, label)
        alternatives = Alternatives([no, yes], label=label, split=split)
        self.__parent._sequence.append(alternatives)
        return self.__parent


class YesNoBuilder(BaseGroupBuilder):
    '''
    A helper for `GroupConditionBuilder` that parses the sub-expressions.
    '''

    def __init__(self, conditional, parser_state, parent, terminals):
        super(YesNoBuilder, self).__init__(parser_state, parent)
        self.__conditional = conditional
        self.__terminals = terminals

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is None:
            raise RxpyError('Incomplete conditional match')
        elif not escaped and char_str in self.__terminals:
            return self.__conditional.callback(self, character)
        else:
            return super(YesNoBuilder, self).append_character(character, escaped)


class NamedGroupBuilder(Builder):
    '''
    Parse '(?P<name>pattern)' and '(?P=name)' by creating either a
    matching group (and associating the name with the group number) or a
    group reference (for the group number).
    '''

    def __init__(self, parser_state, parent):
        super(NamedGroupBuilder, self).__init__(parser_state)
        self._parent = parent
        self._create = None
        self._name = ''

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if self._create is None:
            if char_str == '<':
                self._create = True
            elif char_str == '=':
                self._create = False
            else:
                raise RxpyError(
                    'Unexpected qualifier after (?P - ' + char_str)

        else:
            if self._create and not escaped and char_str == '>':
                if not self._name:
                    raise RxpyError('Empty name for group')
                return GroupBuilder(self._parser_state, self._parent, True, self._name)
            elif not self._create and not escaped and char_str == ')':
                self._parent._sequence.append(
                    GroupReference(self._parser_state.index_for_name_or_count(self._name)))
                return self._parent
            elif not escaped and char_str == '\\':
                # this is just for the name
                return SimpleEscapeBuilder(self._parser_state, self)
            elif character:
                self._name += char_str
            else:
                raise RxpyError('Incomplete named group')

        return self


class CommentGroupBuilder(Builder):
    '''
    Parse comments - expressions of the form (#...).
    '''

    def __init__(self, parser_state, parent):
        super(CommentGroupBuilder, self).__init__(parser_state)
        self._parent = parent

    def append_character(self, character, escaped=False):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if not escaped and char_str == ')':
            return self._parent
        elif not escaped and char_str == '\\':
            return SimpleEscapeBuilder(self._parser_state, self)
        elif character is not None:
            return self
        else:
            raise RxpyError('Incomplete comment')


class CharacterBuilder(Builder):
    '''
    Parse a character range - expressions of the form [...].
    These can include character classes (\\s for example), which we handle
    in the alphabet as functions rather than character code ranges, so the
    final graph node can be quite complex.
    '''

    def __init__(self, parser_state, parent):
        super(CharacterBuilder, self).__init__(parser_state)
        self._parent = parent
        self._charset = Character([], alphabet=parser_state.alphabet)
        self._invert = None
        self._queue = None
        self._range = False

    def append_character(self, character, escaped=False):
        '''Add the next character.'''

        def append(character=character):
            '''Helper function to avoid repetition below - adds character.'''

            def unpack(character):
                '''Generate a `CharSet` or a character pair.'''
                (is_charset, value) = \
                    self._parser_state.alphabet.expression_to_charset(
                        character, self._parser_state.flags)
                if not is_charset:
                    value = (character, character)
                return value

            if self._range:
                if self._queue is None:
                    raise RxpyError('Incomplete range')
                else:
                    (alo, ahi) = unpack(self._queue)
                    (blo, bhi) = unpack(character)
                    self._charset.append_interval((alo, blo))
                    self._charset.append_interval((ahi, bhi))
                    self._queue = None
                    self._range = False
            else:
                if self._queue:
                    (lo, hi) = unpack(self._queue)
                    self._charset.append_interval((lo, lo))
                    self._charset.append_interval((hi, hi))
                self._queue = character

        char_str = self._parser_state.alphabet.expression_to_str(character)
        if self._invert is None and char_str == '^':
            self._invert = True
        elif not escaped and char_str == '\\':
            return SimpleEscapeBuilder(self._parser_state, self)
        elif escaped and char_str in 'dD':
            self._charset.append_class(self._parser_state.alphabet.digit,
                                       character, char_str=='D')
        elif escaped and char_str in 'wW':
            self._charset.append_class(self._parser_state.alphabet.word,
                                       character, char_str=='W')
        elif escaped and char_str in 'sS':
            self._charset.append_class(self._parser_state.alphabet.space,
                                       character, char_str=='S')
        # not charset allows first character to be unescaped - or ]
        elif character is not None and \
                ((not self._charset and not self._queue)
                 or escaped or char_str not in "-]"):
            append()
        elif char_str == '-':
            if self._range:
                # repeated - is range to -?
                append()
            else:
                self._range = True
        elif char_str == ']':
            if self._queue:
                if self._range:
                    self._range = False
                    # convert open range to '-'
                    append('-')
                append(None)
            if self._invert:
                self._charset.invert()
            self._parent._sequence.append(self._charset.simplify())
            return self._parent
        else:
            raise RxpyError('Syntax error in character set')

        # after first character this must be known
        if self._invert is None:
            self._invert = False

        return self


class SimpleEscapeBuilder(Builder):
    '''
    Parse the standard escaped characters, character codes
    (\\x, \\u and \\U, by delegating to `CharacterCodeBuilder`),
    and octal codes (\\000 etc, by delegating to `OctalEscapeBuilder`)
    '''

    def __init__(self, parser_state, parent):
        super(SimpleEscapeBuilder, self).__init__(parser_state)
        self._parent = parent
        self.__std_escapes = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n',
                              'r': '\r', 't': '\t', 'v': '\v'}

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is None:
            raise RxpyError('Incomplete character escape')
        elif char_str in 'xuU':
            return CharacterCodeBuilder(self._parser_state, self._parent, character)
        elif char_str in digits:
            return OctalEscapeBuilder(self._parser_state, self._parent, character)
        elif char_str in self.__std_escapes:
            return self._parent.append_character(
                        self.__std_escapes[char_str], escaped=True)
        elif char_str not in ascii_letters: # matches re.escape
            return self._parent.append_character(character, escaped=True)
        else:
            return self._unexpected_character(character)

    def _unexpected_character(self, character):
        self._parent.append_character(character, escaped=True)
        return self._parent


class IntermediateEscapeBuilder(SimpleEscapeBuilder):
    '''
    Extend `SimpleEscapeBuilder` to also handle group references (\\1 etc).
    '''

    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is None:
            raise RxpyError('Incomplete character escape')
        elif char_str in digits and char_str != '0':
            return GroupReferenceBuilder(self._parser_state, self._parent, character)
        else:
            return super(IntermediateEscapeBuilder, self).append_character(character)


class ComplexEscapeBuilder(IntermediateEscapeBuilder):
    '''
    Extend `IntermediateEscapeBuilder` to handle character classes
    (\\b, \\s etc).
    '''

    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is None:
            raise RxpyError('Incomplete character escape')
        elif char_str in digits and char_str != '0':
            return GroupReferenceBuilder(self._parser_state, self._parent, character)
        elif char_str == 'A':
            self._parent._sequence.append(StartOfLine(False))
            return self._parent
        elif char_str in 'bB':
            self._parent._sequence.append(WordBoundary(char_str=='B'))
            return self._parent
        elif char_str in 'dD':
            self._parent._sequence.append(Digit(char_str=='D'))
            return self._parent
        elif char_str in 'wW':
            self._parent._sequence.append(Word(char_str=='W'))
            return self._parent
        elif char_str in 'sS':
            self._parent._sequence.append(Space(char_str=='S'))
            return self._parent
        elif char_str == 'Z':
            self._parent._sequence.append(EndOfLine(False))
            return self._parent
        else:
            return super(ComplexEscapeBuilder, self).append_character(character)


class CharacterCodeBuilder(Builder):
    '''
    Parse character code escapes - expressions of the form \\x..., \\u...,
    and \\U....
    '''

    LENGTH = {'x': 2, 'u': 4, 'U': 8}

    def __init__(self, parser_state, parent, initial):
        super(CharacterCodeBuilder, self).__init__(parser_state)
        self.__parent = parent
        self.__buffer = ''
        self.__remaining = self.LENGTH[initial]

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        if character is None:
            raise RxpyError('Incomplete unicode escape')
        self.__buffer += character
        self.__remaining -= 1
        if self.__remaining:
            return self
        try:
            return self.__parent.append_character(
                    self._parser_state.alphabet.unescape(int(self.__buffer, 16)),
                    escaped=True)
        except:
            raise
            raise RxpyError('Bad unicode escape: ' + self.__buffer)


class OctalEscapeBuilder(Builder):
    '''
    Parse octal character code escapes - expressions of the form \\000.
    '''

    def __init__(self, parser_state, parent, initial=0):
        super(OctalEscapeBuilder, self).__init__(parser_state)
        self.__parent = parent
        self.__buffer = initial

    @staticmethod
    def decode(buffer, alphabet):
        '''Convert the octal sequence to a character.'''
        try:
            return alphabet.unescape(int(buffer, 8))
        except:
            raise RxpyError('Bad octal escape: ' + buffer)

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is not None and char_str in '01234567':
            self.__buffer += character
            if len(self.__buffer) == 3:
                return self.__parent.append_character(
                            self.decode(self.__buffer, self._parser_state.alphabet),
                            escaped=True)
            else:
                return self
        else:
            chain = self.__parent.append_character(
                            self.decode(self.__buffer, self._parser_state.alphabet),
                            escaped=True)
            return chain.append_character(character)


class GroupReferenceBuilder(Builder):
    '''
    Parse group references - expressions of the form \\1.
    This delegates to `OctalEscapeBuilder` when appropriate (ambiguous).
    '''

    def __init__(self, parser_state, parent, initial):
        super(GroupReferenceBuilder, self).__init__(parser_state)
        self.__parent = parent
        self.__buffer = initial

    def __octal(self):
        if len(self.__buffer) != 3:
            return False
        for c in self.__buffer:
            if c not in OCTAL:
                return False
        return True

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''
        char_str = self._parser_state.alphabet.expression_to_str(character)
        if character is not None and (
                (char_str in digits and len(self.__buffer) < 2) or
                (char_str in OCTAL and len(self.__buffer) < 3)):
            self.__buffer += char_str
            if self.__octal():
                return self.__parent.append_character(
                            OctalEscapeBuilder.decode(self.__buffer,
                                                      self._parser_state.alphabet),
                            escaped=True)
            else:
                return self
        else:
            self.__parent._sequence.append(GroupReference(self.__buffer))
            return self.__parent.append_character(character)


class CountBuilder(Builder):
    '''
    Parse explicit counted repeats - expressions of the form ...{n,m}.
    If the `_LOOP_UNROLL` flag is set then this expands the expression
    as an explicit series of repetitions, so 'a{2,4}' would become
    equivalent to 'aaa?a?'
    '''

    def __init__(self, parser_state, parent, open):
        super(CountBuilder, self).__init__(parser_state)
        self._parent = parent
        self._open = open
        self._begin = None
        self._end = None
        self._acc = ''
        self._range = False
        self._closed = False
        self._lazy = False

    #noinspection PyMethodOverriding
    def append_character(self, character):
        '''Add the next character.'''

        char_str = self._parser_state.alphabet.expression_to_str(character)

        if self._closed:
            if not self._lazy and char_str == '?':
                self._lazy = True
                return self
            else:
                self.__build()
                return self._parent.append_character(character)

        empty = not self._acc and self._begin is None
        if empty and char_str == '}':
            # oops - not a count at all
            self._parent.append_character(self._open, escaped=True)
            self._parent.append_character(character, escaped=True)
            return self._parent
        elif char_str == '}':
            self.__store_value()
            self._closed = True
        elif char_str == ',':
            self.__store_value()
        elif character is not None:
            self._acc += character
        else:
            raise RxpyError('Incomplete count specification')
        return self

    def __store_value(self):
        if self._begin is None:
            if not self._acc:
                raise RxpyError('Missing lower limit for repeat')
            else:
                try:
                    self._begin = int(self._acc)
                except ValueError:
                    raise RxpyError(
                            'Bad lower limit for repeat: ' + self._acc)
        else:
            if self._range:
                raise RxpyError('Too many values in repeat')
            self._range = True
            if self._acc:
                try:
                    self._end = int(self._acc)
                except ValueError:
                    raise RxpyError(
                            'Bad upper limit for repeat: ' + self._acc)
                if self._begin > self._end:
                    raise RxpyError('Inconsistent repeat range')
        self._acc = ''

    def __build(self):
        if not self._parent._sequence:
            raise RxpyError('Nothing to repeat')
        latest = self._parent._sequence.pop()
        if (self._parser_state.flags & ParserState._LOOP_UNROLL) and (
                (self._end is None and self._parser_state.unwind(self._begin)) or
                (self._end is not None and self._parser_state.unwind(self._end))):
            for _i in range(self._begin):
                self._parent._sequence.append(latest.clone())
            if self._range:
                if self._end is None:
                    RepeatBuilder.build_star(
                            self._parent, latest.clone(),
                            self._lazy, self._parser_state)
                else:
                    for _i in range(self._end - self._begin):
                        RepeatBuilder.build_optional(
                                self._parent, latest.clone(), self._lazy)
        else:
            self.build_count(self._parent, latest, self._begin,
                             self._end if self._range else self._begin,
                             self._lazy, self._parser_state)

    @staticmethod
    def build_count(parent, latest, begin, end, lazy, parser_state):
        '''
        If end is None, then range is open.
        '''
        RepeatBuilder.assert_consumer(latest, parser_state)
        loop = CountedLoop([latest], begin, end, parser_state=parser_state, lazy=lazy)
        parent._sequence.append(loop)


def parse_pattern(text, engine, flags=0, alphabet=None):
    '''
    Parse a standard regular expression.
    '''
    from lepl.rxpy.compat.support import default_alphabet
    alphabet = default_alphabet(alphabet, text)
    parser_state = ParserState(alphabet=alphabet, flags=flags,
                        refuse=engine.REFUSE, require=engine.REQUIRE)
    return parse(text, parser_state, SequenceBuilder)


def parse_groups(texts, engine, flags=0, alphabet=None):
    '''
    Parse set of expressions, used to define groups for `Scanner`.
    '''
    from lepl.rxpy.compat.support import default_alphabet
    if not texts:
        raise ValueError('Empty set of texts for scanner')
    alphabet = default_alphabet(alphabet, texts[0])
    parser_state = ParserState(flags=flags, alphabet=alphabet,
                        refuse=engine.REFUSE, require=engine.REQUIRE)
    sequence = SequenceBuilder(parser_state)
    for text in texts:
        sequence.parse_group(text)
    if parser_state.has_new_flags:
        parser_state = parser_state.clone_with_new_flags(texts[0])
        sequence = SequenceBuilder(parser_state)
        for text in texts:
            sequence.parse_group(text)
        if parser_state.has_new_flags:
            raise RxpyError('Inconsistent flags')
    return parser_state, sequence.to_sequence().join(Match(), parser_state)
