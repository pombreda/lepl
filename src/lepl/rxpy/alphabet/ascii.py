#LICENCE

'''
Logic related to ASCII input.
'''

from string import digits, ascii_letters

from lepl.rxpy.alphabet.base import BaseAlphabet
from lepl.rxpy.support import RxpyError


WORD = set(ascii_letters + digits + '_')


class Ascii(BaseAlphabet):
    '''
    Define character sets etc for ASCII strings.  We could maybe extend or
    subclass this for Locale-dependent logic.
    
    See base class for full documentation.
    '''
        
    def __init__(self):
        super(Ascii, self).__init__(0, 127)
        
    def code_to_char(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''
        # TODO - check range
        return chr(code)
    
    def char_to_code(self, char):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''
        # TODO - check range
        return ord(char)
        
    def coerce(self, char):
        '''
        Force a character in str, unicode, or the alphabet itself, to be a
        member of the alphabet.
        '''
        return str(char)
    
    def join(self, *strings):
        '''
        Construct a word in the alphabet, given a list of words and/or
        characters.
        '''
        return self.coerce('').join(strings)

    def to_str(self, char):
        '''
        Display the character.
        
        Note - this is the basis of hash and equality for intervals, so must
        be unique, repeatable, etc.
        '''
        return repr(char)[1:-1]

    def digit(self, char):
        '''Test whether the character is a digit or not.'''
        return char and char in digits
    
    def space(self, char):
        '''Test whether the character is a whitespace or not.'''
        return char and char in ' \t\n\r\f\v'
        
    def word(self, char):
        '''Test whether the character is a word character or not.'''
        return char in WORD
    
    def unpack(self, char, flags):
        '''
        Return either (True, (lo, hi)) or (False, char)
        '''
        from lepl.rxpy.parser.support import ParserState
        char = self.join(self.coerce(char))
        # restrict case conversion to 7bit values
        if flags & ParserState.IGNORE_CASE and self.char_to_code(char) < 128:
            lo = char.lower()
            hi = char.upper()
            if lo != hi:
                return True, (lo, hi)
        return False, char
    
    def unescape(self, code):
        '''For compatibility with python.'''
        if code < 512:
            return self.code_to_char(code % 256)
        else:
            raise RxpyError('Unexpected character code for ASCII: ' + str(code))
