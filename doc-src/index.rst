
LEPL - A Parser Library for Python 3 (and 2.6)
==============================================

* `API Documentation <api>`_

* :ref:`Documentation Contents <contents>`

  * :ref:`Tutorial <tutorial>`
  * :ref:`Manual <manual>`
  * :ref:`Download etc <support>`

LEPL is written and maintained by `Andrew Cooke <http://www.acooke.org>`_.


Features
--------

* :ref:`Parsers are Python code <example>`, defined in Python itself.  No
  separate grammar is necessary.

* Friendly syntax using Python's :ref:`operators <operators>` allows grammars
  to be defined in a declarative style close to BNF.

* Optional, integrated :ref:`Lexer <lexer>` simplifies handling whitespace.

* Built-in :ref:`AST support <trees>` with support for iteration, traversal
  and re--writing.

* Generic, pure-Python approach supports parsing a wide variety of data
  including :ref:`binary data <binary>` (Python 3+ only).

* Well documented and easy to extend.

* :ref:`Unlimited recursion depth <trampolining>`.  The underlying algorithm
  is recursive descent, which can exhaust the stack for complex grammars and
  large data sets.  LEPL avoids this problem by using Python generators as
  coroutines.

* The parser can itself be :ref:`manipulated <rewriting>` by Python code.
  This gives unlimited opportunities for future expansion and optimisation.

* Support for :ref:`ambiguous grammars <backtracking>`.  A parser can return
  more than one result ("complete backtracking", "parse forests").

* Parsers can be made much more efficient with automatic :ref:`memoisation
  <memoisation>` ("packrat parsing").

* Memoisation can detect and control :ref:`left recursive grammars
  <left_recursion>`.  Together with LEPL's support for ambiguity this means
  that "any" grammar can be supported.

* Pluggable trace and resource management, including :ref:`deepest match
  <deepest_match>` diagnostics and the ability to :ref:`limit backtracking
  <resources>`.

.. _example:

Example
-------

To generate an AST for an arithmetic expression::

  >>> from lepl import *

  >>> class Term(Node): pass
  >>> class Factor(Node): pass
  >>> class Expression(Node): pass

  >>> expr   = Delayed()
  >>> number = Digit()[1:,...]                          > 'number'
  >>> spaces = Drop(Regexp(r'\s*'))

  >>> with Separator(spaces):
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

.. _contents:

Contents
--------

.. toctree::
   :maxdepth: 2

   intro
   manual
   support


Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

