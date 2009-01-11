

from unittest import TestCase


from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.match import Any, And, Not, Or
from lepl.resources import managed
from lepl.trace import LogMixin


class BaseTest(TestCase):
    
    def assert_direct(self, stream, match, target):
        result = [x for (x, s) in match(stream)]
        assert target == result, result
    

class AndTest(BaseTest):

    def test_simple(self):
        basicConfig(level=DEBUG)
        self.assert_join([1], Any(), ['1'])
        self.assert_join([1,2], And(Any(), Any()), ['12'])
        self.assert_join([1,2,3], And(Any(), Any()), ['12'])
        self.assert_join([1], And(Any(), Any()), [])
        
    def test_and(self):
        basicConfig(level=DEBUG)
        self.assert_join([1,2], Any() & Any(), ['12'])
        self.assert_join([1,2,3], Any() & Any(), ['12'])
        self.assert_join([1,2,3], Any() & Any() & Any(), ['123'])
        self.assert_join([1], Any() & Any(), [])
        
    def assert_join(self, stream, match, target):
        result = [''.join(map(str, l)) 
                  for (l, s) in match(stream)]
        assert target == result, result

    def test_add(self):
        basicConfig(level=DEBUG)
        self.assert_direct(['1','2'], Any() + Any(), [['12']])
        self.assert_direct(['1','2','3'], Any() + Any(), [['12']])
        self.assert_direct(['1','2','3'], Any() + Any() + Any(), [['123']])
        self.assert_direct(['1'], Any() + Any(), [])
        

class OrTest(BaseTest):

    def test_simple(self):
        self.assert_direct('a', Or(Any('x'), Any('a'), Any()), [['a'],['a']])

    def test_bar(self):
        self.assert_direct('a', Any('x') | Any('a') | Any(), [['a'],['a']])


class NotTest(BaseTest):
    
    def test_simple(self):
        self.assert_direct('ab', Any() + Not(Any('c')) + Any(), [['ab']])
        self.assert_direct('ab', Any() + Not(Any('b')) + Any(), [])

    def test_bang(self):
        self.assert_direct('ab', Any() + ~Any('c') + Any(), [['ab']])
        self.assert_direct('ab', Any() + ~Any('b') + Any(), [])

        