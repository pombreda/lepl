
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
Tests for the lepl.matchers.variables module.
'''

from io import StringIO
#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers.core import Any
from lepl.matchers.variables import NamedResult, TrackVariables


class ExplicitTest(TestCase):
    
    def test_wrapper(self):
        output = StringIO()
        matcher = NamedResult('foo', Any()[:], out=output)
        repr(matcher)
        matcher.config.clear()
        parser = matcher.string_matcher()
        list(parser('abc'))
        text = output.getvalue()
        assert text == '''foo = ['a', 'b', 'c']
    "abc" -> ""
foo (2) = ['a', 'b']
    "abc" -> "c"
foo (3) = ['a']
    "abc" -> "bc"
foo (4) = []
    "abc" -> "abc"
! foo (after 4 matches)
    "abc"
''', '>' + text + '<'
        
    def test_context(self):
        #basicConfig(level=DEBUG)
        output = StringIO()
        with TrackVariables(out=output):
            bar = Any()
        bar.config.no_full_match()
        repr(bar)
        list(bar.match('abc'))
        text = output.getvalue()
        assert text == '''         bar = ['a']                            stream = 'bc'
         bar failed                             stream = 'abc'
''', '>' + text + '<'

        