
'''
LEPL is a parser library written in Python.
  
This is the API documentation; the module index is at the bottom of this page.  
There is also a `manual <../manual/index.html>`_ which explains how to use the 
library in more detail.

The source and documentation can be downloaded from the `LEPL website
<http://www.acooke.org/lepl>`_.

**Note** - LEPL is written in Python 3, which is not yet fully supported by
the tool that generates this documentation.  A s a result, some small, 
auto-generated details may contain slight errors (for example, constructor
chaining is reported as overriding).

Example
-------

A simple example of how to use LEPL::

    from lepl.match import *
    from lepl.node import Node
    
    # For a simpler result these could be replaced with 'list', giving
    # an AST as a set of nested lists 
    # (ie replace '> Term' etc with '> list' below).
    
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
    
    def parse_expression(text):
        
        # Here we define the grammar
        
        # A delayed value is defined later (see last line in block) 
        expression  = Delayed()
        number      = Digit()[1:,...]                   > 'number'
        term        = (number | '(' / expression / ')') > Term
        muldiv      = Any('*/')                         > 'operator'
        factor      = (term / (muldiv / term)[0:])      > Factor
        addsub      = Any('+-')                         > 'operator'
        expression += (factor / (addsub / factor)[0:])  > Expression
        
        # parse_string returns a list of tokens, but expression 
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
 