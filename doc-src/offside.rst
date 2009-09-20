
.. index:: offside rule, whitespace sensitive parsing
.. _offside:

Offside Rule
============

From release 3.3 LEPL includes support to simplify parsing text where
whitespace is important.  For example, in both Python and Haskell, the
relative indentation of lines changes the meaning of a program.

There is nothing special about spaces, of course, so in principle it was
always possible to handle such grammars in LEPL, but in practice doing so was
frustratingly complex.  The new extensions make things much simpler.

Note that I ues the phrase "offside rule" in a general way (only) to describe
indentation--aware parsing.  I am not claiming to support the exact parsing
used in any one language, but instead to provide a general toolkit that should
make a variety of different syntaxes possible.


Introduction
------------

Below I will describe the way that LEPL handles indentation in three separate
stages.  Most people will use the "high level" tools described in the final
approach, but those are built on top of the "lower level" stages, so it is
best to start there.


Line Aware Alphabet
-------------------

LEPL treats the data to be parsed as a stream --- typically a stream of
characters, or tokens.  For indentation--sensitive parsing, however, it is
important to know about `lines`, so we must add extra markers to the stream.
The `LineAwareConfiguration() <api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ does just this, modifying the stream so that,
in addition to the normal characters, it contains additional "markers" for the
start and end of lines.

The markers can be matched with `SOL()
<api/redirect.html#lepl.offside.matchers.SOL>`_ and `EOL()
<api/redirect.html#lepl.offside.matchers.EOL>`_::

  >>> start = SOL() & Space()[:, ...]
  >>> words = Word()[:,~Space()[:]] > list
  >>> end = EOL()
  >>> line = start & words & end
  >>> parser = line.string_parser(LineAwareConfiguration())
  >>> parser('  abc def')
  ['  ', ['abc', 'def']]

The start and end of line markers are not returned by the matchers.

The extra markers are also added to the default alpabet (Unicode), so that
LEPL's regular expressions (the `DfaRegexp() <api/redirect.html#lepl.regexp.matchers.DfaRegexp>`_ and `NfaRegexp() <api/redirect.html#lepl.regexp.matchers.NfaRegexp>`_ matchers)
can match the start and end of lines (using the ``^`` and ``$`` symbols).

Here is an example showing the use of regular expressions::

  >>> start = DfaRegexp('^ *')
  >>> words = Word()[:,~Space()[:]] > list
  >>> end = DfaRegexp('$')
  >>> line = start & words & end
  >>> parser = line.string_parser(LineAwareConfiguration())
  >>> parser('  abc def')
  ['  ', ['abc', 'def'], '']

Note how the ``start`` expression returns the matched spaces, but the start
and end markers are automatically suppressed from the results.


Indent and Eol Tokens
---------------------

Once we have start and end of line markers, supported by regular expressions,
we can define tokens that match those markers.  This is done by
`IndentConfiguration()
<api/redirect.html#lepl.offside.config.IndentConfiguration>`_ which creates
two tokens: `Indent() <api/redirect.html#lepl.lexer.matchers.Indent>`_ and
`Eol() <api/redirect.html#lepl.lexer.matchers.Eol>`_.  As you might expect,
the first of these matches the start of line marker plus any additional
spaces, while the second matchers the end of line marker.

In addition, this configuration includes additional stream processing that
converts tabs to a given number of spaces::

  >>> words = Token(Word(Lower()))[:] > list
  >>> line = Indent() & words & Eol()
  >>> parser = line.string_parser(IndentConfiguration(tabsize=4))
  >>> parser('\tabc def')
  ['    ', ['abc', 'def'], '']

And because we use tokens there is no need to worry about spaces between
words.


Lines and Blocks
----------------

Matching each `Indent() <api/redirect.html#lepl.lexer.matchers.Indent>`_ and
`Eol() <api/redirect.html#lepl.lexer.matchers.Eol>`_ is cumbersome, so the top
level of support for whitespace matching in LEPL defines some extra matchers
that simplfy the task.

`Block() <api/redirect.html#lepl.offside.matchers.Block>`_ and `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_ colaborate with a monitor
(an advanced feature of LEPL that allows matchers to share data as they are
added to or leave the call stack) to share the "current indentation level".

The structure of some text, in terms of `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ and `Block() <api/redirect.html#lepl.offside.matchers.Block>`_, might
look a little like this::

  BLine()
  BLine()
  Block(BLine()
        BLine()
        Block(BLine()
              BLine())
        BLine()
        Block(Bline()))
  Bline()

Where every line is in a separate ``Bline()`` and then groups of indented
lines are collected inside `Block() <api/redirect.html#lepl.offside.matchers.Block>`_ elements.  Each `Block() <api/redirect.html#lepl.offside.matchers.Block>`_ sets the
indent required for the ``Bline()`` elements it contains.

