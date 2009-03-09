
.. index:: matchers
.. _matchers:

Matchers
========

The `API Documentation <api/redirect.html#lepl.matchers>`_ contains an
exhaustive list of the matches available.  This chapter only describes the
most important.

The final section gives some `implementation details`_.


.. index:: Literal()

Literal 
-------

`[API] <api/redirect.html#lepl.matchers.Literal>`_
This matcher identifies a given string.  For example, ``Literal('hello')``
will give the result "hello" when that text is at the start of a stream::

  >>> Literal('hello').parse_string('hello world')
  ['hello']

In many cases it is not necessary to use `Literal()
<api/redirect.html#lepl.matchers.Literal>`_ explicitly.  Most matchers, when
they receive a string as a constructor argument, will automatically create a
literal match from the given text.


.. index:: Any()

Any
---

`[API] <api/redirect.html#lepl.matchers.Any>`_ This matcher identifies any
single character.  It can be restricted to match only characters that appear
in a given string.  For example::

  >>> Any().parse_string('hello world')
  ['h']

  >>> Any('abcdefghijklm')[0:].parse_string('hello world')
  ['h', 'e', 'l', 'l']


.. index:: And(), &

And (&)
-------

`[API] <api/redirect.html#lepl.matchers.And>`_ This matcher combines other
matchers in order.  For example::

  >>> And(Any('h'), Any()).parse_string('hello world')
  ['h', 'e']

All matchers must succeed for `And() <api/redirect.html#lepl.matchers.And>`_
as a whole to succeed::

  >>> And(Any('h'), Any('x')).parse_string('hello world')
  None


.. index:: Or(), |

Or (|)
------

`[API] <api/redirect.html#lepl.matchers.Or>`_ This matcher searches through a
list of other matchers to find a successful match.  For example::

  >>> Or(Any('x'), Any('h'), Any('z')).parse_string('hello world')
  ['h']

The first match found is the one returned::

  >>> Or(Any('h'), Any()[3]).parse_string('hello world')
  ['h']

But with the "match" rather than the "parse" methods, subsequent calls return
the other possibilities::

  >>> matcher = Or(Any('h'), Any()[3]).match('hello world')
  >>> next(matcher)
  (['h'], 'ello world')
  >>> next(matcher)
  (['h', 'e', 'l'], 'lo world')

This shows how `Or() <api/redirect.html#lepl.matchers.Or>`_ --- backtracking
may call the matcher times before a result is found that "fits" with the rest
of the grammar.


.. index:: Repeat(), [], backtracking, breadth-first, depth-first

Repeat ([...])
--------------

`[API] <api/redirect.html#lepl.matchers.Repeat>`_ This matcher repeats another
matcher a given number of times.  For example::

  >>> Repeat(Any(), 3, 3).parse_string('12345')
  ['1', '2', '3']

If only a lower bound to the number of repeats is given the match will be
repeated as often as possible::

  >>> Repeat(Any(), 3).parse_string('12345')
  ['1', '2', '3', '4', '5']

If the match cannot be repeated the requested number of times no result is
returned::

  >>> Repeat(Any(), 3).parse_string('12')
  None

When used as with the "match" methods, different numbers of matches are
available on subsequent calls (backtracking)::

  >>> matcher = Repeat(Any(), 3).match('12345')
  >>> next(matcher)
  (['1', '2', '3', '4', '5'], '')
  >>> next(matcher)
  (['1', '2', '3', '4'], '5')
  >>> next(matcher)
  (['1', '2', '3'], '45')
  >>> next(matcher)
  StopIteration

By default a depth--first search is used (giving the longest match first).
Specifying an third argument (the increment when used with ``[]`` syntax) of
``'b'`` gives breadth--first search (shortest first)::

  >>> matcher = Repeat(Any(), 3, None, 'b').match('12345')
  >>> next(matcher)
  (['1', '2', '3'], '45')
  >>> next(matcher)
  (['1', '2', '3', '4'], '5')
  >>> next(matcher)
  (['1', '2', '3', '4', '5'], '')
  >>> next(matcher)
  StopIteration


.. index:: Lookahead(), ~
.. _lookahead:

Lookahead
---------

