
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers import *
from lepl.manager import managed
from lepl.parser import string_matcher, Configuration
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
#        basicConfig(level=DEBUG)
        # i'm worried something odd is happening here - this changed
        # at some point, and i don't understand if the old behaviour was
        # wrong, or whether the new behaviour isn't right.
        self.assert_range(3, 4, 'g', [15,1,1,3,3,3,6,6,6,10,10,10,15], 4)
        self.assert_range(3, 4, 'b', [15,0,1,1,1,1,5,5,5,5,5,5,5,5,5,5,5,15], 4)
        self.assert_range(3, 4, 'd', [15,1,1,3,3,3,6,6,6,10,10,10,15], 4)
        
    def assert_range(self, n_match, n_char, direcn, results, multiplier):
        text = '*' * n_char
        for index in range(len(results)):
            min_queue = index * multiplier
            matcher = string_matcher(
                        Literal('*')[::direcn,...][n_match] & Eos(),
                        Configuration(queue_len=min_queue))
            self.assert_count(matcher, min_queue, index, results[index])
            
    def assert_count(self, matcher, min_queue, index, count):
        results = list(matcher('****'))
        found = len(results)
        assert found == count, (min_queue, index, found)

    def test_single(self):
#        basicConfig(level=DEBUG)
        matcher = string_matcher(Literal('*')[:,...][3],
                                 Configuration(queue_len=5))('*' * 4)
        results = list(matcher)
        print(results)
        