#LICENCE


from unittest import TestCase

from lepl.rxpy.engine.backtrack.engine import BacktrackingEngine
from lepl.rxpy.engine._test.api import ReTest


class BacktrackingReTest(ReTest, TestCase):
    
    def default_engine(self):
        return BacktrackingEngine

