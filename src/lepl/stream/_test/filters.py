
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
Tests for the lepl.filters module.
'''

#from logging import basicConfig, DEBUG
from operator import eq
from unittest import TestCase

from lepl.filters import Filter, FilteredSource, Exclude, ExcludeSequence, \
    FilterException
from lepl.matchers import Any, Literal
from lepl.stream import  DEFAULT_STREAM_FACTORY


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, R0904, R0201
# (dude this is just a test)


class FilterTest(TestCase):
    
    def test_filter(self):
        def consonant(s):
            return s[0] not in 'aeiou'
        stream1 = DEFAULT_STREAM_FACTORY.from_string('abcdef\nghijklm\n')
        stream2 = FilteredSource.filtered_stream(consonant, stream1)
        assert stream2[0:2] == 'bc', stream2[0:2]
        assert stream2[0:].line_number == 1, stream2[0:].line_number
        assert stream2[0:].line_offset == 1, stream2[0:].line_offset
        assert stream2[0:12] == 'bcdf\nghjklm\n'
        assert stream2[5:].line_number == 2, stream2[5:].line_number
        assert stream2[5:].line_offset == 0, stream2[5:].line_offset
        assert len(stream2) == 12
        
        
class CachedFilterTest(TestCase):
    
    def test_cached_filter(self):
        def consonant(x):
            return x not in 'aeiou'
        stream1 = DEFAULT_STREAM_FACTORY.from_string('abcdef\nghijklm\n')
        filter_ = Filter(consonant, stream1)
        stream2 = filter_.stream
        assert stream2[0:2] == 'bc', stream2[0:2]
        assert stream2[0:].line_number == 1, stream2[0:].line_number
        assert stream2[0:].line_offset == 1, stream2[0:].line_offset
        assert stream2[0:12] == 'bcdf\nghjklm\n'
        assert filter_.locate(stream2[0:])[0] == 'a', \
                filter_.locate(stream2[0:])[0]
        assert filter_.locate(stream2[1:])[0] == 'c', \
                filter_.locate(stream2[1:])[0]
        assert stream2[5:].line_number == 2, stream2[5:].line_number
        assert stream2[5:].line_offset == 0, stream2[5:].line_offset
        assert len(stream2) == 12, len(stream2)
        

class ExcludeTest(TestCase):
    
    def test_exclude(self):
        #basicConfig(level=DEBUG)
        def vowel(x):
            return x in 'aeiou'
        stream1 = 'abcdef\nghijklm\n'
        matcher = Exclude(vowel)(Any()[:]).string_matcher()
        (match, _stream) = next(matcher('abcdef\nghijklm\n'))
        assert match[0:2] == ['b', 'c'], match[0:2]
        (_result, stream) = next(Exclude(vowel)(Any()[0]).match_string(stream1))
        assert stream[0] == 'a', stream[0]
        (_result, stream) = next(Exclude(vowel)(Any()).match_string(stream1))
        assert stream[0] == 'c', stream[0]
        (_result, stream) = next(Exclude(vowel)(Any()[5]).match_string(stream1))
        assert stream.line_number == 2, stream.line_number == 2
        assert stream.line_offset == 0, stream.line_offset == 0
        assert len(match) == 12, len(match)

    def test_example(self):
        factory = Exclude(lambda x: x == 'a')
        matcher = factory(Literal('b')[:, ...]) + Literal('c')[:, ...]
        result = matcher.parse_string('abababccc')
        assert result == ['bbbccc'], result  


class ExcludeSequenceTest(TestCase):
    
    def test_exclude_sequence(self):
        #basicConfig(level=DEBUG)
        stream = 'ababcdababcabcdbcd'
        matcher = ExcludeSequence(eq, 'abc')
        try:
            matcher(Any()[:, ...]).parse(stream)
            assert False, 'expected error'
        except FilterException as error:
            assert str(error) == 'Can only filter LocationStream instances.'
        result = matcher(Any()[:, ...]).parse_string(stream)
        assert result == ['abdabdbcd'], result
