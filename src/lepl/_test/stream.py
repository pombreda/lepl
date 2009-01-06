
from unittest import TestCase

from lepl.stream import Stream


class StreamTest(TestCase):
    
    def test_single_line(self):
        s1 = Stream.from_string('abc')
        assert s1[0] == 'a', s1[0]
        assert s1[0:3] == 'abc', s1[0:3]
        assert s1[2] == 'c' , s1[2]
        s2 = s1[1:]
        assert s2[0] == 'b', s2[0]

    def test_multiple_lines(self):
        s1 = Stream.from_string('abc\npqs\nxyz')
        assert s1[0:3] == 'abc'
        assert s1[0:4] == 'abc\n'
        assert s1[0:5] == 'abc\np'
        assert s1[0:11] == 'abc\npqs\nxyz'
        assert s1[5] == 'q', s1[5]
        s2 = s1[5:]
        assert s2[0] == 'q', s2[0]
        assert repr(s2) == "Chunk('pqs\\n'...)[1:]", repr(s2)
        
    def test_eof(self):
        s1 = Stream.from_string('abc\npqs')
        assert s1[6] == 's', s1[6]
        try:
            s1[7]
            assert False, 'expected error'
        except IndexError:
            pass
        
