
from unittest import TestCase

from lepl.stream import Stream


class StreamTest(TestCase):
    
    def test_single_line(self):
        s1 = Stream.from_string('abc')
        assert s1[0] == 'a', s1[0]
        assert s1[0:3] == 'abc', s1[0:3]
        s2 = s1[1:]
        assert s2[0] == 'b', s2[0]
        