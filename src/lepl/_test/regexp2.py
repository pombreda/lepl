
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
    
    def test_simple(self):
        r = _test_parser('ab')
        m = r.nfa()
        s = list(m(Stream.from_string('abc')))
        assert len(s) == 1, s
        assert s[0] == ('label', 'ab'), s[0]
    
    def test_star(self):
        r = _test_parser('a*b')
        m = r.nfa()
        s = list(m(Stream.from_string('aaabc')))
        assert len(s) == 1, s
        assert s[0] == ('label', 'aaab'), s[0]
    
    def test_choice(self):
        r = _test_parser('(a|b)')
        m = r.nfa()
        s = list(m(Stream.from_string('ac')))
        assert len(s) == 1, s
        assert s[0] == ('label', 'a'), s[0]
    
    def test_star_choice(self):
#        basicConfig(level=DEBUG)
        r = _test_parser('(a|b)*')
        m = r.nfa()
        s = list(m(Stream.from_string('aababbac')))
        assert len(s) == 8, s
        assert s[0] == ('label', 'aababba'), s[0]
    
    def test_multiple_choice(self):
        '''
        Currently fails as backtracking doesn't backtrack on stream.
        '''
        #basicConfig(level=DEBUG)
        r = _test_parser('(a|ab)b')
        m = r.nfa()
        s = list(m(Stream.from_string('abb')))
        assert len(s) == 2, s
        assert s[0] == ('label', 'ab'), s[0]
        assert s[1] == ('label', 'abb'), s[0]

    