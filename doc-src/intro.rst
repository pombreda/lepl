
.. _introduction:

Introduction
============

Below I will work through a simple example using LEPL.

The `final section`_ is a technical description of the library.  Understanding
how LEPL works will help you use it more efficiently, but detailed knowledge
is not necessary for simple use.


Matchers
--------

.. index:: matchers

The structure of a piece of text is described in LEPL using *matchers*.
Simple matchers might recognise a letter, digit or space.  More complex
matchers can be built from these, to recognise words, equations, etc.

One a matcher has been built up in this way it can be used to process text.
Internally, this means that the text is given to the original, simple matchers
that were used as "building blocks".  These break the text into pieces in a
way that reflects the matcher's structure.

So we describe a structure (or grammar) using matchers then use those
matchers to break text into pieces that match that structure.  This process is
called parsing.

An example will make this clearer.  Imagine that we are given a username and
phone numbers, separated by a comma, and we want to split that into the two
values.

  >>> from lepl.match import *
  >>> from lepl.node import make_dict

  >>> matcher = (Word() > 'name') / ',' / (Integer() > 'phone') > make_dict
  >>> matcher.parse_string('andrew, 3333253')[0]
  {'phone': '3333253', 'name': 'andrew'}

The first line (``matcher = ...``) defines the matcher.  The second line
(``matcher.parse_string...``) uses it to split the text "andrew, 3333253" into
a name and a phone number.

There's a lot going on here, some of which I will explain in later sections,
but the most important thing to notice is that ``matcher`` was constructed
from ``Word()`` and ``Integer()``, and that these two matchers identified the
values 'andrew' and '3333253'.


More Detail
-----------

The example above contains more matchers than just ``Word()`` and
``Integer()``.  The ``','`` string is converted into a matcher that
recognises a comma and the ``/`` is converted into a matcher that matches
optional spaces.

We can see these extra matchers in action if we don't send the output to
``make_dict``:

  >>> matcher = (Word() > 'name') / ',' / (UnsignedInteger() > 'phone')
  >>> matcher.parse_string('andrew, 3333253')
  [('name', 'andrew'), ',', ' ', ('phone', '3333253')]

What does this tell us?

First, we can see the comma and space that were identified by the extra
matchers.  Only one of the ``/`` identified any space, but that's OK, because
they are optional.  If we had wanted to *require* space then we could have
used ``//``, but that would have failed to work because there is no space
between "andrew" and "," in our input text.

Second, it's probably obvious that ``Word() > 'name'`` takes the output from
``Word()`` and creates the tuple ``('name', 'andrew')``.  This helps explain
how ``make_dict`` works (the constructor for an ordinary Python dict can take
a list of tuples like that).

Third, you may have noticed that I dropped ``[0]`` from the first example,
and that parsing returns a list of results (in the first example the list
contained just a single dict, so I used ``[0]`` to simplify the output).


Repetition
----------

.. index:: repetition, [], ~

Now let's extend the matcher so that we can process a list of several
usernames and phone numbers.

  >>> spaces  = Space()[0:]
  >>> name    = Word()                       > 'name'
  >>> phone   = Integer()                    > 'phone'
  >>> line    = spaces / name / ',' / phone  > make_dict
  >>> newline = spaces & Newline()
  >>> matcher = line[0:,~newline]
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  [{'phone': '3333253', 'name': 'andrew'}, {'phone': '12345', 'name': 'bob'}]

Since this is becoming increasingly complex I've changed the layout to one
that I personally find useful (it is similar to the "BNF grammars" that some
textbooks used).

The most important change here is the introduction of repetition via
``line[0:,~newline]``.  Before I describe that, though, I should explain the
``~`` that precedes ``newline``.  This modifies the matcher so that it does
not return any result.  Until now we have been relying on ``make_dict`` to
discard spaces and commas that we are not interested in (``make_dict`` will
ignore anything that is not a pair of values starting with a string), but
without the ``~`` we would have had the results of matching the newline in our
final result (because they do not go through ``make_dict``).

(One obscure exception for experts --- when using lookahead, ``~`` inverts the
logic, indicating that the lookahead should succeed when the embedded match
fails).

OK, so how do we describe repetition?  As shown above, we use ``[]`` which can
contain three different kinds of entry, separated by commas:

#. **Start, stop and step values.** These are written ``[start:stop:step]``
   and indicate the number of times to repeat.  If *start* is omitted, it is
   assumed to be 0.  If *stop* is omitted it is assumed to be "as big as
   possible".  If *step* is omitted it is assumed to be -1 (this may seem odd,
   but means that the matching is "greedy" by default).

   For example, ``[0:1]`` means "none or one", while ``[:]`` means "as many as
   possible, trying the largest value possible first, and then smaller ones"
   (check the default values above).

   If you want to repeat the minimum number of times necessary then use a
   *step* of 1 --- that will start with small matches and increase as
   necessary.

#. **An ellipsis (...).** If the ``[]`` contains an ellipsis then the results
   of matching are joined together with ``+``.  This is useful when matching
   characters that should join up to form a single word.  For example:

   >>> Digit()[1:].parse_string('123')
   ['1', '2', '3']
   >>> Digit()[1:,...].parse_string('123')
   ['123']

#. **A matcher.** If a matcher is given it will be used between the list
   elements.  This is useful for matching the commas or newlines (as above)
   that separate list items.  As is common in LEPL, a string can also be
   given, and will automatically be changed into a literal matcher (ie one
   that matches the string, like ``','`` earlier).

With that it should be clear that ``Space()[0:]`` matches any spaces.


Technical Summary
-----------------

.. _final section:
.. index:: recursive descent, generators, stack, parser combinators

In the sections above I have tried to explain LEPL without mentioning any
"theoretical" details.  Now I am going to jump ahead and give a short,
technical description that requires a lot more background knowledge.  The aim
here is to show experts how the system is implemented; you do not need to
understand this section to use LEPL.

LEPL is, at heart, a recursive descent parser.  It owes much to standard
parser combinator libraries in functional languages.  For example, each
matcher takes a stream as an argument and, on success, returns a tuple
containing a list of matches and a new stream.  

However, LEPL also exploits Python in two ways.  First, it overloads operators
to provide a large helping of syntactic sugar (operators simply apply more
combinators, so ``a | b`` is equivalent to ``Or(a, b)``).  Second, generators
are used to manage backtracking.

Consistent use of generators means that the entire parser can backtrack
(typically recursive descent parsing restricts backtracking to ``Or(...)``).
It also reduces the use of the C stack (naturally replacing recursion with
iteration) and allows the environmental cost of backtracking to be managed
(generators can be tracked and closed, effectively reclaiming resources on the
"stack"; the same mechanism can implement "cut").
