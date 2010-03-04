
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
Decorator tests.

(These need to be copied into an example and the tutorial). 
'''

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers.support import function_matcher_factory, function_matcher, \
    sequence_matcher_factory, sequence_matcher
    

@function_matcher
def char(support, stream):
    if stream:
        return ([stream[0]], stream[1:])

@function_matcher_factory
def char_in(chars):
    def match(support, stream):
        if stream and stream[0] in chars:
            return ([stream[0]], stream[1:])
    return match

@sequence_matcher
def any_char(support, stream):
    while stream:
        yield ([stream[0]], stream[1:])
        stream = stream[1:]

@sequence_matcher_factory
def any_char_in(chars):
    def match(support, stream):
        while stream:
            if stream[0] in chars:
                yield ([stream[0]], stream[1:])
            stream = stream[1:]
    return match


class DecoratorTest(TestCase):
    
    def test_char(self):
        #basicConfig(level=DEBUG)
        matcher = char()
        matcher.config.no_full_match()
        result = list(matcher.match('ab'))
        assert result == [(['a'], 'b')], result
        matcher = char()[2:,...]
        matcher.config.no_full_match()
        result = list(matcher.match('abcd'))
        assert result == [(['abcd'], ''), (['abc'], 'd'), (['ab'], 'cd')], result
        
    def test_char_in(self):
        #basicConfig(level=DEBUG)
        matcher = char_in('abc')
        matcher.config.no_full_match()
        result = list(matcher.match('ab'))
        assert result == [(['a'], 'b')], result
        result = list(matcher.match('pqr'))
        assert result == [], result
        matcher = char_in('abc')[2:,...]
        matcher.config.no_full_match()
        result = list(matcher.match('abcd'))
        assert result == [(['abc'], 'd'), (['ab'], 'cd')], result
        
    def test_any_char(self):
        #basicConfig(level=DEBUG)
        matcher = any_char()
        # with this set we have an extra eos that messes things up
        matcher.config.no_full_match()
        result = list(matcher.match('ab'))
        assert result == [(['a'], 'b'), (['b'], '')], result
        matcher = any_char()[2:,...]
        matcher.config.no_full_match()
        result = list(matcher.match('abcd'))
        assert result == [(['abcd'], ''), (['abc'], 'd'), (['abd'], ''), 
                          (['ab'], 'cd'), (['acd'], ''), (['ac'], 'd'), 
                          (['ad'], ''), (['bcd'], ''), (['bc'], 'd'), 
                          (['bd'], ''), (['cd'], '')], result
        
    def test_any_char_in(self):
        matcher = any_char_in('abc')
        matcher.config.no_full_match()
        result = list(matcher.match('ab'))
        assert result == [(['a'], 'b'), (['b'], '')], result
        result = list(matcher.match('pqr'))
        assert result == [], result
        matcher = any_char_in('abc')[2:,...]
        matcher.config.no_full_match()
        result = list(matcher.match('abcd'))
        assert result == [(['abc'], 'd'), (['ab'], 'cd'), 
                          (['ac'], 'd'), (['bc'], 'd')], result
    
    def test_bad_args(self):
        #basicConfig(level=DEBUG)
        try:
            char(foo='abc')
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            char('abc')
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            char_in()
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            @function_matcher
            def foo(a): return
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            @function_matcher_factory
            def foo(a, *, b=None): return
            assert False, 'expected error'
        except TypeError:
            pass
            

class FunctionMatcherBugTest(TestCase):
    
    def test_bug(self):
        #basicConfig(level=DEBUG)
        from string import ascii_uppercase
        @function_matcher
        def capital(support, stream):
            if stream[0] in ascii_uppercase:
                return ([stream[0]], stream[1:])
        parser = capital()[3]
        assert parser.parse_string('ABC')
        