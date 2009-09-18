
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
Tests for the lepl.support module.
'''

from unittest import TestCase

from lepl.support import assert_type, CircularFifo


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, R0201, R0913
# (dude this is just a test)

    
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
            
    def test_pop(self):
        fifo = CircularFifo(3)
        for i in range(1,3):
            for j in range(i):
                assert None == fifo.append(j)
            for j in range(i):
                popped = fifo.pop()
                assert j == popped, '{0} {1} {2}'.format(i, j, popped)
        for i in range(4):
            fifo.append(i)
        assert 1 == fifo.pop()
        
    def test_list(self):
        fifo = CircularFifo(3)
        for i in range(7):
            fifo.append(i)
        assert [4,5,6] == list(fifo)
        fifo.append(7)
        assert [5,6,7] == list(fifo)
        fifo.append(8)
        assert [6,7,8] == list(fifo)
        fifo.append(9)
        assert [7,8,9] == list(fifo)
