#LICENCE

'''
Logic related to Unicode input.
'''


from sys import maxunicode

from lepl.rxpy.alphabet.base import BaseAlphabet


WORD = set(['Ll', 'Lo', 'Lt', 'Lu', 'Mc', 'Me', 'Mn', 'Nd', 'Nl', 'No', 'Pc'])


class Unicode(BaseAlphabet):
    '''
    Define character sets etc for Unicode strings.
    
    See base class for full documentation.
    '''
    
    def __init__(self):
        super(Unicode, self).__init__(0, maxunicode)
        
    def code_to_char(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''
        return chr(code)
    
    def char_to_code(self, char):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''
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
        text = repr(unicode(char))
        if text[0] == 'u':
            text = text[1:]
        return text[1:-1]

    def digit(self, char):
        '''Test whether the character is a digit or not.'''
        # http://bugs.python.org/issue1693050
        return char and category(self.coerce(char)) == 'Nd'

    def space(self, char):
        '''Test whether the character is a whitespace or not.'''
        # http://bugs.python.org/issue1693050
        if char:
            c = self.coerce(char)
            return c in ' \t\n\r\f\v' or category(c) == 'Z'
        else:
            return False
        
    def word(self, char):
        '''Test whether the character is a word character or not.'''
        # http://bugs.python.org/issue1693050
        return char and category(self.coerce(char)) in WORD
    
    def unpack(self, char, flags):
        '''
        Return either (True, (lo, hi)) or (False, char)
        '''
        from lepl.rxpy.parser.support import ParserState
        char = self.join(self.coerce(char))
        if flags & ParserState.IGNORE_CASE:
            lo = char.lower()
            hi = char.upper()
            if lo != hi:
                return True, (lo, hi)
        return False, char
