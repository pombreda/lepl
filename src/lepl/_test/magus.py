

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *
from lepl.graph import ConstructorWalker, Clone, postorder, LEAF, ROOT
from lepl.matchers import Matcher
from lepl.rewriters import DelayedClone


class MagusTest(TestCase):
    
    def test_magus(self):
        #basicConfig(level=DEBUG)
        
        name = Word(Letter())
        
        expression = Delayed()
        variable = Delayed()
        
        function = (expression / '()') > 'function'
        expression += (variable | function)
        variable += (name | expression / '.' / name)
        
        dotted_name = function & Eos()
        
        parser = dotted_name.string_parser(Configuration())
        print(parser.matcher)
#        result = parser("func")


class DelayedCloneTest(TestCase):
    
    def test_clone(self):
        a = Delayed()
        b = (a | 'c')
        a += b
        
        def simple_clone(node):
            walker = ConstructorWalker(node, Matcher)
            return walker(DelayedClone())
            
        self.assert_children(b)
        
        print('')
        for x in postorder(b, Matcher, LEAF):
            print('> {1} {0!s}'.format(x, type(x)))
        
        # this should be an exact copy
        bb = simple_clone(b)
        # this fails because the first child is None
        self.assert_children(bb)
        
    def assert_children(self, b):
        print('>>>{0!s}<<<'.format(b))
        assert isinstance(b, Or)
        for child in b.matchers:
            assert child
            
