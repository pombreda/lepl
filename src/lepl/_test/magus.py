
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
from lepl.graph import ConstructorWalker
from lepl.matchers import Matcher, Transform, Transformation
from lepl.memo import _LMemo, _RMemo
from lepl.rewriters import DelayedClone, NodeStats


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
        desc0 = NodeStats(dotted_name)
        #print(desc0)
        assert desc0.total == 27, desc0
        self.assert_count(desc0, And, 5)
        self.assert_count(desc0, Or, 2)
        self.assert_count(desc0, Delayed, 2)
        
        clone1 = flatten(dotted_name)
        desc1 = NodeStats(clone1)
        #print(desc1)
        # flattened two matchers - one each of And and Or
        assert desc1.total == 25, desc1
        self.assert_count(desc1, And, 4)
        self.assert_count(desc1, Or, 1)
        self.assert_count(desc1, Delayed, 2)
        self.assert_count(desc1, Transform, 7)
        self.assert_count(desc1, Transformation, 7)
        
        clone2 = compose_transforms(clone1)
        desc2 = NodeStats(clone2)
        #print(desc2)
        # compressed two transforms
        assert desc2.total == 23, desc2
        self.assert_count(desc2, And, 4)
        self.assert_count(desc2, Or, 1)
        self.assert_count(desc2, Delayed, 2)
        self.assert_count(desc2, Transform, 5)
        self.assert_count(desc2, Transformation, 5)
        
        clone3 = memoize(RMemo)(clone2)
        desc3 = NodeStats(clone3) 
        #print(desc3)
        assert desc3.total == 44, desc3
        self.assert_count(desc3, _RMemo, 21)
        self.assert_count(desc3, Delayed, 2)

        clone4 = memoize(LMemo)(clone2)
        desc4 = NodeStats(clone4) 
        #print(desc4)
        assert desc4.total == 44, desc4
        self.assert_count(desc4, _LMemo, 21)
        self.assert_count(desc4, Delayed, 2)
        
        clone5 = context_memoize()(clone2)
        desc5 = NodeStats(clone5) 
        #print(desc5)
        assert desc5.total == 44, desc5
        self.assert_count(desc5, _RMemo, 16)
        self.assert_count(desc5, _LMemo, 5)
        self.assert_count(desc5, Delayed, 2)
        
        try:
            clone3.parse_string('1join()', config=Configuration())
            assert False, 'Expected error'
        except MemoException as error:
            assert str(error) == 'Left recursion with RMemo?', str(error)
            
        clone4.parse_string('1join()', config=Configuration())
        clone5.parse_string('1join()', config=Configuration())
        
    def assert_count(self, desc, type_, count):
        '''
        Check the count for a given type.
        '''
        assert type_ in desc.types and len(desc.types[type_]) == count, \
            len(desc.types[type_]) if type_ in desc.types else type_

        