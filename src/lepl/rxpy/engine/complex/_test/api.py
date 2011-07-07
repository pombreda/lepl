#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.api import ReTest
from lepl.rxpy.engine.complex.engine import ComplexEngine


class ComplexReTest(ReTest, TestCase):
    
    def default_engine(self):
        return ComplexEngine

