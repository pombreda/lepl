
from unittest import TestCase

from logging import basicConfig, DEBUG
from lepl.regexp import parser, State, Regexp, Character, Fsm


def _test_parser(text):
    return parser(None, text)

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
        
    def test_in(self):
        c = _test_parser('b')
        assert 'a' not in c
        assert 'b' in c
        assert 'c' not in c
        c = _test_parser('[bq]')
        assert 'a' not in c
        assert 'b' in c
        assert 'q' in c
        assert 'c' not in c
        c = _test_parser('[a-b]')
        assert 'a' in c
        assert 'b' in c
        assert 'c' not in c
        c = _test_parser('[a-b,q]')
        assert 'a' in c
        assert 'b' in c
        assert 'c' not in c
        assert 'p' not in c
        assert 'q' in c
        assert 'r' not in c


class StateTest(TestCase):
    
    def test_simple(self):
        a = parser('a', 'a')
        s1 = State([a])
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        t = list(s2.transitions())
        assert [] == t, t
        assert ['a'] == list(s2.terminals()), list(s2.terminals())
        
    def test_independent(self):
        a = parser('a', 'a')
        b = parser('b', 'b')
        s = State([a, b])
        [(ca, s1), (cb, s2)] = s.transitions()
        # order uncertain
        if 'a' != str(ca): (ca, s1, cb, s2) = (cb, s2, ca, s1)
        assert 'a' == str(ca), str(ca)
        assert 'b' == str(cb), str(cb)
        assert [] == list(s1.transitions())
        assert [] == list(s2.transitions())
    
    def test_chain(self):
        ab = parser('ab', 'ab')
        s1 = State([ab])
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        [(cb, s3)] = s2.transitions()
        assert 'b' == str(cb), str(cb)
        t = list(s3.transitions())
        assert [] == t, t
        
    def test_overlap(self):
        a = parser('ab', '[ab]')
        b = parser('bc', '[bc]')
        s = State([a, b])
        chars = ['a', 'b', 'c']
        for (c, s2) in s.transitions():
            assert str(c) in chars, str(c)
            if 'b' == str(c):
                assert 2 == len(s2), len(s2)
            else:
                assert 1 == len(s2), len(s2)
            del chars[chars.index(str(c))]
        assert not chars, chars
        

class FsmTest(TestCase):
    
    def test_single_match(self):
        abc = parser(1, 'abc')
        fsm = Fsm([abc])
        assert [(1, 'abc')] == list(fsm.all_for_string('abcde'))
        
    def test_all(self):
        regexps = [parser(1, 'a*'),
                   parser(2, 'a([a-c]x)*'),
                   parser(3, 'aax')]
        fsm = Fsm(regexps)
        results = list(fsm.all_for_string('aaxbxcxdx'))
        assert results == [(1, ''), (1, 'a'), (2, 'a'), (1, 'aa'), (2, 'aax'), 
                           (3, 'aax'), (2, 'aaxbx'), (2, 'aaxbxcx')], \
               results
        