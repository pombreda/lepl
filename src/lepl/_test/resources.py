
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.match import MatchMixin
from lepl.repeat import RepeatMixin
from lepl.resources import managed
from lepl.trace import LogMixin


class LimitedDepthTest(LogMixin, TestCase):
    
    def test_limited_depth(self):
        basicConfig(level=DEBUG)
        self._debug('test null')
        self.assert_list(NullMatch()[3]([2,2,2]), 
                         [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]], 0)
        self._debug('test null with stream')
        self.assert_list(NullMatch()[3].match_list([2,2,2]), 
                         [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]], 0)
        for max_queue in range(20):
            if max_queue == 0:
                result = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
            elif max_queue <= 3:
                result = [[0,0,0]]
            elif max_queue <= 8:
                result = [[0,0,0], [0,0,1]]
            elif max_queue <= 18:
                result = [[0,0,0], [0,0,1], [0,1,0], [0,1,1]]
            else:
                result = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
            self._debug('**** test max_queue={0}'.format(max_queue))
            self.assert_list(LimitedMatch()[3].match_list([2,2,2], max_queue=max_queue),
                             result, max_queue) 
        
    def assert_list(self, match, expected, max_queue):
        result = [i for (i, _) in match]
        assert expected == result, '{0}: {1}'.format(max_queue, result)
              

class NullMatch(MatchMixin, RepeatMixin, LogMixin):
    
    def __init__(self):
        super().__init__()
    
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])
                

class LimitedMatch(MatchMixin, RepeatMixin, LogMixin):

    def __init__(self):
        super().__init__()
    
    @managed
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])
