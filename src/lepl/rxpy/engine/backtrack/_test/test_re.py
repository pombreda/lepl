#LICENCE


from unittest import TestCase

from lepl.rxpy.engine.backtrack.engine import BacktrackingEngine
from lepl.rxpy.engine._test.test_re import ReTests


class BacktrackingTest(ReTests, TestCase):
    
    def default_engine(self):
        return BacktrackingEngine

