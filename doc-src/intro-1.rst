
Part 1 - Basic Matching
=======================

.. index:: parsing

What is Parsing?
----------------

When we talk about "parsing some data" we generally have some data (often in
the form of text) and a description of the way that data is organised, and we
want to bring those two together so that we can break the data into known
pieces.

For example, we might want to write a program that lists the prices of various
items on Amazon's web site.  We can get the web page for each item (maybe
using Python's `HTTP client
<http://docs.python.org/3.0/library/http.client.html>`_), and we know that all
the pages have the same structure --- but how do we extract the price?  This is
where the parser comes in.  We give the parser a description of the page
structure, together with a web page, and it will return the price as a result.

That example is a little ambitious for a simple introduction.  Here we will
look at a simpler problem.  We will write a program that can take a simple
mathematical expression, like "1+2*3", understand the structure, and work out
the answer.  For example, when given "2+2" we want the result "4".

.. index:: SignedFloat(), import

Recognising a Number
--------------------

LEPL has built--in support for parsing a number.  We can see this by typing
the following at a Python prompt::

  >>> from lepl import *
  >>> SignedFloat().parse('123')
  ['123']

What is happening here?

The first line imports the contents of LEPL's main module.  LEPL is structured
as a collection of different packages, but the most important functions and
classes are collected together in the ``lepl`` module --- for most work this
is all you will need.

In the rest of the examples below I will assume that you have already imported
this module.

The second line creates a matcher --- `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ --- and uses it to
match the text "123".  The result is a list that contains the text "123".

In other words, `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ looked at "123" and recognised that it was a
number.

What would happen if we gave `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ something that wasn't a number?
We can try it and see::

  >>> SignedFloat().parse('cabbage')

Nothing happens.  More exactly, the result was ``None``, which Python hides.
We can see this by adding a ``print()``::

   >>> print(SignedFloat().parse('cabbage'))
   None

Which seems clear enough --- "cabbage" is not a number.

But things are often not as simple as they first appear.  For example: why is
"123" a single number, and not three different numbers joined together?

.. index:: ambiguity

Ambiguity
---------

In fact, LEPL doesn't know that "123" is a single number.  Because of the way
`SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ is defined internally, it gives the `longest` number it can
find.  But that doesn't mean it is the only possibility.  We can see all the
different possibilities by calling ``match()`` instead of ``parse()``:

  >>> SignedFloat().match('123')
  <generator object trampoline at 0x7fcaba6141e0>

That will not seem very useful unless you already understand Python's
`generators <http://docs.python.org/3.0/glossary.html#term-generator>`_.  A
generator is something like a list that hasn't been built yet.  We can use it
in a ``for`` loop just like a list, for example::

  >>> for result in SignedFloat().match('123'):
  ...   print(result)
  ...
  (['123'], '')
  (['12'], '3')
  (['1'], '23')

Or we can create a list directly:

  >>> list(SignedFloat().match('123'))
  [(['123'], ''), (['12'], '3'), (['1'], '23')]

Either way we can see that `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ is giving us a choice of
different results.  It can match the number "123", or the number "12", or the
number "1".

Remaining Text
--------------

You may have noticed that the results from ``match()`` above differ from
``parse()`` in two ways.  First, of course, we have a variety of different
matches.  But second, we also get "the rest of the string".  For example, the
result ``(['12'], '3')`` contains both the match ``['12']`` and the remaining
text ``'3'``.

This extra information --- the remaining text --- isn't shown by ``parse()``,
which is a simple way of calling a matcher to get a single answer.  But it is
critical to the way LEPL works internally.

In the next few sections we'll be combining matchers to parse more complicated
text.  When two matchers are combined the second one is given the remaining
text that we've seen above.

Don't worry if this doesn't make much sense yet --- it will become clearer
below.

.. index:: &, And(), Literal()

Matching a Sum
--------------

So how do we extend matching a number to match a sum?

Here's the answer::

  >>> add = SignedFloat() & Literal('+') & SignedFloat()
  >>> add.parse('12+30')
  ['12', '+', '30']

In LEPL all that is necessary to join matchers together is ``&``.  This is
shorthand for::

  >>> add = And(SignedFloat(), Literal('+'), SignedFloat())
  >>> add.parse('12+30')
  ['12', '+', '30']

which is sometimes useful.

The parser above also used `Literal() <api/redirect.html#lepl.matchers.Literal>`_.  Like its name suggests, this
matches whatever value it is given::

  >>> Literal('hello').parse('hello world')
  ['hello']
  >>> list(Literal('hello').match('hello world'))
  [(['hello'], ' world')]

In the final use of `Literal() <api/redirect.html#lepl.matchers.Literal>`_, just above, we can see that ``match()``
also returns the remaining string, just as I described earlier.

