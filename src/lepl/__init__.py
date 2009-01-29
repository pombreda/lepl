
'''
LEPL is a parser library written in Python.
  
This is the API documentation; the module index is at the bottom of this page.  
There is also a `manual <../index.html>`_ which gives a higher level
overview. 

The home page for this package is the 
`LEPL website <http://www.acooke.org/lepl>`_.


Example
-------

A simple example of how to use LEPL::

    from lepl import *
    
    # For a simpler result these could be replaced with 'list', giving
    # an AST as a set of nested lists 
    # (ie replace '> Term' etc with '> list' below).
    
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
        
    def parse_expression(text):
        
        # Here we define the grammar
        
        # A delayed value is defined later (see last line in block) 
        expr   = Delayed()
        number = Digit()[1:,...]                        > 'number'
        spaces = DropEmpty(Regexp(r'\s*'))
        # Allow spaces between items
        with Separator(spaces):
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')                         > 'operator'
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')                         > 'operator'
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = Trace(expr) & Eos()
    
        # parse_string returns a list of tokens, but expr 
        # returns a single value, so take the first entry
        return expression.parse_string(text)[0]
    
    if __name__ == '__main__':
        print(parse_expression('1 + 2 * (3 + 4 - 5)'))

Running this gives the result::

    Expression
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
             `- ')'


Generating Documentation
------------------------

To regenerate this documentation, run::

  rm -fr doc/api
  epydoc -v -o doc/api --html --graph-all --docformat=restructuredtext --exclude="_test" --exclude="_example" src/*

'''
 
from lepl.custom import *
from lepl.match import *
from lepl.node import *
from lepl.stream import *

__all__ = [
        # custom
        'Override',
        # match
        'Empty',
        'Repeat',
        'And',
        'Or',
        'First',
        'Any',
        'Literal',
        'Empty',
        'Lookahead',
        'Apply',
        'KApply',
        'Regexp', 
        'Delayed', 
        'Commit', 
        'Trace', 
        'AnyBut', 
        'Optional', 
        'Star', 
        'ZeroOrMore', 
        'Plus', 
        'OneOrMore', 
        'Map', 
        'Add', 
        'Drop',
        'Substitute', 
        'Name', 
        'Eof', 
        'Eos', 
        'Identity', 
        'Newline', 
        'Space', 
        'Whitespace', 
        'Digit', 
        'Letter', 
        'Upper', 
        'Lower', 
        'Printable', 
        'Punctuation', 
        'UnsignedInteger', 
        'SignedInteger', 
        'Integer', 
        'UnsignedFloat', 
        'SignedFloat', 
        'SignedEFloat', 
        'Float', 
        'Word',
        'Separator',
        'DropEmpty',
        'GREEDY',
        'NON_GREEDY',
        'DEPTH_FIRST',
        'BREADTH_FIRST',
        # node
        'Node',
        'make_dict',
        'join_with',
        'make_error',
        'raise_error',
        'Error',
        'throw',
        # stream
        'Stream']

__version__ = '1.0b1'
