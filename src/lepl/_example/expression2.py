#LICENCE

'''
Check grouping.
'''

from __future__ import with_statement
#from logging import basicConfig, DEBUG
from operator import neg, add, mul, sub, truediv
from functools import reduce

from lepl import *
from lepl._example.support import Example


class ExpressionExample(Example):

    def test_broken(self):
        '''
        This shows the original problem.
        '''
        #noinspection PyUnresolvedReferences
        class Op(List):
            def __float__(self):
                return self._op(float(self[0]), float(self[1]))
        class Add(Op): _op = add
        class Sub(Op): _op = sub
        class Mul(Op): _op = mul
        class Div(Op): _op = truediv
        value = Token(UnsignedReal())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = Optional(symbol('-')) + value >> float
        group2, group3 = Delayed(), Delayed()
        # first layer, most tightly grouped, is parens and numbers
        parens = ~symbol('(') & group3 & ~symbol(')')
        group1 = parens | number
        # second layer, next most tightly grouped, is multiplication
        mul_ = group1 & ~symbol('*') & group2 > Mul
        div_ = group1 & ~symbol('/') & group2 > Div
        group2 += mul_ | div_ | group1
        # third layer, least tightly grouped, is addition
        add_ = group2 & ~symbol('+') & group3 > Add
        sub_ = group2 & ~symbol('-') & group3 > Sub
        group3 += add_ | sub_ | group2

        group3.config.auto_memoize()

        self.examples([(lambda: group3.parse('4-3-2')[0],
"""Sub
 +- 4.0
 `- Sub
     +- 3.0
     `- 2.0""")])
        
    def test_flat(self):
        '''
        This from elsewhere in the examples.
        '''

        #basicConfig(level=INFO)

        class Term(List): pass
        class Factor(List): pass
        class Expression(List): pass

        expr   = Delayed()
        number = Digit()[1:,...]                        >> int

        with DroppedSpace():
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = Trace(expr) & Eof()

        parser = line.get_parse()

        self.examples([(lambda: parser('4-3-2')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- 4
 +- '-'
 +- Factor
 |   `- Term
 |       `- 3
 +- '-'
 `- Factor
     `- Term
         `- 2"""),
                       (lambda: parser('1+2*(3-4)+5/6+7')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- 1
 +- '+'
 +- Factor
 |   +- Term
 |   |   `- 2
 |   +- '*'
 |   `- Term
 |       +- '('
 |       +- Expression
 |       |   +- Factor
 |       |   |   `- Term
 |       |   |       `- 3
 |       |   +- '-'
 |       |   `- Factor
 |       |       `- Term
 |       |           `- 4
 |       `- ')'
 +- '+'
 +- Factor
 |   +- Term
 |   |   `- 5
 |   +- '/'
 |   `- Term
 |       `- 6
 +- '+'
 `- Factor
     `- Term
         `- 7""")])

    def test_repeat(self):
        '''
        Use the repeat approach above to fix the broken problem.
        '''
        class Op(List):
            def __float__(self):
                return None
        class Expr(Op): pass
        class Factor(Op): pass
        value = Token(UnsignedReal())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = Optional(symbol('-')) + value >> float
        group3 = Delayed()
        # first layer, most tightly grouped, is parens and numbers
        parens = ~symbol('(') & group3 & ~symbol(')')
        group1 = parens | number
        # second layer, next most tightly grouped, is multiplication
        group2 = group1[1:,Or(symbol('*'), symbol('/'))] > Factor
        # third layer, least tightly grouped, is addition
        group3 += group2[1:,Or(symbol('+'), symbol('-'))] > Expr

        self.examples([(lambda: group3.parse('4-3-2')[0],
"""Expr
 +- Factor
 |   `- 4.0
 +- '-'
 +- Factor
 |   `- 3.0
 +- '-'
 `- Factor
     `- 2.0""")])

    def test_repeat2(self):
        '''
        Expand the above to be more explicit with node classes.

        This fails when we have both + and - because there's no way to join
        those together.
        '''
        #basicConfig(level=DEBUG)
        class Op(List):
            def __float__(self):
                return self._op(float(self[0]), float(self[1]))
        class Add(Op): _op = add
        class Sub(Op): _op = sub
        class Mul(Op): _op = mul
        class Div(Op): _op = truediv
        with TraceVariables(False):
            value = Token(UnsignedReal())
            symbol = Token('[^0-9a-zA-Z \t\r\n]')
            number = Optional(symbol('-')) + value >> float
            group3 = Delayed()
            # first layer, most tightly grouped, is parens and numbers
            parens = ~symbol('(') & group3 & ~symbol(')')
            group1 = parens | number
            # second layer, next most tightly grouped, is multiplication
            mul_ = group1[1:,~symbol('*')] > Mul
            div_ = group1[2:,~symbol('/')] > Div
            group2 = mul_ | div_
            # third layer, least tightly grouped, is addition
            add_ = group2[1:,~symbol('+')] > Add
            sub_ = group2[2:,~symbol('-')] > Sub
            group3 += add_ | sub_

        line = group3 & Eos()

        self.examples([(lambda: line.parse('4-3-2')[0],
"""Sub
 +- Mul
 |   `- 4.0
 +- Mul
 |   `- 3.0
 `- Mul
     `- 2.0"""),
                       (lambda: line.parse('1+2-3-4+5+6+7-8-9-10-11'),
"""FullFirstMatchException: The match failed in <string> at '' (line 1, character 5).
""")])

    def test_repeat3(self):
        '''
        Fix the problem above by folding - and / into the value itself.
        '''
        #basicConfig(level=DEBUG)

        class Val(List):
            def __float__(self):
                return float(self._op(float(self[0])))
        class Neg(Val): _op = neg
        class Inv(Val): _op = lambda self, x: 1.0/x
        class Seq(List):
            def __float__(self):
                return float(reduce(self._op, map(float, self)))
        class Sum(Seq): _op = add
        class Prd(Seq): _op = mul

        with TraceVariables(False):

            value = Token(UnsignedReal())
            symbol = Token('[^0-9a-zA-Z \t\r\n]')
            number = Optional(symbol('-')) + value >> float

            sum = Delayed()

            # first layer, most tightly grouped, is parens and numbers
            parens = ~symbol('(') & sum & ~symbol(')')
            val = parens | number

            inv_ = ~symbol('/') & val > Inv
            eve = ~symbol('*') & val
            prd = val & (inv_ | eve)[0:] > Prd

            neg_ = ~symbol('-') & prd > Neg
            pos = ~symbol('+') & prd
            sum += prd & (neg_ | pos)[0:] > Sum

        line = sum & Eos()

        self.examples([
            (lambda: float(Neg([1])), -1.0),
            (lambda: float(Inv([2])), 0.5),
            (lambda: float(Sum([1,2])), 3.0),
            (lambda: float(Prd([2,3])), 6.0),
            (lambda: float(Sum([1,Neg([2])])), -1.0),
            (lambda: line.parse('4-3-2')[0],
"""Sum
 +- Prd
 |   `- 4.0
 +- Neg
 |   `- Prd
 |       `- 3.0
 `- Neg
     `- Prd
         `- 2.0"""),
            (lambda: float(line.parse('4-3-2')[0]), -1.0),
            (lambda: line.parse('1+2-3-4+5+6+7-8-9-10-11')[0],
"""Sum
 +- Prd
 |   `- 1.0
 +- Prd
 |   `- 2.0
 +- Neg
 |   `- Prd
 |       `- 3.0
 +- Neg
 |   `- Prd
 |       `- 4.0
 +- Prd
 |   `- 5.0
 +- Prd
 |   `- 6.0
 +- Prd
 |   `- 7.0
 +- Neg
 |   `- Prd
 |       `- 8.0
 +- Neg
 |   `- Prd
 |       `- 9.0
 +- Neg
 |   `- Prd
 |       `- 10.0
 `- Neg
     `- Prd
         `- 11.0"""),
            (lambda: float(line.parse('1+2-3-4+5+6+7-8-9-10-11')[0]), -24.0),
            (lambda: line.parse('1+2*(3-4)+5/10+7')[0],
"""Sum
 +- Prd
 |   `- 1.0
 +- Prd
 |   +- 2.0
 |   `- Sum
 |       +- Prd
 |       |   `- 3.0
 |       `- Neg
 |           `- Prd
 |               `- 4.0
 +- Prd
 |   +- 5.0
 |   `- Inv
 |       `- 10.0
 `- Prd
     `- 7.0"""),
            (lambda: float(line.parse('1+2*(3-4)+5/10+7')[0]), 6.5)
        ])
