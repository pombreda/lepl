#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.engine import EngineTest
from lepl.rxpy.engine.complex.engine import ComplexEngine


class ComplexEngineTest(EngineTest, TestCase):
    
    def default_engine(self):
        return ComplexEngine

