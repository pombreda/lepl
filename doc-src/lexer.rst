
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

Here the ``name`` `Token <api/redirect.html#lepl.lexer.matchers.Token>`_ defined above
is further restricted to match only the string "sin" (this comes from the
:ref:`calculator_example` example).
