
from unittest import TestCase

from logging import basicConfig, DEBUG
from lepl.regexp import unicode_parser, State, Regexp, Character, SimpleFsm, UNICODE


def _test_parser(text):
    return unicode_parser(None, text)

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
        a = unicode_parser('a', 'a')
        s1 = State([a], UNICODE)
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        t = list(s2.transitions())
        assert [] == t, t
        assert ['a'] == list(s2.terminals()), list(s2.terminals())
        
    def test_independent(self):
        a = unicode_parser('a', 'a')
        b = unicode_parser('b', 'b')
        s = State([a, b], UNICODE)
        [(ca, s1), (cb, s2)] = s.transitions()
        # order uncertain
        if 'a' != str(ca): (ca, s1, cb, s2) = (cb, s2, ca, s1)
        assert 'a' == str(ca), str(ca)
        assert 'b' == str(cb), str(cb)
        assert [] == list(s1.transitions())
        assert [] == list(s2.transitions())
    
    def test_chain(self):
        ab = unicode_parser('ab', 'ab')
        s1 = State([ab], UNICODE)
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        [(cb, s3)] = s2.transitions()
        assert 'b' == str(cb), str(cb)
        t = list(s3.transitions())
        assert [] == t, t
        
    def test_overlap(self):
        a = unicode_parser('ab', '[ab]')
        b = unicode_parser('bc', '[bc]')
        s = State([a, b], UNICODE)
        chars = ['a', 'b', 'c']
        for (c, s2) in s.transitions():
            assert str(c) in chars, str(c)
            if 'b' == str(c):
                assert 2 == len(s2), len(s2)
            else:
                assert 1 == len(s2), len(s2)
            del chars[chars.index(str(c))]
        assert not chars, chars
        
    def test_choice(self):
        abc = unicode_parser('(a|bc)', '(a|bc)')
        s1 = State([abc], UNICODE)
        [(ca, s2), (cb, s3)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        assert 'b' == str(cb), str(cb)
        t = list(s2.transitions())
        assert [] == t, t
        [(cc, s4)] = s3.transitions()
        assert 'c' == str(cc), str(cc)
        t = list(s4.transitions())
        
    def test_repeat_choice(self):
        basicConfig(level=DEBUG)
        aab = unicode_parser('a(a|b)*', 'a(a|b)*')
        s1 = State([aab], UNICODE)
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        [(cab, s3)] = s2.transitions()
        assert '[a-b]' == str(cab), str(cab)
        assert s3 == s2, '\n' + str(s3) + '\n' + str(s2)
        
    def test_option_in_repeat(self):
        basicConfig(level=DEBUG)
        aab = unicode_parser('(ax?)*', '(ax?)*')
        s1 = State([aab], UNICODE)
        [(ca, s2)] = s1.transitions()
        assert 'a' == str(ca), str(ca)
        [(cx1, s2), (cx2, s3)] = s2.transitions()
        assert 'x' == str(cx1), str(cx1)
        assert 'x' == str(cx2), str(cx2)


class FsmTest(TestCase):
    
    def test_single_match(self):
        abc = unicode_parser(1, 'abc')
        fsm = SimpleFsm([abc], UNICODE)
        assert [(1, 'abc')] == list(fsm.all_for_string('abcde'))
        
    def test_repeats(self):
        regexps = [unicode_parser(1, 'a*'),
                   unicode_parser(2, 'a([a-c]x)*'),
                   unicode_parser(3, 'aax')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('aaxbxcxdx'))
        expected = [(1, ''), (1, 'a'), (2, 'a'), (1, 'aa'), (2, 'aax'), 
                    (3, 'aax'), (2, 'aaxbx'), (2, 'aaxbxcx')]
        assert results == expected, '\n' + str(results) + '\n' + str(expected)
    
    def test_choices(self):
#        basicConfig(level=DEBUG)
        regexps = [unicode_parser(1, 'a*'),
                   unicode_parser(2, 'a(a|b)*')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('aabbc'))
        assert results == [(1, ''), (1, 'a'), (2, 'a'), (1, 'aa'), 
                           (2, 'aa'), (2, 'aab'), (2, 'aabb')], results
    
    def test_choice_and_repeat(self):
#        basicConfig(level=DEBUG)
        regexps = [unicode_parser(1, 'a*'),
                   unicode_parser(2, 'a([a-c]x|axb)*'),
                   unicode_parser(3, 'aax')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('aaxbxcxdx'))
        expected = [(1, ''), (1, 'a'), (2, 'a'), (1, 'aa'), (2, 'aax'), 
                    (3, 'aax'), (2, 'aaxb'), (2, 'aaxbx'), (2, 'aaxbxcx')]
        assert results == expected, '\n' + str(results) + '\n' + str(expected)

    def test_embedded_repeat(self):
        regexps = [unicode_parser(1, 'ab*c')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('abbc'))
        assert results == [(1, 'abbc')], results
        
    def test_optional(self):
        #basicConfig(level=DEBUG)
        regexps = [unicode_parser(1, 'ab?c')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('abc'))
        assert results == [(1, 'abc')], results
        results = list(fsm.all_for_string('ac'))
        assert results == [(1, 'ac')], results
        
    def test_all(self):
        regexps = [unicode_parser(1, 'a*'),
                   unicode_parser(2, 'a([a-c]x?|axb)*'),
                   unicode_parser(3, 'aax')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('aaxbxcxdx'))
        expected = [(1, ''), (1, 'a'), (2, 'a'), (1, 'aa'), (2, 'aax'), 
                    (3, 'aax'), (2, 'aaxb'), (2, 'aaxbx'), 
                    (2, 'aaxbxc'), (2, 'aaxbxcx')]
        assert results == expected, '\n' + str(results) + '\n' + str(expected)

    def test_final_option(self):
        basicConfig(level=DEBUG)
        regexps = [unicode_parser(1, 'ax?')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('a'))
        assert results == [(1, 'a')], results

    def test_option2_in_repeat(self):
        basicConfig(level=DEBUG)
        regexps = [unicode_parser(1, '(ax?)*')]
        fsm = SimpleFsm(regexps, UNICODE)
        results = list(fsm.all_for_string('aa'))
        assert results == [(1, ''), (1, 'a'), (1, 'aa')], results

        