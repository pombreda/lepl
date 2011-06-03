#LICENCE

'''
Check grouping.
'''

from __future__ import with_statement
#from logging import basicConfig, INFO

from lepl import *
from lepl._example.support import Example


class ExpressionExample(Example):

    def test_expression(self):

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
            line    = Trace(expr) & Eos()

        parser = line.get_parse()

        self.examples([(lambda: parser('4-3-2')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- 1
 +- '+'
 `- Factor
     +- Term
     |   `- 2
     +- '*'
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   `- Term
         |   |       `- 3
         |   +- '+'
         |   +- Factor
         |   |   `- Term
         |   |       `- 4
         |   +- '-'
         |   `- Factor
         |       `- Term
         |           `- 5
         `- ')'"""),
                       (lambda: parser('12+ 23*45 + 34')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- 12
 +- '+'
 +- Factor
 |   +- Term
 |   |   `- 23
 |   +- '*'
 |   `- Term
 |       `- 45
 +- '+'
 `- Factor
     `- Term
         `- 34""")])

