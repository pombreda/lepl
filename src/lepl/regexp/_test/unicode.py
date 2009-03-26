
from unittest import TestCase

from logging import basicConfig, DEBUG, getLogger
from lepl import *
from lepl.regexp.unicode import *


def _test_parser(text):
    return unicode_single_parser('label', text)

class CharactersTest(TestCase):
    
    def test_dot(self):
        #basicConfig(level=DEBUG)
        c = _test_parser('.')
        assert '.' == str(c), str(c)
        c = _test_parser('.\\.')
        assert '.\\.' == str(c), str(c)

    def test_brackets(self):
        #basicConfig(level=DEBUG)
        c = _test_parser('a')
        assert 'a' == str(c), str(c)
        c = _test_parser('[ac]')
        assert '[ac]' == str(c), str(c)
        c = _test_parser('[a-c]')
        assert '[a-c]' == str(c), str(c)
        c = _test_parser('[a-cp-q]')
        assert '[a-cp-q]' == str(c), str(c)
        c = _test_parser(r'\\')
        assert r'\\' == str(c), str(c)
        c = _test_parser(r'\-')
        assert r'\-' == str(c), str(c)
        c = _test_parser(r'[\\-x]')
        assert r'[\\-x]' == str(c), str(c)
        c = _test_parser('[a-bq,]')
        assert '[,a-bq]' == str(c), str(c)
        c = _test_parser('[a-b,q]')
        assert '[,a-bq]' == str(c), str(c)
        c = _test_parser('[,a-bq]')
        assert '[,a-bq]' == str(c), str(c)
        c = _test_parser('[^a]')
        assert '[^a]' == str(c), str(c)
   
    def test_merge(self):
        c = _test_parser('[a-ce-g]')
        assert '[a-ce-g]' == str(c), str(c)
        c = _test_parser('[a-cd-f]')
        assert '[a-f]' == str(c), str(c)
        c = _test_parser('[a-cc-e]')
        assert '[a-e]' == str(c), str(c)
        c = _test_parser('[a-cb-d]')
        assert '[a-d]' == str(c), str(c)
        c = _test_parser('[a-ca-c]')
        assert '[a-c]' == str(c), str(c)
        c = _test_parser('[a-a]')
        assert 'a' == str(c), str(c)
        c = _test_parser('[e-ga-c]')
        assert '[a-ce-g]' == str(c), str(c)
        c = _test_parser('[d-fa-c]')
        assert '[a-f]' == str(c), str(c)
        c = _test_parser('[c-ea-c]')
        assert '[a-e]' == str(c), str(c)
        c = _test_parser('[b-da-c]')
        assert '[a-d]' == str(c), str(c)
        c = _test_parser('[a-gc-e]')
        assert '[a-g]' == str(c), str(c)
        c = _test_parser('[c-ea-g]')
        assert '[a-g]' == str(c), str(c)
        c = _test_parser('[a-eg]')
        assert '[a-eg]' == str(c), str(c)
        c = _test_parser('[ga-e]')
        assert '[a-eg]' == str(c), str(c)

    def test_star(self):
        c = _test_parser('a*')
        assert 'a*' == str(c), str(c)
        c = _test_parser('a(bc)*d')
        assert 'a(bc)*d' == str(c), str(c)
        c = _test_parser('a(bc)*d[e-g]*')
        assert 'a(bc)*d[e-g]*' == str(c), str(c)
        c = _test_parser('a[a-cx]*')
        assert 'a[a-cx]*' == str(c), str(c)
        
    def test_option(self):
        c = _test_parser('a?')
        assert 'a?' == str(c), str(c)
        c = _test_parser('a(bc)?d')
        assert 'a(bc)?d' == str(c), str(c)
        c = _test_parser('a(bc)?d[e-g]?')
        assert 'a(bc)?d[e-g]?' == str(c), str(c)
        c = _test_parser('ab?c')
        assert 'ab?c' == str(c), str(c)
        
    def test_choice(self):
        c = _test_parser('(a*|b|[c-d])')
        assert '(a*|b|[c-d])' == str(c), str(c)
        c = _test_parser('a(a|b)*')
        assert 'a(a|b)*' == str(c), str(c)
        c = _test_parser('a([a-c]x|axb)*')
        assert 'a([a-c]x|axb)*' == str(c), str(c)


