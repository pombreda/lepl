
from unittest import TestCase

from lepl.bin.node import unpack_length, RawBits, Binary


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
        
    def assert_length_value(self, length, value, raw):
        assert raw._length == length, (raw._length, length)
        assert raw._value == value, (raw._value, value)
    
    def test_coerce_unknown(self):
        self.assert_error(lambda: RawBits(-1))
        self.assert_length_value(8, b'\x00', RawBits(0))
        self.assert_length_value(8, b'\x01', RawBits(1))
        self.assert_length_value(8, b'\xff', RawBits(255))
        self.assert_error(lambda: RawBits(256))
        self.assert_length_value(8, b'\x00', RawBits(b'\x00'))
        self.assert_length_value(16, b'ab', RawBits(b'ab'))
        self.assert_length_value(16, b'ab', RawBits(bytearray(b'ab')))
        self.assert_length_value(3, b'\x00', RawBits('0o0'))
        self.assert_length_value(3, b'\x01', RawBits('0o1'))
        self.assert_length_value(6, b'\x00', RawBits('0o00'))
        self.assert_length_value(9, b'\x40', RawBits('0o100'))
        self.assert_length_value(12, b'\xff\x03', RawBits('0o1777'))
        self.assert_length_value(12, b'\xff\x03', RawBits('0x3ff'))
        self.assert_length_value(12, b'\x03\xff', RawBits('1777o0'))
        self.assert_length_value(12, b'\x03\xff', RawBits('3ffx0'))
        self.assert_length_value(3, b'\x04', RawBits('0b100'))
        self.assert_length_value(8, b'\x01', RawBits([1]))
        self.assert_error(lambda: RawBits([256]))
        self.assert_length_value(16, b'\x01\x02', RawBits([1,2]))
    
    def test_coerce_known(self):
        self.assert_error(lambda: RawBits(1, 0))
        self.assert_length_value(1, b'\x00', RawBits((0, 1)))
        self.assert_length_value(7, b'\x00', RawBits((0, 7)))
        self.assert_length_value(8, b'\x00', RawBits((0, 8)))
        self.assert_length_value(1, b'\x00', RawBits((0, 0.1)))
        self.assert_length_value(8, b'\x00', RawBits((0, 1.)))
        self.assert_length_value(16, b'\x34\x12', RawBits((0x1234, 16)))
        self.assert_length_value(16, b'\x34\x12', RawBits(('0x1234', 16)))
        self.assert_length_value(16, b'\x12\x34', RawBits(('1234x0', 16)))
        self.assert_length_value(16, b'\x34\x12', RawBits(('4660', 16)))
        self.assert_length_value(16, b'\x34\x12', RawBits(('0d4660', 16)))
        self.assert_length_value(16, b'\x12\x34', RawBits(('4660d0', 16)))
        

class BinaryTest(TestCase):
    
    def test_constructor(self):
        b = Binary([(0, 8)])
        assert b[0]._value == b'\x00', str(b)
        assert b[0]._length == 8, str(b)
        b = Binary([(0, 8), (0, 8)])
        assert b[1]._value == b'\x00', str(b)
        assert b[1]._length == 8, str(b)
        b = Binary([(0, 8), (0,)])
        assert b[1]._value == b'\x00', str(b)
        assert b[1]._length == 8, str(b)
        b = Binary([(0, 8), 0])
        assert b[1]._value == b'\x00', str(b)
        assert b[1]._length == 8, str(b)
        b = Binary(["12"])
        assert b[0]._value == b'\x0c', str(b)
        assert b[0]._length == 8, str(b)
        
