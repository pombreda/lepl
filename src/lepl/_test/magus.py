
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests added for 3.2, 3.2.1
'''

# pylint: disable-msg=W0614, W0401, C0103, R0201, R0914, R0915
# test
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.graph import ConstructorWalker, LEAF, NONTREE, dfs_edges
from lepl.matchers import Matcher, Transform, Transformation
from lepl.memo import _LMemo, _RMemo
from lepl.rewriters import DelayedClone


class MagusTest(TestCase):
    '''
    Based on the original bug report. 
    '''
    
    def test_magus(self):
        '''
        This was failing.
        '''
        #basicConfig(level=DEBUG)

        name = Word(Letter()) > 'name'

        expression = Delayed()
        variable = Delayed()

        function = (expression / '()') > 'function'
        expression += (variable | function) > 'expression'
        variable += (name | expression / '.' / name)

        dotted_name = function & Eos()

        parser = dotted_name.string_parser(
                    Configuration(
                        rewriters=[flatten, compose_transforms, 
                                   auto_memoize()],
                        monitors=[TraceResults(False)]))
        parser("1func()")
        

class DelayedCloneTest(TestCase):
    '''
    The original problem for 3.2 was related to clones losing children.
    '''
    
    def test_clone(self):
        '''
        Clone and check children.
        '''
        a = Delayed()
        b = (a | 'c')
        a += b
        
        def simple_clone(node):
            '''
            Clone the node.
            '''
            walker = ConstructorWalker(node, Matcher)
            return walker(DelayedClone())
            
        self.assert_children(b)
        bb = simple_clone(b)
        self.assert_children(bb)
        
        
    def assert_children(self, b):
        '''
        Check children are non-None.
        '''
#        print('>>>{0!s}<<<'.format(b))
        assert isinstance(b, Or)
        for child in b.matchers:
            assert child
            


class Description(object):
    '''
    A description of a graph.
    '''
    
    def __init__(self, matcher):
        self.total = 0
        self.delayed = 0
        self.leaves = 0
        self.loops = 0
        self.duplicates = 0
        self.others = 0
        self.types = {}
        self.read(matcher)
        
    def assert_count(self, type_, count):
        '''
        Check that the instance count for a particular class is correct.
        '''
        assert self.types[type_] == count, self
        
    def read(self, matcher):
        '''
        Travers a graph from the given matcher, collecting stats.
        '''
        known = set()
        for (_parent, child, type_) in dfs_edges(matcher, Matcher):
            #print(repr(child))
            if type_ & LEAF:
                self.leaves += 1
            if type_ & NONTREE and isinstance(child, Matcher):
                self.loops += 1
            if child not in known:
                known.add(child)
                child_type = type(child)
                if child_type not in self.types:
                    self.types[child_type] = 0
                self.types[child_type] += 1
                if isinstance(child, Matcher):
                    self.total += 1
                    if isinstance(child, Delayed):
                        self.delayed += 1
                else:
                    self.others += 1
            else:
                self.duplicates += 1
                
    def __str__(self):
        counts = 'total:      {total:3d}\n' \
                 'delayed:    {delayed:3d}\n' \
                 'leaves:     {leaves:3d}\n' \
                 'loops:      {loops:3d}\n' \
                 'duplicates: {duplicates:3d}\n' \
                 'others:     {others:3d}\n'.format(**self.__dict__)
        keys = list(self.types.keys())
        keys.sort(key=repr)
        types = '\n'.join(['{0:40s}: {1:3d}'.format(key, self.types[key])
                           for key in keys])
        return counts + types
               
                
class CloneTest(TestCase):
    '''
    Test various clone functions.
    '''
    
    def test_describe(self):
        '''
        Use a description of the graph to check against changes.
        '''
        #basicConfig(level=DEBUG)

        name = Word(Letter()) > 'name'

        expression = Delayed()
        variable = Delayed()

        function = (expression / '()') > 'function'
        expression += (variable | function) > 'expression'
        variable += (name | expression / '.' / name)

        dotted_name = function & Eos()
        desc0 = Description(dotted_name)
        #print(desc0)
        assert desc0.total == 27, desc0
        desc0.assert_count(And, 5)
        desc0.assert_count(Or, 2)
        desc0.assert_count(Delayed, 2)
        
        clone1 = flatten(dotted_name)
        desc1 = Description(clone1)
        #print(desc1)
        # flattened two matchers - one each of And and Or
        assert desc1.total == 25, desc1
        desc1.assert_count(And, 4)
        desc1.assert_count(Or, 1)
        desc1.assert_count(Delayed, 2)
        desc1.assert_count(Transform, 7)
        desc1.assert_count(Transformation, 7)
        
        clone2 = compose_transforms(clone1)
        desc2 = Description(clone2)
        #print(desc2)
        # compressed two transforms
        assert desc2.total == 23, desc2
        desc2.assert_count(And, 4)
        desc2.assert_count(Or, 1)
        desc2.assert_count(Delayed, 2)
        desc2.assert_count(Transform, 5)
        desc2.assert_count(Transformation, 5)
        
        clone3 = memoize(RMemo)(clone2)
        desc3 = Description(clone3) 
        #print(desc3)
        assert desc3.total == 44, desc3
        desc3.assert_count(_RMemo, 21)
        desc3.assert_count(Delayed, 2)

        clone4 = memoize(LMemo)(clone2)
        desc4 = Description(clone4) 
        #print(desc4)
        assert desc4.total == 44, desc4
        desc4.assert_count(_LMemo, 21)
        desc4.assert_count(Delayed, 2)
        
        clone5 = context_memoize()(clone2)
        desc5 = Description(clone5) 
        #print(desc5)
        assert desc5.total == 44, desc5
        desc5.assert_count(_RMemo, 16)
        desc5.assert_count(_LMemo, 5)
        desc5.assert_count(Delayed, 2)
        
        try:
            clone3.parse_string('1join()', config=Configuration())
            assert False, 'Expected error'
        except MemoException as error:
            assert str(error) == 'Left recursion with RMemo?', str(error)
            
        clone4.parse_string('1join()', config=Configuration())
        clone5.parse_string('1join()', config=Configuration())
        
        
        