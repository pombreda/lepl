#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.engine import EngineTest
from lepl.rxpy.engine.simple.engine import SimpleEngine


class SimpleEngineTest(EngineTest, TestCase):
    
    def default_engine(self):
        return SimpleEngine

    def test_unicode_escapes(self):
        pass
    
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

    def test_lookback_bug_1(self):
        pass
    
    def test_groups_in_lookback(self):
        pass
    
    def test_extended_groups(self):
        pass
    
    def test_ascii_escapes(self):
        pass
    
    def test_repeat(self):
        pass
    
    def test_prime(self):
        pass
    
