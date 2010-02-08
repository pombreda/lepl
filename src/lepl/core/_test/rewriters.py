
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
Tests for the lepl.rewriters module.
'''

from logging import basicConfig, DEBUG
from re import sub
from unittest import TestCase

from lepl import Any, Or, Delayed, Optional, Node, Drop, And, Join
from lepl.support.graph import preorder
from lepl.matchers.matcher import Matcher, is_child
from lepl.matchers.support import TransformableWrapper
from lepl.core.rewriters import DelayedClone


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0321
# (dude this is just a test)

    
def str26(value):
    '''
    Hack 2.6 string conversion
    '''
    string = str(value)
    return string.replace("u'", "'")


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
        matcher.config.clear()
        parser = matcher.null_parser()
        result = parser('a')[0]
        assert result == 'ax', result
        
    def test_simple(self):
        matcher = Any() > append('x')
        matcher.config.compose_transforms()
        parser = matcher.null_parser()
        result = parser('a')[0]
        assert result == 'ax', result
        
    def test_double(self):
        matcher = (Any() > append('x')) > append('y')
        matcher.config.compose_transforms()
        parser = matcher.null_parser()
        result = parser('a')[0]
        assert result == 'axy', result
        # TODO - better test
        assert isinstance(parser.matcher, TransformableWrapper)
    
    def test_and(self):
        matcher = (Any() & Optional(Any())) > append('x')
        matcher.config.compose_transforms()
        parser = matcher.null_parser()
        result = parser('a')[0]
        assert result == 'ax', result
        assert is_child(parser.matcher, And), type(parser.matcher)
    
    def test_loop(self):
        matcher = Delayed()
        matcher += (Any() | matcher) > append('x')
        matcher.config.compose_transforms()
        parser = matcher.null_parser()
        result = parser('a')[0]
        assert result == 'ax', result
        assert isinstance(parser.matcher, Delayed)
        
    def test_node(self):
        
        class Term(Node): pass

        number      = Any('1')                             > 'number'
        term        = number                               > Term
        factor      = term | Drop(Optional(term))
        
        factor.config.compose_transforms()
        p = factor.string_parser()
        ast = p('1')[0]
        assert type(ast) == Term, type(ast)
        assert ast[0] == '1', ast[0]
        assert str26(ast) == """Term
 `- number '1'""", ast
        

class OptimizeOrTest(TestCase):
    
    def test_conservative(self):
        matcher = Delayed()
        matcher += matcher | Any()
        assert isinstance(matcher.matcher.matchers[0], Delayed)
        matcher.config.optimize_or(True)
        matcher.string_parser()
        # TODO - better test
        assert isinstance(matcher.matcher.matchers[0], 
                          TransformableWrapper)
        
    def test_liberal(self):
        matcher = Delayed()
        matcher += matcher | Any()
        assert isinstance(matcher.matcher.matchers[0], Delayed)
        matcher.config.optimize_or(False)
        matcher.string_parser()
        # TODO - better test
        assert isinstance(matcher.matcher.matchers[0], 
                          TransformableWrapper)


class AndNoTrampolineTest(TestCase):
    
    def test_replace(self):
        #basicConfig(level=DEBUG)
        matcher = And('a', 'b')
        matcher.config.clear().no_trampoline()
        parser = matcher.null_parser()
        text = str(parser.matcher)
        assert "AndNoTrampoline('a', 'b')" == text, text
        #assert "AndNoTrampoline(Literal, Literal)" == text, text
        result = parser('ab')
        assert result == ['a', 'b'], result
         

class FlattenTest(TestCase):
    
    def test_flatten_and(self):
        matcher = And('a', And('b', 'c'))
        matcher.config.clear().flatten()
        parser = matcher.null_parser()
        text = str(parser.matcher)
        assert text == "And('a', 'b', 'c')", text
        result = parser('abcd')
        assert result == ['a', 'b', 'c'], result
        
    def test_no_flatten_and(self):
        matcher = And('a', Join(And('b', 'c')))
        matcher.config.clear().flatten()
        parser = matcher.null_parser()
        text = str(parser.matcher)
        assert text == "And('a', Transform)", text
        result = parser('abcd')
        assert result == ['a', 'bc'], result
        
    def test_flatten_and_transform(self):
        matcher = Join(And('a', And('b', 'c')))
        matcher.config.clear().flatten()
        parser = matcher.null_parser()
        text = sub('<.*>', '<>', str(parser.matcher))
        assert text == "Transform(And, Transformation([<>]))", text
        result = parser('abcd')
        assert result == ['abc'], result
        
    def test_flatten_or(self):
        matcher = Or('a', Or('b', 'c'))
        matcher.config.clear().flatten()
        parser = matcher.null_parser()
        text = str(parser.matcher)
        assert text == "Or('a', 'b', 'c')", text
        result = parser('abcd')
        assert result == ['a'], result
        
    def test_no_flatten_or(self):
        matcher = Or('a', Join(Or('b', 'c')))
        matcher.config.clear().flatten()
        parser = matcher.null_parser()
        text = str(parser.matcher)
        assert text == "Or('a', Transform)", text
        result = parser('abcd')
        assert result == ['a'], result
        
