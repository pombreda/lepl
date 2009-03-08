
from logging import basicConfig, DEBUG
from types import MethodType
from unittest import TestCase

from lepl import *
from lepl.parser import string_parser, string_matcher, Configuration
from lepl.support import LogMixin


class InstanceMethodTest(TestCase):
    
    class Foo():
        class_attribute = 1
        def __init__(self):
            self.instance_attribute = 2
        def bar(self):
            return (self.class_attribute,
                    self.instance_attribute,
                    hasattr(self, 'baz'))

    def test_method(self):
        foo = self.Foo()
        assert foo.bar() == (1, 2, False)
        def my_baz(myself):
             return (myself.class_attribute,
                     myself.instance_attribute,
                     hasattr(myself, 'baz'))
        foo.baz = MethodType(my_baz, foo)
        assert foo.baz() == (1, 2, True)
        assert foo.bar() == (1, 2, True)


class FlattenTest(TestCase):
    
    def test_flatten(self):
        matcher = Literal('a') & Literal('b') & Literal('c')
        assert str(matcher) == "And(And(Literal('a'), Literal('b')), Literal('c'))", str(matcher)
        parser = matcher.string_parser(Configuration(rewriters=[flatten({And: '*matchers', Or: '*matchers'})]))
        assert str(parser.matcher) == "And(Literal('a'), Literal('b'), Literal('c'))", str(parser.matcher)


class RepeatTest(TestCase):
    
    def test_depth(self):
        matcher = Any()[:,...]
        matcher = matcher.string_matcher()
        results = [m for (m, s) in matcher('abc')]
        assert results == [['abc'], ['ab'], ['a'], []], results

    def test_breadth(self):
        matcher = Any()[::'b',...]
        matcher = matcher.string_matcher()
        results = [m for (m, s) in matcher('abc')]
        assert results == [[], ['a'], ['ab'], ['abc']], results
        