#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.digits import DigitsTest
from lepl.rxpy.engine.simple.engine import SimpleEngine


class SimpleDigitsTest(DigitsTest, TestCase):
    
    def default_engine(self):
        return SimpleEngine

    def test_nested_group(self):
        pass
    
    def test_groups(self):
        pass
    
    def test_group_reference(self):
        pass
    
    def test_group(self):
        pass

    def test_conditional(self):
        pass
    
