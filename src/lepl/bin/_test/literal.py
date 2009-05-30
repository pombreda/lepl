
from unittest import TestCase

from lepl.bin.literal import parse
from lepl.bin.node import Binary


class ParseTest(TestCase):
    '''
    Test whether we correctly parse a spec.
    '''
    
    def test_single(self):
        b = parse('''(123, foo=0x123/2.0,\nbar=1111100010001000b0)''')
        assert b[0][0] == 8, str(b)
        assert b[0][1] == b'\x7b', str(b)
        assert b[1][1][0] == 16, str(b)
        assert b[1][1][1] == b'\x23\x01', str(b)
        assert b.foo[0][0] == 16, str(b.foo)
        assert b.foo[0][1] == b'\x23\x01', str(b)
        assert b[2][1][0] == 16, str(b)
        assert b[2][1][1] == b'\xf8\x88', str(b)
        assert b.bar[0][0] == 16, str(b)
        assert b.bar[0][1] == b'\xf8\x88', str(b)
        
    def test_nested(self):
        b = parse('(123, (foo=123x0/2.))')
        assert b[0][0] == 8, str(b)
        assert b[0][1] == b'\x7b', str(b)
        assert isinstance(b[1], Binary), str(b)
        assert b[1].foo[0][0] == 16, str(b)
    
    def test_named(self):
        b = parse('A(B(1), B(2))')
        assert b.B[0][0][1] == b'\x01', str(b)
        assert b.B[1][0][1] == b'\x02', str(b)

    def test_list(self):
         b = parse('([1,2,3,4])')
         assert b[0][0] == 32, str(b)
         assert b[0][1] == b'\x01\x02\x03\x04', str(b)

    def test_repeat(self):
         b = parse('([1,2]*3)')
         assert b[0][0] == 48, str(b)
         assert b[0][1] == b'\x01\x02\x01\x02\x01\x02', str(b)
         b = parse('(a=[1,2]*3)')
         assert b.a[0][0] == 48, str(b)
         assert b.a[0][1] == b'\x01\x02\x01\x02\x01\x02', str(b)