`[API] <api/redirect.html#lepl.matchers.Lookahead>`_ This matcher checks
whether another matcher would succeed, but returns the original stream with an
empty result list.

  >>> next(Lookahead(Literal('hello')).match('hello world'))
  ([], 'hello world')
  >>> Lookahead(Literal('hello')).parse('hello world')
  []

It fails if the match would not be possible (specifying a string as matcher is
equivalent to using `Literal()
<api/redirect.html#lepl.matchers.Literal>`_)::

  >>> Lookahead('hello').parse_string('goodbye cruel world')
  None

When preceded by a ``~`` the logic is reversed::

  >>> (~Lookahead('hello')).parse_string('hello world')
  None
  >>> (~Lookahead('hello')).parse_string('goodbye cruel world')
  []

.. note::

  Because ``~`` binds less strongly than method invocation extra parentheses
  are needed above.

.. note::

  This change in behaviour is specific to `Lookahead()
  <api/redirect.html#lepl.matchers.Lookahead>`_ --- usually ``~`` applies
  `Drop() <api/redirect.html#lepl.matchers.Drop>`_ as described below.


.. index:: Drop(), ~

Drop (~)
--------

`[API] <api/redirect.html#lepl.matchers.Drop>`_ This matcher calls another
matcher, but discards the results::

  >>> (Drop('hello') / 'world').parse_string('hello world')
  [' ', 'world']

(The empty string in the first result is from ``/`` which joins two matchers
together, with optional spaces between).

This is different to `Lookahead()
<api/redirect.html#lepl.matchers.Lookahead>`_ because the matcher after
`Drop() <api/redirect.html#lepl.matchers.Drop>`_ receives a stream that has
"moved on" to the next part of the input.  With `Lookahead()
<api/redirect.html#lepl.matchers.Lookahead>`_ the stream is not advanced and
so this example will fail::

  >>> (Lookahead('hello') / 'world').parse_string('hello world')
  None


.. index:: Apply(), >, *

Apply (>, *)
------------

`[API] <api/redirect.html#lepl.matchers.Apply>`_ This matcher passes the
results of another matcher to a function, then returns the value from the
function as a new result::

  >>> def show(results):
  ...     print('results:', results)
  ...     return results
  >>> Apply(Any()[:,...], show).parse_string('hello world')
  results: ['hello world']
  [['hello world']]

The returned result is placed in a new list, which is not always what is
wanted (it is useful when you want :ref:`nestedlists`); setting ``raw=True``
uses the result directly::

  >>> Apply(Any()[:,...], show, raw=True).parse_string('hello world')
  results: ['hello world']
  ['hello world']

Setting another optional argument, ``args``, to ``True`` changes the way the
function is called.  Instead of passing the results as a single list each is
treated as a separate argument.  This is familiar as the way ``*args`` works
in Python (hence the shortcut operator, ``*``).


.. index:: **

KApply (**)
-----------

`[API] <api/redirect.html#lepl.matchers.KApply>`_ This matcher passes the
results of another matcher to a function, along with additional information
about the match, then returns the value from the function as a new result.
Unlike `Apply() <api/redirect.html#lepl.matchers.Apply>`_, this names the
arguments as follows:

  stream_in
    The stream passed to the matcher before matching.

  stream_out
    The stream returned from the matcher after matching.

  results
    A list of the results returned.


.. index:: First(), Empty(), Regexp(), Delayed(), Commit(), Trace(), AnyBut(), Optional(), Star(), ZeroOrMore(), Plus(), OneOrMore(), Map(), Add(), Substitute(), Name(), Eof(), Eos(), Identity(), Newline(), Space(), Whitespace(), Digit(), Letter(), Upper(), Lower(), Printable(), Punctuation(), UnsignedInteger(), SignedInteger(), Integer(), UnsignedFloat(), SignedFloat(), SignedEFloat(), Float(), Word().

More
----

