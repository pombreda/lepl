#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.base import BaseTest
from lepl.rxpy.engine.simple.engine import SimpleEngine


class SimpleEngineTest(BaseTest, TestCase):

    def default_engine(self):
        return SimpleEngine
    
    def test_string(self):
        assert self.engine(self.parse('a'), 'a')
        assert not self.engine(self.parse('a'), 'b')
        assert self.engine(self.parse('a'), 'ba', search=True)
        assert self.engine(self.parse('abc'), 'abc')
        assert not self.engine(self.parse('abcd'), 'abc')
        
    def test_dot(self):
        assert self.engine(self.parse('.'), 'a')
        assert not self.engine(self.parse('..'), 'a')
        assert not self.engine(self.parse('.a'), 'abb', search=True)
        assert self.engine(self.parse('.a'), 'aba', search=True)

    def test_start_of_line(self):
        assert self.engine(self.parse('^'), 'a')
        assert self.engine(self.parse('^a'), 'a')
        assert not self.engine(self.parse('a^'), 'a')
        assert not self.engine(self.parse('a^'), 'ab')
        assert not self.engine(self.parse('^b'), 'a\nb')
        assert not self.engine(self.parse('(?m)^b'), 'a\nb')
        assert self.engine(self.parse('(?m)^b'), 'a\nb', search=True)

    def test_split(self):
        assert self.engine(self.parse('(?:a|b)'), 'a')
        assert self.engine(self.parse('(?:a|b)'), 'b')
        assert not self.engine(self.parse('(?:a|b)'), 'c')

    def test_lookahead(self):
        assert self.engine(self.parse('a(?=b)'), 'ab')
        assert not self.engine(self.parse('a(?=c)'), 'ab')
        assert not self.engine(self.parse('a(?!b)'), 'ab')
        assert self.engine(self.parse('a(?!c)'), 'ab')
        assert self.engine(self.parse('b(?<=ab)'), 'ab', search=True)
        assert not self.engine(self.parse('b(?<=cb)'), 'ab', search=True)
        assert not self.engine(self.parse('b(?<!ab)'), 'ab', search=True)
        assert self.engine(self.parse('b(?<!cb)'), 'ab', search=True)
        
    def test_checkpoint(self):
        assert self.engine(self.parse('(?_e)(?:|a)*'), 'ab')
        assert self.engine(self.parse('(?_e)(?:|a)*'), 'b')
        