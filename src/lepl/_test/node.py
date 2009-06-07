
from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl import *


class NodeTest(TestCase):

    def test_node(self):
        basicConfig(level=DEBUG)
        
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
        assert str(ast[0]) == """Expression
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
         `- ')'""", ast[0]

class ListTest(TestCase):

    def test_list(self):
        basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

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
        basicConfig(level=INFO)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                                        > 'number'
        term        = Or(
            AnyBut(Space() | Digit() | '(')[1:,...]                          ^ 'unexpected text: {results[0]}', 
            number                                                           > Term,
            number ** make_error('no ( before {stream_out}') / ')'           >> throw,
            '(' / expression / ')'                                           > Term,
            ('(' / expression / Eos()) ** make_error('no ) for {stream_in}') >> throw)
        muldiv      = Any('*/')                                              > 'operator'
        factor      = (term / (muldiv / term)[0:,r'\s*'])                    >  Factor
        addsub      = Any('+-')                                              > 'operator'
        expression += (factor / (addsub / factor)[0:,r'\s*'])                >  Expression
        line        = expression / Eos()
       
        parser = line.string_parser()
        ast = parser('1 + 2 * (3 + 4 - 5)')
        
        try:
            ast = parser('1 + 2 * 3 + 4 - 5)')[0]
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "no ( before ')'", e.msg

        try:
            ast = parser('1 + 2 * (3 + 4 - 5')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "no ) for '(3 + 4...'", e.msg
            
        try:
            ast = parser('1 + 2 * foo')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "unexpected text: foo", e.msg
                     