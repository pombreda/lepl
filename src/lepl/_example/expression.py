
from __future__ import with_statement
from logging import basicConfig, DEBUG, INFO
from lepl import *
from lepl._example.support import Example


class ExpressionExample(Example):
    
    def test_expression(self):
        
        basicConfig(level=INFO)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
            
        expr   = Delayed()
        number = Digit()[1:,...]                        > 'number'
        spaces = DropEmpty(Regexp(r'\s*'))
        
        with Separator(spaces):
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')                         > 'operator'
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')                         > 'operator'
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = Trace(expr) & Eos()
        
        parser = line.parse_string
        
        self.examples([(lambda: parser('1 + 2 * (3 + 4 - 5)')[0],
"""Expression
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
         `- ')'"""),
                       (lambda: parser('12+ 23*45 + 34')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- number '12'
 +- operator '+'
 +- ' '
 +- Factor
 |   +- Term
 |   |   `- number '23'
 |   +- operator '*'
 |   `- Term
 |       `- number '45'
 +- ' '
 +- operator '+'
 +- ' '
 `- Factor
     `- Term
         `- number '34'""")])
        
