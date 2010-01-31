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
Tests for the combining matchers.
'''

from unittest import TestCase

from lepl.matchers.combine import DepthFirst, BreadthFirst
from lepl.matchers.core import Any


class DirectionTest1(TestCase):
    
    def matcher(self):
        return Any()
    
    def test_depth(self):
        matcher = DepthFirst(self.matcher(), 1, 2).null_matcher()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['12', '1'], results
        
    def test_breadth(self):
        matcher = BreadthFirst(self.matcher(), 1, 2).null_matcher()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['1', '12'], results
        
class DirectionTest2(TestCase):
    
    def matcher(self):
        return ~Any()[:] & Any()
    
    def test_depth(self):
        matcher = DepthFirst(self.matcher(), 1, 2).null_matcher()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['3', '23', '2', '13', '12', '1'], results
        
    def test_breadth(self):
        matcher = BreadthFirst(self.matcher(), 1, 2).null_matcher()
        results = list(map(''.join, map(lambda x: x[0], matcher('123'))))
        assert results == ['3', '2', '1', '23', '13', '12'], results
