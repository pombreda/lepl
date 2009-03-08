
from unittest import TestCase

from lepl import *
from lepl.graph import preorder
from lepl.matchers import Transform
from lepl.rewriters import DelayedClone


class DelayedCloneTest(TestCase):
    
    def assert_clone(self, matcher):
        copy = matcher.postorder(DelayedClone())
        original = preorder(matcher)
        duplicate = preorder(copy)
        try:
            while True:
                o = next(original)
                d = next(duplicate)
                assert type(o) == type(d), (o, d)
                assert o is not d, (o, d)
        except StopIteration:
            self.assert_empty(original, 'original')
            self.assert_empty(duplicate, 'duplicate')
            
    def assert_empty(self, generator, name):
        try:
            next(generator)
            assert False, name + ' not empty'
        except StopIteration:
            pass
            
    def test_no_delayed(self):
        matcher = Any('a') | Any('b')[1:2,...]
        self.assert_clone(matcher)
        
    def test_simple_loop(self):
        delayed = Delayed()
        matcher = Any('a') | Any('b')[1:2,...] | delayed
        self.assert_clone(matcher)
        
    def test_complex_loop(self):
        delayed1 = Delayed()
        delayed2 = Delayed()
        line1 = Any('a') | Any('b')[1:2,...] | delayed1
        line2 = delayed1 & delayed2
        matcher = line1 | line2 | delayed1 | delayed2 > 'foo'
        self.assert_clone(matcher)


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
        
        print(factor)
        p = factor.string_parser(Configuration(rewriters=[compose_transforms]))
        print(p.matcher)
        ast = p('1')
        assert str(ast[0]) == """Term
 `- number '1'""", ast[0]
        

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
        print(p.matcher)
        assert isinstance(matcher.matcher.matchers[0], Any)
        