
from unittest import TestCase

from lepl import Literal, Error
from lepl.error import make_error


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
        