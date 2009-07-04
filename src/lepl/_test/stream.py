
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests for the lepl.stream module.
'''

from random import choice
from unittest import TestCase

from lepl.stream import SimpleStream, SequenceByLine, SimpleGeneratorStream


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324
# (dude this is just a test)

    
class StreamTest(TestCase):
    
    def test_single_line(self):
        s1 = SequenceByLine.from_string('abc')
        assert s1[0] == 'a', s1[0]
        assert s1[0:3] == 'abc', s1[0:3]
        assert s1[2] == 'c' , s1[2]
        s2 = s1[1:]
        assert s2[0] == 'b', s2[0]

    def test_multiple_lines(self):
        s1 = SequenceByLine.from_string('abc\npqr\nxyz')
        assert s1[0:3] == 'abc'
        assert s1[0:4] == 'abc\n'
        assert s1[0:5] == 'abc\np'
        assert s1[0:11] == 'abc\npqr\nxyz'
        assert s1[5] == 'q', s1[5]
        s2 = s1[5:]
        assert s2[0] == 'q', s2[0]
        assert repr(s2) == "Line('pqr\\n')[1:]", repr(s2)
        s3 = s2[3:]
        assert repr(s3) == "Line('xyz')[0:]", repr(s3)
        
    def test_eof(self):
        s1 = SequenceByLine.from_string('abc\npqs')
        assert s1[6] == 's', s1[6]
        try:
            # pylint: disable-msg=W0104
            s1[7]
            assert False, 'expected error'
        except IndexError:
            pass
        
    def test_string(self):
        s1 = SequenceByLine.from_string('12')
        assert '1' == s1[0:1]
        assert '12' == s1[0:2]
        s2 = s1[1:]
        assert '2' == s2[0:1]
        
    def test_read(self):
        s1 = SequenceByLine.from_string('12\n123\n')
        assert '12\n' == s1.text()


class SimpleStreamTester(object):
    '''
    Support for testing simple streams.
    '''
    
    def __init__(self, values, from_list):
        self.__values = values
        self.__from_list = from_list
        
    def build(self, n):
        l = [choice(self.__values) for _i in range(n)]
        s = self.__from_list(l)
        assert isinstance(s, SimpleStream)
        return (l, s)
    
    def test_single_index(self, n=3):
        (l, s) = self.build(n)
        for i in range(n):
            assert l[i] == s[i]
    
    def test_range(self, n=3, with_len=True):
        (l, s) = self.build(n)
        for i in range(n):
            for j in range(i, n):
                (lr, sr) = (l[i:j], s[i:j])
                for k in range(j-i):
                    assert lr[k] == sr[k], str(i) + ':' + str(j) + ': ' + str(lr) + '/' + str(sr)
                if with_len: 
                    assert len(lr) == len(sr)
                    for k in range(len(lr)):
                        assert lr[k] == sr[k]
                    
    def test_offset(self, n=3, with_len=True):
        (l, s) = self.build(n)
        for i in range(n):
            (lo, so) = (l[i:], s[i:])
            while lo:
                if with_len:
                    assert len(lo) == len(so), str(lo) + '/' + str(so)
                assert lo[0] == so[0]
                (lo, so) = (lo[1:], so[1:])
            assert not so
        

class SimpleStringTest(TestCase):
    
    def test_type(self):
        assert issubclass(str, SimpleStream)
        assert isinstance('abc', SimpleStream)
    
    def get_tester(self):
        return SimpleStreamTester(['a', 'b', 'c'], ''.join)
    
    def test_single_index(self):
        self.get_tester().test_single_index()
        
    def test_range(self):
        self.get_tester().test_range(with_len=False)
        self.get_tester().test_range(with_len=True)
        
    def test_offset(self):
        self.get_tester().test_offset(with_len=False)
        self.get_tester().test_offset(with_len=True)
        
        
class SimpleListTest(TestCase):
    
    def test_type(self):
        assert issubclass(list, SimpleStream)
        assert isinstance([1,2,3], SimpleStream)
    
    def get_tester(self):
        return SimpleStreamTester([1,2,3], list)
    
    def test_single_index(self):
        self.get_tester().test_single_index()
        
    def test_range(self):
        self.get_tester().test_range(with_len=False)
        self.get_tester().test_range(with_len=True)
        
    def test_offset(self):
        self.get_tester().test_offset(with_len=False)
        self.get_tester().test_offset(with_len=True)
        
        
class SimpleGeneratorStreamTest(TestCase):
    
    def get_tester(self):
        return SimpleStreamTester([1,"two", [3]],
                                  lambda l: SimpleGeneratorStream(iter(l)))
    
    def test_single_index(self):
        self.get_tester().test_single_index()
        
    def test_range(self):
        self.get_tester().test_range(with_len=False)
        self.get_tester().test_range(with_len=True)
        
    def test_offset(self):
        self.get_tester().test_offset(with_len=False)
        self.get_tester().test_offset(with_len=True)
        
