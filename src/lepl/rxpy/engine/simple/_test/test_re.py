#LICENCE

from unittest import TestCase

from lepl.rxpy.engine._test.test_re import ReTests
from lepl.rxpy.engine.simple.engine import SimpleEngine


class SimpleTest(ReTests, TestCase):
    
    def default_engine(self):
        return SimpleEngine

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
        pass

    def test_symbolic_refs(self):
        pass
    
    def test_sub_template_numeric_escape(self):
        pass
    
    def test_special_escapes(self):
        pass
    
    def test_search_coverage(self):
        pass
    
    def test_scanner(self):
        pass

    def test_repeat_minmax(self):
        pass
    
    def test_re_split(self):
        pass
    
    def test_re_match(self):
        pass
    
    def test_re_groupref_exists(self):
        pass
    
    def test_re_groupref(self):
        pass
    
    def test_re_findall(self):
        pass
    
    def test_qualified_re_split(self):
        pass
    
    def test_not_literal(self):
        pass
    
    def test_non_consuming(self):
        pass
    
    def test_ignore_case(self):
        pass
    
    def test_groupdict(self):
        pass
    
    def test_getattr(self):
        pass
    
    def test_expand(self):
        pass
    
    def test_category(self):
        pass
    
    def test_bug_725149(self):
        pass
    
    def test_bug_725106(self):
        pass

    def test_bug_527371(self):
        pass
    
    def test_bug_449964(self):
        pass
    
    def test_bug_117612(self):
        pass
    
    def test_bug_114660(self):
        pass
    
    def test_bug_113254(self):
        pass
    
    def test_bigcharset(self):
        pass
    
    def test_basic_re_sub(self):
        pass
    
    def test_all(self):
        pass
    
    def test_bug_448951(self):
        pass
    
