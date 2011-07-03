#LICENCE

'''
These are both graph nodes, constructed from the regexp text (based on
classes from base_graph), and opcodes for the engine (the target interface,
based on classes from base_compilable).
'''

from lepl.rxpy.graph.base_compilable import NextCompilableMixin, \
    SimpleCompilableMixin, BranchCompilableMixin, SelfIdCompilableMixin, BranchCompilableMixin2
from lepl.rxpy.graph.base_graph import BaseNode, BaseGroupReference, \
    BaseLabelledNode, BaseLineNode, BaseEscapedNode
from lepl.rxpy.graph.support import ReadsGroup, CharSet


class String(BaseNode, NextCompilableMixin):
    '''
    Match a series of literal characters.

    - `text` will contain the characters (in the form appropriate for the
      alphabet)

    - `next` will contain a single value, which is the opcode to use if the
      match is successful.
    '''

    def __init__(self, text):
        super(String, self).__init__(consumes=True, size=len(text))
        self.text = text

    def __str__(self):
        return self.text

    def extend(self, text, parser_state):
        '''Extend the text to match.'''
        # TODO - use alphabet from parser state!
        self.text += text
        self.size = len(self.text)

    def _untranslated_args(self):
        return [self.text]


class StartGroup(BaseGroupReference, SimpleCompilableMixin):
    '''
    Mark the start of a group (to be saved).

    - `number` is the index for the group.

    - `next` will contain a single value, which is the following opcode.
    '''

    def __init__(self, number):
        assert isinstance(number, int)
        super(StartGroup, self).__init__(number, consumes=False, size=0)

    def __str__(self):
        return "(?P<%s>" % self.number


class EndGroup(BaseGroupReference, SimpleCompilableMixin):
    '''
    Mark the end of a group (to be saved).

    - `number` is the index for the group.

    - `next` will contain a single value, which is the following opcode.
    '''

    def __init__(self, number):
        assert isinstance(number, int)
        super(EndGroup, self).__init__(number, consumes=False, size=0)

    def __str__(self):
        return ")"


class Split(BaseLabelledNode, BranchCompilableMixin):
    '''
    Branch the graph, providing alternative matches for the current context
    (eg via backtracking on failure).

    - `label` is a string for display (since this node represents many
      different parts of a regexp, like `|` and `*`).

    - `next` contains the alternatives, in ordered priority (`next[0]` first).
      There should be more than 1, but only `|` should give more than 2.
      However, the number of alternatives is not something the engine should
      assume (I may be wrong, or there may be a "bug" that generates a single
      entry in some cases, for example).
    '''

    def __init__(self, label, consumes=None):
        super(Split, self).__init__(label=label, consumes=consumes,
                                    size=None if consumes is None else 0)
        self.fixed.remove('consumes') # set via constructor

    def length(self, groups, known=None):
        '''
        Exact runtime length (with groups) or None.
        '''
        if known is None:
            known = set()
        known.add(self)
        # avoid triggering loop detection via alternative different paths
        avoid_loops = set(known)
        size = self.next[0].length(groups, known)
        if size is not None:
            for next in self.next[1:]:
                if size != next.length(groups, set(avoid_loops)):
                    return None
            return size
        else:
            return None

    def _compile_args(self):
        return []


class Match(BaseNode, SimpleCompilableMixin):
    '''
    The terminal node.  If the engine "reaches" here then the match was a
    success.

    - `next` is undefined.
    '''

    def __init__(self):
        super(Match, self).__init__(consumes=False, size=0)

    def __str__(self):
        return 'Match'

    def length(self, groups, known=None):
        '''
        Exact runtime length is 0.
        '''
        return 0


class NoMatch(BaseNode, SimpleCompilableMixin):
    '''
    The current match has failed.  Currently this is generated when an attempt
    is made to match the complement of `.` (since `.` matches everything, the
    complement matches nothing).

    - `next` is undefined.
    '''
    # TODO - remove by rewriting graph

    def __init__(self):
        super(NoMatch, self).__init__(consumes=False, size=0)

    def __str__(self):
        return 'NoMatch'


class Dot(BaseLineNode, SimpleCompilableMixin):
    '''
    Match "any" single character.  The exact behaviour will depend on the
    alphabet and `multiline` (see the Python `re` documentation).

    - `multiline` indicates whether multiline mode is enabled (see the Python
      `re` documentation).

    - `next` will contain a single value, which is the opcode to use if the
      match is successful.
    '''

    def __init__(self, multiline):
        super(Dot, self).__init__(multiline, consumes=True, size=1)

    def __str__(self):
        return '.'


