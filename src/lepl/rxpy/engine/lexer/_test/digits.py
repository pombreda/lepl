#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.digits import DigitsTest
from lepl.rxpy.engine.lexer.engine import LexerEngine


class LexerDigitsTest(DigitsTest, TestCase):
    
    def default_engine(self):
        return LexerEngine

    def test_nested_group(self):
        pass
    
    def test_groups(self):
        pass
    
    def test_group_reference(self):
        pass
    
    def test_group(self):
        pass

    def test_conditional(self):
        pass
    
    # search

    def test_lookahead(self):
        pass

    def test_lookback(self):
        pass

    def test_search(self):
        pass
