
from unittest import TestCase

from lepl.regexp.interval import IntervalMap, TaggedFragments, Character
from lepl.regexp.unicode import UNICODE


class IntervalMapTest(TestCase):
    
    def test_single(self):
        m = IntervalMap()
        m[(1,2)] = 12
        assert m[0] == None, m[0]
        assert m[1] == 12, m[1]
        assert m[1.5] == 12, m[1.5]
        assert m[2] == 12, m[2]
        assert m[3] == None, m[3]
    
    def test_multiple(self):
        m = IntervalMap()
        m[(1,2)] = 12
        m[(4,5)] = 45
        for (i, v) in [(0, None), (1, 12), (2, 12), 
                       (3, None), (4, 45), (5, 45), (6, None)]:
            assert m[i] == v, (i, m[i])

    def test_delete(self):
        m = IntervalMap()
        m[(1,2)] = 12
        m[(4,5)] = 45
        for (i, v) in [(0, None), (1, 12), (2, 12), 
                       (3, None), (4, 45), (5, 45), (6, None)]:
            assert m[i] == v, (i, m[i])
        del m[(1,2)]
        for (i, v) in [(0, None), (1, None), (2, None), 
                       (3, None), (4, 45), (5, 45), (6, None)]:
            assert m[i] == v, (i, m[i])
        
        
class TaggedFragmentsTest(TestCase):
    
    def test_single(self):
        m = TaggedFragments(UNICODE)
        m.append(Character([('b', 'c')], UNICODE), 'bc')
        l = list(m)
        assert l == [(('b', 'c'), ['bc'])], l
        
    def test_overlap(self):
        m = TaggedFragments(UNICODE)
        m.append(Character([('b', 'd')], UNICODE), 'bd')
        m.append(Character([('c', 'e')], UNICODE), 'ce')
        l = list(m)
        assert l == [(('b', 'b'), ['bd']), 
                     (('c', 'd'), ['bd', 'ce']), 
                     (('e', 'e'), ['ce'])], l
        