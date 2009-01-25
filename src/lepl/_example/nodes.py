
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
            return [(name, getattr(ast, name)) for name in ast.child_names()]
        
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
         `- ')'"""),
                    (example2, 
"[Factor(...), '', ('operator', '+'), ' ', Factor(...)]"),
                    (example2b, 
"[Factor(...), '', ('operator', '+'), ' ', Factor(...)]"),
                    (example3, 
"[('operator', ['+']), ('Factor', [Factor(...), Factor(...)])]"),
                    (example4, '2')])
