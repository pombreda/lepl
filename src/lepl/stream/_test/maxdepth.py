
# Copyright 2010 Andrew Cooke

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
Tests for the lepl.stream.maxdepth module.
'''


from unittest import TestCase
from lepl import Any, Eos, Optional
from lepl.stream.maxdepth import FullFirstMatch, FullFirstMatchException, facade_factory


class FullFirstMatchTest(TestCase):
    
    def test_stream(self):
        matcher = Any('a')
        matcher.config.clear()
        result = list(matcher.match('b'))
        assert result == [], result
        (stream, _memory) = facade_factory('b')
        result = list(matcher.match_null(stream))
        assert result == [], result
    
    def test_exception(self):
        matcher = FullFirstMatch(Any('a'))
        matcher.config.clear()
        try:
            list(matcher.match('b'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 0 of str: 'b'.""", str(e)
            
    def test_message(self):
        matcher = FullFirstMatch(Any('a'))
        matcher.config.clear()
        try:
            list(matcher.match_string('b'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 0 of str: 'b'.""", str(e)
            
    def test_location(self):
        matcher = FullFirstMatch(Any('a')[:] & Eos())
        matcher.config.clear()
        try:
            list(matcher.match_string('aab'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 2 of str: 'aab'.""", str(e)
            
    def test_ok(self):
        matcher = FullFirstMatch(Any('a'))
        matcher.config.clear()
        result = list(matcher.match_null('a'))
        assert result == [(['a'], '')], result
        

class FullFirstMatchConfigTest(TestCase):
    
    def test_exception(self):
        matcher = Any('a')
        matcher.config.full_first_match(eos=False)
        try:
            list(matcher.match('b'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 0 of str: 'b'.""", str(e)
            
    def test_eos(self):
        matcher = Optional(Any('a'))
        matcher.config.full_first_match(eos=True)
        try:
            list(matcher.match('b'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 0 of str: 'b'.""", str(e)
            
    def test_message(self):
        matcher = Any('a')
        matcher.config.full_first_match(eos=False)
        try:
            list(matcher.match_string('b'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 0 of str: 'b'.""", str(e)
            
    def test_location(self):
        matcher = Any('a')[:]
        matcher.config.full_first_match(eos=True)
        try:
            list(matcher.match_string('aab'))
            assert False, 'expected error'
        except FullFirstMatchException as e:
            assert str(e) == """The match failed at 'b',
Line 1, character 2 of str: 'aab'.""", str(e)
            
    def test_ok(self):
        matcher = Any('a')
        matcher.config.full_first_match(eos=False)
        result = list(matcher.match_null('a'))
        assert result == [(['a'], '')], result
        matcher.config.full_first_match(eos=True)
        result = list(matcher.match_null('a'))
        assert result == [(['a'], '')], result
        
    
