
from unittest import TestCase

from logging import basicConfig, DEBUG
from lepl import *
from lepl.regexp2 import unicode_single_parser, Regexp, Character, UNICODE


def _test_parser(text):
    return unicode_single_parser('label', text)

class CharactersTest(TestCase):
    
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

