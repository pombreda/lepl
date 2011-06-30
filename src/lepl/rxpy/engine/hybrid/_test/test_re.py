#LICENCE


from unittest import TestCase

from lepl.rxpy.engine._test.test_re import ReTests
from lepl.rxpy.engine.hybrid.engine import HybridEngine


class HybridTest(ReTests, TestCase):
    
    def default_engine(self):
        return HybridEngine

    def test_bug_418626(self):
        # bugs 418626 at al. -- Testing Greg Chapman's addition of op code
        # SRE_OP_MIN_REPEAT_ONE for eliminating recursion on simple uses of
        # pattern '*?' on a long string.
        self.assertEqual(self._re.match('.*?c', 10000*'ab'+'cd').end(0), 20001)
        self.assertEqual(self._re.match('.*?cd', 5000*'ab'+'c'+5000*'ab'+'cde').end(0),
                         20003)
        self.assertEqual(self._re.match('.*?cd', 20000*'abc'+'de').end(0), 60001)
        # non-simple '*?' still used to hit the recursion limit, before the
        # non-recursive scheme was implemented.
        self.assertEqual(self._re.search('(a|b)*?c', 10000*'ab'+'cd').end(0), 20001)
