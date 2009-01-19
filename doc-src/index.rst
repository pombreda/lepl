
LEPL - A Parser Library for Python
==================================

Using LEPL you can describe how text is structured and then generate Python
data (lists, dicts, and even trees of objects) with the text in that form.  It
is intended to be simple and easy to use, but also has some features that may
interest advanced users, including full backtracking.

::

  >>> from lepl.match import *
  >>> from lepl.node import Node

  >>> class Term(Node): 
  ...   pass
  >>> class Factor(Node):
  ...   pass
  >>> class Expression(Node): 
  ...   pass

  >>> expression  = Delayed()
  >>> number      = Digit()[1:,...]                   >= 'number'
  >>> term        = (number | '(' / expression / ')') >= Term
  >>> muldiv      = Any('*/')                         >= 'operator'
  >>> factor      = (term / (muldiv / term)[0:])      >= Factor
  >>> addsub      = Any('+-')                         >= 'operator'
  >>> expression += (factor / (addsub / factor)[0:])  >= Expression

  >>> ast = expression.parse_string('1 + 2 * (3 + 4 - 5)')[0]
  >>> print(ast)
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
  >>> print(ast.Factor[0])
  Factor
   +- Term
   |   `- number ['1']
   `- ' '

LEPL's *weakest* point is probably performance.  It is intended more for
exploratory and one--off jobs than, for example, a compiler front--end; it
values your time, as a programmer, over CPU time (or, less favourably, the
time of the end--user).

The `API documentation <../api/index.html>`_ is also available.

Contents
--------

.. toctree::
   :maxdepth: 2

   intro
   matchers
   operators
   nodes
   resources
   debugging
   credits

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

