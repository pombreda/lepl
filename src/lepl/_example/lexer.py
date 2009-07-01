
from logging import basicConfig, getLogger, DEBUG, INFO

from lepl import *
from lepl._example.support import Example


class LexerExample(Example):
    
    def test_add(self):
        
        #basicConfig(level=DEBUG)
        basicConfig(level=INFO)
        #getLogger('lepl.lexer.stream.lexed_simple_stream').setLevel(DEBUG)
        
        value = Token(UnsignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = value >> float
        add = number & ~symbol('+') & number > sum
        self.examples([
            (lambda: add.parse('12+30'), '[42.0]')])

    def test_bad(self):
        
        #basicConfig(level=DEBUG)
        basicConfig(level=INFO)
        getLogger('lepl.lexer.stream.lexed_simple_stream').setLevel(DEBUG)
        
        value = Token(SignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = value >> float
        add = number & ~symbol('+') & number > sum
        self.examples([
            (lambda: add.parse('12+30'), 'None')])

