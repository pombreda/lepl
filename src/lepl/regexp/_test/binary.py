
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests for the lepl.regexp.binary module.
'''

from unittest import TestCase

#from logging import basicConfig, DEBUG
from lepl.regexp.binary import binary_single_parser
from lepl.support import format

# pylint: disable-msg=C0103, C0111, C0301, C0324, R0201, R0903, R0904
# (dude this is just a test)


def _test_parser(text):
    return binary_single_parser('label', text)

def label(text):
    return format('({{label:{0!s}}})', text)
    
class CharactersTest(TestCase):
    
    def test_dot(self):
        #basicConfig(level=DEBUG)
        c = _test_parser('.')
        assert label('.') == str(c), str(c)
        assert 0 == c[0][0][0][0], type(c[0][0][0][0])
        assert 1 == c[0][0][0][1], type(c[0][0][0][1])

    def test_brackets(self):
        #basicConfig(level=DEBUG)
        c = _test_parser('0')
        assert label('0') == str(c), str(c)
        # this is the lower bound for the interval
        assert 0 == c[0][0][0][0], type(c[0][0][0][0])
        # and the upper - we really do have a digit
        assert 0 == c[0][0][0][1], type(c[0][0][0][1])
        c = _test_parser('1')
        assert label('1') == str(c), str(c)
        c = _test_parser('0101')
        assert label('0101') == str(c), str(c)
   
    def test_star(self):
        c = _test_parser('0*')
        assert label('0*') == str(c), str(c)
        c = _test_parser('0(01)*1')
        assert label('0(01)*1') == str(c), str(c)
        
    def test_option(self):
        c = _test_parser('1?')
        assert label('1?') == str(c), str(c)
        c = _test_parser('0(01)?1')
        assert label('0(01)?1') == str(c), str(c)
        
    def test_choice(self):
        c = _test_parser('(0*|1)')
        assert label('(0*|1)') == str(c), str(c)


