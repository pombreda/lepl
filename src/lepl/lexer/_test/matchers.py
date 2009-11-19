
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
Wide range of tests for lexer.
'''

# pylint: disable-msg=R0201, R0904, R0903, R0914
# tests

#from logging import basicConfig, DEBUG
from math import sin, cos
from operator import add, sub, truediv, mul
from unittest import TestCase

from lepl import Token, Literal, Float, LexerError, Configuration, \
    lexer_rewriter, Node, Delayed, Any, Eos, TraceResults, UnsignedFloat, \
    Or, UnicodeAlphabet, RuntimeLexerError
from lepl.support import str


def str26(value):
    '''
    Convert to string with crude hack for 2.6 Unicode
    '''
    string = str(value)
    return string.replace("u'", "'")


class RegexpCompilationTest(TestCase):
    '''
    Test whether embedded matchers are converted to regular expressions.
    '''
    
    def test_literal(self):
        '''
        Simple literal should compile directly.
        '''
        token = Token(Literal('abc'))
        token.compile()
        assert token.regexp == 'abc', repr(token.regexp)
        
    def test_float(self):
        '''
        A float is more complex, but still compiles.
        '''
        token = Token(Float())
        token.compile()
        assert token.regexp == \
            '([\\+\\-]|)(([0-9]([0-9])*|)\\.[0-9]([0-9])*|' \
            '[0-9]([0-9])*(\\.|))([Ee]([\\+\\-]|)[0-9]([0-9])*|)', \
            repr(token.regexp)
        
    def test_impossible(self):
        '''
        Cannot compile arbitrary functions.
        '''
        try:
            token = Token(Float() > (lambda x: x))
            token.compile()
            assert False, 'Expected error'
        except LexerError:
            pass


class TokenRewriteTest(TestCase):
    '''
    Test token support.
    '''
    
    def test_defaults(self):
        '''
        Basic configuration.
        '''
        reals = (Token(Float()) >> float)[:]
        parser = reals.null_parser(Configuration(rewriters=[lexer_rewriter()]))
        results = parser('1 2.3')
        assert results == [1.0, 2.3], results
    
    def test_string_arg(self):
        '''
        Skip anything(not just spaces)
        '''
        word = Token('[a-z]+')
        parser = (word[:]).null_parser(
                        Configuration(rewriters=[lexer_rewriter(discard='.')]))
        results = parser('abc defXghi')
        assert results == ['abc', 'def', 'ghi'], results
        
    def test_bad_error_msg(self):
        '''
        An ugly error message (can't we improve this?)
        '''
        #basicConfig(level=DEBUG)
        word = Token('[a-z]+')
        parser = (word[:]).null_parser(
                        Configuration(rewriters=[lexer_rewriter()]))
        try:
            parser('abc defXghi')
            assert False, 'expected error'
        except RuntimeLexerError as err:
            assert str(err) == 'No lexer for \'Xghi\'.', str(err)
        
    def test_good_error_msg(self):
        '''
        Better error message with streams.
        '''
        #basicConfig(level=DEBUG)
        word = Token('[a-z]+')
        parser = (word[:]).string_parser(
                        Configuration(rewriters=[lexer_rewriter()]))
        try:
            parser('abc defXghi')
            assert False, 'expected error'
        except RuntimeLexerError as err:
            assert str(err) == 'No lexer for \'Xghi\' at line 1 character 7 ' \
                'of str: \'abc defXghi\'.', str(err)
        
    def test_expr_with_functions(self):
        '''
        Expression with function calls and appropriate binding.
        '''
        
        #basicConfig(level=DEBUG)
        
        # pylint: disable-msg=C0111, C0321
        class Call(Node): pass
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
            
        value  = Token(Float())                         > 'value'
        name   = Token('[a-z]+')
        symbol = Token('[^a-zA-Z0-9\\. ]')
        
        expr    = Delayed()
        open_   = ~symbol('(')
        close   = ~symbol(')')
        funcn   = name                                  > 'name'
        call    = funcn & open_ & expr & close          > Call
        term    = call | value | open_ & expr & close   > Term
        muldiv  = symbol(Any('*/'))                     > 'operator'
        factor  = term & (muldiv & term)[:]             > Factor
        addsub  = symbol(Any('+-'))                     > 'operator'
        expr   += factor & (addsub & factor)[:]         > Expression
        line    = expr & Eos()
        
        parser = line.string_parser(
                    Configuration(monitors=[TraceResults(True)],
                                  rewriters=[lexer_rewriter()]))
        results = str26(parser('1 + 2*sin(3+ 4) - 5')[0])
        assert results == """Expression
 +- Factor
 |   `- Term
 |       `- value '1'
 +- operator '+'
 +- Factor
 |   +- Term
 |   |   `- value '2'
 |   +- operator '*'
 |   `- Term
 |       `- Call
 |           +- name 'sin'
 |           `- Expression
 |               +- Factor
 |               |   `- Term
 |               |       `- value '3'
 |               +- operator '+'
 |               `- Factor
 |                   `- Term
 |                       `- value '4'
 +- operator '-'
 `- Factor
     `- Term
         `- value '5'""", '[' + results + ']'
        

    def test_expression2(self):
        '''
        As before, but with evaluation.
        '''
        
        #basicConfig(level=DEBUG)
        
        # we could do evaluation directly in the parser actions. but by
        # using the nodes instead we allow future expansion into a full
        # interpreter
        
        # pylint: disable-msg=C0111, C0321
        class BinaryExpression(Node):
            op = lambda x, y: None
            def __float__(self):
                return self.op(float(self[0]), float(self[1]))
        
        class Sum(BinaryExpression): op = add
        class Difference(BinaryExpression): op = sub
        class Product(BinaryExpression): op = mul
        class Ratio(BinaryExpression): op = truediv
        
        class Call(Node):
            funs = {'sin': sin,
                    'cos': cos}
            def __float__(self):
                return self.funs[self[0]](self[1])
            
        # we use unsigned float then handle negative values explicitly;
        # this lets us handle the ambiguity between subtraction and
        # negation which requires context (not available to the the lexer)
        # to resolve correctly.
        number  = Token(UnsignedFloat())
        name    = Token('[a-z]+')
        symbol  = Token('[^a-zA-Z0-9\\. ]')
        
        expr    = Delayed()
        factor  = Delayed()
        
        float_  = Or(number                            >> float,
                     ~symbol('-') & number             >> (lambda x: -float(x)))
        
        open_   = ~symbol('(')
        close   = ~symbol(')')
        trig    = name(Or('sin', 'cos'))
        call    = trig & open_ & expr & close          > Call
        parens  = open_ & expr & close
        value   = parens | call | float_
        
        ratio   = value & ~symbol('/') & factor        > Ratio
        prod    = value & ~symbol('*') & factor        > Product
        factor += prod | ratio | value
        
        diff    = factor & ~symbol('-') & expr         > Difference
        sum_    = factor & ~symbol('+') & expr         > Sum
        expr   += sum_ | diff | factor | value
        
        line    = expr & Eos()
        parser  = line.null_parser()
        
        def myeval(text):
            return float(parser(text)[0])
        
        self.assertAlmostEqual(myeval('1'), 1)
        self.assertAlmostEqual(myeval('1 + 2*3'), 7)
        self.assertAlmostEqual(myeval('1 - 4 / (3 - 1)'), -1)
        self.assertAlmostEqual(myeval('1 -4 / (3 -1)'), -1)
        self.assertAlmostEqual(myeval('1 + 2*sin(3+ 4) - 5'), -2.68602680256)


class ErrorTest(TestCase):
    '''
    Test various error messages.
    '''

    def test_mixed(self):
        '''
        Cannot mix tokens and non-tokens at same level.
        '''
        bad = Token(Any()) & Any()
        try:
            bad.null_parser()
            assert False, 'expected failure'
        except LexerError as err:
            assert str(err) == 'The grammar contains a mix of Tokens and ' \
                               'non-Token matchers at the top level. If ' \
                               'Tokens are used then non-token matchers ' \
                               'that consume input must only appear "inside" ' \
                               'Tokens.  The non-Token matchers include: ' \
                               'Any.', str(err)
        else:
            assert False, 'wrong exception'

    def test_bad_space(self):
        '''
        An unexpected character fails to match.
        '''
        token = Token('a')
        parser = token.null_parser(Configuration(rewriters=[lexer_rewriter(
                                        UnicodeAlphabet.instance(), 
                                        discard='b')]))
        assert parser('a') == ['a'], parser('a')
        assert parser('b') == None, parser('b')
        try:
            parser('c')
            assert False, 'expected failure'
        except RuntimeLexerError as err:
            assert str(err) == 'No lexer for \'c\'.', str(err)

    def test_incomplete(self):
        '''
        A token is not completely consumed (this doesn't raise error messages,
        it just fails to match).
        '''
        token = Token('[a-z]+')(Any())
        parser = token.string_parser()
        assert parser('a') == ['a'], parser('a')
        # even though this matches the token, the Any() sub-matcher doesn't
        # consume all the contents
        assert parser('ab') == None, parser('ab')
        token = Token('[a-z]+')(Any(), complete=False)
        parser = token.string_parser()
        assert parser('a') == ['a'], parser('a')
        # whereas this is fine, since complete=False
        assert parser('ab') == ['a'], parser('ab')
    
    def test_none_discard(self):
        '''
        If discard is None, discard nothing.
        '''
        token = Token('a')
        parser = token[1:].null_parser(Configuration(
                            rewriters=[lexer_rewriter(discard=None)]))
        result = parser('aa')
        assert result == ['a', 'a'], result
        try:
            parser(' a')
        except RuntimeLexerError as error:
            assert str26(error) == "No discard for ' a'.", str26(error)
            