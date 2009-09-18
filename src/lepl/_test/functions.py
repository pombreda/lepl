
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
Tests for the lepl.functions module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.functions import Space, Repeat, SkipTo, Newline
from lepl.matchers import Any, OperatorMatcher, Trace
from lepl.parser import tagged
from lepl._test.matchers import BaseTest


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201, R0913, R0901, R0904
# (dude this is just a test)

class RepeatTest(TestCase):

    def test_simple(self):
        #basicConfig(level=DEBUG)
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
                  for (l, _s) in Repeat(RangeMatch(), start, stop, step).match_items(stream)]
        assert target == result, result
        
    def test_mixin(self):
        #basicConfig(level=DEBUG)
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
        result = [''.join(map(str, l)) for (l, _s) in match.match_items(stream)]
        assert target == result, result
       
    def test_separator(self):
        #basicConfig(level=DEBUG)
        self.assert_separator('a', 1, 1, 'd', ['a'])
        self.assert_separator('a', 1, 1, 'b', ['a'])
        self.assert_separator('a,a', 1, 2, 'd', ['a,a', 'a'])
        self.assert_separator('a,a', 1, 2, 'b', ['a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'd', ['a,a,a', 'a,a'])
        self.assert_separator('a,a,a,a', 2, 3, 'b', ['a,a', 'a,a,a'])
        
    def assert_separator(self, stream, start, stop, step, target):
        result = [''.join(l) 
                  for (l, _s) in Repeat(Any('abc'), start, stop, step, Any(',')).match_string(stream)]
        assert target == result, result
        
    def test_separator_mixin(self):
        #basicConfig(level=DEBUG)
        abc = Any('abc')
        self.assert_separator_mixin(abc[1:1:'d',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:1:'b',','], 'a', ['a'])
        self.assert_separator_mixin(abc[1:2:'d',','], 'a,b', ['a,b', 'a'])
        self.assert_separator_mixin(abc[1:2:'b',','], 'a,b', ['a', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'d',','], 'a,b,c,a', ['a,b,c', 'a,b'])
        self.assert_separator_mixin(abc[2:3:'b',','], 'a,b,c,a', ['a,b', 'a,b,c'])

    def assert_separator_mixin(self, matcher, stream, target):
        result = [''.join(map(str, l)) for (l, _s) in matcher.match_string(stream)]
        assert target == result, result
    
class RangeMatch(OperatorMatcher):
    '''
    We test repetition by looking at "strings" of integers, where the 
    matcher for any particular value returns all values less than the
    current value. 
    '''
    
    def __init__(self):
        super(RangeMatch, self).__init__()
    
    @tagged
    def _match(self, values):
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

 
class SkipToTest(BaseTest):
    
    def test_skip(self):
        self.assert_direct('aabcc', SkipTo('b'), [['aab']])
        self.assert_direct('aabcc', SkipTo('b', False), [['aa']])
    
    def test_next_line(self):
        #basicConfig(level=DEBUG)
        self.assert_direct('''abc
d''', Trace(~SkipTo(Newline()) + 'd'), [['d']])
