#LICENCE

'''
Logic related to string (Unicode) input.
'''

from string import digits
from sys import maxunicode
from unicodedata import category

from lepl.rxpy.alphabet.base import BaseAlphabet
from lepl.rxpy.parser.support import ParserState
from lepl.support.lib import basestring
from lepl.rxpy.alphabet.bytes import ASCII_WORD


UNICODE_WORD = {'Ll', 'Lo', 'Lt', 'Lu', 'Mc', 'Me', 'Mn', 'Nd', 'Nl', 'No', 'Pc'}


class String(BaseAlphabet):
    '''
    Define character sets etc for (Unicode) strings.  This expects the
    regular expression to also be a Unicode string.
    
    See base class for full documentation.
    '''
    
    def __init__(self):
        super(String, self).__init__(0, maxunicode, '\\')
        
    def code_to_letter(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''
        return chr(code)
    
    def letter_to_code(self, letter):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''
        return ord(letter)
        
    def validate_expression(self, expression, flags):
        if not isinstance(expression, basestring):
            raise TypeError('Expression for string (Unicode) alphabet must be a string')

    def validate_input(self, input, flags):
        if not isinstance(input, basestring):
            raise TypeError('Input for string (Unicode) alphabet must be a string')

    def expression_to_letter(self, char):
        return char

    def expression_to_str(self, char):
        return char if char else None

    def letter_to_str(self, letter):
        if letter is None: return None
        text = repr(letter)
        if text[0] == 'u':
            text = text[1:]
        return text[1:-1] # drop quotes

    def expression_to_charset(self, char, flags):
        from lepl.rxpy.parser.support import ParserState
        if flags & ParserState.IGNORECASE and \
                (flags & ParserState.UNICODE or ord(char) < 128):
            lo = char.lower()
            hi = char.upper()
            if lo != hi:
                return True, (lo, hi)
        return False, char

    def join(self, *strings):
        '''
        Construct a word in the alphabet, given a list of words and/or
        characters.
        '''
        return ''.join(strings)
        
    def digit(self, char, flags):
        '''Test whether the character is a digit or not.'''
        # http://bugs.python.org/issue1693050
        if flags & ParserState.ASCII:
            return char in digits
        else:
            return char and category(char) == 'Nd'

    def space(self, char, flags):
        '''Test whether the character is a whitespace or not.'''
        # http://bugs.python.org/issue1693050
        return char and (char in ' \t\n\r\f\v' or
                         (flags & ParserState.UNICODE and category(char) == 'Z'))

    def word(self, char, flags):
        '''Test whether the character is a word character or not.'''
        # http://bugs.python.org/issue1693050
        return char and (char in ASCII_WORD or
                (flags & ParserState.UNICODE and category(char) in UNICODE_WORD))
    
    def unescape(self, code):
        '''No idea why, but needed for some tests.'''
        return self.code_to_letter(code % 256)
