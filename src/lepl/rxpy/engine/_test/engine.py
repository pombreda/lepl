#LICENCE
from lepl.matchers.derived import Real
from lepl.regexp.rewriters import CompileRegexp

from lepl.rxpy.parser.pattern import EmptyError
from lepl.rxpy.parser.support import ParserState
from lepl.rxpy.support import RxpyError
from lepl.rxpy.engine._test.base import BaseTest


class EngineTest(BaseTest):
    
    def test_string(self):
        assert self.engine(self.parse('abc'), 'abc')
        assert self.engine(self.parse('abc'), 'abcd')
        assert not self.engine(self.parse('abc'), 'ab')
        
    def test_dot(self):
        assert self.engine(self.parse('a.c'), 'abc')
        assert self.engine(self.parse('...'), 'abcd')
        assert not self.engine(self.parse('...'), 'ab')
        assert not self.engine(self.parse('a.b'), 'a\nb')
        assert self.engine(self.parse('a.b', flags=ParserState.DOT_ALL), 'a\nb')
       
    def test_char(self):
        assert self.engine(self.parse('[ab]'), 'a')
        assert self.engine(self.parse('[ab]'), 'b')
        assert not self.engine(self.parse('[ab]'), 'c')

    def test_group(self):
        groups = self.engine(self.parse('(.).'), 'ab')
        assert len(groups) == 1, len(groups)
        groups = self.engine(self.parse('((.).)'), 'ab')
        assert len(groups) == 2, len(groups)
        
    def test_group_reference(self):
        assert self.engine(self.parse('(.)\\1'), 'aa')
        assert not self.engine(self.parse('(.)\\1'), 'ab')
        self.parse('\\1(.)')
        try:
            self.parse('\\1')
            assert False, 'expected error'
        except RxpyError:
            pass
 
    def test_split(self):
        assert self.engine(self.parse('a*b'), 'b')
        assert self.engine(self.parse('a*b'), 'ab')
        assert self.engine(self.parse('a*b'), 'aab')
        assert not self.engine(self.parse('a*b'), 'aa')
        groups = self.engine(self.parse('a*'), 'aaa')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('a*'), 'aab')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        assert self.engine(self.parse('a*'), 'a')
        assert self.engine(self.parse('a*'), 'aa')
        assert self.engine(self.parse('a*'), '')
        assert self.engine(self.parse('a+'), 'a')
        assert self.engine(self.parse('a+'), 'aa')
        assert not self.engine(self.parse('a+'), '')
        
    def test_nested_group(self):
        groups = self.engine(self.parse('(.)*'), 'ab')
        assert len(groups) == 1

    def test_lookahead(self):
        assert self.engine(self.parse('a(?=b)'), 'ab')
        assert not self.engine(self.parse('a(?=b)'), 'ac')
        assert not self.engine(self.parse('a(?!b)'), 'ab')
        assert self.engine(self.parse('a(?!b)'), 'ac')
    
    def test_lookback(self):
        assert self.engine(self.parse('.(?<=a)'), 'a')
        assert not self.engine(self.parse('.(?<=a)'), 'b')
        assert not self.engine(self.parse('.(?<!a)'), 'a')
        assert self.engine(self.parse('.(?<!a)'), 'b')
    
    def test_lookback_bug_1(self):
        result = self.engine(self.parse('.*(?<!abc)(d.f)'), 'abcdefdof')
        assert result.group(1) == 'dof', result.group(1)
        result = self.engine(self.parse('(?<!abc)(d.f)'), 'abcdefdof', search=True)
        assert result.group(1) == 'dof', result.group(1)
        
    def test_lookback_bug_2(self):
        assert not self.engine(self.parse(r'.*(?<=\bx)a'), 'xxa')
        assert self.engine(self.parse(r'.*(?<!\bx)a'), 'xxa')
        assert not self.engine(self.parse(r'.*(?<!\Bx)a'), 'xxa')
        assert self.engine(self.parse(r'.*(?<=\Bx)a'), 'xxa')
    
    def test_conditional(self):
        assert self.engine(self.parse('(.)?b(?(1)\\1)'), 'aba')
        assert not self.engine(self.parse('(.)?b(?(1)\\1)'), 'abc')
        assert self.engine(self.parse('(.)?b(?(1)\\1|c)'), 'bc')
        assert not self.engine(self.parse('(.)?b(?(1)\\1|c)'), 'bd')
        
    def test_star_etc(self):
        assert self.engine(self.parse('a*b'), 'b')
        assert self.engine(self.parse('a*b'), 'ab')
        assert self.engine(self.parse('a*b'), 'aab')
        assert not self.engine(self.parse('a+b'), 'b')
        assert self.engine(self.parse('a+b'), 'ab')
        assert self.engine(self.parse('a+b'), 'aab')
        assert self.engine(self.parse('a?b'), 'b')
        assert self.engine(self.parse('a?b'), 'ab')
        assert not self.engine(self.parse('a?b'), 'aab')
        
        assert self.engine(self.parse('a*b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a*b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert self.engine(self.parse('a*b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert not self.engine(self.parse('a+b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a+b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert self.engine(self.parse('a+b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert self.engine(self.parse('a?b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a?b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert not self.engine(self.parse('a?b', flags=ParserState._LOOP_UNROLL), 'aab')

    def test_counted(self):
        groups = self.engine(self.parse('a{2}', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('a{2}?', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}?', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}?', flags=ParserState._LOOP_UNROLL), 'aaa')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}?b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}?b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        
        assert self.engine(self.parse('a{0,}?b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a{0,}?b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert self.engine(self.parse('a{0,}?b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert not self.engine(self.parse('a{1,}?b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a{1,}?b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert self.engine(self.parse('a{1,}?b', flags=ParserState._LOOP_UNROLL), 'aab')
        assert self.engine(self.parse('a{0,1}?b', flags=ParserState._LOOP_UNROLL), 'b')
        assert self.engine(self.parse('a{0,1}?b', flags=ParserState._LOOP_UNROLL), 'ab')
        assert not self.engine(self.parse('a{0,1}?b', flags=ParserState._LOOP_UNROLL), 'aab')

        groups = self.engine(self.parse('a{2}'), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}'), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}'), 'aaa')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('a{2}?'), 'aaa')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}?'), 'aaa')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}?'), 'aaa')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,2}?b'), 'aab')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('a{1,}?b'), 'aab')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        
        assert self.engine(self.parse('a{0,}?b'), 'b')
        assert self.engine(self.parse('a{0,}?b'), 'ab')
        assert self.engine(self.parse('a{0,}?b'), 'aab')
        assert not self.engine(self.parse('a{1,}?b'), 'b')
        assert self.engine(self.parse('a{1,}?b'), 'ab')
        assert self.engine(self.parse('a{1,}?b'), 'aab')
        assert self.engine(self.parse('a{0,1}?b'), 'b')
        assert self.engine(self.parse('a{0,1}?b'), 'ab')
        assert not self.engine(self.parse('a{0,1}?b'), 'aab')

    def test_ascii_escapes(self):
        groups = self.engine(self.parse('\\d*', flags=ParserState.ASCII), '12x')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('\\D*', flags=ParserState.ASCII), 'x12')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('\\w*', flags=ParserState.ASCII), '12x a')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('\\W*', flags=ParserState.ASCII), ' a')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('\\s*', flags=ParserState.ASCII), '  a')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('\\S*', flags=ParserState.ASCII), 'aa ')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        assert self.engine(self.parse(r'a\b ', flags=ParserState.ASCII), 'a ')
        assert not self.engine(self.parse(r'a\bb', flags=ParserState.ASCII), 'ab')
        assert not self.engine(self.parse(r'a\B ', flags=ParserState.ASCII), 'a ')
        assert self.engine(self.parse(r'a\Bb', flags=ParserState.ASCII), 'ab')
        groups = self.engine(self.parse(r'\s*\b\w+\b\s*', flags=ParserState.ASCII), ' a ')
        assert groups.data(0)[0] == ' a ', groups.data(0)[0]
        groups = self.engine(self.parse(r'(\s*(\b\w+\b)\s*){3}', flags=ParserState._LOOP_UNROLL|ParserState.ASCII), ' a ab abc ')
        assert groups.data(0)[0] == ' a ab abc ', groups.data(0)[0]
        
    def test_unicode_escapes(self):
        groups = self.engine(self.parse('\\d*'), '12x')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('\\D*'), 'x12')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('\\w*'), '12x a')
        assert len(groups.data(0)[0]) == 3, groups.data(0)[0]
        groups = self.engine(self.parse('\\W*'), ' a')
        assert len(groups.data(0)[0]) == 1, groups.data(0)[0]
        groups = self.engine(self.parse('\\s*'), '  a')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        groups = self.engine(self.parse('\\S*'), 'aa ')
        assert len(groups.data(0)[0]) == 2, groups.data(0)[0]
        assert self.engine(self.parse(r'a\b '), 'a ')
        assert not self.engine(self.parse(r'a\bb'), 'ab')
        assert not self.engine(self.parse(r'a\B '), 'a ')
        assert self.engine(self.parse(r'a\Bb'), 'ab')
        groups = self.engine(self.parse(r'\s*\b\w+\b\s*'), ' a ')
        assert groups.data(0)[0] == ' a ', groups.data(0)[0]
        groups = self.engine(self.parse(r'(\s*(\b\w+\b)\s*){3}', flags=ParserState._LOOP_UNROLL), ' a ab abc ')
        assert groups.data(0)[0] == ' a ab abc ', groups.data(0)[0]
    
    def test_or(self):
        assert self.engine(self.parse('a|b'), 'a')
        assert self.engine(self.parse('a|b'), 'b')
        assert not self.engine(self.parse('a|b'), 'c')
        assert self.engine(self.parse('(?:a|ac)$'), 'ac')

    def test_search(self):
        assert self.engine(self.parse('a'), 'ab', search=True)
        assert self.engine(self.parse('$'), '', search=True)
        assert self.engine(self.parse('$'), 'a', search=True)
        
    def test_end_of_line(self):
        assert self.engine(self.parse('ab$'), 'ab')
        assert self.engine(self.parse('ab$'), 'ab\n')
        assert not self.engine(self.parse('ab$'), 'abc')
        assert not self.engine(self.parse('ab$'), 'ab\nc')
        assert self.engine(self.parse('(?m)ab$'), 'ab\nc')
        
    def test_groups_in_lookback(self):
        result = self.engine(self.parse('(.).(?<=a(.))'), 'ab')
        assert result
        assert result.group(1) == 'a'
        assert result.group(2) == 'b', result.group(2)

        assert self.engine(self.parse('(.).(?<=(?(1)))'), 'ab')
        try:
            self.parse('(.).(?<=(?(2)))')
            assert False, 'expected error'
        except RxpyError:
            pass
        
        assert self.engine(self.parse('(a)b(?<=b)(c)'), 'abc')
        assert not self.engine(self.parse('(a)b(?<=c)(c)'), 'abc')
        assert self.engine(self.parse('(a)b(?=c)(c)'), 'abc')
        assert not self.engine(self.parse('(a)b(?=b)(c)'), 'abc')
        
        assert not self.engine(self.parse('(?:(a)|(x))b(?<=(?(2)x|c))c'), 'abc')
        assert not self.engine(self.parse('(?:(a)|(x))b(?<=(?(2)b|x))c'), 'abc')
        assert self.engine(self.parse('(?:(a)|(x))b(?<=(?(2)x|b))c'), 'abc')
        assert not self.engine(self.parse('(?:(a)|(x))b(?<=(?(1)c|x))c'), 'abc')
        assert self.engine(self.parse('(?:(a)|(x))b(?<=(?(1)b|x))c'), 'abc')
        
        assert self.engine(self.parse('(?:(a)|(x))b(?=(?(2)x|c))c'), 'abc')
        assert not self.engine(self.parse('(?:(a)|(x))b(?=(?(2)c|x))c'), 'abc')
        assert self.engine(self.parse('(?:(a)|(x))b(?=(?(2)x|c))c'), 'abc')
        assert not self.engine(self.parse('(?:(a)|(x))b(?=(?(1)b|x))c'), 'abc')
        assert self.engine(self.parse('(?:(a)|(x))b(?=(?(1)c|x))c'), 'abc')
      
        assert not self.engine(self.parse('(a)b(?<=(?(2)x|c))(c)'), 'abc')
        assert not self.engine(self.parse('(a)b(?<=(?(2)b|x))(c)'), 'abc')
        assert not self.engine(self.parse('(a)b(?<=(?(1)c|x))(c)'), 'abc')
        assert self.engine(self.parse('(a)b(?<=(?(1)b|x))(c)'), 'abc')
        
        assert self.engine(self.parse('(a)b(?=(?(2)x|c))(c)'), 'abc')
        assert not self.engine(self.parse('(a)b(?=(?(2)b|x))(c)'), 'abc')
        assert self.engine(self.parse('(a)b(?=(?(1)c|x))(c)'), 'abc')
        
    def test_empty_loops(self):
        try:
            self.parse('a**')
            assert False, 'expected error'
        except RxpyError:
            pass
        try:
            self.parse('(?_e)a**')
            assert False, 'expected error'
        except RxpyError:
            pass
        
        try:
            self.parse('a{0,1}*')
            assert False, 'expected error'
        except EmptyError:
            pass
        self.parse('(?_e)a{0,1}*')
        
        try:
            self.parse('(?_l)a{0,1}*')
            assert False, 'expected error'
        except EmptyError:
            pass
        self.parse('(?_l_e)a{0,1}*')
            
        try:
            self.parse('(a|)*')
            assert False, 'expected error'
        except EmptyError:
            pass
        self.parse('(?_e)(a|)*')

        self.parse('a{1,1}*')
        self.parse('(?_l)a{1,1}*')

        try:
            self.parse('(a|)*')
            assert False, 'expected error'
        except EmptyError:
            pass
        self.parse('a(?:b|(c|e){1,2}?|d)+?')
        
    def test_extended_groups(self):
        try:
            self.parse('(?P<4>.)(?P<4>).')
            assert False, 'expected error'
        except RxpyError:
            pass
        result = self.engine(self.parse('(?_g)(?P<4>.)(?P<4>.)'), 'ab')
        assert result
        assert result.group(4) == 'b'
        assert len(result) == 1
        
    def test_repeat(self):
        assert self.engine(self.parse('a{20}b{10}c'), 20*'a' + 10*'b' + 'c')
        assert self.engine(self.parse('a{20,}b{0,10}c'), 20*'a' + 10*'b' + 'c')
        assert not self.engine(self.parse('a{20,}b{0,9}c'), 20*'a' + 10*'b' + 'c')
        assert not self.engine(self.parse('a{21,}b{0,10}c'), 20*'a' + 10*'b' + 'c')
        assert self.engine(self.parse('a{19,21}b{9,11}c'), 20*'a' + 10*'b' + 'c')
        result = self.engine(self.parse('a{3,4}'), 'aaaa')
        assert result.group(0) == 'aaaa', result.group(0)
        result = self.engine(self.parse('a{3,4}?'), 'aaaa')
        assert result.group(0) == 'aaa', result.group(0)

    def test_prime(self):
        assert self.engine(self.parse('^1?$|^(11+?)\1+$'), 1*'1')
        assert not self.engine(self.parse(r'^1?$|^(11+?)\1+$'), 2*'1')
        assert self.engine(self.parse(r'^1?$|^(11+?)\1+$'), 4*'1')
        assert self.engine(self.parse(r'^1?$|^(11+?)\1+$'), 100*'1')
        assert not self.engine(self.parse(r'^1?$|^(11+?)\1+$'), 101*'1')

    def test_real(self):
        compiler = CompileRegexp()
        regexp = str(compiler(Real()).regexp)
        parsed = self.parse(regexp)
        assert self.engine(parsed, '1')
        assert self.engine(parsed, '1.2')
        assert self.engine(parsed, '1.2e3')
        assert self.engine(parsed, '-1')
        assert self.engine(parsed, '-1.2')
        assert self.engine(parsed, '-1.2e3')
        assert self.engine(parsed, '1.2e-3')
        assert self.engine(parsed, '-1.2e-3')
