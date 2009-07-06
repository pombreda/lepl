
Part 2 - Handling Spaces, Repetition
====================================

Recap
-----

In the previous chapter we defined a parser that could identify the different
parts of an addition, separate out the numbers, and return their sum::

  >>> from lepl import *
  >>> number = SignedFloat() >> float
  >>> add = number & ~Literal('+') & number > sum
  >>> add.parse('12+30')
  [42.0]

(remember that I will not repeat the import statement in the examples below).

An obvious problem with this parser is that it does not handle spaces::

  >>> print(add.parse('12 + 30'))
  None

where I've used the same trick as earlier to show that ``None`` is returned.

So in this section we'll look at the various ways we can handle spaces (and
learn more about other features of LEPL along the way).

.. index:: Space()

Explicit Spaces
---------------

The simplest way to handle spaces is to add them to the parser.  LEPL includes
the `Space() <api/redirect.html#lepl.functions.Space>`_ matcher which recognises a single space::

  >>> number = SignedFloat() >> float
  >>> add = number & ~Space() & ~Literal('+') & ~Space() & number > sum
  >>> add.parse('12 + 30')
  [42.0]

But now our parser won't work without spaces!
::

  >>> print(add.parse('12+30'))
  None

.. index:: Star()

The Star Matcher
----------------

To fix the problem described above, where we can match only a single space, we
would like to match any number of spaces.  There are various ways of doing
this.  If you are used to using regular expressions you may realise that this
is what the "*" symbol does.  And in LEPL we have something similar.

The `Star() <api/redirect.html#lepl.functions.Star>`_ matcher repeats its argument as may times as necessary
(including none at all).  This is what we need for our spaces::

  >>> number = SignedFloat() >> float
  >>> spaces = ~Star(Space())
  >>> add = number & spaces & ~Literal('+') & spaces & number > sum
  >>> add.parse('12 + 30')
  [42.0]
  >>> add.parse('12+30')
  [42.0]
  >>> add.parse('12+     30')
  [42.0]

Note that I included a ``~`` in the definition of ``spaces`` so that they are
`dropped` from the results.

.. index:: [], repetition

Repetition
----------

As well as `Star() <api/redirect.html#lepl.functions.Star>`_, LEPL supports a more general way of specifying
repetitions.  This uses Python's array syntax, which looks a bit odd at first,
but turns out to be a really neat, compact, powerful way of describing what we
want.

The easiest way to show how this works is with some examples.

First, here's how we specify that exactly three things are matched:

  >>> a = Literal('a')
  >>> a[3].parse('aaaaa')
  ['a', 'a', 'a']

and here's how we specify that 2 to 4 should be matched:

  >>> a[2:4].parse('aaaaa')
  ['a', 'a', 'a', 'a']
  >>> list(a[2:4].match('aaaaa'))
  [(['a', 'a', 'a', 'a'], 'a'), (['a', 'a', 'a'], 'aa'), (['a', 'a'], 'aaa')]

As we saw earlier ``match()`` returns a generator (which we convert to a list)
that contains all the different possible combinations: 2, 3 and 4 letters
(along with the remaining text in each case), while ``parse()`` returns just
the first result (repetition with ``[]`` returns the largest number of
matches first).

If we give a range with a missing start value then the minimum number of
matches is zero:

  >>> list(a[0:1].match('aaaaa'))
  [(['a'], 'aaaa'), ([], 'aaaaa')]

so here we have 0 or 1 matches (zero matches means we get an empty list of
results --- that's not the same as failing to match, which would return
``None``).

And if the end value is missing as many as possible will be matched:

  >>> list(a[4:].match('aaaaa'))
  [(['a', 'a', 'a', 'a', 'a'], ''), (['a', 'a', 'a', 'a'], 'a')]

Finally, we can get the shortest number of matches first by specifying an
array index "step" of 'b' (short for "breadth--first search"; the default is
'd' for "depth--first")::

  >>> list(a[2:4:'b'].match('aaaaa'))
  [(['a', 'a'], 'aaa'), (['a', 'a', 'a'], 'aa'), (['a', 'a', 'a', 'a'], 'a')]

