
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
An example from the manual based on a test in this package (currently not used
in docs because something similar is developed in the tutorial).
'''

from math import sin, cos
from operator import add, sub, truediv, mul

from lepl import Node, Token, UnsignedFloat, Delayed, Or, Eos
from lepl._example.support import Example


class Calculator(Example):
    '''
    Show how tokens can help simplify parsing of an expression; also
    give a simple interpreter.
    '''
    
    def test_calculation(self):
        '''
        We could do evaluation directly in the parser actions. but by
        using the nodes instead we allow future expansion into a full
        interpreter.
        '''
        
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
        
        float_  = Or(number                       >> float,
                     ~symbol('-') & number        >> (lambda x: -float(x)))
        
        open_   = ~symbol('(')
        close   = ~symbol(')')
        trig    = name(Or('sin', 'cos'))
        call    = trig & open_ & expr & close     > Call
        parens  = open_ & expr & close
        value   = parens | call | float_
        
        ratio   = value & ~symbol('/') & factor   > Ratio
        prod    = value & ~symbol('*') & factor   > Product
        factor += prod | ratio | value
        
        diff    = factor & ~symbol('-') & expr    > Difference
        sum_    = factor & ~symbol('+') & expr    > Sum
        expr   += sum_ | diff | factor | value
        
        line    = expr & Eos()
        parser  = line.null_parser()
        
        def calculate(text):
            return float(parser(text)[0])
        
        self.examples([(lambda: calculate('1'), '1.0'),
                       (lambda: calculate('1 + 2*3'), '7.0'),
                       (lambda: calculate('-1 - 4 / (3 - 1)'), '-3.0'),
                       (lambda: calculate('1 -4 / (3 -1)'), '-1.0'),
                       (lambda: calculate('1 + 2*sin(3+ 4) - 5'), 
                        '-2.68602680256')])
