#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.digits import DigitsTest
from lepl.rxpy.engine.complex.engine import ComplexEngine


class ComplexDigitsTest(DigitsTest, TestCase):
    
    def default_engine(self):
        return ComplexEngine
