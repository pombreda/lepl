

Results
=======


Flat List
---------

Simple declarations produce a single list of tokens (ignoring
:ref:`backtracking`).  For example::

  >>> from lepl import *
  
  >>> expr   = Delayed()
  >>> number = Digit()[1:,...]
  
  >>> with Separator(r'\s*'):
  >>>     term    = number | '(' & expr & ')'
  >>>     muldiv  = Any('*/')
  >>>     factor  = term & (muldiv & term)[:]
  >>>     addsub  = Any('+-')
  >>>     expr   += factor & (addsub & factor)[:]
  >>>     line    = expr & Eos()
  >>> line.parse_string('1 + 2 * (3 + 4 - 5)')
  ['1', ' ', '', '+', ' ', '2', ' ', '*', ' ', '(', '', '3', ' ', '', '+', ' ', '4', ' ', '', '-', ' ', '5', '', '', ')', '']

.. index:: Drop()
.. note::

  The empty strings are a result of the separator and could be removed by
  using ``with Separator(Drop(Regexp(r'\s*'))):``


.. index:: s-expressions, list, nested lists
.. _nestedlists:

Nested Lists
------------

Nested lists (S-Expressions) are a traditional way of structuring parse
results.  With LEPL they are easy to construct with ``> list``::

  >>> expr   = Delayed()
  >>> number = Digit()[1:,...]

  >>> with Separator(Drop(Regexp(r'\s*'))):
  >>>     term    = number | (Drop('(') & expr & Drop(')') > list)
  >>>     muldiv  = Any('*/')
  >>>     factor  = (term & (muldiv & term)[:])
  >>>     addsub  = Any('+-')
  >>>     expr   += factor & (addsub & factor)[:]
  >>>     line    = expr & Eos()
  >>> line.parse_string('1 + 2 * (3 + 4 - 5)')
  ['1', '+', '2', '*', ['3', '+', '4', '-', '5']]

.. note::

  ``list`` is just the usual Python constructor.

  (Since ``list`` is idempotent (or a fixed point or something) ---
  ``list(list(x)) == list(x)`` --- the operator ``>``
  (`lepl.matchers.Apply(raw=false)`) actually has to add wrap the result of
  any function in a list.  If this comment is confusing, please ignore it, but
  it may help explain an otherwise annoying design detail.)


.. index:: Node(), AST, parse tree, trees

Trees
-----

LEPL includes a simple base class that can be used to construct trees::

  >>> class Term(Node): pass
  >>> class Factor(Node): pass
  >>> class Expression(Node): pass

  >>> expr   = Delayed()
  >>> number = Digit()[1:,...]                        > 'number'

  >>> with Separator(r'\s*'):
  >>>     term    = number | '(' & expr & ')'         > Term
  >>>     muldiv  = Any('*/')                         > 'operator'
  >>>     factor  = term & (muldiv & term)[:]         > Factor
  >>>     addsub  = Any('+-')                         > 'operator'
  >>>     expr   += factor & (addsub & factor)[:]     > Expression
  >>>     line    = expr & Eos()

  >>> ast = line.parse_string('1 + 2 * (3 + 4 - 5)')[0]

  >>> ast
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
	   `- ')

The `Node <api/redirect.html#lepl.node.Node>`_ class functions like an
array of the original results (including spaces)::

  >>> [child for child in ast]
  [Factor(...), '', ('operator', '+'), ' ', Factor(...)]

  >>> [ast[i] for i in range(len(ast))]
  [Factor(...), '', ('operator', '+'), ' ', Factor(...)]

Nodes also provide attribute access to child nodes and named pairs.  These are
returned as lists, since sub--node types and names need not be unique::

  >>> [(name, getattr(ast, name)) for name in dir(ast)]
  [('operator', ['+']), ('Factor', [Factor(...), Factor(...)])]

  >>> ast.Factor[1].Term[0].number[0]
  '2'

Finally, Nodes extend `SimpleGraphNode()
<api/redirect.html#lepl.graph.SimpleGraphNode>`_, which means that some of the
routines in the `graph <api/redirect.html#lepl.graph>`_ package can be used to
process ASTs.
