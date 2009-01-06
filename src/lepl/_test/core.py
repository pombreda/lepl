
from unittest import TestCase

from lepl.core import CircularFifo, no_depth


class CircularFifoTest(TestCase):
    
    def test_expiry(self):
        fifo = CircularFifo(3)
        assert None == fifo.append(1)
        assert None == fifo.append(2)
        assert None == fifo.append(3)
        for i in range(4,10):
            assert i-3 == fifo.append(i)
            

class NoDeptTest(TestCase):
    
    def test_no_depth(self):
        n = NullMatch()
        l = [i for (i, _) in n([3])]
        assert [[0],[1],[2]] == l, l
        m = SingleMatch()
        l = [i for (i, _) in m([3])]
        assert [[0]] == l


class NullMatch():

    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])


class SingleMatch():

    @no_depth
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])

