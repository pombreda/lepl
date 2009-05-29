
from unittest import TestCase

from lepl.bin.node import unpack_length, coerce_unknown_length, coerce_known_length


class UnpackTest(TestCase):
    '''
    Test whether we correctly parse arguments to Binary()
    '''

    def test_lengths(self):
        assert 0 == unpack_length(0), unpack_length(0)
        assert 1 == unpack_length(1), unpack_length(1)
        assert 7 == unpack_length(7), unpack_length(7)
        assert 8 == unpack_length(8), unpack_length(8)
        assert 9 == unpack_length(9), unpack_length(9)
        assert 0 == unpack_length(0.), unpack_length(0.)
        assert 1 == unpack_length(0.1), unpack_length(0.1)
        assert 7 == unpack_length(0.7), unpack_length(0.7)
        assert 8 == unpack_length(1.), unpack_length(1.)
        assert 8 == unpack_length(1.0), unpack_length(1.0)
        assert 9 == unpack_length(1.1), unpack_length(1.1)
        assert 15 == unpack_length(1.7), unpack_length(1.7)
        assert 16 == unpack_length(2.), unpack_length(2.)
        self.assert_error(lambda: unpack_length(0.8))
        
    def assert_error(self, thunk):
        try:
            thunk()
            assert False, 'expected error'
        except:
            pass
        
    def assert_length_value(self, length, value, results):
        (l, v) = results
        assert l == length, (l, length)
        assert v == value, (v, value)
    
    def test_coerce_unknown(self):
        self.assert_error(lambda: coerce_unknown_length(-1))
        self.assert_length_value(8, b'\x00', coerce_unknown_length(0))
        self.assert_length_value(8, b'\x01', coerce_unknown_length(1))
        self.assert_length_value(8, b'\xff', coerce_unknown_length(255))
        self.assert_error(lambda: coerce_unknown_length(256))
        self.assert_length_value(8, b'\x00', coerce_unknown_length(b'\x00'))
        self.assert_length_value(16, b'ab', coerce_unknown_length(b'ab'))
        self.assert_length_value(16, b'ab', coerce_unknown_length(bytearray(b'ab')))
        self.assert_length_value(3, b'\x00', coerce_unknown_length('0o0'))
        self.assert_length_value(3, b'\x01', coerce_unknown_length('0o1'))
        self.assert_length_value(6, b'\x00', coerce_unknown_length('0o00'))
        self.assert_length_value(9, b'\x40', coerce_unknown_length('0o100'))
        self.assert_length_value(12, b'\xff\x03', coerce_unknown_length('0o1777'))
        self.assert_length_value(12, b'\xff\x03', coerce_unknown_length('0x3ff'))
        self.assert_length_value(12, b'\x03\xff', coerce_unknown_length('1777o0'))
        self.assert_length_value(12, b'\x03\xff', coerce_unknown_length('3ffx0'))
        self.assert_length_value(3, b'\x04', coerce_unknown_length('0b100'))
        self.assert_length_value(8, b'\x01', coerce_unknown_length([1]))
        self.assert_error(lambda: coerce_unknown_length([256]))
        self.assert_length_value(16, b'\x01\x02', coerce_unknown_length([1,2]))
    
    def test_coerce_known(self):
        self.assert_error(lambda: coerce_known_length(0, 1))
        self.assert_length_value(1, b'\x00', coerce_known_length(1, 0))
        self.assert_length_value(7, b'\x00', coerce_known_length(7, 0))
        self.assert_length_value(8, b'\x00', coerce_known_length(8, 0))
        self.assert_length_value(1, b'\x00', coerce_known_length(0.1, 0))
        self.assert_length_value(8, b'\x00', coerce_known_length(1., 0))
        self.assert_length_value(16, b'\x34\x12', coerce_known_length(16, 0x1234))
        self.assert_length_value(16, b'\x34\x12', coerce_known_length(16, '0x1234'))
        self.assert_length_value(16, b'\x12\x34', coerce_known_length(16, '1234x0'))
        
        
    