Perhaps now it is clearer why the remaining text is important?  Using ``&``
tells LEPL to give that remaining text to the next matcher.  So when "12+34"
is given to the `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ it matches "12" and leaves "+34"; the "+34"
is then given to ``Literal('+')``, which matches "+" and leaves "34"; the "34"
is then given to the second `SignedFloat() <api/redirect.html#lepl.matchers.SignedFloat>`_ which completes the task.

Implicit Literals
-----------------

Often we can just use an ordinary string, instead of `Literal() <api/redirect.html#lepl.matchers.Literal>`_, and LEPL
will still understand what we mean::

  >>> add = SignedFloat() & '+' & SignedFloat()
  >>> add.parse('12+30')
  ['12', '+', '30']

Unfortunately this doesn't always work, and predicting exactly when it's going
to fail can be difficult (technically, the string must be an argument to a
matcher's overloaded operator or constructor).  So if you get a strange error
on a line with strings, try adding a `Literal() <api/redirect.html#lepl.matchers.Literal>`_ around the text --- after a
while you'll get a feeling for when it is needed, and when not.

Anyway, we still haven't added those numbers.  To do that we need to do
something with the results.

.. index:: ~, Drop()

Ignoring Values
---------------

To simplify adding the two values, we need to get rid of the "+" (please just
trust me on this; it will be clear why in a few more sections).

It is quite common when parsing data that we do not need to see all the values
we have matched.  That doesn't mean that it isn't important to do the match
--- in this case we need to check that there is a "+" between the two numbers
to be sure that we are doing the right thing by adding them --- but once we
have done that check, we don't actually want the "+" to be returned as a
result.

We can indicate that a match should be ignored by preceding the matcher with
``~``::

  >>> add = SignedFloat() & ~Literal('+') & SignedFloat()
  >>> add.parse('12+30')
  ['12', '30']

Just like ``&``, this is shorthand for another matcher, in this case
`Drop() <api/redirect.html#lepl.matchers.Drop>`_::

  >>> add = SignedFloat() & Drop(Literal('+')) & SignedFloat()
  >>> add.parse('12+30')
  ['12', '30']

.. index:: >>

Creating Numbers
----------------

Our result above, ``['12', '30']``, is a list of numbers.  But the numbers are
still strings.  We need to convert them to floats before we can add them.  To
see what I mean, consider the two examples below::

  >>> 12 + 30
  42
  >>> '12' + '30'
  '1230'

We want the first case, not the second.

To do this we can define a new matcher, which takes the output from
``SignedFloat`` (a list of strings) and passes each value in the list to the
Python built--in function, ``float()``::

  >>> number = SignedFloat() >> float

We can test this by calling ``parse()``::

  >>> number = SignedFloat() >> float
  >>> number.parse('12')
  [12.0]

So now we can re-define ``add`` to use this matcher instead::

  >>> number = SignedFloat() >> float
  >>> add = number & ~Literal('+') & number
  >>> add.parse('12+30')
  [12.0, 30.0]

(I have repeated the definition of number here and in the previous example so
that each is complete by itself).

Note that, because ``>>`` works on each result in turn, we could have written
this in a different, but equivalent way::

  >>> add = SignedFloat() & Drop(Literal('+')) & SignedFloat() >> float
  >>> add.parse('12+30')
  ['12', 30.0]

But as a general rule it is better to process results as soon as possible.
This usually keeps the parser simpler.

Adding Values
-------------

Now that we have just the two numbers, we can add them.  How?  Well, we have a
list of numbers that we need to add, and Python has a function that does
exactly this, called ``sum()``::

  >>> sum([1,2,3])
  6

So we can send our results to that function::

  >>> number = SignedFloat() >> float
  >>> add = number & ~Literal('+') & number > sum
  >>> add.parse('12+30')
  [42.0]

which gives the answer we wanted!

The difference between ``>`` and ``>>`` is quite subtle, but important: ``>``
sends the entire list of results to a function as a single argument (so the
function must take a list of values), while ``>>`` sends each result
separately (so the function must take a single value).

We have come a long way --- from nothing to a parser that can add two numbers.
In the next section we will make this more robust, allowing us to have spaces
in the expression.

Summary
-------

What have we learnt so far?

* Parsing is all about recognising structure (eg. mathematical expressions).

* Once we have recognised structure we can process it (eg. adding numbers
  together).

* To use LEPL we must first use import the lepl module: ``from lepl import
  *``.

* LEPL builds up a parser using matchers.

* Matchers can return one value (with ``parse()``) or all possible values
  (with ``match()``).

* We can join matchers together with ``&`` or ``And()``.

* We can ignore the results of a matcher with ``~`` or `Drop() <api/redirect.html#lepl.matchers.Drop>`_.

* We can process each value in a list of results with ``>>``.

* We can process the list of results (as a complete list) with ``>``.
