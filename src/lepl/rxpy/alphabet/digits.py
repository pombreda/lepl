#LICENCE

'''
Logic related to input of lists of digits (this is a proof of
concept used to test non-string data).
'''

from itertools import chain

from lepl.rxpy.alphabet.base import BaseAlphabet


class Digits(BaseAlphabet):
    '''
    Define character sets etc for lists of single digits.  The expression is
    a string, while the alphabet is a list of ints with values between 0 and 9.
    Each "letter" is a singleton list containing an int (in this way we have
    letters being the same type as sentences, as with strings).
    
    See base class for full documentation.
    '''
    
    def __init__(self):
        super(Digits, self).__init__(0, 9, None)
        
    def code_to_letter(self, code):
        '''
        Convert a code - an integer value between min and max, that maps the
        alphabet to a contiguous set of integers - to a character in the
        alphabet.
        '''
        return [code]
    
    def letter_to_code(self, char):
        '''
        Convert a character in the alphabet to a code - an integer value
        between min and max, that maps the alphabet to a contiguous set of
        integers.
        '''
        return char[0]
        
    def validate_expression(self, expression, flags):
        if not isinstance(expression, str):
            raise TypeError('Expression for digits alphabet must be a string')

    def validate_input(self, input, flags):
        if not isinstance(input, list) or (list and not isinstance(input[0], int)):
            raise TypeError('Input for digits alphabet must be a list of integers')

    def expression_to_letter(self, char):
        return [int(char)]

    def expression_to_str(self, char):
        return char

    def letter_to_str(self, letter):
        return None if letter is None else str(letter[0])

    def expression_to_charset(self, char, flags):
        return (False, [int(char)])

    def join(self, *letters):
        return list(chain(*letters))

    def unescape(self, code):
        return [code]

    def digit(self, char, flags):
        return True

    def space(self, char, flags):
        return False

    def word(self, char, flags):
        return False