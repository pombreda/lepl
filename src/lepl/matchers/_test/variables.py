
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

from unittest import TestCase

from lepl.matchers.core import Any
from lepl.matchers.variables import NamedResult, log_these_variables


class ExplicitTest(TestCase):
    
    def test_wrapper(self):
        matcher = NamedResult('foo', Any()[:])
        print(repr(matcher))
        matcher.config.clear()
        parser = matcher.string_matcher()
        print(repr(parser.matcher))
        print(type(parser))
        list(parser('abc'))
        
    def test_context(self):
        with log_these_variables():
            bar = Any()[:]
        print(repr(bar))
        list(bar.match('abc'))
        
        