Putting all that together, `Star() <api/redirect.html#lepl.functions.Star>`_ is the same as ``[:]`` (which starts at
zero, takes as many as possible, and returns the longest match first).

So we can write our parser like this::

  >>> number = SignedFloat() >> float
  >>> spaces = ~Space()[:]
  >>> add = number & spaces & ~Literal('+') & spaces & number > sum
  >>> add.parse('12 + 30')
  [42.0]
  >>> add.parse('12+30')
  [42.0]
  >>> add.parse('12+     30')
  [42.0]

That's perhaps not as clear as using `Star() <api/redirect.html#lepl.functions.Star>`_, but personally I prefer this
approach so I'll continue to use it below.

.. index:: ...

More Repetition
---------------

While we are looking at ``[]`` I should quickly explain two extra features
which are often useful.

First, including ``...`` will join together the results::

  >>> a[3].parse('aaaaa')
  ['a', 'a', 'a']
  >>> a[3,...].parse('aaaaa')
  ['aaa']

Second, we can specify a "separator" that is useful when matching lists.  This
is used to match "in-between" whatever we are repeating.  For example, we
might have a sequence of "a"s separated by "x"s, which we want to ignore::

  >>> a[3,Drop('x')].parse('axaxa')
  ['a', 'a', 'a']

.. index:: Separator()

Separators
----------

Enough about repetition; let's return to our main example.

The solution above works fine, but it gets a bit tedious adding ``spaces``
everywhere.  It would be much easier if we could just say that they should be
added wherever there is a ``&``.  And, of course, we can do that in LEPL::

  >>> number = SignedFloat() >> float
  >>> spaces = ~Space()[:]
  >>> with Separator(spaces):
  ...   add = number & ~Literal('+') & number > sum
  ...
  >>> add.parse('12 + 30')
  [42.0]
  >>> add.parse('12+30')
  [42.0]

Which works as before, but can save some typing in longer programs.

`Separator() <api/redirect.html#lepl.operators.Separator>`_ is implemented as a redefinition of the matchers used by ``&``
and ``[]`` to include spaces.  The matcher associated with any operator can be
redefined in LEPL, but doing so is pretty advanced and outside the scope of
this tutorial.

Because `Separator() <api/redirect.html#lepl.operators.Separator>`_ changes everything "inside" the "with" it's usually
best to define matchers that `don't` need spaces beforehand.

.. note::

   Separator() only modifies ``&`` and ``[]``, which can lead to (at least)
   two surprising results.

   First, there's nothing added before or after any pattern that's defined.
   For that, you still need to explicitly add spaces as described earlier.
   `Separator() <api/redirect.html#lepl.operators.Separator>`_ only adds
   spaces `between` items joined with ``&``.

   Second, if you specify `at least one` space (rather than `zero or more`)
   then `every` ``&`` in the separator's context `must` have a space.  This
   can be surprising if you have, for example, ``& Eos()`` because it means
   that there `must` be a space before the end of the stream.

.. index:: regular expressions

Regular Expressions
-------------------

I'm going to take a small diversion now to discuss regular expressions.  Once
I've finished I'll return to the issue of spaces with a different approach.

Regular expressions are like "mini-parsers".  They are used in a variety of
languages, and Python has a `module
<http://docs.python.org/3.0/library/re.html>`_ that supports them.  I don't
have space here (or the time and energy) to explain them in detail, but the
basic idea is that you can write a string (an "expression") that describes a
sequence of letters to be matched.  This expression can contain things like
"." which matches any letter, or "[a-m]" which matches any letter between "a"
and "m", for example.

So regular expressions are very like a parser.  But a parser can usually
(exact details depend on the language and parser) describe more complicated
structures and tends to be easier to use for "big" problems.

That doesn't mean that regular expressions don't play a part in LEPL.  In
fact, LEPL supports three kinds of regular expressions, and I will describe
these below.  But please note that all the options below have limitations ---
LEPL is a parser in its own right and does not need powerful regular
expressions.

.. index:: Regexp()

