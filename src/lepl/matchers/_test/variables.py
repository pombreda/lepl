
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

from lepl._test.base import assert_str
from lepl.matchers.core import Any
from lepl.matchers.variables import NamedResult, TraceVariables


class ExplicitTest(TestCase):
    
    def test_wrapper(self):
        output = StringIO()
        matcher = NamedResult('foo', Any()[:], out=output)
        repr(matcher)
        matcher.config.clear()
        parser = matcher.get_match_string()
        list(parser('abc'))
        text = output.getvalue()
        assert_str(text, '''foo = ['a', 'b', 'c']
    "abc" -> ""
foo (2) = ['a', 'b']
    "abc" -> "c"
foo (3) = ['a']
    "abc" -> "bc"
foo (4) = []
    "abc" -> "abc"
! foo (after 4 matches)
    "abc"
''')
        
    def test_context(self):
        #basicConfig(level=DEBUG)
        output = StringIO()
        with TraceVariables(out=output):
            bar = Any()
        bar.config.no_full_first_match()
        repr(bar)
        list(bar.match('abc'))
        text = output.getvalue()
        assert_str(text, '''         bar = ['a']                            stream = 'bc'
         bar failed                             stream = 'abc'
''')

        