class StartOfLine(BaseLineNode, SimpleCompilableMixin):
    '''
    Match the start of a line.  The exact behaviour will depend on the
    alphabet and `multiline` (see the Python `re` documentation).

    - `multiline` indicates whether multiline mode is enabled (see the Python
      `re` documentation).

    - `next` will contain a single value, which is the opcode to use if the
      match is successful.
    '''

    def __init__(self, multiline):
        super(StartOfLine, self).__init__(multiline, consumes=False, size=0)

    def __str__(self):
        return '^'


class EndOfLine(BaseLineNode, SimpleCompilableMixin):
    '''
    Match the end of a line.  The exact behaviour will depend on the
    alphabet and `multiline` (see the Python `re` documentation).

    - `multiline` indicates whether multiline mode is enabled (see the Python
      `re` documentation).

    - `next` will contain a single value, which is the opcode to use if the
      match is successful.
    '''

    def __init__(self, multiline):
        super(EndOfLine, self).__init__(multiline, consumes=False, size=0)

    def __str__(self):
        return '$'


class GroupReference(BaseGroupReference, ReadsGroup, NextCompilableMixin):
    '''
    Match the text previously matched by the given group.

    - `number` is the group index.

    - `next` will contain a single value, which is the opcode to use if the
      match is successful.
    '''

    def __init__(self, number):
        super(GroupReference, self).__init__(number, consumes=None, size=None)

    def __str__(self):
        return '\\' + str(self.number)

    def length(self, groups, known=None):
        '''
        Exact runtime length depends on whether group was found.
        '''
        if known is None:
            known = set()
        if self not in known:
            known.add(self)
            if groups and groups.data(self.number) is not None:
                return len(groups.group(self.number))


class Lookahead(BaseNode, BranchCompilableMixin2):
    '''
    Lookahead match (one that does not consume any input).

    - `equal` is `True` if the lookahead should succeed for the match to
      continue and `False` if the lookahead should fail.

    - `forwards` is `True` if the lookahead should start from the current
      position and `False` if it should end there.

    - `next` contains two values.  `next[1]` is the lookahead expression;
      `next[0]` is the continuation of the normal match on success.

    For lookbacks (`forwards` is `False`) the expression has a postfix of "$"
    so that direct searching (not matching) of the string up to the current
    point provides the to check.  Engines are welcome to use more efficient
    approaches, as long as the results remain correct.
    '''

    def __init__(self, equal, forwards, reads=False, mutates=False):
        super(Lookahead, self).__init__(consumes=False, size=0)
        self.equal = equal
        self.forwards = forwards
        self.reads = reads
        self.mutates = mutates

    def __str__(self):
        return '(?' + \
            ('' if self.forwards else '<') + \
            ('=' if self.equal else '!') + '...)'

    def _compile_args(self):
        args = super(Lookahead, self)._compile_args()
        args.append(lambda graph: self.next[1].length(graph))
        return args


class Repeat(BaseNode, BranchCompilableMixin):
    '''
    A numerical repeat (used in, for example, `CountedLoop`).

    - `begin` is the minimum count value.

    - `end` is the maximum count value (None for open ranges).

    - `lazy` indicates that matching should be lazy if `True`.

    - `next` contains two values.  `next[1]` is the expression to repeat
      (which loops back to here); `next[0]` is the continuation of the match
      after repetition has finished.
    '''

    def __init__(self, begin, end, lazy):
        super(Repeat, self).__init__(consumes=None, size=None)
        self.begin = begin
        self.end = end
        self.lazy = lazy

    def __str__(self):
        text = '{' + str(self.begin)
        if self.end != self.begin:
            text += ','
            if self.end is not None:
                text += str(self.end)
        text += '}'
        if self.lazy:
            text += '?'
        return text

    def length(self, groups, known=None):
        '''
        Exact length can be calculated only for a fixed number of repeats.
        '''
        if known is None:
            known = set()
        if self.end == self.begin and self not in known:
            known.add(self)
            return self.begin * self.next[1].length(groups, known)


class Conditional(BaseLabelledNode, BaseGroupReference, ReadsGroup,
                  BranchCompilableMixin):
    '''
    Branch the graph, depending on the existence of a group.

    - `number` is the group index.

    - `label` is used to generate an informative graph plot.

    - `next` contains two nodes.  If the group exists, matching should continue
      with `next[1]`, otherwise with `next[0]`.
    '''

    def __init__(self, number, label):
        if str(number) not in label:
            label = '(?(' + str(number) + ')' + label + ')'
        super(Conditional, self).__init__(label=label,
                                               number=number, consumes=None)

    def length(self, groups, known=None):
        '''
        Exact length depends on branch.
        '''
        if known is None:
            known = set()
        if self not in known:
            known.add(self)
            if groups:
                if groups.data(self.number) is not None:
                    return self.next[1].length(groups, known)
                else:
                    return self.next[0].length(groups, known)

    def _compile_args(self):
        return [self.number]


