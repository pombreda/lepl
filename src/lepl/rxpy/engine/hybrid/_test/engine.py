#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.engine import EngineTest
from lepl.rxpy.engine.hybrid.engine import HybridEngine


class HybridEngineTest(EngineTest, TestCase):
    
    def default_engine(self):
        return HybridEngine

