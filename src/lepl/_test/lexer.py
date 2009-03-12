
from unittest import TestCase

from logging import basicConfig, DEBUG
from lepl.lexer import _parser


class CharactersTest(TestCase):
    
    def test_brackets(self):
        #basicConfig(level=DEBUG)
        c = _parser('a')
        assert 'a' == str(c), str(c)
        c = _parser('[ac]')
        assert '[ac]' == str(c), str(c)
        c = _parser('[a-c]')
        assert '[a-c]' == str(c), str(c)
        c = _parser('[a-cp-q]')
        assert '[a-cp-q]' == str(c), str(c)
        c = _parser(r'\\')
        assert r'\\' == str(c), str(c)
        c = _parser(r'\-')
        assert r'\-' == str(c), str(c)
        c = _parser(r'[\\-x]')
        assert r'[\\-x]' == str(c), str(c)
    
    def test_merge(self):
        c = _parser('[a-ce-g]')
        assert '[a-ce-g]' == str(c), str(c)
        c = _parser('[a-cd-f]')
        assert '[a-f]' == str(c), str(c)
        c = _parser('[a-cc-e]')
        assert '[a-e]' == str(c), str(c)
        c = _parser('[a-cb-d]')
        assert '[a-d]' == str(c), str(c)
        c = _parser('[a-ca-c]')
        assert '[a-c]' == str(c), str(c)
        c = _parser('[a-a]')
        assert 'a' == str(c), str(c)
        c = _parser('[e-ga-c]')
        assert '[a-ce-g]' == str(c), str(c)
        c = _parser('[d-fa-c]')
        assert '[a-f]' == str(c), str(c)
        c = _parser('[c-ea-c]')
        assert '[a-e]' == str(c), str(c)
        c = _parser('[b-da-c]')
        assert '[a-d]' == str(c), str(c)
        c = _parser('[a-gc-e]')
        assert '[a-g]' == str(c), str(c)
        c = _parser('[c-ea-g]')
        assert '[a-g]' == str(c), str(c)
        c = _parser('[a-eg]')
        assert '[a-eg]' == str(c), str(c)
        c = _parser('[ga-e]')
        assert '[a-eg]' == str(c), str(c)

    def test_star(self):
        c = _parser('a*')
        assert 'a*' == str(c), str(c)
        c = _parser('a(bc)*d')
        assert 'a(bc)*d' == str(c), str(c)
        c = _parser('a(bc)*d[e-g]*')
        assert 'a(bc)*d[e-g]*' == str(c), str(c)
