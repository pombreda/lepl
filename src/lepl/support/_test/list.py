
# Copyright 2010 Andrew Cooke

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
Tests for the lepl.support.list module.
'''

#from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl import *
from lepl._test.base import assert_str
from lepl.support.list import clone_sexpr, count_sexpr, join, \
    sexpr_flatten, sexpr_to_str


class FoldTest(TestCase):
    
    def test_clone(self):
        def test(list_):
            copy = clone_sexpr(list_)
            assert copy == list_, sexpr_to_str(copy)
        test([])
        test([1,2,3])
        test([[1],2,3])
        test([[[1]],2,3])
        test([[[1]],2,[3]])
        test([[[1]],'2',[3]])
        test(((1),List([2,3,[4]])))

    def test_count(self):
        def test(list_, value):
            measured = count_sexpr(list_)
            assert measured == value, measured
        test([], 0)
        test([1,2,3], 3)
        test([[1],2,3], 3)
        test([[[1,2],3],'four',5], 5)
        
    def test_flatten(self):
        def test(list_, joined, flattened):
            if joined is not None:
                result = join(list_)
                assert result == joined, result
            result = sexpr_flatten(list_)
            assert result == flattened, result
        test([[1],[2, [3]]], [1,2,[3]], [1,2,3])
        test([], [], [])
        test([1,2,3], None, [1,2,3])
        test([[1],2,3], None, [1,2,3])
        test([[[1,'two'],3],'four',5], None, [1,'two',3,'four',5])

    def test_sexpr_to_string(self):
        def test(list_, value):
            result = sexpr_to_str(list_)
            assert result == value, result
        test([1,2,3], '[1,2,3]')
        test((1,2,3), '(1,2,3)')
        test(List([1,2,3]), 'List([1,2,3])')
        class Foo(List): pass
        test(Foo([1,2,(3,List([4]))]), 'Foo([1,2,(3,List([4]))])')


class AstTest(TestCase):
    
    def test_ast(self):
        
        class Term(List): pass
        class Factor(List): pass
        class Expression(List): pass
            
        expr   = Delayed()
        number = Digit()[1:,...]                         >> int
        
        with Separator(Drop(Regexp(r'\s*'))):
            term    = number | '(' & expr & ')'          > Term
            muldiv  = Any('*/')
            factor  = term & (muldiv & term)[:]          > Factor
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]      > Expression
            line    = expr & Eos()
            
        ast = line.parse_string('1 + 2 * (3 + 4 - 5)')[0]
        text = str(ast)
        assert_str(text, """Expression
 +- Factor
 |   `- Term
 |       `- 1
 +- '+'
 `- Factor
     +- Term
     |   `- 2
     +- '*'
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   `- Term
         |   |       `- 3
         |   +- '+'
         |   +- Factor
         |   |   `- Term
         |   |       `- 4
         |   +- '-'
         |   `- Factor
         |       `- Term
         |           `- 5
         `- ')'""")

        