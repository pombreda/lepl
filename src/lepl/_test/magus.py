

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.graph import ConstructorWalker, Clone, postorder, LEAF, ROOT,\
    NONTREE, dfs_edges
from lepl.matchers import Matcher
from lepl.rewriters import DelayedClone


class MagusTest(TestCase):
    
    def test_magus(self):
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
    
    def test_clone(self):
        a = Delayed()
        b = (a | 'c')
        a += b
        
        def simple_clone(node):
            walker = ConstructorWalker(node, Matcher)
            return walker(DelayedClone())
            
        self.assert_children(b)
        bb = simple_clone(b)
        self.assert_children(bb)
        
        
    def assert_children(self, b):
#        print('>>>{0!s}<<<'.format(b))
        assert isinstance(b, Or)
        for child in b.matchers:
            assert child
            


class Description(object):
    
    def __init__(self, matcher):
        self.total = 0
        self.delayed = 0
        self.leaves = 0
        self.loops = 0
        self.duplicates = 0
        self.others = 0
        self.types = {}
        self.read(matcher)
        
    def read(self, matcher):
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
        keys.sort(key=lambda x: repr(x))
        types = '\n'.join(['{0:40s}: {1:3d}'.format(key, self.types[key])
                           for key in keys])
        return counts + types
               
                
class ClonetTest(TestCase):
    
    def test_describe(self):
        #basicConfig(level=DEBUG)

        name = Word(Letter()) > 'name'

        expression = Delayed()
        variable = Delayed()

        function = (expression / '()') > 'function'
        expression += (variable | function) > 'expression'
        variable += (name | expression / '.' / name)

        dotted_name = function & Eos()
        #desc0 = Description(dotted_name)
        #print(desc0)
        
        clone1 = flatten(dotted_name)
        #desc1 = Description(clone1)
        #print(desc1)
        
        clone2 = compose_transforms(clone1)
        #desc2 = Description(clone2)
        #print(desc2)
        
        clone3 = memoize(RMemo)(clone2)
        #desc3 = Description(clone3) 
        #print(desc3)

        clone4 = memoize(LMemo)(clone2)
        #desc4 = Description(clone4) 
        #print(desc4)
        
        clone5 = context_memoize()(clone2)
        #desc5 = Description(clone5) 
        #print(desc5)
        
        try:
            clone3.parse_string('1join()', config=Configuration())
            assert False, 'Expected error'
        except MemoException as error:
            assert str(error) == 'Left recursion with RMemo?', str(error)
            
        clone4.parse_string('1join()', config=Configuration())
        clone5.parse_string('1join()', config=Configuration())
        
        
        