Because blocks can be nested we typically have a recursive grammar.  For
example::

  >>> introduce = ~Token(':')
  >>> word = Token(Word(Lower()))

  >>> statement = Delayed()

  >>> simple = BLine(word[:])
  >>> empty = BLine(Empty())
  >>> block = BLine(word[:] & introduce) & Block(statement[:])

  >>> statement += (simple | empty | block) > list

  >>> parser = statement[:].string_parser(OffsideConfiguration(policy=2))
  >>> parser('''
  ... abc def
  ... ghijk:
  ...   mno pqr:
  ...     stu
  ...   vwx yz
  ... '''
  [[], 
   ['abc', 'def'], 
   ['ghijk', 
    ['mno', 'pqr', 
     ['stu']], 
    ['vwx', 'yz']]]

I will now explain the parser above in detail.

As with any recursive grammar, we introduce a matcher that we will use before
we define it.  In this case, we introduce ``statement``.

Next we define three different kinds of statement.  The first, ``simple``, is
a statement that fits in a single line.  The next, ``empty``, is an empty
statement.  Finally, ``block`` defines a block statement as one that is
introduced by a line that ends in ":" and then contains a series of statements
that are indented relative to the first line.

So you can see that the `Block() <api/redirect.html#lepl.offside.matchers.Block>`_ matcher's job is to collect together lines
that are indented relative to whatever came just before.  This works with
`BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ which matches a line if it is indented at the correct level.
Finally (and implicitly) the indentation starts at zero.


Further Matchers
----------------

In addition to `Block() <api/redirect.html#lepl.offside.matchers.Block>`_ and `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_, discussed above, the
`OffsideConfiguration() <api/redirect.html#lepl.offside.config.OffsideConfiguration>`_ can be used with several other matchers:


.. index:: Line()

Line

  The `Line() <api/redirect.html#lepl.offside.matchers.Line>`_ matcher matches a line with any indentation.


.. index:: CLineFactory()

CLineFactory

  `CLineFactory() <api/redirect.html#lepl.offside.matchers.CLineFactory>`_ can be used to construct a matcher (usually called
  ``CLine``) that allows a statement to continue ofver several lines if each
  line ends with a continuation symbol.


.. index:: Extend()

Extend

  The `Extend() <api/redirect.html#lepl.offside.matchers.Extend>`_ matcher allows part of a statement to continue over more
  than one line.  Note that, unlike `Line() <api/redirect.html#lepl.offside.matchers.Line>`_, `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ and ``CLine``,
  this does not match an entire line --- it just skips line breaks.


The following example shows these matchers being used in a grammar that has a
Python--like structure::

  >>> word = Token(Word(Lower()))
  >>> continuation = Token(r'\\')
  >>> symbol = Token(Any('()'))
  >>> introduce = ~Token(':')
  >>> comma = ~Token(',')

  >>> CLine = CLineFactory(continuation)
                
  >>> statement = Delayed()

  >>> empty = Line(Empty())
  >>> simple = CLine(word[1:])
  >>> ifblock = CLine(word[1:] & introduce) & Block(statement[1:])

  >>> args = Extend(word[:, comma]) > tuple
  >>> fundef = word[1:] & ~symbol('(') & args & ~symbol(')')
  >>> function = CLine(fundef & introduce) & Block(statement[1:])
        
  >>> statement += (empty | simple | ifblock | function) > list
        
  >>> parser = statement[:].string_parser(OffsideConfiguration(policy=2))
  >>> parser('''
  ... this is a grammar with a similar 
  ... line structure to python
  ... 
  ... if something:
  ...   then we indent
  ... else:
  ...   something else
  ... 
  ... def function(a, b, c):
  ...   we can nest blocks:
  ...     like this
  ...   and we can also \
  ...     have explicit continuations \
  ...     with \
  ... any \
  ...       indentation
  ... 
  ... same for (argument,
  ...           lists):
  ...   which do not need the
  ...   continuation marker
  ... '''
  [[], 
   ['this', 'is', 'a', 'grammar', 'with', 'a', 'similar'],
   ['line', 'structure', 'to', 'python'], 
   []
   ['if', 'something', 
    ['then', 'we', 'indent']]
   ['else', 
    ['something', 'else'], 
    []],
   ['def', 'function', ('a', 'b', 'c'),
    ['we', 'can', 'nest', 'blocks', 
     ['like', 'this']],
    ['and', 'we', 'can', 'also', 'have', 'explicit', 'continuations', 'with', 'any', 'indentation'], 
    []],
   ['same', 'for', ('argument', 'lists'),
    ['which', 'do', 'not', 'need', 'the'],
    ['continuation', 'marker']]]

