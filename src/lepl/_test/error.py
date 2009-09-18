
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
Tests for the lepl.error module.
'''

from unittest import TestCase

from lepl import Literal, Error
from lepl.error import make_error


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201
# (dude this is just a test)

    
class MessageTest(TestCase):
    '''
    Check generation of Error nodes.
    '''
    
    def test_simple(self):
        '''
        Test a message with no formatting.
        '''
        parser = (Literal('abc') > 'name') ** make_error('msg')
        node = parser.parse('abc')[0]
        assert isinstance(node, Error)
        assert node[0] == 'abc', node[0]
        assert node.name == ['abc'], node.name
        assert str(node).startswith('msg ('), str(node)
        assert isinstance(node, Exception), type(node)

    def test_formatted(self):
        '''
        Test a message with formatting.
        '''
        parser = (Literal('abc') > 'name') ** make_error('msg {stream_in}')
        node = parser.parse('abc')[0]
        assert isinstance(node, Error)
        assert node[0] == 'abc', node[0]
        assert node.name == ['abc'], node.name
        assert str(node).startswith('msg abc ('), str(node)
        assert isinstance(node, Exception), type(node)
        
    def test_bad_format(self):
        '''
        Test a message with formatting.
        '''
        parser = (Literal('abc') > 'name') ** make_error('msg {0}')
        assert None == parser.parse('abc')

    def test_list(self):
        '''
        Code has an exception for handling lists.
        '''
        parser = (Literal([1, 2, 3]) > 'name') ** make_error('msg {stream_in}')
        node = parser.parse([1, 2, 3])[0]
        assert isinstance(node, Error)
        assert node[0] == [1, 2, 3], node[0]
        assert node.name == [[1, 2, 3]], node.name
        assert str(node).startswith('msg [1, 2, 3] ('), str(node)
        assert isinstance(node, Exception), type(node)
        