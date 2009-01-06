
from unittest import TestCase

from lepl.support import assert_type


class AssertTypeTestCase(TestCase):
    
    def test_ok(self):
        assert_type('', int, 1)
        assert_type('', str, '')
        assert_type('', int, None, none_ok=True)
        
    def test_bad(self):
        self.assert_bad('The foo attribute in Bar', int, '', False, 
                        "The foo attribute in Bar (value '') must be of type int.")
        self.assert_bad('The foo attribute in Bar', int, None, False, 
                        "The foo attribute in Bar (value None) must be of type int.")
        
    def assert_bad(self, name, type_, value, none_ok, msg):
        try:
            assert_type(name, type_, value, none_ok=none_ok)
            assert False, 'Expected failure'
        except TypeError as e:
            assert e.msg == msg, e.msg
