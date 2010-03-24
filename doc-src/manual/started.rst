
.. _getting-started:

Getting Started
===============

This chapter works through a simple example using Lepl.  For a longer, more
detailed example, see the :ref:`Tutorial <tutorial>`.  There are also some
additional :ref:`examples` at the end of this manual.

After reading this chapter you should have a better understanding of what
matchers and parsers do, and how they can be constructed.

.. index:: example, get_parse(), parse()

First Example
-------------

The structure of a piece of text is described in Lepl using *matchers*.  A
simple matcher might recognise a letter, digit or space.  More complex
matchers are built from these to recognise words, equations, etc.

One a matcher has been built up in this way it can be used to create a
*parser* to process text.

Internally, when the parser is used to analyse some text, it passes the string
to the matchers that were used as "building blocks".  These break the text
into pieces that are then assembled into the final result.

The assembly of the matched text can include extra processing that modifies
the data however you like.

So we describe a structure (called a *grammar*) using matchers then use those
matchers to break text into pieces that match that structure.  Finally, we
process and assemble those pieces to give a final result.

An example will make this clearer.  Imagine that we are given a username and a
phone number, separated by a comma, and we want to split that into the two
values::

  >>> from lepl import *
  
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> matcher = name / ',' / phone  > make_dict
  
  >>> parser = matcher.get_parse()
  >>> parser('andrew, 3333253')
  [{'phone': '3333253', 'name': 'andrew'}]

The main body of this program (after the import statements) defines the
matcher.  Then the parser is constructed, and, finally, the string ``'andrew,
3333253'`` parsed to create a ``dict``.

We can shorten the last two lines to::

  >>> matcher.parse('andrew, 3333253')
  [{'phone': '3333253', 'name': 'andrew'}]

(a parser is still created, inside the matcher).

There's a lot going on here, some of which I will explain in later sections,
but the most important thing to notice is that ``matcher`` was constructed
from two simpler matchers [#]_ --- `Word()
<api/redirect.html#lepl.matchers.derived.Word>`_ and `Integer()
<api/redirect.html#lepl.matchers.derived.Integer>`_ [#]_.  It is those two
matchers that identify the values 'andrew' (a word) and '3333253' (an
integer).

.. [#] In fact there are probably a dozen or so matchers involved here: the
       ``,`` is converted into a matcher that matches commas; the ``/``
       construct new matchers from the matchers on either side with matchers
       for spaces between them; most of the matchers I've just mentioned are
       actually implemented using other matchers for single characters, or to
       repeat values, or to join characters found together into a string...
       Fortunately you don't need to know all this just to *use* a matcher.

.. [#] Matcher names are linked to the API documentation which contains more
       detail.

.. index:: matchers, Word(), Integer(), And(), &, match()

Matchers
--------

Internally, all matchers work in the same way: they take a *stream* of input
and produce some results and a new stream as output.  But, because a matcher
may find more than one match, it does not return the results and stream
directly.  Instead, it returns a *generator*.

Generators are a fairly new part of Python, rather like lists.  All you need
to know to use them is that, to read the value, you use the function
``next()``.

We can see how this works with the simple generators `Word()
<api/redirect.html#lepl.matchers.derived.Word>`_ by calling the
``matcher.match() method::

  >>> matcher = Word()
  >>> matcher.config.no_full_first_match()
  >>> next(matcher.match('hello world') )
  (['hello'], 'hello world'[5:])

You can see the result and the remaining stream.  We needed to call
`.config.no_full_first_match()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_full_first_match>`_
otherwise we would have triggered an error due to incomplete matching (in case
you are wondering, that error is from the parser that was automatically
created when we called ``match()``; individual matchers don't check for a
complete parse).

We can join together matchers with `And()
<api/redirect.html#lepl.matchers.combine.And>`_::

  >>> next( And(Word(), Space(), Integer()).match('hello 123') )
  (['hello', ' ', '123'], ''[0:])

which can also be written as::

  >>> next( (Word() & Space() & Integer()).match('hello 123') )
  (['hello', ' ', '123'], ''[0:])

or even::

  >>> next( (Word() / Integer()).match('hello 123') )
  (['hello', ' ', '123'], ''[0:])

because ``&`` is shorthand for `And()
<api/redirect.html#lepl.matchers.combine.And>`_, while ``/`` is similar, but
allows optional spaces.

We can get an idea of how Lepl works internally by looking at the output
above.  In particular, note that results are contained in a list and the
returned stream starts after the results.  Putting the results in a list
allows a matcher to return more than one result (or none at all) and the new
stream can be used by another matcher to continue the work on the rest of the
input data.

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
  ([('name', 'andrew')], ''[0:])

  >>> next( (Integer() > 'phone').match('3333253') )
  ([('phone', '3333253')], ''[0:])

This makes `make_dict <api/redirect.html#lepl.support.node.make_dict>`_ easier
to understand.  Python's standard ``dict()`` will construct a dictionary from
named pairs::

  >>> dict([('name', 'andrew'), ('phone', '3333253')])
  {'phone': '3333253', 'name': 'andrew'}

And the results from ``name / ',' / phone`` include named pairs::

  >>> next( (name / ',' / phone).match('andrew, 3333253') )
  ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], ''[0:])

Now we know that ``>`` passes results to a function, so it looks like
`make_dict <api/redirect.html#lepl.make_dict>`_ is almost identical to the
Python builtin ``dict``.  In fact, the only difference is that it strips out
results that are not named pairs (in this case, the comma and space).

.. index:: repetition, [], ~, Drop()
.. _repetition:

Repetition
----------

Next we will extend the matcher so that we can process a list of several
usernames and phone numbers::

  >>> spaces  = Space()[0:]
  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> line    = name / ',' / phone  > make_dict
  >>> newline = spaces & Newline() & spaces
  >>> matcher = line[0:,~newline]

  >>> matcher.parse('andrew, 3333253\n bob, 12345')
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
also have been written as `Drop(newline) <api/redirect.html#lepl.matchers.derived.Drop>`_ --- another example of making a
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
  
  >>> matcher.parse('andrew, 3333253\n bob, 12345')
  [{'bob': '12345', 'andrew': '3333253'}]

Summary and Going Further
-------------------------

Lepl can be extended in several ways:

* You can contruct new matchers by combining existing ones.  You will do this
  all the time using Lepl --- almost every line in the examples above defines
  a new matcher.

* You can define and call functions to process results (using ``>``).  This is
  quite common, too, and there's an example just above.

* TODO - UPDATE You can write your own matchers (see the Lepl source for
  examples; they should inherit from `BaseMatcher
  <api/redirect.html#lepl.functions.BaseMatcher>`_ to take full advantage of
  the operator syntax).  Hopefully this is not often needed.  If you think you
  do need to write a new matcher, feel free to discuss it on the `mailing list
  <http://groups.google.com/group/lepl>`_ --- someone might have already
  written something, or it's possible I will think it worth adding to Lepl
  myself.

* You can also change the definition of operators (``&``, ``/`` etc; see
  :ref:`replacement`).  Again, this is unusual to do directly, but forms the
  basis for :ref:`separators`.

