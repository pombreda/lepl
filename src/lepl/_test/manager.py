
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
Tests for the lepl.manager module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.config import Configuration
from lepl.functions import Eos
from lepl.manager import GeneratorManager
from lepl.matchers import Literal
from lepl.support import LogMixin


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201, R0904
# (dude this is just a test)

    
class LimitedDepthTest(LogMixin, TestCase):
    '''
    The test here takes '****' and divides it amongst the matchers, all of
    which will take 0 to 4 matches.  The number of different permutations
    depends on backtracking and varies depending on the queue length
    available.
    '''
    
    def test_limited_depth(self):
        '''
        These show something is happening.  Whether they are exactly correct
        is another matter altogether...
        '''
        #basicConfig(level=DEBUG)
        # there was a major bug here that made this test vary often
        # it should now be fixed
        self.assert_range(3, 'g', [15,1,1,1,3,3,6,6,10,10,10,15,15,15,15], 4)
        self.assert_range(3, 'b', [15,0,1,1,5,5,5,5,5,5,5,5,5,15,15,15], 4)
        self.assert_range(3, 'd', [15,1,1,3,3,6,6,10,10,10,15,15,15], 4)
        
    def assert_range(self, n_match, direcn, results, multiplier):
        for index in range(len(results)):
            queue_len = index * multiplier
            matcher = (Literal('*')[::direcn,...][n_match] & Eos())\
                        .string_matcher(
                        Configuration(monitors=[GeneratorManager(queue_len)]))
            self.assert_count(matcher, queue_len, index, results[index])
            
    def assert_count(self, matcher, queue_len, index, count):
        results = list(matcher('****'))
        found = len(results)
        assert found == count, (queue_len, index, found, count)

    def test_single(self):
        #basicConfig(level=DEBUG)
        matcher = (Literal('*')[:,...][3]).string_matcher(
                        Configuration(monitors=[GeneratorManager(queue_len=5)])
                        )('*' * 4)
        list(matcher)
        