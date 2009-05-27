
from math import sin, cos
from logging import basicConfig, DEBUG
from operator import add, sub, truediv, mul
from unittest import TestCase

from lepl import *
from lepl._example.support import Example


class Calculator(Example):
    '''
    Show how tokens can help simplify parsing of an expression; also
    give a simple interpreter.
    '''
    
    def test_calculation(self):
        
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
        
        float_  = Or(number                       >> float,
                     ~symbol('-') & number        >> (lambda x: -float(x)))
        
        open    = ~symbol('(')
        close   = ~symbol(')')
        trig    = name(Or('sin', 'cos'))
        call    = trig & open & expr & close      > Call
        parens  = open & expr & close
        value   = parens | call | float_
        
        ratio   = value & ~symbol('/') & factor   > Ratio
        prod    = value & ~symbol('*') & factor   > Product
        factor += prod | ratio | value
        
        diff    = factor & ~symbol('-') & expr    > Difference
        sum     = factor & ~symbol('+') & expr    > Sum
        expr   += sum | diff | factor | value
        
        line    = expr & Eos()
        parser  = line.null_parser(Configuration.tokens())
        
        def calculate(text):
            return float(parser(text)[0])
        
        self.examples([(lambda: calculate('1'), '1.0'),
                       (lambda: calculate('1 + 2*3'), '7.0'),
                       (lambda: calculate('-1 - 4 / (3 - 1)'), '-3.0'),
                       (lambda: calculate('1 -4 / (3 -1)'), '-1.0'),
                       (lambda: calculate('1 + 2*sin(3+ 4) - 5'), '-2.68602680256')])
