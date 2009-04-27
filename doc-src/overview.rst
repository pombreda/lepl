
.. _overview:

Overview
========

* :ref:`Parsers are Python code <example>`, defined in Python itself.  No
  separate grammar is necessary.

* Friendly syntax using Python's :ref:`operators <operators>`.

* Built-in :ref:`AST support <trees>`.

* Well documented and easy to extend.

* :ref:`Unlimited recursion depth <trampolining>`.  The underlying algorithm
  is recursive descent, which can exhaust the stack for complex grammars and
  large data sets.  LEPL avoids this problem by using Python generators as
  coroutines.

* Support for :ref:`ambiguous grammars <backtracking>`.  A parser can return
  more than one result ("complete backtracking", "parse forests").

* Parsers can be made much more efficient with automatic :ref:`memoisation
  <memoisation>` ("packrat parsing" and support for left recursive grammars).

* The parser can itself be :ref:`manipulated <rewriting>` by Python code.
  This gives unlimited opportunities for future expansion and optimisation.

* :ref:`Left recursive grammars <left_recursion>`.  Memoisation can detect and
  control left--recursive grammars.

* Pluggable trace and resource management, including :ref:`deepest match
  <deepest_match>` diagnostics and the ability to :ref:`limit backtracking
  <resources>`.


API Documentation
-----------------

The `API documentation <api/index.html>`_ is available online.


Download
--------

See :ref:`install` for complete instructions.

Python 2.6 users can get the latest stable version using ``easy_install
lepl``.  Packages and documentation are available from the `support site
<http://lepl.googlecode.com/>`_.


.. _example:

Example
-------

Using LEPL you can define a grammar (that describes how some text is
structured) and then generate Python data (lists, dicts, and even trees of
objects) from a string formatted according to that grammar.  You can also
generate helpful errors when the input does not match the structure expected.

In this example a tree of objects is generated from an arithmetic expression::

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


