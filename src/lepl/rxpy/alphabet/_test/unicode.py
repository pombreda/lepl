#LICENCE

from unittest import TestCase

from lepl.rxpy.alphabet.ascii import Ascii
from lepl.rxpy.graph.opcode import Character


class CharacterTest(TestCase):
    
    def do_test_str(self, intervals, target):
        result = str(Character(intervals, Ascii()))
        assert result == target, result
    
    def test_str(self):
        self.do_test_str([], '[]')
        self.do_test_str([('a','a')], '[a]')
        self.do_test_str([('a','b')], '[ab]')
        self.do_test_str([('a','c')], '[a-c]')
        self.do_test_str([('a','a'), ('b', 'b')], '[ab]')
       
    def test_coallesce(self):
        self.do_test_str([('a','a'), ('c', 'c')], '[ac]')
        self.do_test_str([('a','a'), ('b', 'c')], '[a-c]')
        self.do_test_str([('a','b'), ('a', 'c')], '[a-c]')
        self.do_test_str([('a','b'), ('b', 'c')], '[a-c]')
        self.do_test_str([('a','c'), ('c', 'c')], '[a-c]')
        self.do_test_str([('b','c'), ('a', 'b')], '[a-c]')
        self.do_test_str([('c','c'), ('a', 'a')], '[ac]')
        self.do_test_str([('a','c'), ('p', 's')], '[a-cp-s]')
        self.do_test_str([('b','c'), ('p', 's')], '[bcp-s]')
        self.do_test_str([('b','c'), ('a', 's')], '[a-s]')
    
    def test_reversed(self):
        self.do_test_str([('c','a')], '[a-c]')
        self.do_test_str([('b','a')], '[ab]')
        self.do_test_str([('b','a'), ('b', 'c')], '[a-c]')
    
    def test_contains(self):
        assert 'a' not in Character([('b', 'b')], Ascii())
        assert 'b' in Character([('b', 'b')], Ascii())
        assert 'c' not in Character([('b', 'b')], Ascii())
        assert 'a' in Character([('a', 'b')], Ascii())
        assert 'b' in Character([('a', 'b')], Ascii())
        assert 'c' not in Character([('a', 'b')], Ascii())
        assert 'a' in Character([('a', 'c')], Ascii())
        assert 'b' in Character([('a', 'c')], Ascii())
        assert 'c' in Character([('a', 'c')], Ascii())
        assert 'a' in Character([('a', 'b'), ('b', 'c')], Ascii())
        assert 'b' in Character([('a', 'b'), ('b', 'c')], Ascii())
        assert 'c' in Character([('a', 'b'), ('b', 'c')], Ascii())
        assert 'a' in Character([('a', 'a'), ('c', 'c')], Ascii())
        assert 'b' not in Character([('a', 'a'), ('c', 'c')], Ascii())
        assert 'c' in Character([('a', 'a'), ('c', 'c')], Ascii())
