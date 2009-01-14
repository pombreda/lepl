

from unittest import TestCase


from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.match import * 
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
    
    
class CoercionTest(BaseTest):
    
    def test_right(self):
        basicConfig(level=DEBUG)
        self.assert_direct('12', Any() + '2', [['12']])
         
    def test_left(self):
        basicConfig(level=DEBUG)
        self.assert_direct('12', '1' + Any(), [['12']])
         

class OrTest(BaseTest):

    def test_simple(self):
        self.assert_direct('a', Or(Any('x'), Any('a'), Any()), [['a'],['a']])

    def test_bar(self):
        self.assert_direct('a', Any('x') | Any('a') | Any(), [['a'],['a']])


class LookaheadTest(BaseTest):
    
    def test_simple(self):
        self.assert_direct('ab', Any() + Lookahead('c') + Any(), [])
        self.assert_direct('ab', Any() + Lookahead('b') + Any(), [['ab']])

    def test_bang(self):
        self.assert_direct('ab', Any() + ~Lookahead('c') + Any(), [['ab']])
        self.assert_direct('ab', Any() + ~Lookahead('b') + Any(), [])


class RepeatTest(TestCase):

    def test_simple(self):
        basicConfig(level=DEBUG)
        self.assert_simple([1], 1, 1, -1, ['0'])
        self.assert_simple([1], 1, 2, -1, ['0'])
        self.assert_simple([2], 1, 1, -1, ['0','1'])
        self.assert_simple([2], 1, 2, -1, ['0','1'])
        self.assert_simple([2], 0, 2, -1, ['0','1', ''])
        self.assert_simple([1,2], 1, 1, -1, ['0'])
        self.assert_simple([1,2], 1, 2, -1, ['00','01', '0'])
        self.assert_simple([1,2], 2, 2, -1, ['00','01'])
        self.assert_simple([1,2], 1, 2, 1, ['0', '00','01'])
        self.assert_simple([1,2,3], 1, None, 2, ['0', '000', '001', '002', '010', '011', '012'])
        self.assert_simple([1,2,3], 1, 3, -2, ['000', '001', '002', '010', '011', '012', '0'])
        
    def assert_simple(self, stream, start, stop, step, target):
        result = [''.join(map(str, l)) 
                  for (l, s) in Repeat(RangeMatch(), start, stop, step)(stream)]
        assert target == result, result
        
    def test_mixin(self):
        basicConfig(level=DEBUG)
        r = RangeMatch()
        self.assert_mixin(r[1:1], [1], ['0'])
        self.assert_mixin(r[1:2], [1], ['0'])
        self.assert_mixin(r[1:1], [2], ['0','1'])
        self.assert_mixin(r[1:2], [2], ['0','1'])
        self.assert_mixin(r[0:], [2], ['0','1', ''])
        self.assert_mixin(r[:], [2], ['0','1', ''])
        self.assert_mixin(r[0:2], [2], ['0','1', ''])
        self.assert_mixin(r[1], [1,2], ['0'])
        self.assert_mixin(r[1:2], [1,2], ['00','01', '0'])
        self.assert_mixin(r[2], [1,2], ['00','01'])
        self.assert_mixin(r[1:2:1], [1,2], ['0', '00','01'])
        self.assert_mixin(r[1::2], [1,2,3], ['0', '000', '001', '002', '010', '011', '012'])
        self.assert_mixin(r[1:3:-2], [1,2,3], ['000', '001', '002', '010', '011', '012', '0'])
        try:        
            self.assert_mixin(r[1::-2], [1,2,3], [])
            assert False, 'expected error'
        except ValueError:
            pass
    
    def assert_mixin(self, match, stream, target):
        result = [''.join(map(str, l)) for (l, s) in match(stream)]
        assert target == result, result
       
    def test_separator(self):
        basicConfig(level=DEBUG)
        self.assert_separator('a', 1, 1, -1, ['a'])
        self.assert_separator('a', 1, 1, 1, ['a'])
        self.assert_separator('a,a', 1, 2, -1, ['a,a', 'a'])
        self.assert_separator('a,a', 1, 2, 1, ['a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, -1, ['a,a,a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 1, ['a,a', 'a,a,a'])
        
    def assert_separator(self, stream, start, stop, step, target):
        result = [''.join(l) 
                  for (l, s) in Repeat(Any('abc'), start, stop, step, Any(','))(stream)]
        assert target == result, result
        
    def test_separator_mixin(self):
        basicConfig(level=DEBUG)
        abc = Any('abc')
        self.assert_separator_mixin(abc[1:1:-1,','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:1:1,','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:2:-1,','], 'a,b', ['a,b', 'a'])
        self.assert_separator_mixin(abc[1:2:1,','], 'a,b', ['a', 'a,b'])
        self.assert_separator_mixin(abc[2:3:-1,','], 'a,b,c,a', ['a,b,c', 'a,b'])
        self.assert_separator_mixin(abc[2:3:1,','], 'a,b,c,a', ['a,b', 'a,b,c'])

    def assert_separator_mixin(self, match, stream, target):
        result = [''.join(map(str, l)) for (l, s) in match(stream)]
        assert target == result, result
    
class RangeMatch(BaseMatch):
    '''
    We test repetition by looking at "strings" of integers, where the 
    matcher for any particular value returns all values less than the
    current value. 
    '''
    
    def __init__(self):
        super().__init__()
    
    @managed
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])


class SpaceTest(BaseTest):
    
    def test_space(self):
        self.assert_direct('  ', Space(), [[' ']])
        self.assert_direct('  ', Space()[0:], [[' ', ' '], [' '], []])
        self.assert_direct('  ', Space()[0:,...], [['  '], [' '], []])
        
    def test_slash(self):
        ab = Any('ab')
        self.assert_direct('ab', ab / ab, [['a', 'b']])
        self.assert_direct('a b', ab / ab, [['a', ' ', 'b']])
        self.assert_direct('a  b', ab / ab, [['a', '  ', 'b']])
        self.assert_direct('ab', ab // ab, [])
        self.assert_direct('a b', ab // ab, [['a', ' ', 'b']])
        self.assert_direct('a  b', ab // ab, [['a', '  ', 'b']])

 
class CommitTest(BaseTest):
    
    def test_commit(self):
        self.assert_direct('abcd', 
            (Any()[0::-1] + (Literal('d') | 
                             Literal('cd') + Commit() | 
                             Literal('bcd')) + Eof()).match_string(min_queue=100), 
            [['abcd'], ['abcd']])
        

class RegexpTest(BaseTest):
    
    def test_group(self):
        self.assert_direct('  123x', Regexp(r'\s*\d+') & Any(), [['  123', 'x']])
        
    def test_groups(self):
        self.assert_direct('  123x', Regexp(r'\s*(\d)(\d+)') & Any(), [['1','23','x']])


class WordTest(BaseTest):
    
    def test_phone(self):
        self.assert_direct('andrew, 3333253', Word() / ',' / Integer() / Eof(), 
                           [['andrew', ',', ' ', '3333253']])
        