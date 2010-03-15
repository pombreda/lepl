
.. _errors:

Error Reporting
===============


.. index:: errors

Introduction
------------

In some applications it is important not only to parse correctly structured
input, but also to give a helpful responses when the input is incorrectly
structured.

Lepl provides support for reporting errors in the input in two ways.  First,
it allows a matcher to directly raise an exception.  Second, parse tree nodes
can be constructed which represent errors; these error nodes can then be used,
later, to raise exceptions.

The advantage of the second approach is that it allows for additional context
to determine whether an error is present.  An error node may be added to the
results only to be later discarded during backtracking --- information from
later in the input stream has shown that the error did not occur.

The implementation of both these approaches is simple, building directly on
the functionality already available within Lepl (in particular, Nodes and
function invocation).  They should therefore be easy to extend to more complex
schemes.


.. index:: ^, make_error(), **, throw(), Error()

Example
-------

Here is an example of both approaches in use::

  >>> from lepl import *

  >>> class Term(Node): pass
  >>> class Factor(Node): pass
  >>> class Expression(Node): pass

  >>> expr    = Delayed()
  >>> number  = Digit()[1:,...]                          > 'number'
  >>> badChar = AnyBut(Space() | Digit() | '(')[1:,...]

  >>> with Separator(r'\s*'):

  >>>     unopen   = number ** make_error('no ( before {stream_out}') & ')'
  >>>     unclosed = ('(' & expr & Eos()) ** make_error('no ) for {stream_in}')

  >>>     term    = Or(
  >>>                  (number | '(' & expr & ')')      > Term,
  >>>                  badChar                          ^ 'unexpected text: {results[0]}',
  >>>                  unopen                           >> throw,
  >>>                  unclosed                         >> throw
  >>>                  )
  >>>     muldiv  = Any('*/')                           > 'operator'
  >>>     factor  = (term & (muldiv & term)[:])         > Factor
  >>>     addsub  = Any('+-')                           > 'operator'
  >>>     expr   += (factor & (addsub & factor)[:])     > Expression
  >>>     line    = Empty() & Trace(expr) & Eos()

  >>> parser = line.string_parser()

  >>> parser('1 + 2 * (3 + 4 - 5')[0]
    File "str: '1 + 2 * (3 + 4 - 5'", line 1
      1 + 2 * (3 + 4 - 5
	      ^
  lepl.matchers.error.Error: no ) for '(3 + 4...'

  >>> parser('1 + 2 * 3 + 4 - 5)')[0]
    File "str: '1 + 2 * 3 + 4 - 5)'", line 1
      1 + 2 * 3 + 4 - 5)
		      ^
  lepl.matchers.error.Error: no ( before ')'

  >>> parser('1 + 2 * (3 + four - 5)')[0]
    File "str: '1 + 2 * (3 + four - 5)'", line 1
      1 + 2 * (3 + four - 5)
		   ^
  lepl.matchers.error.Error: unexpected text: four

  >>> parser('1 + 2 ** (3 + 4 - 5)')[0]
    File "str: '1 + 2 ** (3 + 4 - 5)'", line 1
      1 + 2 ** (3 + 4 - 5)
	     ^
  lepl.matchers.error.Error: unexpected text: *


.. note::

  This example follows the :ref:`applycase` and :ref:`complexor` patterns.

.. warning::

  The *order* of expressions is important in the example above.  The default
  :ref:`configuration` will *change the order* of some expressions if the
  grammar is left--recursive.  So if you have a left--recursive grammar and
  want to use the approach shown to error handling then you must use a custom
  configuration that excludes the `optimize_or(conservative)
  <api/redirect.html#lepl.rewriters.optimize_or>`_ rewriter.  For more
  information see :ref:`memoisation`.


.. index:: ^, Error(), SyntaxError()

Operators, Functions and Classes
--------------------------------

===============  ========  ========
Name             Type      Action
===============  ========  ========
``^``            Operator  Raises an exception, given a format string.  Formatting has the same named parameters as the `KApply()  <api/redirect.html#lepl.functions.KApply>`_ matcher (results, stream_in, stream_out); implemented as KApply(`raise_error <api/redirect.html#lepl.node.raise_error>`_)
---------------  --------  --------
``raise_error``  Function  See above.  `API <api/redirect.html#lepl.node.raise_error>`_
---------------  --------  --------
``Error``        Class     Creates a parse tree node that can be used to trigger a later exception (`Error <api/redirect.html#lepl.node.Error>`_ is a subclass of both `Node <api/redirect.html#lepl.node.Node>`_ and ``SyntaxError``).  `API <api/redirect.html#lepl.node.Error>`_ 
---------------  --------  --------
``throw``        Function  Walks the parse tree (typically this is a sub--tree associated with a matcher's result and `throw <api/redirect.html#lepl.node.throw>`_ is invoked by `Apply() <api/redirect.html#lepl.functions.Apply>`_) and raises the first `Error <api/redirect.html#lepl.node.Error>`_ found.  `API <api/redirect.html#lepl.node.make_throw>`_.
---------------  --------  --------
``make_error``   Function  Creates an `Error <api/redirect.html#lepl.node.Error>`_ node, given a format string.  `API <api/redirect.html#lepl.node.make_error>`_.
===============  ========  ========
