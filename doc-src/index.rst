
LEPL - A Parser Library for Python 3 (and 2.6)
==============================================

Introducing version 2.0 of LEPL with a new, more powerful core.

I am trying to keep LEPL simple and intuitive to the "end user" (the
:ref:`example` shows just how friendly it can be) while making it easier to
add features from recent research papers "under the hood".  The combination of
trampolining (which exposes the inner loop) and matcher graph rewriting (which
allows the parser to be restructured programmatically) should allow further
extensions without changing the original, simple grammar syntax.

The aim is a powerful, extensible parser that will also give solid, reliable
results to first--time users.  This release is a major step towards that goal.


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
  ambiguity this means that "any" grammar can be supported. [1]_

* Pluggable trace and resource management, including **"deepest match"
  diagnostics** and the ability to limit backtracking. [1]_

LEPL's *weakest* point is probably performance.  This has improved
with memoisation, but it is still more suited for exploratory and
one--off jobs than, for example, a compiler front--end.  Measuring and
improving performance is the main target of the next release.

The `API documentation <api/index.html>`_ is also available.

.. [1] These features rely on the most ambitious changes in the new
       2.0 core and so are not yet as reliable or efficient as the
       rest of the code.  This will be addressed in the 2.1 release.


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

