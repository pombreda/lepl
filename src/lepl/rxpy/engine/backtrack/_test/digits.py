#LICENCE


from unittest import TestCase

from lepl.rxpy.engine.backtrack.engine import BacktrackingEngine
from lepl.rxpy.engine._test.digits import DigitsTest


class BacktrackDigitsTest(DigitsTest, TestCase):
    
    def default_engine(self):
        return BacktrackingEngine
