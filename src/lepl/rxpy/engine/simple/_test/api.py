#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.api import ReTest
from lepl.rxpy.engine.simple.engine import SimpleEngine


class SimpleReTest(ReTest, TestCase):
    
    def default_engine(self):
        return SimpleEngine

    def test_zero(self):
        pass
    
    def test_numbered(self):
        pass
    
    def test_split_from_docs(self):
        pass
    
    def test_match(self):
        pass
    
    def test_findall(self):
        pass
    
    
            