
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0903,R0914
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

from lepl import *
from lepl._example.support import Example


class NodeExample(Example):
    
    def test_flat(self):
        
        expr   = Delayed()
        number = Digit()[1:,...]
        
        with Separator(r'\s*'):
            term    = number | '(' & expr & ')'
            muldiv  = Any('*/')
            factor  = term & (muldiv & term)[:]
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]
            line    = expr & Eos()

        def example1():
            return line.parse_string('1 + 2 * (3 + 4 - 5)')
        
        self.examples([(example1,
"['1', ' ', '', '+', ' ', '2', ' ', '*', ' ', '(', '', '3', ' ', '', '+', ' ', '4', ' ', '', '-', ' ', '5', '', '', ')', '']")
            ])
        
    def test_drop_empty(self):
        
        expr   = Delayed()
        number = Digit()[1:,...]
        
        with Separator(DropEmpty(Regexp(r'\s*'))):
            term    = number | '(' & expr & ')'
            muldiv  = Any('*/')
            factor  = term & (muldiv & term)[:]
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]
            line    = expr & Eos()

        def example1():
            return line.parse_string('1 + 2 * (3 + 4 - 5)')
        
        self.examples([(example1,
"['1', ' ', '+', ' ', '2', ' ', '*', ' ', '(', '3', ' ', '+', ' ', '4', ' ', '-', ' ', '5', ')']")
            ])
        

class ListExample(Example):
    
    def test_nested(self):
        
        expr   = Delayed()
        number = Digit()[1:,...]
        
        with Separator(Drop(Regexp(r'\s*'))):
            term    = number | (Drop('(') & expr & Drop(')') > list)
            muldiv  = Any('*/')
            factor  = (term & (muldiv & term)[:])
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]
            line    = expr & Eos()
            
        def example1():
            return line.parse_string('1 + 2 * (3 + 4 - 5)')
        
        self.examples([(example1,
"['1', '+', '2', '*', ['3', '+', '4', '-', '5']]")
            ])
        

# pylint: disable-msg=W0612
class TreeExample(Example):

    def test_ast(self):
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
            
        expr   = Delayed()
        number = Digit()[1:,...]                        > 'number'
        
        with Separator(r'\s*'):
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')                         > 'operator'
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')                         > 'operator'
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = expr & Eos()
            
        ast = line.parse_string('1 + 2 * (3 + 4 - 5)')[0]
        
        def example1():
            return ast
        
        def example2():
            return [child for child in ast]
                
        def example2b():
            return [ast[i] for i in range(len(ast))]
                
        def example3():
            return [(name, getattr(ast, name)) for name in dir(ast)]
        
        def example4():
            return ast.Factor[1].Term[0].number[0]
                

        self.examples([(example1,
"""Expression
 +- Factor
 |   +- Term
 |   |   `- number '1'
 |   `- ' '
 +- ''
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
         +- ''
         +- Expression
         |   +- Factor
         |   |   +- Term
         |   |   |   `- number '3'
         |   |   `- ' '
         |   +- ''
         |   +- operator '+'
         |   +- ' '
         |   +- Factor
         |   |   +- Term
         |   |   |   `- number '4'
         |   |   `- ' '
         |   +- ''
         |   +- operator '-'
         |   +- ' '
         |   `- Factor
         |       +- Term
         |       |   `- number '5'
         |       `- ''
         +- ''
         `- ')'""")#,
#                    (example2, 
#"[Factor(...), '', ('operator', '+'), ' ', Factor(...)]"),
#                    (example2b, 
#"[Factor(...), '', ('operator', '+'), ' ', Factor(...)]"),
#                    (example3, 
#"[('Factor', [Factor(...), Factor(...)]), ('operator', ['+'])]"),
#                    (example4, '2')
                    ])