Regexp()
--------

The ``Regexp()`` matcher calls the Python regular expression library.  So if
you are experienced at using that you may find it useful.

However, there are some limitations.  First, the interface exposed by LEPL
doesn't include all Python's options (it would make things too complicated and
LEPL has other ways of doing things --- sorry!).

Second, the expression is only matched against the "current line".  Exactly
what the "current line" is depends on some internal details (sorry again), but
you should work on the assumption that the regular expression will only
receive data up to the next newline character.

The reason for this second limitation is that LEPL is quite careful about how
it manages memory.  In theory it should be possible to process huge amounts of
text, because only a section of the document is held in memory at any one
time.  Unfortunately that doesn't play well with Python's regular expressions,
which expect all the data to be in a single string.

Here are some examples showing what is possible::

  >>> Regexp('a+').parse('aaabb')
  ['aaa']
  >>> Regexp(r'\w+').parse('abc def')
  ['abc']
  >>> Regexp('a*(b*)c*(d*)e*').parse('abbcccddddeeeeee')
  ['bb', 'dddd']

The last example above shows how groups can be used to define results.

.. index:: DfaRegexp()

DfaRegexp()
-----------

The ``DfaRegexp`` calls LEPL's own regular expression library.  It understands
simple regular expressions and is not limited in the amount of data it can
match.  However, it does not support grouping, references, etc.

  >>> DfaRegexp('a*b').parse('aabbcc')
  ['aab']

.. index:: NfaRegexp()

NfaRegexp()
-----------

This is implemented by LEPL's own regular expression library and, like
``DfaRegexp()``, is not limited in the amount of data it can access.

``NfaRegexp()`` differs from "normal" regular expressions in that it can
return multiple matches (usually a regular expression returns only the
"longest match")::

  >>> list(NfaRegexp('a*').match('aaa'))
  [(['aaa'], ''), (['aa'], 'a'), (['a'], 'aa'), ([''], 'aaa')]
  >>> list(DfaRegexp('a*').match('aaa'))
  [(['aaa'], '')]
  >>> list(Regexp('a*').match('aaa'))
  [(['aaa'], '')]

.. index:: tokens, Token()

Tokens (First Attempt)
----------------------

Now that we have discussed regular expressions I can explain the final
alternative for handling spaces.

This approach uses regular expressions to classify the input into different
"tokens".  It then lets us match both the token type and, optionally, the
token contents.

By itself, this doesn't make handling spaces any simpler, but we can also tell
LEPL to ignore certain values.  So if we define tokens for the different
"words" we will need, we can then tell LEPL to discard any spaces that occur
between (in fact, by default, spaces are skipped, so we don't need to actually
say that below).

For more detailed information on tokens, see :ref:`lexer` in the manual (and
particularly, :ref:`lexer_process`).


