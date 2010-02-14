
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
Tests for the lepl.node module.
'''

#from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl import Delayed, Digit, Any, Node, make_error, throw, Or, Space, \
    AnyBut, Eos
from lepl.support.graph import preorder, postorder, order, \
    PREORDER, POSTORDER, LEAF


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, R0201, R0903
# (dude this is just a test)

    
def str26(value):
    '''
    Hack 2.6 string conversion
    '''
    string = str(value)
    return string.replace("u'", "'")


class NodeTest(TestCase):

    def test_node(self):
        #basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                      > 'number'
        term        = (number | '(' / expression / ')')    > Term
        muldiv      = Any('*/')                            > 'operator'
        factor      = (term / (muldiv / term)[0::])        > Factor
        addsub      = Any('+-')                            > 'operator'
        expression += (factor / (addsub / factor)[0::])    > Expression
        
        p = expression.string_parser()
        ast = p('1 + 2 * (3 + 4 - 5)')
        assert str26(ast[0]) == """Expression
 +- Factor
 |   +- Term
 |   |   `- number '1'
 |   `- ' '
 +- operator '+'
 +- ' '
 `- Factor
     +- Term
     |   `- number '2'
     +- ' '
     +- operator '*'
     +- ' '
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   +- Term
         |   |   |   `- number '3'
         |   |   `- ' '
         |   +- operator '+'
         |   +- ' '
         |   +- Factor
         |   |   +- Term
         |   |   |   `- number '4'
         |   |   `- ' '
         |   +- operator '-'
         |   +- ' '
         |   `- Factor
         |       `- Term
         |           `- number '5'
         `- ')'""", str26(ast[0])

class ListTest(TestCase):

    def test_list(self):
        #basicConfig(level=DEBUG)
        
        expression  = Delayed()
        number      = Digit()[1:,...]                   > 'number'
        term        = (number | '(' / expression / ')') > list
        muldiv      = Any('*/')                         > 'operator'
        factor      = (term / (muldiv / term)[0:])      > list
        addsub      = Any('+-')                         > 'operator'
        expression += (factor / (addsub / factor)[0:])  > list
        
        ast = expression.parse_string('1 + 2 * (3 + 4 - 5)')
        assert ast == [[[[('number', '1')], ' '], ('operator', '+'), ' ', [[('number', '2')], ' ', ('operator', '*'), ' ', ['(', [[[('number', '3')], ' '], ('operator', '+'), ' ', [[('number', '4')], ' '], ('operator', '-'), ' ', [[('number', '5')]]], ')']]]], ast


class ErrorTest(TestCase):

    def test_error(self):
        #basicConfig(level=INFO)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                                        > 'number'
        term        = Or(
            AnyBut(Space() | Digit() | '(')[1:,...]                          ^ 'unexpected text: {results[0]}', 
            number                                                           > Term,
            number ** make_error("no ( before '{stream_out}'") / ')'           >> throw,
            '(' / expression / ')'                                           > Term,
            ('(' / expression / Eos()) ** make_error("no ) for '{stream_in}'") >> throw)
        muldiv      = Any('*/')                                              > 'operator'
        factor      = (term / (muldiv / term)[0:,r'\s*'])                    >  Factor
        addsub      = Any('+-')                                              > 'operator'
        expression += (factor / (addsub / factor)[0:,r'\s*'])                >  Expression
        line        = expression / Eos()
       
        parser = line.string_parser()
        
        try:
            parser('1 + 2 * 3 + 4 - 5)')[0]
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "no ( before ')'", e.msg

        try:
            parser('1 + 2 * (3 + 4 - 5')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "no ) for '(3 + 4 - 5'", e.msg
            
        try:
            parser('1 + 2 * foo')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "unexpected text: foo", e.msg


class EqualityTest(TestCase):
    
    def test_object_eq(self):
        a = Node('a')
        b = Node('a')
        assert a != b
        assert b != a
        assert a is not b
        assert b is not a
        assert a == a
        assert b == b
        assert a is a
        assert b is b
        
    def test_recursive_eq(self):
        a = Node('a', Node('b'))
        b = Node('a', Node('b'))
        c = Node('a', Node('c'))
        assert a._recursively_eq(b)
        assert not a._recursively_eq(c)
        

class ChildrenTest(TestCase):
    
    def test_children(self):
        a = Node('a')
        for c in a:
            assert c == 'a', c


class OrderTest(TestCase):

    def tree(self):
        return Node('a', 
                 Node('b',
                   Node('c',
                     Node('d'),
                     Node('e')),
                   Node('f')), 
                 Node('g'), 
                 Node('h',
                   Node('i',
                     Node('j'),
                     Node('k')),
                   Node('l')))
    
    def order(self, tree, flags):
        return list(map(lambda x: x[0], order(tree, flags, Node, LEAF)))
    
    def test_orders(self):
        tree = self.tree()
        ordered = self.order(tree, PREORDER)
        assert ordered == ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'], ordered
        ordered = self.order(tree, POSTORDER)
        assert ordered == ['d', 'e', 'c', 'f', 'b', 'g', 'j', 'k', 'i', 'l', 'h', 'a'], ordered
        
        
    