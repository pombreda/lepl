

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.core import CircularFifo, no_depth, limited_depth
from lepl.match import MatchMixin
from lepl.repeat import RepeatMixin
from lepl.trace import LogMixin


class CircularFifoTest(TestCase):
    
    def test_expiry(self):
        fifo = CircularFifo(3)
        assert None == fifo.append(1)
        assert None == fifo.append(2)
        assert None == fifo.append(3)
        for i in range(4,10):
            assert i-3 == fifo.append(i)
            
            
class BaseDepthTest(TestCase):
    
    def assert_list(self, match, expected):
        result = [i for (i, _) in match]
        assert expected == result, result
        

class NoDepthTest(BaseDepthTest):
    
    def test_no_depth(self):
        self.assert_list(NullMatch()([3]), [[0],[1],[2]])
        self.assert_list(SingleMatch()([3]), [[0]])

    def test_no_depth_via_mixin(self):
        self.assert_list(SingleMatch()([3]), [[0]])
        
        
class LimitedDepth(LogMixin, BaseDepthTest):
    
    def test_limited_depth(self):
        basicConfig(level=DEBUG)
        self._debug('test 1')
        self.assert_list(NullMatch()[3]([1,2,3]), 
                         [[0,0,0], [0,0,1], [0,0,2], [0,1,0], [0,1,1], [0,1,2]])
        self._debug('test 2')
        self.assert_list(NullMatch()[3].match_list([1,2,3]), 
                         [[0,0,0], [0,0,1], [0,0,2], [0,1,0], [0,1,1], [0,1,2]])
        self._debug('test 3')
        self.assert_list(LimitedMatch()[3].match_list([1,2,3], search_depth=1), 
                         [[0,0,0]])
        self._debug('test 4')
        self.assert_list(LimitedMatch()[3].match_list([1,2,3], search_depth=2), 
                         [[0,0,0], [0,0,1]])
        self._debug('test 5')
        self.assert_list(LimitedMatch()[3].match_list([1,2,3], search_depth=3), 
                         [[0,0,0], [0,0,1], [0,0,2]])
        self._debug('test 6')
        self.assert_list(LimitedMatch()[3].match_list([1,2,3], search_depth=4), 
                         [[0,0,0], [0,0,1], [0,0,2]])
        self._debug('test 7')
        self.assert_list(LimitedMatch()[3].match_list([1,2,3], search_depth=5), 
                         [[0,0,0], [0,0,1], [0,0,2], [0,1,0], [0,1,1], [0,1,2]])
        
       

class NullMatch(MatchMixin, RepeatMixin, LogMixin):
    
    def __init__(self):
        super().__init__()
    
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])
                

class SingleMatch(MatchMixin, RepeatMixin, LogMixin):

    def __init__(self):
        super().__init__()
    
    @no_depth
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])


class LimitedMatch(MatchMixin, RepeatMixin, LogMixin):

    def __init__(self):
        super().__init__()
    
    @limited_depth
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])

