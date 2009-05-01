
.. index:: lexer
.. _lexer:

Lexer
=====

The use of LEPL's lexer is optional.  In the preceding sections it has not
been used.  However, for many applications it will both simplify the grammar
and give a more efficient parser.

.. note::

   The lexer was added to LEPL in version 2.4.  It is therefore less mature
   than other parts of the system.


Introduction
------------

The lexer pre-processes the stream that is being parsed, dividing it into
tokens that correspond to regular expressions.  The tokens, and their
contents, can then be matched in the grammar.

`Tokens <api/redirect.html#lepl.lexer.matchers.Token>`_ give a "rough"
description of the text to be parsed.  A simple parser of numerical
expressions might have the following different token types:

  * Numeric values (eg. 1, 2.3, 4e5).

  * Function names (eg. sin, cos).

  * Symbols (eg. ``(``, ``+``).

Note that in the sketch above, a token is not defined for spaces.  By default,
when the lexer runs, any character that doesn't match a token is discarded.
This process allows spaces to separate tokens without them cluttering the
grammar.


.. index:: Token()

Use
---

`Tokens <api/redirect.html#lepl.lexer.matchers.Token>`_ are used in two ways.
First, they work like matchers (with the exceptions noted below) for the
regular expression given as their argument.  For example::

  >>> name = Token('[A-Z][a-z]*')
  >>> number = Token(Integer())

Here, ``name`` with match a string that starts with a capital letter and then
has zero or more lower case letters.  The second `Token
<api/redirect.html#lepl.lexer.matchers.Token>`_, ``number``, is similar, but
uses a matcher (`Integer() <api/redirect.html#lepl.matchers.Integer>`_) to
define the regular expression that is matched.

.. note::

  Not all matchers can be used to define the pattern for a `Token
  <api/redirect.html#lepl.lexer.matchers.Token>`_ --- only those that LEPL
  knows how to convert into regular expressions.

The second way in which `Tokens
<api/redirect.html#lepl.lexer.matchers.Token>`_ are used is by specialisation,
which gives an *additional* constraint.  This is easiest to see with another
example::

  >>> sin = name('sin')

Here the ``name`` `Token <api/redirect.html#lepl.lexer.matchers.Token>`_
defined above is further restricted to match only the string "sin" (this comes
from the :ref:`calculator_example` example).


Limitations
-----------

Unlike regular matchers, `Tokens
<api/redirect.html#lepl.lexer.matchers.Token>`_ only match the text once.
They divide the input into fixed blocks that match the largest possible `Token
<api/redirect.html#lepl.lexer.matchers.Token>`_; no alternatives are
considered.

For example, consider "1-2", which might be parsed as two integers (1 and -2),
or as a subtraction expression (1 minus 2)::

  >>> matchers = (Integer() | Literal('-'))[:] & Eos()
  >>> list(matchers.match('1-2'))
  [(['1', '-2'], ''), (['1', '-', '2'], '')]

When `Tokens <api/redirect.html#lepl.lexer.matchers.Token>`_ are used, "-2" is
preferred to "-" because it is a longer match, so we get only the single
result::

  >>> tokens = (Token(Integer()) | Token(r'\-'))[:] & Eos()
  >>> list(tokens.match('1-2', config=Configuration.tokens()))
  [(['1', '-2'], <SimpleGeneratorStream>)]

(In the examples above, ``list()`` is used to expand the generator and the
`Token <api/redirect.html#lepl.lexer.matchers.Token>`_ is given `r'\-'`
because its argument is a regular expression, not a literal value.)


.. index:: lexer_rewriter()

Advanced Options
----------------

The `lexer_rewriter()
<api/redirect.html#lepl.lexer.rewriters.lexer_rewriter>`_ can take additional
arguments that specify a regular expression for (discarded) spaces and an
exception that is raised when neither the `Tokens
<api/redirect.html#lepl.lexer.matchers.Token>`_ nor the space patter match the
input.

By default `Tokens <api/redirect.html#lepl.lexer.matchers.Token>`_ require
that any sub--expression consumes the entire contents::

  >>> abc = Token('abc')
  >>> incomplete = abc(Literal('ab'))
  >>> incomplete.parse('abc', config=Configuration.tokens())
  None

However, this constraint can be relaxed, in which case the matched portion is
returned as a result::

  >>> abc = Token('abc')
  >>> incomplete = abc(Literal('ab'), complete=False)
  >>> incomplete.parse('abc', config=Configuration.tokens())
  ['ab']


Example
-------

:ref:`calculator_example` is a complete, worked example using `Tokens
<api/redirect.html#lepl.lexer.matchers.Token>`_.