class NfaTest(TestCase):
    
    def assert_matches(self, pattern, text, results):
        r = _test_parser(pattern)
        m = r.nfa()
        s = list(m(Stream.from_string(text)))
        assert len(s) == len(results), s
        for (a, b) in zip(s, results):
            assert a[1] == b, a[1] + ' != ' + b
    
    def test_simple(self):
#        basicConfig(level=DEBUG)
        self.assert_matches('ab', 'abc', ['ab'])
    
    def test_star(self):
        self.assert_matches('a*b', 'aaabc', ['aaab'])
    
    def test_choice(self):
        self.assert_matches('(a|b)', 'ac', ['a'])
    
    def test_star_choice(self):
        self.assert_matches('(a|b)*', 'aababbac', 
                            ['aababba', 'aababb', 'aabab', 'aaba', 'aab', 'aa', 'a', ''])
    
    def test_multiple_choice(self):
        self.assert_matches('(a|ab)b', 'abb', ['ab', 'abb'])

    def test_range(self):
        self.assert_matches('[abc]*', 'bbcx', ['bbc', 'bb', 'b', ''])
        
    def test_range_overlap(self):
        '''
        Matches with 'b' are duplicated, since it appears in both ranges.
        '''
        self.assert_matches('([ab]|[bc])*', 'abc', 
                            ['abc', 'ab', 'abc', 'ab', 'a', ''])

    def test_complex(self):
        self.assert_matches('a([x-z]|a(g|b))*(u|v)p',
                            'ayagxabvp', ['ayagxabvp'])


class DfaGraphTest(TestCase):
    
    def assert_dfa_graph(self, regexp, desc):
        r = _test_parser(regexp)
        nfa = NfaGraph(UNICODE)
        r.build(nfa)
        dfa = NfaToDfa(nfa, UNICODE).dfa
        assert str(dfa) == desc, str(dfa)

    def test_dfa_no_empty(self):
        self.assert_dfa_graph('abc',
            '0 [0] a:1, 1 [3] b:2, 2 [4] c:3, 3 [1, 2] label') 
        
    def test_dfa_simple_repeat(self):
        self.assert_dfa_graph('ab*c',
            '0 [0] a:1, 1 [3, 4] b:1;c:2, 2 [1, 2] label')
        
    def test_dfa_simple_choice(self):
        self.assert_dfa_graph('a(b|c)', 
            '0 [0] a:1, 1 [3, 4] [b-c]:2, 2 [1, 2] label')
        
    def test_dfa_repeated_choice(self):
        self.assert_dfa_graph('a(b|cd)*e', 
            '0 [0] a:1, 1 [3, 4, 5] c:2;e:3;b:1, 2 [6] d:1, 3 [1, 2] label')
        
    def test_dfa_overlapping_choice(self):
        self.assert_dfa_graph('a(bcd|bce)', 
            '0 [0] a:1, 1 [3, 6] b:2, 2 [4, 7] c:3, 3 [8, 5] [d-e]:4, 4 [1, 2] label')

    def test_dfa_conflicting_choice(self):
        self.assert_dfa_graph('a(bc|b*d)', 
            '0 [0] a:1, 1 [3, 5, 6] d:2;b:3, 2 [1, 2] label, 3 [4, 5, 6] b:4;[c-d]:2, 4 [5, 6] b:4;d:2')

    def test_dfa_conflicting_choice_2(self):
        self.assert_dfa_graph('a(bb|b*c)', 
            '0 [0] a:1, 1 [3, 5, 6] c:2;b:3, 2 [1, 2] label, 3 [4, 5, 6] b:4;c:2, 4 [1, 2, 5, 6] b:5;c:2 label, 5 [5, 6] b:5;c:2')

    def test_dfa_dot_option(self):
        '''
        This one's nice - the 'a' completely disappears.
        '''
#        basicConfig(level=DEBUG)
        self.assert_dfa_graph('.*a?b', 
            '0 [0, 3, 4] b:1;[^b]:0, 1 [0, 1, 2, 3, 4] b:1;[^b]:0 label')
