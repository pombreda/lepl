
from unittest import TestCase

from lepl.support import assert_type, CircularFifo


class AssertTypeTestCase(TestCase):
    
    def test_ok(self):
        assert_type('', 1, int)
        assert_type('', '', str)
        assert_type('', None, int, none_ok=True)
        
    def test_bad(self):
        self.assert_bad('The foo attribute in Bar', '', int, False, 
                        "The foo attribute in Bar (value '') must be of type int.")
        self.assert_bad('The foo attribute in Bar', None, int, False, 
                        "The foo attribute in Bar (value None) must be of type int.")
        
    def assert_bad(self, name, value, type_, none_ok, msg):
        try:
            assert_type(name, value, type_, none_ok=none_ok)
            assert False, 'Expected failure'
        except TypeError as e:
            assert e.args[0] == msg, e.args[0]


class CircularFifoTest(TestCase):
    
    def test_expiry(self):
        fifo = CircularFifo(3)
        assert None == fifo.append(1)
        assert None == fifo.append(2)
        assert None == fifo.append(3)
        for i in range(4,10):
            assert i-3 == fifo.append(i)
            
            
