
LEPL - A Parser Library for Python 3
====================================

Using LEPL you can define a grammar (that describes how some text is
structured) and then generate Python data (lists, dicts, and even trees of
objects) from a string formatted according to that grammar.  You can also
generate helpful errors when the input does not match the structure expected.

LEPL is intended to be simple and easy to use, but also has some features that
may interest advanced users, including full backtracking and multiple results
("parse forests").

In this example a tree of objects is generated from an arithmetic expression::

  >>> from lepl.match import *
  >>> from lepl.node import Node, make_error, Error, throw

  >>> class Term(Node): pass
  >>> class Factor(Node): pass
  >>> class Expression(Node): pass

  >>> expr   = Delayed()
  >>> number = Digit()[1:,...]                          > 'number'

  >>> with Separator(r'\s*'):
  >>>     term    = number | '(' & expr & ')'           > Term
  >>>     muldiv  = Any('*/')                           > 'operator'
  >>>     factor  = term & (muldiv & term)[:]           > Factor
  >>>     addsub  = Any('+-')                           > 'operator'
  >>>     expr   += factor & (addsub & factor)[:]       > Expression
  >>>     line    = expr & Eos()

  >>> parser = line.parse_string
  >>> parser('1 + 2 * (3 + 4 - 5)')[0]
  
  Expression
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
	   `- ')'

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
   search
   resources
   errors
   debugging
   style
   technical
   credits

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

