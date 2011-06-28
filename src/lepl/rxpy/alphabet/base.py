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

    An alphabet defines the data expected for input/output when matching.

    Note that this is not the same as the type used to express the regular
    expression itself (which is almost always a string - the only exception
    is bytes, which require bytes for input, to be consistent with Python).
    Below I will call this the "expression type".

    It must do several things:

    - Define a mapping between "letters" (atomic fragments of input) and
      integers, to form a contiguous range between min and max.  This is
      used for character ranges.

    - Validate the expression type (almost always strings - see above)

    - Provide a conversion from the expression type to the alphabet's
      letters.

    - Provide a conversion from the expression type to Unicode, so that
      the parser can check for symbols like "*".

    - Provide a conversion from numerical values (escape sequences) to the
      alphabet's letters.

    - Combine letters to form a "sentence" (a list or string).

    - Define classes for characters (digits, case, etc).
    '''

    def __init__(self, min, max, escape):
        '''
        min and max define the range of values that `letter_to_code` will map
        characters to (inclusive).
        '''
        self.min = min
        self.max = max
        self.escape = escape

    @unimplemented
    def code_to_letter(self, letter):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''

    @unimplemented
    def letter_to_code(self, letter):
        '''
        Convert a letter in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''

    @unimplemented
    def validate_expression(self, expression, flags):
        '''
        Raise an exception if the expression is not of the correct type.
        '''

    @unimplemented
    def validate_input(self, input, flags):
        '''
        Raise an exception if the input is not of the correct type.
        '''

    @unimplemented
    def expression_to_letter(self, char):
        '''
        Convert from the expression type to the alphabet letter type.
        '''

    @unimplemented
    def expression_to_str(self, char):
        '''
        Convert from the expression type to the str type.  The result
        is compared against "*" etc by the parser and for display of
        character ranges.

        This must return None when passed None.
        '''

    @unimplemented
    def letter_to_str(self, letter):
        '''
        Convert a letter in the alphabet to a form suitable for display
        (eg. for Unicode, this might be a letter to escape sequence).
        '''

    def expression_to_charset(self, char, flags):
        '''
        Given an input character (of expression type), return either a charset
        or a letter from the alphabet.

        Return either (True, CharSet) or (False, letter)
        '''
        from lepl.rxpy.parser.support import ParserState
        if flags & ParserState.IGNORE_CASE:
            raise RxpyError('Default alphabet does not handle case')
        return False, self.join(self.expression_to_letter(char))

    @unimplemented
    def join(self, *letters):
        '''
        Construct a sentence in the alphabet, given a list of letters or
        sentences (typically letters and sentences are the same type in
        Python).
        '''

    def unescape(self, code):
        '''
        Called to handle "escape codes".

        By default, assume escape codes map to character codes.
        '''
        return self.code_to_letter(code)

    def after(self, char):
        '''The character "before" the given one, or None.'''
        code = self.letter_to_code(char)
        if code < self.max:
            return self.code_to_letter(code + 1)
        else:
            return None

    def before(self, char):
        '''The character "before" the given one, or None.'''
        code = self.letter_to_code(char)
        if code > self.min:
            return self.code_to_letter(code - 1)
        else:
            return None

    def digit(self, char, flags):
        '''Test whether the character is a digit or not.'''
        raise UnsupportedOperation('digit')

    def space(self, char, flags):
        '''Test whether the character is a whitespace or not.'''
        raise UnsupportedOperation('space')

    def word(self, char, flags):
        '''Test whether the character is a word character or not.'''
        raise UnsupportedOperation('word')

