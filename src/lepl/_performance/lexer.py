
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
Performance related tests.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401
# pylint: disable-msg=E1101

from __future__ import print_function
from math import sin, cos
from operator import add, sub, mul, truediv

from lepl import *


def lexer():
    
    #basicConfig(level=DEBUG)
        
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
    
    open_   = ~symbol('(')
    close   = ~symbol(')')
    trig    = name(Or('sin', 'cos'))
    call    = trig & open_ & expr & close           > Call
    parens  = open_ & expr & close
    value   = parens | call | float_
    
    # omitting symbol around "/" didn't give an error below.
    ratio   = value & ~symbol('/') & factor         > Ratio
    prod    = value & ~symbol('*') & factor         > Product
    factor += prod | ratio | value
    
    diff    = factor & ~symbol('-') & expr          > Difference
    sum_    = factor & ~symbol('+') & expr          > Sum
    expr   += sum_ | diff | factor | value
    
    line    = expr & Eos()
    parser  = line.null_parser(Configuration.tokens())
    
    def myeval(text):
        result = parser(text)[0]
        return float(result)
    
    for i in range(1,1001):
        print('.', end='')
        p = i % 100 == 0
        if p: print()
        x = myeval('1')
        if p: print(x)
        x = myeval('1 + 2*3')
        if p: print(x)
        x = myeval('1 - 4 / (3 - 1)')
        if p: print(x)
        x = myeval('1 -4 / (3 -1)')
        if p: print(x)
        x = myeval('1 + 2*sin(3+ 4) - 5')
        if p: print(x)


def time():
    from timeit import Timer
    t = Timer("lexer()", "from __main__ import lexer")
    print(t.timeit(number=1))
    # 15.1772289276
    # 12.5665969849 with flatten, compose
    # 7.47127509117 without Trace() matcher
    # 7.02462887764 without trace monitor 
    # 6.95 with RMemo
    # rewrote to only compile once(!) and then run 1000 times
    # 243 without memo
    # 0.77 with RMemo
    # 0.69 with LMemo
    # 0.77 with auto_memoize
    

def profile():
    '''
import pstats
p=pstats.Stats('lexer.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('lexer()', 'lexer.prof')

if __name__ == '__main__':
#    time()
#    profile()
    lexer()

    
    