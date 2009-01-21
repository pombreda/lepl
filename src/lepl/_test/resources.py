
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.match import *
from lepl.resources import managed
from lepl.trace import LogMixin


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
        basicConfig(level=DEBUG)
        self.assert_range(3, 4, 0, [15,1,1,1,15])
        self.assert_range(3, 4, 1, [15,0,0,1,15])
        self.assert_range(3, 4, -1, [15,1,1,1,15])
        
    def assert_range(self, n_match, n_char, direcn, results):
        text = '*' * n_char
        for min_queue in range(len(results)):
            matcher = (Literal('*')[::direcn,...][n_match] & Eos()).match_string(min_queue=min_queue)
            self.assert_count(matcher, min_queue, results[min_queue])
            
    def assert_count(self, matcher, min_queue, count):
        results = list(matcher('****'))
        print(results)
        found = len(results)
        assert found == count, (min_queue, found)
