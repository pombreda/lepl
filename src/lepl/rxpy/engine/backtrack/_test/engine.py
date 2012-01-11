#LICENCE


from unittest import TestCase

from lepl.rxpy.engine.backtrack.engine import BacktrackingEngine
from lepl.rxpy.engine._test.engine import EngineTest


class BacktrackingEngineTest(EngineTest, TestCase):
    
    def default_engine(self):
        return BacktrackingEngine
    
    def test_stack(self):
        # optimized
        assert self.engine(self.parse('(?:abc)*x'), ('abc' * 50000) + 'x',  max_depth=1)
        # this defines a group, so requires state on stack
        assert self.engine(self.parse('(abc)*x'), ('abc' * 5) + 'x',  max_depth=6)
        # this is lazy, so doesn't
        assert self.engine(self.parse('(abc)*?x'), ('abc' * 5) + 'x',  max_depth=1)
        
    def test_lookback_with_offset(self):
        assert self.engine(self.parse('..(?<=a)'), 'xa', ticks=7)
        assert not self.engine(self.parse('..(?<=a)'), 'ax')
        
    def test_lookback_optimisations(self):
        assert self.engine(self.parse('(.).(?<=a)'), 'xa', ticks=9)
        # only one more tick with an extra character because we avoid starting
        # from the start in this case
        assert self.engine(self.parse('.(.).(?<=a)'), 'xxa', ticks=10)
        
        assert self.engine(self.parse('(.).(?<=\\1)'), 'aa', ticks=9)
        # again, just one tick more
        assert self.engine(self.parse('.(.).(?<=\\1)'), 'xaa', ticks=10)
        assert not self.engine(self.parse('.(.).(?<=\\1)'), 'xxa')
        
        assert self.engine(self.parse('(.).(?<=(\\1))'), 'aa', ticks=15)
        # but here, three ticks more because we have a group reference with
        # changing groups, so can't reliably calculate lookback distance
        assert self.engine(self.parse('.(.).(?<=(\\1))'), 'xaa', ticks=18)
        assert not self.engine(self.parse('.(.).(?<=(\\1))'), 'xxa')
        
        assert self.engine(self.parse('(.).(?<=a)'), 'xa', ticks=9)

        assert self.engine(self.parse('(.).(?<=(?:a|z))'), 'xa', ticks=10)
        assert self.engine(self.parse('(.).(?<=(a|z))'), 'xa', ticks=12)
        # only one more tick with an extra character because we avoid starting
        # from the start in this case
        assert self.engine(self.parse('.(.).(?<=(?:a|z))'), 'xxa', ticks=11)
        assert self.engine(self.parse('.(.).(?<=(a|z))'), 'xxa', ticks=13)
        
