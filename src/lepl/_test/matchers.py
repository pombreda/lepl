
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers import * 
from lepl.node import Node
from lepl.parser import string_parser, tagged
from lepl.support import LogMixin


class BaseTest(TestCase):
    
    def assert_direct(self, stream, match, target):
        result = [x for (x, s) in match.match_string(stream, config=Configuration())]
        assert target == result, result
    
    def assert_list(self, stream, match, target):
        matcher = match.list_matcher()
#        print(matcher.matcher)
        result = [x for (x, s) in matcher(stream)]
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
                  for (l, s) in match.match_list(stream)]
        assert target == result, result

    def test_add(self):
        basicConfig(level=DEBUG)
        self.assert_list(['1','2'], Any() + Any(), [['12']])
        self.assert_list(['1','2','3'], Any() + Any(), [['12']])
        self.assert_list(['1','2','3'], Any() + Any() + Any(), [['123']])
        self.assert_list(['1'], Any() + Any(), [])
    
    
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
        self.assert_simple([1], 1, 1, 'd', ['0'])
        self.assert_simple([1], 1, 2, 'd', ['0'])
        self.assert_simple([2], 1, 1, 'd', ['0','1'])
        self.assert_simple([2], 1, 2, 'd', ['0','1'])
        self.assert_simple([2], 0, 2, 'd', ['0','1', ''])
        self.assert_simple([1,2], 1, 1, 'd', ['0'])
        self.assert_simple([1,2], 1, 2, 'd', ['00','01', '0'])
        self.assert_simple([1,2], 2, 2, 'd', ['00','01'])
        self.assert_simple([1,2], 1, 2, 'b', ['0', '00','01'])
        self.assert_simple([1,2], 1, 2, 'g', ['00', '01','0'])
        
    def assert_simple(self, stream, start, stop, step, target):
        result = [''.join(map(str, l)) 
                  for (l, s) in Repeat(RangeMatch(), start, stop, step).match_list(stream)]
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
        self.assert_mixin(r[1:2:'b'], [1,2], ['0', '00','01'])
        self.assert_mixin(r[1:2:'d'], [1,2], ['00', '01','0'])
        try:        
            self.assert_mixin(r[1::'x'], [1,2,3], [])
            assert False, 'expected error'
        except ValueError:
            pass
    
    def assert_mixin(self, match, stream, target):
        result = [''.join(map(str, l)) for (l, s) in match.match_list(stream)]
        assert target == result, result
       
    def test_separator(self):
        basicConfig(level=DEBUG)
        self.assert_separator('a', 1, 1, 'd', ['a'])
        self.assert_separator('a', 1, 1, 'b', ['a'])
        self.assert_separator('a,a', 1, 2, 'd', ['a,a', 'a'])
        self.assert_separator('a,a', 1, 2, 'b', ['a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'd', ['a,a,a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'b', ['a,a', 'a,a,a'])
        
    def assert_separator(self, stream, start, stop, step, target):
        result = [''.join(l) 
                  for (l, s) in Repeat(Any('abc'), start, stop, step, Any(',')).match_string(stream)]
        assert target == result, result
        
    def test_separator_mixin(self):
        basicConfig(level=DEBUG)
        abc = Any('abc')
        self.assert_separator_mixin(abc[1:1:'d',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:1:'b',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:2:'d',','], 'a,b', ['a,b', 'a'])
        self.assert_separator_mixin(abc[1:2:'b',','], 'a,b', ['a', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'d',','], 'a,b,c,a', ['a,b,c', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'b',','], 'a,b,c,a', ['a,b', 'a,b,c'])

    def assert_separator_mixin(self, matcher, stream, target):
        result = [''.join(map(str, l)) for (l, s) in matcher.match_string(stream)]
        assert target == result, result
    
class RangeMatch(BaseMatcher):
    '''
    We test repetition by looking at "strings" of integers, where the 
    matcher for any particular value returns all values less than the
    current value. 
    '''
    
    def __init__(self):
        super(RangeMatch, self).__init__()
    
    @tagged
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
            (Any()[0::'b'] + (Literal('d') | 
                              Literal('cd') + Commit() | 
                              Literal('bcd')) + Eof()), 
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
        
        
class EofTest(BaseTest):
    
    def test_eof(self):
        self.assert_direct('foo ', 'foo' / Eof(), [['foo', ' ']])
        

class LiteralTest(BaseTest):
    
    def test_literal(self):
        self.assert_direct('foo ', Literal('foo'), [['foo']])
        
        
class TransformTest(BaseTest):
    
    @staticmethod
    def mkappend(x):
        return lambda a: a + x
    
    def test_apply(self):
        # note extra list 
        self.assert_direct('foo ', Literal('foo') > self.mkappend(['b']), [[['foo', 'b']]])
        
    def test_kapply(self):
        # note extra list 
        self.assert_direct('foo ', Literal('foo') >> self.mkappend('b'), [['foob']])
        
    def test_nested(self):
        # note extra list 
        self.assert_direct('foo ', 
                           (Literal('foo') >> self.mkappend('b')) > self.mkappend(['c']), 
                           [[['foob', 'c']]])
        
       