class WordBoundary(BaseEscapedNode, SimpleCompilableMixin):
    '''
    Match a word boundary.  See Python `re` documentation and `BaseAlphabet.word`.

    - `inverted` indicates whether the test should succeed.  If `inverted` is
      `False` then the match should continue if the test succeeds; if `False`
      then the test should fail.
    '''

    def __init__(self, inverted=False):
        super(WordBoundary, self).__init__('b', inverted, consumes=False, size=0)


class Digit(BaseEscapedNode, SimpleCompilableMixin):
    '''
    Match a digit.  See `BaseAlphabet.digit`.

    - `inverted` indicates whether the test should succeed.  If `inverted` is
      `False` then the match should continue if the test succeeds; if `False`
      then the test should fail.
    '''

    def __init__(self, inverted=False):
        super(Digit, self).__init__('d', inverted, consumes=True, size=1)


class Space(BaseEscapedNode, SimpleCompilableMixin):
    '''
    Match a space.  See `BaseAlphabet.space`.

    - `inverted` indicates whether the test should succeed.  If `inverted` is
      `False` then the match should continue if the test succeeds; if `False`
      then the test should fail.
    '''

    def __init__(self, inverted=False):
        super(Space, self).__init__('s', inverted, consumes=True, size=1)


class Word(BaseEscapedNode, SimpleCompilableMixin):
    '''
    Match a word character.  See `BaseAlphabet.word`.

    - `inverted` indicates whether the test should succeed.  If `inverted` is
      `False` then the match should continue if the test succeeds; if `False`
      then the test should fail.
    '''

    def __init__(self, inverted=False):
        super(Word, self).__init__('w', inverted, consumes=True, size=1)


class Character(BaseNode, SimpleCompilableMixin):
    '''
    Match a single character.  Currently the `__contains__` method should be
    used for testing; that will call the `BaseAlphabet` as required.

    How can this be improved?

    - `intervals` define simple character ranges (eg. 0-9).

    - `alphabet` is the alphabet used.

    - `classes` is a list of `(class_, label, invert)` triplets, where:
      - `class_` is a method on `alphabet` (eg. `.digit`)
      - `label` is used for display
      - `invert` is true if `class_` should fail

    - `inverted` is a global boolean that inverts the entire result (if `True`
      the test should fail).

    - `complete` is True if the test (without `invert`) will always succeed.
    '''

    def __init__(self, intervals, alphabet, classes=None,
                 inverted=False, complete=False):
        super(Character, self).__init__(consumes=True, size=1)
        self.__simple = CharSet(intervals, alphabet)
        self.alphabet = alphabet
        self.classes = classes if classes else []
        self.inverted = inverted
        self.complete = complete

    def _kargs(self):
        kargs = super(Character, self)._kargs()
        kargs['intervals'] = self.__simple.intervals
        return kargs

    def _compile_args(self):
        return [self]

    def append_interval(self, interval):
        '''Add an additional interval.'''
        self.__simple.append(interval, self.alphabet)

    def append_class(self, class_, label, inverted=False):
        '''Add a character class (see class docs).'''
        for (class2, _, inverted2) in self.classes:
            if class_ == class2:
                self.complete = self.complete or inverted != inverted2
                # if inverted matches, complete, else we already have it
                return
        self.classes.append((class_, label, inverted))

    def invert(self):
        '''Invert the selection.'''
        self.inverted = not self.inverted

    def __contains__(self, character):
        result = self.complete
        if not result:
            for (class_, _, invert) in self.classes:
                result = class_(character) != invert
                if result:
                    break
        if not result:
            result = character in self.__simple
        if self.inverted:
            result = not result
        return result

    def __str__(self):
        '''This returns (the illegal) [^] for all and [] for none.'''
        if self.complete:
            return '[]' if self.inverted else '[^]'
        contents = ''.join('\\' + label for (_, label, _) in self.classes)
        contents += self.__simple.to_str(self.alphabet)
        return '[' + ('^' if self.inverted else '') + contents + ']'

    def __hash__(self):
        return hash(str(self))

    def __bool__(self):
        return bool(self.classes or self.__simple)

    def __nonzero__(self):
        return self.__bool__()

    def simplify(self):
        '''Reduce to a simpler opcode if possible.'''
        if self.complete:
            if self.inverted:
                return NoMatch()
            else:
                return Dot(True)
        else:
            if self.classes or self.inverted:
                return self
            else:
                return self.__simple.simplify(self.alphabet, self)


class Checkpoint(BaseNode, SelfIdCompilableMixin):
    '''
    Repetition of this point should include consumption of input.  This lets
    us detect and about infinite loops while using as little state and logic
    in the engine as possible.
    '''

    def __init__(self):
        # guarantees consumption of region
        super(Checkpoint, self).__init__(consumes=True, size=0)

    def __str__(self):
        return '!'

