
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.manager import GeneratorManager
from lepl.matchers import *
from lepl.parser import string_matcher, Configuration
from lepl.support import LogMixin


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
        # i'm worried something odd is happening here - this changed
        # at some point, and i don't understand if the old behaviour was
        # wrong, or whether the new behaviour isn't right.
        self.assert_range(3, 4, 'g', [15,1,1,1,6,6,15,15], 4)
        self.assert_range(3, 4, 'b', [15,0,1,1,5,5,5,5,15], 4)
        self.assert_range(3, 4, 'd', [15,1,1,1,6,10,10,10,15], 4)
        
    def assert_range(self, n_match, n_char, direcn, results, multiplier):
        text = '*' * n_char
        for index in range(len(results)):
            queue_len = index * multiplier
            matcher = string_matcher(
                        Literal('*')[::direcn,...][n_match] & Eos(),
                        Configuration(monitors=[GeneratorManager(queue_len)]))
            self.assert_count(matcher, queue_len, index, results[index])
            
    def assert_count(self, matcher, queue_len, index, count):
        results = list(matcher('****'))
        found = len(results)
        assert found == count, (queue_len, index, found, count)

    def test_single(self):
#        basicConfig(level=DEBUG)
        matcher = string_matcher(Literal('*')[:,...][3],
                                 Configuration(monitors=[GeneratorManager(queue_len=5)]))('*' * 4)
        results = list(matcher)
        print(results)
        