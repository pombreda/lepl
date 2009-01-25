
.. _introduction:

Introduction
============

This chapter works through a simple example using LEPL.

After reading this chapter you should have a better understanding of what
matchers do and how they can be constructed.


Matchers
--------

.. index:: matchers

The structure of a piece of text is described in LEPL using *matchers*.  A
simple matcher might recognise a letter, digit or space.  More complex
matchers are built from these to recognise words, equations, etc.

One a matcher has been built up in this way it can be used to process text.
Internally, this means that the final, complex, matcher passes the text to the
simpler matchers that were used as "building blocks".  These break the text
into pieces that are then assembled into the final result.

So we describe a structure (called a *grammar*) using matchers then use those
matchers to break text into pieces that match that structure.  This process is
called parsing.

An example will make this clearer.  Imagine that we are given a username and a
phone number, separated by a comma, and we want to split that into the two
values::

  >>> from lepl import *
  
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> matcher = name / ',' / phone  > make_dict
  
  >>> next(matcher('andrew, 3333253'))
  ([{'phone': '3333253', 'name': 'andrew'}], '')

The main body of this program (after the import statements) defines the
matcher.  The last line uses that to make a ``dict`` that contains the values
from the string ``'andrew, 3333253'``.

There's a lot going on here, some of which I will explain in later sections,
but the most important thing to notice is that ``matcher`` was constructed
from two simpler matchers --- ``Word()`` and ``Integer()``.  It is those two
matchers that identify the values 'andrew' (a word) and '3333253' (an
integer).


Combinations
------------

All matchers work in the same way: they take a *stream* of input and produce
some results and a new stream as output (for now we use strings as simple
streams).  But, because a matcher may find more than one match, it does not
return the results and stream directly.  Instead, it returns a *generator*.

Generators are a fairly new part of Python, rather like lists.  All you need
to know to use them is that, to read the value, you use the function
``next()``.

We can see how this works with the simple generators ``Word()`` and
``Integer()``::

  >>> next( Word()('hello world') )
  (['hello'], ' world')
  
  >>> next( Integer()('123 four five') )
  (['123'], ' four five')

Hopefully you can see the result and the remaining stream in both cases.

We can make a more complicated matcher from these by joining them together
with ``And()``::

  >>> next( And(Word(), Space(), Integer())('hello 123') )
  (['hello', ' ', '123'], '')

which can also be written as::

  >>> next( (Word() & Space() & Integer())('hello 123')) )
  (['hello', ' ', '123'], '')

or even::

  >>> next( (Word() / Integer())('hello 123')) )
  (['hello', ' ', '123'], '')

because ``&`` is shorthand for ``And()``, while ``/`` is similar, but allows
optional spaces.

Note how, in all the examples above, the results are contained in a list and
the returned stream starts after the results.  Putting the results in a list
allows a matcher to return more than one result (or none at all).  The new
stream can be used by another matcher to continue the work on the rest of the
input data.

This standard behaviour --- taking a stream as an argument then returning a
list of results and a new stream from a generator --- is useful internally,
but messy when we only want to see the final results.  So matchers also have
methods for simplifying the output::

  >>> (Word() / Integer()).parse_string('hello 123')
  ['hello', ' ', '123']


More Detail
-----------

Let's look at the initial example in more detail::

  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> matcher = name / ',' / phone  > make_dict
  
  >>> matcher.parse_string('andrew, 3333253')[0]
  {'phone': '3333253', 'name': 'andrew'}

The ``','`` is converted into a matcher that recognises a comma.  And the
``/`` joins the other matchers together with optional spaces.  But what does
the ``>`` do?

In general, ``>`` passes the results to a function.  But when the target is a
string a *named pair* is generated.

Since the ``>`` produces a matcher, we can test this at the command line::

  >>> next( (Word() > 'name')('andrew') )
  ([('name', 'andrew')], '')

  >>> next( (Integer() > 'phone')('3333253') )
  ([('phone', '3333253')], '')

This makes ``make_dict`` easier to understand.  Python's standard ``dict()``
will construct a dictionary from named pairs::

  >>> dict([('name', 'andrew'), ('phone', '3333253')])
  {'phone': '3333253', 'name': 'andrew'}

And the results from ``name / ',' / phone`` include named pairs::

  >>> next( (name / ',' / phone)('andrew, 3333253') )
  ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], '')

Now we know that ``>`` passes results to a function, so it looks like
``make_dict`` is almost identical to ``dict``.  In fact, the only difference
is that it strips out results that are not named pairs (in this case, the
comma and space).


Repetition
----------

.. index:: repetition, [], ~

Next we will extend the matcher so that we can process a list of several
usernames and phone numbers.

  >>> spaces  = Space()[0:]
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> line    = name / ',' / phone  > make_dict
  >>> newline = spaces & Newline() & spaces
  >>> matcher = line[0:,~newline]

  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  [{'phone': '3333253', 'name': 'andrew'}, {'phone': '12345', 'name': 'bob'}]

This uses repetition in two places.  First, and simplest, is ``Space()[0:]``.
This matches 0 or more spaces.  In general, adding ``[start:stop]`` to a
matcher will repeat it for between *start* and *stop* times (the defaults for
missing values and 0 and "as many as possible").

.. note:

  *stop* is *inclusive*, so ``Space()[2:3]`` would match 2 or 3 spaces.  This
  is subtly different from Python's normal array behaviour.

The second use of repetition is ``line[0:,~newline]``.  This repeats the
matcher ``line`` 0 or more times, but also includes another matcher,
``~newline``, which is used a *separator*.  The separator is placed between
each repeated item, like commas in a list.

So ``line[0:,~newline]`` will recognise repeated names and phone numbers,
separated by spaces and newlines.  The ``~`` used to modify ``newline``
discards any results so that they do not clutter the final list.  It could
also have been written as ``Drop(newline)`` --- another example of making a
more complex matcher from simpler pieces.


Extension
---------

The repeated matcher above returns a list of dicts.  But what we really want
is a single dict that associates each username with a telephone number.

We can write our own function to do this, then call it with ``>``::


  >>> def combine(results):
  >>>     all = {}
  >>>     for result in results:
  >>>         all[result['name']] = result['phone']
  >>>     return all
  
  >>> spaces  = Space()[0:]
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> line    = name / ',' / phone  > make_dict
  >>> newline = spaces & Newline() & spaces
  >>> matcher = line[0:,~newline]   > combine
  
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  [{'bob': '12345', 'andrew': '3333253'}]

LEPL can be extended in several ways:

* You can define and call functions to process results, as shown above.

* You can write your own matchers (see the LEPL source for examples; they
  should inherit from ``BaseMatch`` to take full advantage of the operator
  syntax).

* You can even change the definition of operators (``&``, ``/`` etc).


