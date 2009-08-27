
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.lexer.matchers import Token
from lepl.functions import Word, Letter
from lepl.offside.config import IndentationConfiguration
from lepl.offside.lexer import Indentation


class IndentationTest(TestCase):
    
    def test_indentation(self):
        basicConfig(level=DEBUG)
        text = '''
left
    four'''
        word = Token(Word(Letter()))
        indent = Indentation()
        line1 = indent('')
        line2 = indent('') & word('left')
        line3 = indent('    ') & word('four')
        parser = (line1 & line2 & line3).string_parser(
                                        config=IndentationConfiguration())
        result = parser(text)
        assert result == ['', '', 'left', '    ', 'four'], result
        
        