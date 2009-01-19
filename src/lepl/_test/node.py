

from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl.match import *
from lepl.node import Node, raise_error


class NodeTest(TestCase):

    def test_node(self):
        basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                   > 'number'
        term        = (number | '(' / expression / ')') > Term
        muldiv      = Any('*/')                         > 'operator'
        factor      = (term / (muldiv / term)[0:])      > Factor
        addsub      = Any('+-')                         > 'operator'
        expression += (factor / (addsub / factor)[0:])  > Expression
        
        ast = expression.parse_string('1 + 2 * (3 + 4 - 5)')
        print(ast[0])
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
        print(ast)
        assert ast == [[[[('number', '1')], ' '], ('operator', '+'), ' ', [[('number', '2')], ' ', ('operator', '*'), ' ', ['(', [[[('number', '3')], ' '], ('operator', '+'), ' ', [[('number', '4')], ' '], ('operator', '-'), ' ', [[('number', '5')]]], ')']]]], ast


class ErrorTest(TestCase):

    def test_error(self):
        basicConfig(level=INFO)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                          > 'number'
        term        = (number | '(' / expression / ')' | AnyBut(Whitespace() | Digit())[1:,...] ^ 'unexpected text: {results[0]}' | Error('no ( at {stream_in}')) > Term
        muldiv      = Any('*/')                                > 'operator'
        factor      = (term / (muldiv / term)[0:])             > Factor
        addsub      = Any('+-')                                > 'operator'
        expression += (factor / (addsub / factor)[0:]) / Eos() > Expression
        
        try:
            ast = Trace(expression).parse_string('1 + 2 * 3 + 4 - 5)')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "no ( at '3 + 4 '...", e.msg
        try:
            ast = expression.parse_string('1 + 2 * foo')
            assert False, 'expected error'
        except SyntaxError as e:
            assert e.msg == "unexpected text: foo", e.msg
            
