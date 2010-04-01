
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0903
# (the code style is for documentation, not "real")
#@PydevCodeAnalysisIgnore

'''
Examples from the documentation.
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
        
        self.examples([(lambda: parser('1 + 2 * (3 + 4 - 5)')[0],
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
        
