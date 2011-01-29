
'''
Validate the parsers.
'''

from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl._performance.dynamic.data import get_data
from lepl._performance.dynamic.parsers import base, restricted, \
    restricted_with_tokens
from lepl.support.lib import basestring


class Validate(TestCase):
    
    def signature(self, data):
        '''
        convert a tree to a series of lengths.
        '''
        if data and not isinstance(data, basestring):
            yield len(data)
            for child in data:
                for value in self.signature(child):
                    yield value

    def test_base(self):
        #basicConfig(level=DEBUG)
        result = base().parse(get_data(2))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 54, 2, 7, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 891, 2, 72, 2, 118, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 4, 2, 1, 2], sig
        result = base().parse(get_data(3))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 55, 2, 7, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 3, 2, 9, 2, 1, 2, 2, 2, 37, 2, 15, 2, 2, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 15, 2, 2, 2, 2, 4, 2, 3, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 15, 2, 2, 2, 2, 4, 2, 3, 2, 15, 2, 2, 2, 2, 4, 2, 3, 2, 10, 2, 2, 2, 16, 2, 3, 2, 2, 3, 2, 3, 2, 14, 2, 2, 2, 2, 3, 2, 3, 2, 14, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 14, 2, 3, 2, 2, 1, 2, 3, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 9, 2, 2, 2, 2, 10, 2, 2, 2, 2, 8, 2, 2, 2, 2, 4, 2, 3, 2, 14, 2, 3, 2, 2, 1, 2, 3, 2, 14, 2, 3, 2, 2, 1, 2, 3, 2, 17, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 17, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 12, 2, 2, 2, 1, 2, 3, 2, 10, 2, 2, 2, 15, 2, 3, 2, 2, 2, 2, 3, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 14, 2, 2, 2, 4, 2, 2, 891, 2, 72, 2, 118, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 4, 2, 1, 2], sig

    def test_restricted(self):
        result = restricted().parse(get_data(5))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 53, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 230, 2, 23, 2, 14, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
        result = restricted().parse(get_data(6))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 54, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 3, 2, 9, 2, 1, 2, 2, 2, 37, 2, 15, 2, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 17, 2, 2, 2, 8, 2, 2, 2, 2, 8, 2, 2, 2, 2, 8, 2, 2, 2, 2, 3, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 230, 2, 23, 2, 14, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
        result = restricted().parse(get_data(4))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 54, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 3, 2, 14, 2, 37, 2, 15, 2, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 24, 2, 2, 2, 10, 2, 2, 10, 2, 2, 10, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 230, 2, 23, 2, 14, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
        
    def test_tokens(self):
        result = restricted_with_tokens().parse(get_data(5))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 53, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 278, 2, 40, 2, 19, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
        result = restricted().parse(get_data(6))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 54, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 3, 2, 9, 2, 1, 2, 2, 2, 37, 2, 15, 2, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 17, 2, 2, 2, 8, 2, 2, 2, 2, 8, 2, 2, 2, 2, 8, 2, 2, 2, 2, 3, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 230, 2, 23, 2, 14, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
        result = restricted().parse(get_data(4))
        sig = list(self.signature(result))
        assert sig == [1, 2, 9, 2, 3, 2, 54, 2, 3, 2, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 4, 2, 6, 2, 7, 2, 6, 2, 7, 2, 7, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 7, 2, 6, 2, 5, 2, 5, 2, 6, 2, 5, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 5, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 2, 3, 2, 14, 2, 37, 2, 15, 2, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 2, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 24, 2, 2, 2, 10, 2, 2, 10, 2, 2, 10, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 16, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 12, 2, 2, 2, 1, 2, 2, 2, 10, 2, 2, 2, 12, 2, 3, 2, 2, 1, 2, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 14, 2, 2, 2, 3, 2, 2, 230, 2, 23, 2, 14, 2, 7, 2, 1, 2, 2, 2, 5, 2, 1, 2, 2, 2, 3, 2, 1, 2], sig
    