First, let's define the tokens we will match.  We don't have to be very
precise here because we can add more conditions later --- it's enough to
identify the basic types of input.  For our parser these will be values and
symbols::

  >>> value = Token(SignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')

I said that we defined tokens with regular expressions, but the definition of
``value`` above seems to use the matcher `SignedFloat() <api/redirect.html#lepl.functions.SignedFloat>`_.  This is because
LEPL can automatically convert some matchers into regular expressions, saving
us the work (it really does convert them, piece by piece, so it is not limited
to the built--in matchers, but it is limited by how the matcher is constructed
-- it cannot see "inside" arbitrary function calls, for example, so any
matcher that includes ``>`` or ``>>`` won't work).

The second token, defined with the regular expression "[^0-9a-zA-Z \\t\\r\\n]"
means "any single character that is not a digit, letter, or space".  Obviously
we will need to add extra conditions for matching "+" and, later, "*", "-",
etc.

With those tokens we can now try to rewrite our parser::

  >>> number = value >> float
  >>> add = number & ~symbol('+') & number > sum
  >>> print(add.parse('12+30', config=Configuration.tokens()))
  None

Ooops.  That is not what we wanted!

Before we fix the problem, though, I need to explain a few details above.

First, ``symbol('+')`` is the same as ``symbol(Literal('+'))`` and means that
we require a symbol token `and` that the text in that token matches "+".  A
token used like this can contain any LEPL matcher as a constraint (well,
anything except ``Token()`` itself).

Second, I needed to add ``Configuration.tokens()`` to the ``parse()`` call.
This tells LEPL to do all the necessary work to get the lexer working.
There's a reason why this isn't done automatically --- it is supposed to
remind you that you are assuming a certain `alphabet`.  But I am not sure
that's a very good reason, so this might change (an alphabet is the set of all
possible characters that the regular expression might meet, and the default is
the entire unicode character set, which is normally what you want anyway).

.. index:: debugging

Debugging
---------

What went wrong in the example above?

One way to tell is to examine the tokens that were generated.  Luckily LEPL
has a debug logging statement at exactly the right place, so we can enable
that and see what is being returned::

  >>> from logging import basicConfig, getLogger, DEBUG, INFO
  >>> basicConfig(level=INFO)
  >>> getLogger('lepl.lexer.stream.lexed_simple_stream').setLevel(DEBUG)
  >>> value = Token(SignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> number = value >> float
  >>> add = number & ~symbol('+') & number > sum
  >>> print(add.parse('12+30', config=Configuration.tokens()))
  DEBUG:lepl.lexer.stream.lexed_simple_stream:Token: [2] '12'
  DEBUG:lepl.lexer.stream.lexed_simple_stream:Token: [2] '+30'
  None

The string at the end of each "DEBUG" log line is the text of the token that
was found.

So we can see that the lexer (the part of LEPL that generates the tokens) is
identifying two tokens, both of which are `SignedFloat() <api/redirect.html#lepl.functions.SignedFloat>`_ matches.  It has
ignored the possibility of matching "+" as a ``symbol`` because `regular
expressions return the longest match` and "+" is shorter than "+30".

If you're not sure that "+30" is a valid `SignedFloat() <api/redirect.html#lepl.functions.SignedFloat>`_ it's easy to
check::

  >>> SignedFloat().parse('+30')
  ['+30']

Everything worked earlier because LEPL is smart enough to try all possible
combinations and only use what works, but regular expressions aren't that
smart (at least, the ones used here aren't).

This illustrates an important restriction on the use of tokens.  Because they
use simple regular expressions you have to be careful to avoid ambiguity.
This might make them seem pointless, but in practice their advantages --- in
particular, simplifying handling spaces --- often make them worthwhile.

.. index:: tokens

Tokens (Second Attempt)
-----------------------

We can avoid the problem above by using unsigned numbers.  But that means that
we need to worry about possible signs in the parser itself.  Since people
don't really care about a leading "+" I've only included the "-" case below::

  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> add = number & ~symbol('+') & number > sum
  >>> add.parse('12+30', config=Configuration.tokens())
  [42.0]
  >>> add.parse('12 + -30', config=Configuration.tokens())
  [-18.0]

There are two important changes here.

First, I defined ``negfloat`` to create a negative float.  I used a `lambda
expression <http://docs.python.org/3.0/glossary.html#term-lambda>`_ which is
just a compact way of defining a function.

Second, I checked for a ``value`` preceded by ``-`` (which will appear as a
``symbol`` token) and, for that case, called ``negfloat``.  ``Or()`` works
like you'd expect and, in a similar way to ``And()`` and ``&``, also has a
shortcut: ``|``.

Summary
-------

What more have we learnt?

* To handle spaces, we can specify them explicitly.

* The ``[]`` syntax for repetition is compact and powerful.

* `Separator() <api/redirect.html#lepl.operators.Separator>`_ can automate the addition of spaces wherever we use ``&`` or
  ``[]``.

* Regular expressions are supported, in various different ways.

* LEPL has an optional lexer, which generates tokens using regular
  expressions.

* Because regular expressions are "greedy", always matching the longest amount
  of text possible, we need to be careful exactly how we define our tokens.

* In particular, we should worry when two different tokens overlap (in our
  case, a possible ``symbol``, "+", was also the start of a valid ``value``,
  "+3.0").
