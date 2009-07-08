
.. _getting-started:

Getting Started
===============

This chapter works through a simple example using LEPL.

After reading this chapter you should have a better understanding of what
matchers and parsers do, and how they can be constructed.


.. index:: example

First Example
-------------

The structure of a piece of text is described in LEPL using *matchers*.  A
simple matcher might recognise a letter, digit or space.  More complex
matchers are built from these to recognise words, equations, etc.

One a matcher has been built up in this way it can be used to create a
*parser* to process text.

Internally, when the parser is used to analyse some text, it passes the string
to the matchers that were used as "building blocks".  These break the text
into pieces that are then assembled into the final result.

The assembly of the matched text can include extra processing that modifies
the data however you like.

So, ignoring the parser for a moment, we describe a structure (called a
*grammar*) using matchers then use those matchers to break text into pieces
that match that structure.  Finally, we process and assemble those pieces to
give a final result.

An example will make this clearer.  Imagine that we are given a username and a
phone number, separated by a comma, and we want to split that into the two
values::

  >>> from lepl import *
  
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> matcher = name / ',' / phone  > make_dict
  
  >>> parser = matcher.string_parser()
  >>> parser('andrew, 3333253')
  [{'phone': '3333253', 'name': 'andrew'}]

The main body of this program (after the import statements) defines the
matcher.  The last line uses that to make a ``dict`` that contains the values
from the string ``'andrew, 3333253'``.

There's a lot going on here, some of which I will explain in later sections,
but the most important thing to notice is that ``matcher`` was constructed
from two simpler matchers [#]_ --- `Word()
<api/redirect.html#lepl.Word>`_ and `Integer()
<api/redirect.html#lepl.match.Integer>`_ [#]_.  It is those two matchers
that identify the values 'andrew' (a word) and '3333253' (an integer).

.. [#] In fact there are probably a dozen or so matchers involved here: the
       ``,`` is converted into a matcher that matches commas; the ``/``
       construct new matchers from the matchers on either side with matchers
       for spaces between them; most of the matchers I've just mentioned are
       actually implemented using other matchers for single characters, or to
       repeat values, or to join characters found together into a string...
       Fortunately you don't need to know all this just to *use* a matcher.

.. [#] Matcher names are linked to the API documentation which contains more
       detail.


.. index:: matchers, Word(), Integer(), match(), parse_string()

Matchers
--------

All matchers work in the same way: they take a *stream* of input and produce
some results and a new stream as output (for now we use strings as simple
streams).  But, because a matcher may find more than one match, it does not
return the results and stream directly.  Instead, it returns a *generator*.

Generators are a fairly new part of Python, rather like lists.  All you need
to know to use them is that, to read the value, you use the function
``next()``.

We can see how this works with the simple generators `Word()
<api/redirect.html#lepl.Word>`_ and `Integer()
<api/redirect.html#lepl.Integer>`_::

  >>> next( Word().match('hello world') )
  (['hello'], ' world')
  
  >>> next( Integer().match('123 four five') )
  (['123'], ' four five')

Hopefully you can see the result and the remaining stream in both cases.

We can make a more complicated matcher from these by joining them together
with `And() <api/redirect.html#lepl.And>`_::

  >>> next( And(Word(), Space(), Integer()).match('hello 123') )
  (['hello', ' ', '123'], '')

which can also be written as::

  >>> next( (Word() & Space() & Integer()).match('hello 123') )
  (['hello', ' ', '123'], '')

or even::

  >>> next( (Word() / Integer()).match('hello 123') )
  (['hello', ' ', '123'], '')

because ``&`` is shorthand for `And() <api/redirect.html#lepl.And>`_, while
``/`` is similar, but allows optional spaces.

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


.. index:: /, >, make_dict()

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

  >>> next( (Word() > 'name').match('andrew') )
  ([('name', 'andrew')], '')

  >>> next( (Integer() > 'phone').match('3333253') )
  ([('phone', '3333253')], '')

This makes `make_dict <api/redirect.html#lepl.node.make_dict>`_ easier to
understand.  Python's standard ``dict()`` will construct a dictionary from
named pairs::

  >>> dict([('name', 'andrew'), ('phone', '3333253')])
  {'phone': '3333253', 'name': 'andrew'}

And the results from ``name / ',' / phone`` include named pairs::

  >>> next( (name / ',' / phone).match('andrew, 3333253') )
  ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], '')

Now we know that ``>`` passes results to a function, so it looks like
`make_dict <api/redirect.html#lepl.make_dict>`_ is almost identical to
``dict``.  In fact, the only difference is that it strips out results that are
not named pairs (in this case, the comma and space).


.. index:: repetition, [], ~, Drop()
.. _repetition:

Repetition
----------

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
missing values is 0 and "as many as possible").

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


Single Dictionary
-----------------

The repeated matcher above returns a list of dicts.  But what we really want
is a single dict that associates each username with a telephone number.

We can write our own function to do this, then call it with ``>``::


  >>> def combine(results):
  ...     all = {}
  ...     for result in results:
  ...         all[result['name']] = result['phone']
  ...     return all
  
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
  should inherit from `BaseMatcher
  <api/redirect.html#lepl.functions.BaseMatcher>`_ to take full advantage of
  the operator syntax).

* You can even change the definition of operators (``&``, ``/`` etc; see
  :ref:`replacement`).


