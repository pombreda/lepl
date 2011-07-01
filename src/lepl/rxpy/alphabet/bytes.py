#LICENCE

'''
Logic related to ASCII input.
'''

from array import array
from string import digits, ascii_letters

from lepl.rxpy.alphabet.base import BaseAlphabet
from lepl.rxpy.parser.support import ParserState
from lepl.rxpy.support import RxpyError
from lepl.support.lib import fmt


ASCII_WORD = set(ascii_letters + digits + '_')


class Bytes(BaseAlphabet):
    '''
    Define character sets etc for byte-strings.
    
    See base class for full documentation.
    '''
        
    def __init__(self):
        super(Bytes, self).__init__(0, 127, b'\\')
        
    def code_to_letter(self, code):
        if code < 0 or code > 255:
            raise ValueError(fmt('Byte out of range: {}', code))
        return bytes([code])
    
    def letter_to_code(self, char):
        if len(char) != 1 or char[0] < 0 or char[0] > 255:
            raise ValueError(fmt('Byte out of range: {}', char))
        return char[0]

    def validate_expression(self, expression, flags):
        if not isinstance(expression, bytes):
            raise TypeError('Expression for bytes alphabet must be of type bytes')
        if flags & ParserState.UNICODE:
            raise ValueError('Cannot use UNICODE with bytes')

    def validate_input(self, input, flags):
        if not isinstance(input, bytes) and not isinstance(input, array):
            raise TypeError('Input for bytes alphabet must be bytes or array')

    def expression_to_letter(self, char):
        return bytes([char])

    def expression_to_str(self, char):
        return chr(char) if char is not None else None
    
    def letter_to_str(self, letter):
        return chr(letter[0])

    def join(self, *strings):
        '''
        Construct a word in the alphabet, given a list of words and/or
        characters.
        '''
        return b''.join(strings)

    def digit(self, char, flags):
        '''Test whether the character is a digit or not.'''
        if flags & ParserState.UNICODE:
            raise ValueError('Cannot use UNICODE flag with bytes')
        return char and char in b'0123456789'
    
    def space(self, char, flags):
        '''Test whether the character is a whitespace or not.'''
        if flags & ParserState.UNICODE:
            raise ValueError('Cannot use UNICODE flag with bytes')
        return char and char in b' \t\n\r\f\v'
        
    def word(self, char, flags):
        '''Test whether the character is a word character or not.'''
        if flags & ParserState.UNICODE:
            raise ValueError('Cannot use UNICODE flag with bytes')
        return char and chr(char[0]) in ASCII_WORD
    
    def expression_to_charset(self, char, flags):
        from lepl.rxpy.parser.support import ParserState
        if flags & ParserState.UNICODE:
            raise ValueError('Cannot use UNICODE flag with bytes')
        # restrict case conversion to 7bit values
        if flags & ParserState.IGNORECASE and char < 128:
            lo = chr(char).lower().encode('ascii')
            hi = chr(char).upper()
            if lo != hi:
                return True, (lo, hi)
        return False, self.expression_to_letter(char)
    
    def unescape(self, code):
        '''For compatibility with python.'''
        if code < 512:
            return self.code_to_letter(code % 256)
        else:
            raise RxpyError('Unexpected character code for ASCII: ' + str(code))
