
from unittest import TestCase

from lepl.bin.bits import unpack_length, BitString


class BitStringTest(TestCase):

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
        
    def assert_length_value(self, length, value, b):
        assert len(b) == length, (len(b), length)
        assert b.to_bytes() == value, (b.to_bytes(), value, b)
    
    def test_from_byte(self):
        self.assert_error(lambda: BitString.from_byte(-1))
        self.assert_length_value(8, b'\x00', BitString.from_byte(0))
        self.assert_length_value(8, b'\x01', BitString.from_byte(1))
        self.assert_length_value(8, b'\xff', BitString.from_byte(255))
        self.assert_error(lambda: BitString.from_byte(256))
    
    def test_from_byte(self):
        self.assert_length_value(8, b'\x00', BitString.from_bytes(b'\x00'))
        self.assert_length_value(16, b'ab', BitString.from_bytes(b'ab'))
        self.assert_length_value(16, b'ab', BitString.from_bytes(bytearray(b'ab')))
        
    def test_from_extended_int(self):
        self.assert_length_value(3, b'\x00', BitString.from_extended_int('0o0'))
        self.assert_error(lambda: BitString.from_extended_int('0o1'))
        self.assert_error(lambda: BitString.from_extended_int('0o00'))
        self.assert_error(lambda: BitString.from_extended_int('0o100'))
        self.assert_error(lambda: BitString.from_extended_int('0o777'))
        self.assert_length_value(9, b'\x20\x00', BitString.from_extended_int('100o0'))
        self.assert_length_value(9, b'\xff\x80', BitString.from_extended_int('777o0'))
        self.assert_length_value(12, b'\x3f\xf0', BitString.from_extended_int('3ffx0'))
        self.assert_length_value(12, b'\x3f\xf0', BitString.from_extended_int('1777o0'))
        self.assert_length_value(12, b'\x3f\xf0', BitString.from_extended_int('3ffx0'))
        self.assert_length_value(3, b'\x80', BitString.from_extended_int('100b0'))
        
    def test_from_sequence(self):
        self.assert_length_value(8, b'\x01', BitString.from_sequence([1], BitString.from_byte))
        self.assert_error(lambda: BitString.from_sequence([256], BitString.from_byte))
        self.assert_length_value(16, b'\x01\x02', BitString.from_sequence([1,2], BitString.from_byte))
    
    def test_from_int_length(self):
        self.assert_error(lambda: BitString.from_int_length(1, 0))
        self.assert_error(lambda: BitString.from_int_length(0, 1))
        self.assert_error(lambda: BitString.from_int_length(0, 7))
        self.assert_length_value(8, b'\x00', BitString.from_int_length(0, 8))
        self.assert_error(lambda: BitString.from_int_length(0, 0.1))
        self.assert_length_value(8, b'\x00', BitString.from_int_length(0, 1.))
        self.assert_length_value(1, b'\x00', BitString.from_int_length('0x0', 1))
        self.assert_length_value(7, b'\x00', BitString.from_int_length('0x0', 7))
        self.assert_length_value(8, b'\x00', BitString.from_int_length('0x0', 8))
        self.assert_length_value(1, b'\x00', BitString.from_int_length('0x0', 0.1))
        self.assert_length_value(8, b'\x00', BitString.from_int_length('0x0', 1.))
        self.assert_length_value(16, b'\x34\x12', BitString.from_int_length(0x1234, 16))
        self.assert_length_value(16, b'\x34\x12', BitString.from_int_length('0x1234', 16))
        self.assert_length_value(16, b'\x12\x34', BitString.from_int_length('1234x0', 16))
        self.assert_length_value(16, b'\x34\x12', BitString.from_int_length('4660', 16))
        self.assert_length_value(16, b'\x34\x12', BitString.from_int_length('0d4660', 16))
        self.assert_length_value(16, b'\x12\x34', BitString.from_int_length('4660d0', 16))
        
    def test_str(self):
        b = BitString.from_int32(0xabcd1234)
        assert str(b) == '00110100 00010010 11001101 10101011/32', str(b)
        b = BitString.from_extended_int('110b0')
        assert str(b) == '110/3', str(b)

        