
from math import sin, cos
from logging import basicConfig, DEBUG
from operator import add, sub, truediv, mul
from unittest import TestCase

from lepl import *


class RegexpCompilationTest(TestCase):
    '''
    Test whether embedded matchers are converted to regular expressions.
    '''
    
    def test_literal(self):
        token = Token(Literal('abc'))
        token.compile()
        assert token.regexp == 'abc', repr(token.regexp)
        
    def test_float(self):
        token = Token(Float())
        token.compile()
        assert token.regexp == '([\\+\\-]|)([0-9]([0-9])*(\\.|)|([0-9]([0-9])*|)\\.[0-9]([0-9])*)([Ee]([\\+\\-]|)[0-9]([0-9])*|)', repr(token.regexp)
        
    def test_impossible(self):
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
        reals = (Token(Float()) >> float)[:]
        parser = reals.null_parser(Configuration(rewriters=[lexer_rewriter()]))
        results = parser('1 2.3')
        assert results == [1.0, 2.3], results
    
    def test_string_arg(self):
        word = Token('[a-z]+')
        parser = (word[:]).null_parser(Configuration(rewriters=[lexer_rewriter()]))
        results = parser('abc defXghi')
        assert results == ['abc', 'def', 'ghi'], results
        
    def test_expression(self):
        
#        basicConfig(level=DEBUG)
        
        class Call(Node): pass
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
            
        value  = Token(Float())                         > 'value'
        name   = Token('[a-z]+')
        symbol = Token('[^a-zA-Z0-9\\. ]')
        
        expr    = Delayed()
        open    = ~symbol('(')
        close   = ~symbol(')')
        funcn   = name                                  > 'name'
        call    = funcn & open & expr & close           > Call
        term    = call | value | open & expr & close    > Term
        muldiv  = symbol(Any('*/'))                     > 'operator'
        factor  = term & (muldiv & term)[:]             > Factor
        addsub  = symbol(Any('+-'))                     > 'operator'
        expr   += factor & (addsub & factor)[:]         > Expression
        line    = expr & Eos()
        
        parser = line.string_parser(
                    Configuration(monitors=[TraceResults(True)],
                                  rewriters=[lexer_rewriter()]))
        results = parser('1 + 2*sin(3+ 4) - 5')
        assert str(results[0]) == """Expression
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
         `- value '5'""", '[' + str(results[0]) + ']'
        

    def test_expression2(self):
        
#        basicConfig(level=DEBUG)
        
        # we could do evaluation directly in the parser actions. but by
        # using the nodes instead we allow future expansion into a full
        # interpreter
        
        class BinaryExpression(Node):
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
        
        float_  = Or(number                             >> float,
                     ~symbol('-') & number              >> (lambda x: -float(x)))
        
        open    = ~symbol('(')
        close   = ~symbol(')')
        trig    = name(Or('sin', 'cos'))
        call    = trig & open & expr & close            > Call
        parens  = open & expr & close
        value   = parens | call | float_
        
        ratio   = value & ~symbol('/') & factor         > Ratio
        prod    = value & ~symbol('*') & factor         > Product
        factor += prod | ratio | value
        
        diff    = factor & ~symbol('-') & expr          > Difference
        sum     = factor & ~symbol('+') & expr          > Sum
        expr   += sum | diff | factor | value
        
        line    = expr & Eos()
        parser  = line.null_parser(Configuration.tokens())
        
        def myeval(text):
            return float(parser(text)[0])
        
        self.assertAlmostEqual(myeval('1'), 1)
        self.assertAlmostEqual(myeval('1 + 2*3'), 7)
        self.assertAlmostEqual(myeval('1 - 4 / (3 - 1)'), -1)
        self.assertAlmostEqual(myeval('1 -4 / (3 -1)'), -1)
        self.assertAlmostEqual(myeval('1 + 2*sin(3+ 4) - 5'), -2.68602680256)


class ErrorTest(TestCase):

    def test_no_rewriter(self):
        t = Token(Any())
        p = t.null_parser()
        try:
            p('hello world')
            assert False, 'expected failure'
        except LexerError as e:
            assert str(e) == 'A Token has not been compiled. You must use the ' \
                            'lexer_rewriter with Tokens. This can be done by ' \
                            'using Configuration.tokens().', str(e)
        else:
            assert False, 'wrong exception'

    def test_mixed(self):
        t = Token(Any()) & Any()
        try:
            p = t.null_parser(Configuration.tokens())
            assert False, 'expected failure'
        except LexerError as e:
            assert str(e) == 'The grammar contains a mix of Tokens and ' \
                            'non-Token matchers at the top level. If Tokens ' \
                            'are used then non-token matchers that consume ' \
                            'input must only appear "inside" Tokens.  The ' \
                            'non-Token matchers include: Any.', str(e)
        else:
            assert False, 'wrong exception'

    def test_bad_space(self):
        t = Token('a')
        p = t.null_parser(Configuration(rewriters=[lexer_rewriter(
                    UnicodeAlphabet.instance(), 'b')]))
        assert p('a') == ['a'], p('a')
        assert p('b') == None, p('b')
        try:
            p('c')
            assert False, 'expected failure'
        except RuntimeLexerError as e:
            assert str(e) == 'Cannot lex "<unknown> - use stream for better error reporting" at -1/-1', str(e)

    def test_incomplete(self):
        try:
            t = Token('[a-z]+')(Any())
            p = t.string_parser(Configuration.tokens())
            assert p('a') == ['a'], p('a')
            # even though this matches the token, the Any() sub-matcher doesn't
            # consume all the contents
            assert p('ab') == None, p('ab')
            t = Token('[a-z]+')(Any(), complete=False)
            p = t.string_parser(Configuration.tokens())
            assert p('a') == ['a'], p('a')
            # whereas this is fine, since complete=False
            assert p('ab') == ['a'], p('ab')
        except Exception as e:
            assert False, str(e)
            