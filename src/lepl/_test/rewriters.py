
from unittest import TestCase

from lepl import *
from lepl.graph import preorder
from lepl.matchers import Transform
from lepl.operators import Matcher
from lepl.rewriters import DelayedClone


class DelayedCloneTest(TestCase):
    
    def assert_clone(self, matcher):
        copy = matcher.postorder(DelayedClone(), Matcher)
        original = preorder(matcher, Matcher)
        duplicate = preorder(copy, Matcher)
        try:
            while True:
                o = next(original)
                d = next(duplicate)
                assert type(o) == type(d), (o, d)
                if isinstance(o, Matcher):
                    assert o is not d, (o, d)
                else:
                    assert o is d, (o, d)
        except StopIteration:
            self.assert_empty(original, 'original')
            self.assert_empty(duplicate, 'duplicate')
    
    def assert_relative(self, matcher):
        copy = matcher.postorder(DelayedClone(), Matcher)
        def pairs(matcher):
            for a in preorder(matcher, Matcher):
                for b in preorder(matcher, Matcher):
                    yield (a, b)
        for ((a,b), (c,d)) in zip(pairs(matcher), pairs(copy)):
            if a is b:
                assert c is d
            else:
                assert c is not d
            if type(a) is type(b):
                assert type(c) is type(d)
            else:
                assert type(c) is not type(d)
            
    def assert_empty(self, generator, name):
        try:
            next(generator)
            assert False, name + ' not empty'
        except StopIteration:
            pass
            
    def test_no_delayed(self):
        matcher = Any('a') | Any('b')[1:2,...]
        self.assert_clone(matcher)
        self.assert_relative(matcher)
        
    def test_simple_loop(self):
        delayed = Delayed()
        matcher = Any('a') | Any('b')[1:2,...] | delayed
        self.assert_clone(matcher)
        self.assert_relative(matcher)
       
    def test_complex_loop(self):
        delayed1 = Delayed()
        delayed2 = Delayed()
        line1 = Any('a') | Any('b')[1:2,...] | delayed1
        line2 = delayed1 & delayed2
        matcher = line1 | line2 | delayed1 | delayed2 > 'foo'
        self.assert_clone(matcher)
        self.assert_relative(matcher)

    def test_common_child(self):
        a = Any('a')
        b = a | Any('b')
        c = a | b | Any('c')
        matcher = a | b | c
        self.assert_clone(matcher)
        self.assert_relative(matcher)
                

def append(x):
    return lambda l: l[0] + x

class ComposeTransformsTest(TestCase):
    
    def test_null(self):
        matcher = Any() > append('x')
        parser = matcher.null_parser(Configuration(rewriters=[]))
        result = parser('a')[0]
        assert result == 'ax', result
        
    def test_simple(self):
        matcher = Any() > append('x')
        parser = matcher.null_parser(Configuration(rewriters=[compose_transforms]))
        result = parser('a')[0]
        assert result == 'ax', result
        
    def test_double(self):
        matcher = (Any() > append('x')) > append('y')
        parser = matcher.null_parser(Configuration(rewriters=[compose_transforms]))
        result = parser('a')[0]
        assert result == 'axy', result
        assert isinstance(parser.matcher, Transform)
        assert isinstance(parser.matcher.matcher, Any)
    
    def test_and(self):
        matcher = (Any() & Optional(Any())) > append('x')
        parser = matcher.null_parser(Configuration(rewriters=[compose_transforms]))
        result = parser('a')[0]
        assert result == 'ax', result
        assert isinstance(parser.matcher, And)
    
    def test_loop(self):
        matcher = Delayed()
        matcher += (Any() | matcher) > append('x')
        parser = matcher.null_parser(Configuration(rewriters=[compose_transforms]))
        result = parser('a')[0]
        assert result == 'ax', result
        assert isinstance(parser.matcher, Delayed)
        
    def test_node(self):
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        number      = Any('1')                             > 'number'
        term        = number                               > Term
        factor      = term | Drop(Optional(term))
        
        p = factor.string_parser(Configuration(rewriters=[compose_transforms]))
        ast = p('1')[0]
        assert type(ast) == Term, type(ast)
        assert ast[0] == '1', ast[0]
        assert str(ast) == """Term
 `- number '1'""", ast
        

class OptimizeOrTest(TestCase):
    
    def test_conservative(self):
        matcher = Delayed()
        matcher += matcher | Any()
        assert isinstance(matcher.matcher.matchers[0], Delayed)
        p = matcher.string_parser(Configuration(rewriters=[optimize_or(True)]))
        assert isinstance(matcher.matcher.matchers[0], Any)
        
    def test_liberal(self):
        matcher = Delayed()
        matcher += matcher | Any()
        assert isinstance(matcher.matcher.matchers[0], Delayed)
        p = matcher.string_parser(Configuration(rewriters=[optimize_or(False)]))
        assert isinstance(matcher.matcher.matchers[0], Any)
        