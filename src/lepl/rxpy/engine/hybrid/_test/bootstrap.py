#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.base import BaseTest
from lepl.rxpy.engine.hybrid.engine import HybridEngine


class HybridEngineTest(BaseTest, TestCase):

    def default_engine(self):
        return HybridEngine
    
    def test_string(self):
        assert self.engine(self.parse('a'), 'a')
        assert not self.engine(self.parse('a'), 'b')
        assert self.engine(self.parse('a'), 'ba', search=True)
        assert self.engine(self.parse('abc'), 'abc')
        assert not self.engine(self.parse('abcd'), 'abc')
        
    def test_groups(self):
        self.assert_groups('(.)', 'a', {0: ('a', 0, 1), 1: ('a', 0, 1)})
        self.assert_groups('.(.)(.)', 'abc', 
                           {0: ('abc', 0, 3), 1: ('b', 1, 2), 2: ('c', 2, 3)})
    
    def test_null_group_bug(self):
        assert self.engine(self.parse('(a(?=\s[^a]))'), 'a b')
        
        