#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.base import BaseTest
from lepl.rxpy.engine.lexer.engine import LexerEngine


class LexerEngineTest(BaseTest, TestCase):

    def default_engine(self):
        return LexerEngine
    
    def test_string(self):
        assert self.engine(self.parse('a'), 'a')
        assert not self.engine(self.parse('a'), 'b')
        assert self.engine(self.parse('abc'), 'abc')
        assert not self.engine(self.parse('abcd'), 'abc')
        
    def test_dot(self):
        assert self.engine(self.parse('.'), 'a')
        assert not self.engine(self.parse('..'), 'a')

    def test_start_of_line(self):
        assert self.engine(self.parse('^'), 'a')
        assert self.engine(self.parse('^a'), 'a')
        assert not self.engine(self.parse('a^'), 'a')
        assert not self.engine(self.parse('a^'), 'ab')
        assert not self.engine(self.parse('^b'), 'a\nb')
        assert not self.engine(self.parse('(?m)^b'), 'a\nb')

    def test_split(self):
        assert self.engine(self.parse('(?:a|b)'), 'a')
        assert self.engine(self.parse('(?:a|b)'), 'b')
        assert not self.engine(self.parse('(?:a|b)'), 'c')

    def test_checkpoint(self):
        assert self.engine(self.parse('(?_e)(?:|a)*'), 'ab')
        assert self.engine(self.parse('(?_e)(?:|a)*'), 'b')
        