
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
        s1 = Stream.from_string('abc\npqr\nxyz')
        assert s1[0:3] == 'abc'
        assert s1[0:4] == 'abc\n'
        assert s1[0:5] == 'abc\np'
        assert s1[0:11] == 'abc\npqr\nxyz'
        assert s1[5] == 'q', s1[5]
        s2 = s1[5:]
        assert s2[0] == 'q', s2[0]
        assert repr(s2) == "Chunk('pqr\\n')[1:]", repr(s2)
        s3 = s2[3:]
        assert repr(s3) == "Chunk('xyz')[0:]", repr(s3)
        
    def test_eof(self):
        s1 = Stream.from_string('abc\npqs')
        assert s1[6] == 's', s1[6]
        try:
            s1[7]
            assert False, 'expected error'
        except IndexError:
            pass
        
    def test_string(self):
        s1 = Stream.from_string('12')
        assert '1' == s1[0:1]
        assert '12' == s1[0:2]
        s2 = s1[1:]
        assert '2' == s2[0:1]
        
    def test_read(self):
        s1 = Stream.from_string('12\n123\n')
        assert '12\n' == s1.text()
