
LEPL - A Parser Library for Python 3 (and 2.6)
==============================================

LEPL is a recursive descent parser, written in Python, which has a a friendly,
easy--to--use syntax (:ref:`example`).  The underlying implementation includes
several features that make it more powerful than might be expected.

For example, it is not limited by the Python stack, because it uses
trampolining and co--routines.  Multiple parses can be found for ambiguous
grammars and it can also handle left--recursive grammars.

The aim is a powerful, extensible parser that will also give solid, reliable
results to first--time users.

This release (2.1) improves performance.  Typical parsers are now twice as
fast (improved constant factor) while left recursive grammars are re--arranged
to avoid unnecessary deep recursion (improved "big-O" performance; one test
case improved by a factor of 40).  This work is decribed in :ref:`rewriting`,
but is applied automatically and does not need to be understood for simple
applications.


Features
--------

* **Parsers are Python code**, defined in Python itself.  No separate
  grammar is necessary.

* **Friendly syntax** using Python's operators (:ref:`example`).

* Built-in **AST support** (a generic ``Node`` class).  Improved
  support for the visitor pattern and tree re--writing.

* **Well documented** and easy to extend.

* **Unlimited recursion depth**.  The underlying algorithm is
  recursive descent, which can exhaust the stack for complex grammars
  and large data sets.  LEPL avoids this problem by using Python
  generators as coroutines (aka "trampolining").

* Support for ambiguous grammars (**complete backtracking**).  A
  parser can return more than one result (aka **"parse forests"**).

* **Packrat parsing**.  Parsers can be made much more efficient with
  automatic memoisation.

* **Parser rewriting**.  The parser can itself be manipulated by
  Python code.  This gives unlimited opportunities for future
  expansion and optimisation.

* **Left recursive grammars**.  Memoisation can detect and control
  left--recursive grammars.  Together with LEPL's support for
  ambiguity this means that "any" grammar can be supported.

* Pluggable trace and resource management, including **"deepest match"
  diagnostics** and the ability to limit backtracking.

The `API documentation <api/index.html>`_ is also available.


Download
--------

See :ref:`install`.


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


Contents
--------

.. toctree::
   :maxdepth: 2

   intro
   matchers
   operators
   nodes
   errors
   resources
   debugging
   advanced
   style
   download
   implementation
   closing


Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

