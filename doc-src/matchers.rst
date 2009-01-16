
Matchers
========

The `API Documentation <../api/redirect.html#lepl.match>`_ contains an
exhaustive list of the matches available.  This chapter only describes the
most important.

The final section gives some `implementation details`_.


Literal `(API) <../api/redirect.html#lepl.match.Literal>`_
--------------------------------------------------------

This matcher identifies a given string.  For example, ``Literal('hello')``
will give the result "hello" when that text is at the start of a stream::

  >>> Literal('hello').parse_string('hello world')
  ['hello']

Or explicitly using the generator and a simple string as a stream::

  >>> next(Literal('hello')('hello world'))
  (['hello'], ' world')

(The second form above shows how matchers are used internally.  They return
the result and a new stream, which has "moved past" the matched data.)

In many cases it is not necessary to use ``Literal()`` explicitly.  Most
matchers, when they receive a string as a constructor argument, will
automatically create a literal match from the given text.


.. _implementation details:

Implementation Details
----------------------

All matchers work as functions (they may be objects, but will implement the
``__call__`` method) that accept a stream of data and return a generator.  The
generator will supply a sequence of *([results], stream)* pairs, where
*results* depends on the matcher and the new stream continues from after the
matched text.

A matcher may succeed, but provide no results --- the generator will return a
tuple containing an empty list and the new stream.  When there are no more
possible matches, the generator will exit.

Most simple matchers will return a generator that yields a single value.
Generators that return multiple values are used in backtracking.  For example,
the ``Or()`` generator may yield once for each sub--match in turn (in
practice some sub-matches may return generators that themselves return many
values, while others may fail immediately, so it is not a direct 1--to--1
correspondence).

(Obvious if you have used combinator libraries before, but worth mentioning
anyway: all matchers implement this same interface, whether they are
"fundamental" --- do the real work of matching against the stream --- or
delegate work to other sub--matchers, or modify results.  This consistency is
a source of great expressive power.)

Implementations take care to exploit the common interface between lists and
strings, so matching should work on a variety of streams, including
imhomogenous lists of objects.
