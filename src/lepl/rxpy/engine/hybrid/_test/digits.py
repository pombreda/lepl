#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.digits import DigitsTest
from lepl.rxpy.engine.hybrid.engine import HybridEngine


class HybridDigitsTest(DigitsTest, TestCase):
    
    def default_engine(self):
        return HybridEngine
