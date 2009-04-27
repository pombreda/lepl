
from logging import basicConfig, DEBUG
from math import sin, cos
from operator import add, sub, mul, truediv

from lepl import *


def lexer():
    
#    basicConfig(level=DEBUG)
        
    class BinaryExpression(Node):
        def __float__(self):
            return self.op(float(self._children[0]), 
                           float(self._children[1]))
    
    class Sum(BinaryExpression): op = add
    class Difference(BinaryExpression): op = sub
    class Product(BinaryExpression): op = mul
    class Ratio(BinaryExpression): op = truediv
    
    class Call(Node):
        funs = {'sin': sin,
                'cos': cos}
        def __float__(self):
            return self.funs[self._children[0]](self._children[1])
        
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
    
    # omitting symbol around "/" didn't give an error below.
    ratio   = value & ~symbol('/') & factor         > Ratio
    prod    = value & ~symbol('*') & factor         > Product
    factor += prod | ratio | value
    
    diff    = factor & ~symbol('-') & expr          > Difference
    sum     = factor & ~symbol('+') & expr          > Sum
    expr   += sum | diff | factor | value
    
    line    = expr & Eos()
    parser  = line.null_parser(Configuration.tokens())
    
    def myeval(text):
        result = parser(text)[0]
        return float(result)
    
    for i in range(1,1001):
        print('.', end='')
        p = i % 100 == 0
        if p: print
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
    profile()
#    lexer()

    
    