Many more matchers are described in the `API Documentation
<api/redirect.html#lepl.match>`_, including 
`First() <api/redirect.html#lepl.matchers.First>`_,
`Empty() <api/redirect.html#lepl.matchers.Empty>`_,
`Regexp() <api/redirect.html#lepl.matchers.Regexp>`_,
`Delayed() <api/redirect.html#lepl.matchers.Delayed>`_,
`Commit() <api/redirect.html#lepl.matchers.Commit>`_,
`Trace() <api/redirect.html#lepl.matchers.Trace>`_,
`AnyBut() <api/redirect.html#lepl.matchers.AnyBut>`_,
`Optional() <api/redirect.html#lepl.matchers.Optional>`_,
`Star() <api/redirect.html#lepl.matchers.Star>`_,
`ZeroOrMore() <api/redirect.html#lepl.matchers.ZeroOrMore>`_,
`Plus() <api/redirect.html#lepl.matchers.Plus>`_,
`OneOrMore() <api/redirect.html#lepl.matchers.OneOrMore>`_,
`Map() <api/redirect.html#lepl.matchers.Map>`_,
`Add() <api/redirect.html#lepl.matchers.Add>`_,
`Substitute() <api/redirect.html#lepl.matchers.Substitute>`_,
`Name() <api/redirect.html#lepl.matchers.Name>`_,
`Eof() <api/redirect.html#lepl.matchers.Eof>`_,
`Eos() <api/redirect.html#lepl.matchers.Eos>`_,
`Identity() <api/redirect.html#lepl.matchers.Identity>`_,
`Newline() <api/redirect.html#lepl.matchers.Newline>`_,
`Space() <api/redirect.html#lepl.matchers.Space>`_,
`Whitespace() <api/redirect.html#lepl.matchers.Whitespace>`_,
`Digit() <api/redirect.html#lepl.matchers.Digit>`_,
`Letter() <api/redirect.html#lepl.matchers.Letter>`_,
`Upper() <api/redirect.html#lepl.matchers.Upper>`_,
`Lower() <api/redirect.html#lepl.matchers.Lower>`_,
`Printable() <api/redirect.html#lepl.matchers.Printable>`_,
`Punctuation() <api/redirect.html#lepl.matchers.Punctuation>`_,
`UnsignedInteger() <api/redirect.html#lepl.matchers.UnsignedInteger>`_,
`SignedInteger() <api/redirect.html#lepl.matchers.SignedInteger>`_,
`Integer() <api/redirect.html#lepl.matchers.Integer>`_,
`UnsignedFloat() <api/redirect.html#lepl.matchers.UnsignedFloat>`_,
`SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_,
`SignedEFloat() <api/redirect.html#lepl.matchers.SignedEFloat>`_,
`Float() <api/redirect.html#lepl.matchers.Float>`_, and
`Word() <api/redirect.html#lepl.matchers.Word>`_.

  

.. index:: generator, results, failure, implementation, Matcher, BaseMatcher, ABC
.. _implementation_details:

Implementation Details
----------------------

All matchers accept a stream of data and return a generator.  The generator
will supply a sequence of *([results], stream)* pairs, where *results* depends
on the matcher and the new stream continues from after the matched text [*]_.

A matcher may succeed, but provide no results --- the generator will return a
tuple containing an empty list and the new stream.  When there are no more
possible matches, the generator will exit.

Most simple matchers will return a generator that yields a single value.
Generators that return multiple values are used in backtracking.  For example,
the `Or() <api/redirect.html#lepl.matchers.Or>`_ generator may yield once for
each sub--match in turn (in practice some sub-matches may return generators
that themselves return many values, while others may fail immediately, so it
is not a direct 1--to--1 correspondence).

(It is probably obvious if you have used combinator libraries before, but
worth mentioning anyway: all matchers implement this same interface, whether
they are "fundamental" --- do the real work of matching against the stream ---
or delegate work to other sub--matchers, or modify results.  This consistency
is a source of great expressive power.)

Existing matchers take care to exploit the common interface between lists and
strings, so matching should work on a variety of streams, including
inhomogeneous lists of objects.

All matcher implementations should subclass the ABC `Matcher
<api/redirect.html#lepl.operators.Matcher>`_.  Most will do so by inheriting
from `BaseMatcher <api/redirect.html#lepl.matchers.BaseMatcher>`_ which
provides support for operators.

.. [*] I am intentionally omitting details about trampolining here to focus on
       the process of matching.  A more complete description of the entire
       implementation can be found in :ref:`trampolining`.
