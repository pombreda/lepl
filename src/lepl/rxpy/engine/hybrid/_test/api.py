#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.api import ReTest
from lepl.rxpy.engine.hybrid.engine import HybridEngine


class HybridReTest(ReTest, TestCase):
    
    def default_engine(self):
        return HybridEngine

