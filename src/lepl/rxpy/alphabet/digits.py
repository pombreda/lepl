#LICENCE

'''
Logic related to input of lists of digits (this is a proof of
concept used to test non-string data).
'''

from lepl.rxpy.alphabet.base import BaseAlphabet


class Digits(BaseAlphabet):
    '''
    Define character sets etc for lists of single digits.
    
    See base class for full documentation.
    '''
    
    def __init__(self):
        super(Digits, self).__init__(0, 9)
        
    def code_to_char(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''
        return code
    
    def char_to_code(self, char):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''
        return int(char)
        
    def coerce(self, char):
        '''
        Force a character in str, unicode, or the alphabet itself, to be a
        member of the alphabet.
        '''
        return int(char)
        
    def join(self, *strings):
        '''
        Construct a word in the alphabet, given a list of words and/or
        characters.
        '''
        def flatten(list_):
            '''Flatten lists.'''
            for value in list_:
                if isinstance(value, list):
                    for digit in flatten(value):
                        yield digit
                else:
                    yield value
        return list(flatten(strings))
        
    def to_str(self, char):
        '''
        Display the character.
        
        Note - this is the basis of hash and equality for intervals, so must
        be unique, repeatable, etc.
        '''
        return unicode(char)
