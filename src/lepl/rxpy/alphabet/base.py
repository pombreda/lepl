#LICENCE

'''
Base class for alphabets.
'''
from lepl.rxpy.support import UnsupportedOperation, RxpyError
from lepl.support.lib import unimplemented


#noinspection PyUnusedLocal
class BaseAlphabet(object):
    '''
    Defines the interface that all alphabets must implement.

    An alphabet assumes that there's a mapping between "characters" and
    integers, such that each character maps to a separate value in a
    contiguous region between `min` and `max`.  This defines an ordering that
    is used, for example, to infer the content of character ranges.
    '''

    def __init__(self, min, max):
        '''
        min and max define the range of values that `char_to_code` will map
        characters to (inclusive).
        '''
        self.min = min
        self.max = max

    @unimplemented
    def code_to_char(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''

    @unimplemented
    def char_to_code(self, char):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''

    @unimplemented
    def coerce(self, char):
        '''
        Force a character in str, unicode, or the alphabet itself, to be a
        member of the alphabet.
        '''

    @unimplemented
    def join(self, *strings):
        '''
        Construct a word in the alphabet, given a list of words and/or
        characters.
        '''

    @unimplemented
    def to_str(self, char):
        '''
        Support display of the character.

        Note - this is the basis of hash and equality for intervals, so must
        be unique, repeatable, etc.
        '''

    def after(self, char):
        '''The character "before" the given one, or None.'''
        code = self.char_to_code(char)
        if code < self.max:
            return self.code_to_char(code + 1)
        else:
            return None

    def before(self, char):
        '''The character "before" the given one, or None.'''
        code = self.char_to_code(char)
        if code > self.min:
            return self.code_to_char(code - 1)
        else:
            return None

    def digit(self, char):
        '''Test whether the character is a digit or not.'''
        raise UnsupportedOperation('digit')

    def space(self, char):
        '''Test whether the character is a whitespace or not.'''
        raise UnsupportedOperation('space')

    def word(self, char):
        '''Test whether the character is a word character or not.'''
        raise UnsupportedOperation('word')

    def unpack(self, char, flags):
        '''Return either (True, CharSet) or (False, char)'''
        from lepl.rxpy.parser.support import ParserState
        if flags & ParserState.IGNORE_CASE:
            raise RxpyError('Default alphabet does not handle case')
        return False, self.join(self.coerce(char))

    def unescape(self, code):
        '''By default, assume escape codes map to character codes.'''
        return self.code_to_char(code)
