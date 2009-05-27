
from unittest import TestCase

from logging import basicConfig, DEBUG, getLogger
from lepl import *
from lepl.regexp.binary import *


def _test_parser(text):
    return binary_single_parser('label', text)

class CharactersTest(TestCase):
    
    def test_dot(self):
        basicConfig(level=DEBUG)
        c = _test_parser('.')
        assert '.' == str(c), str(c)
        assert 0 == c[0][0][0][0], type(c[0][0][0][0])
        assert 1 == c[0][0][0][1], type(c[0][0][0][1])

    def test_brackets(self):
        #basicConfig(level=DEBUG)
        c = _test_parser('0')
        assert '0' == str(c), str(c)
        # this is the lower bound for the interval
        assert 0 == c[0][0][0][0], type(c[0][0][0][0])
        # and the upper - we really do have a digit
        assert 0 == c[0][0][0][1], type(c[0][0][0][1])
        c = _test_parser('1')
        assert '1' == str(c), str(c)
        c = _test_parser('0101')
        assert '0101' == str(c), str(c)
   
    def test_star(self):
        c = _test_parser('0*')
        assert '0*' == str(c), str(c)
        c = _test_parser('0(01)*1')
        assert '0(01)*1' == str(c), str(c)
        
    def test_option(self):
        c = _test_parser('1?')
        assert '1?' == str(c), str(c)
        c = _test_parser('0(01)?1')
        assert '0(01)?1' == str(c), str(c)
        
    def test_choice(self):
        c = _test_parser('(0*|1)')
        assert '(0*|1)' == str(c), str(c)


