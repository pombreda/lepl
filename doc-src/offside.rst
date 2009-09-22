
.. index:: offside rule, whitespace sensitive parsing
.. _offside:

Line--Aware Parsing and the Offside Rule
========================================

From release 3.3 LEPL includes support to simplify parsing text where lines
and whitespace are significant.  For example, in both Python and Haskell, the
relative indentation of lines changes the meaning of a program.  There are
also many simpler cases where a matcher should be applied to a single line (or
several lines connected with a continuation character).

There is nothing special about spaces and newline characters, of course, so in
principle it was always possible to handle such grammars in LEPL, but in
practice doing so was frustratingly complex.  The new extensions make things
much simpler.

Note that I use the phrase "offside rule" in a general way (only) to describe
indentation--aware parsing.  I am not claiming to support the exact parsing
used in any one language, but instead to provide a general toolkit that should
make a variety of different syntaxes possible.

.. warning::

   This code is still in development.  The documentation here reflects the
   latest code in subversion.  There is also a beta release (3.3b1) which
   contains working line-aware support, but it differs slightly from what is
   documented here (the svn and this documentation are more recent that the
   beta).  There should be another release before the end of September.


Introduction
------------

The offside rule support (indentation sensitive) is built on top of the
line--aware features, so I will describe those first.  To enable line--aware
features, use `LineAwareConfiguration() <api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ (or do the equivalent with a
standard `Configuration() <api/redirect.html#lepl.bin.config.Configuration>`_ object if you want more control over exactly what
options are used).


Line Aware Alphabet
-------------------

LEPL treats the data to be parsed as a stream --- typically a stream of
characters, or tokens.  For line--aware parsing, however, it is important to
know about `lines`, so we must add extra markers to the stream.
`LineAwareConfiguration()
<api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ automatically
modifies the parser so that streams are modified correctly.

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

The extra markers are also added to the alphabet used (Unicode by default), so
that LEPL's regular expressions (the `DfaRegexp()
<api/redirect.html#lepl.regexp.matchers.DfaRegexp>`_ and `NfaRegexp()
<api/redirect.html#lepl.regexp.matchers.NfaRegexp>`_ matchers) can match the
start and end of lines (using the ``^`` and ``$`` symbols).

Here is an example showing the use of regular expressions::

  >>> start = DfaRegexp('^ *')
  >>> words = Word()[:,~Space()[:]] > list
  >>> end = DfaRegexp('$')
  >>> line = start & words & end
  >>> parser = line.string_parser(LineAwareConfiguration())
  >>> parser('  abc def')
  ['  ', ['abc', 'def'], '']

Note how the ``start`` expression returns the matched spaces, but the start
and end markers are, again, automatically suppressed from the results.


Tabs
----

The `LineAwareConfiguration() <api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ has an optional ``tabsize`` parameter.  If
set, tabs are replaced by this many spaces.  By default, no replacement is
made.


Indent and Eol Tokens
---------------------

We can use tokens with line--aware alphabets.  LEPL includes two tokens that
do the basic work: `Indent() <api/redirect.html#lepl.offside.lexer.Indent>`_
and `Eol() <api/redirect.html#lepl.offside.lexer.Eol>`_.  As you might expect,
the first of these matches the start of line marker plus any additional
spaces, while the second matchers the end of line marker.

Like any other token, `Indent()
<api/redirect.html#lepl.offside.lexer.Indent>`_ can be used to create a
specialised token that matches the actual indentation used.

Here is an example using line--aware tokens::

  >>> words = Token(Word(Lower()))[:] > list
  >>> line = Indent() & words & Eol()
  >>> parser = line.string_parser(LineAwareConfiguration(tabsize=4))
  >>> parser('\tabc def')
  ['    ', ['abc', 'def'], '']

And because we use tokens there is no need to worry about spaces between
words.


Lines and Continuations
-----------------------

The `Line() <api/redirect.html#lepl.offside.matchers.Line>`_ matcher hides `Indent() <api/redirect.html#lepl.offside.lexer.Indent>`_ and `Eol() <api/redirect.html#lepl.offside.lexer.Eol>`_ behind a slightly
simpler interface::

  >>> words = Token(Word(Lower()))[:] > list
  >>> line = Line(words)
  >>> parser = line.string_parser(LineAwareConfiguration(tabsize=4))
  >>> parser('\tabc def')
  [['abc', 'def']]

In some cases we would like a line to continue over several lines if it ends
with a certain matcher.  We can make a similar matcher to `Line() <api/redirect.html#lepl.offside.matchers.Line>`_ that
continues over multiple lines using `ContinuedLineFactory() <api/redirect.html#lepl.offside.matchers.ContinuedLineFactory>`_::

  >>> words = Token(Word(Lower()))[:] > list
  >>> CLine = ContinuedLineFactory(r'\+')
  >>> line = CLine(words)
  >>> parser = line.string_parser(LineAwareConfiguration())
  >>> parser('''abc def +
  ghi'''
  [['abc', 'def', 'ghi']]

A similar matcher is `Extend()
<api/redirect.html#lepl.offside.matchers.Extend>`_ which allows some content
within a line to continue onto another line.  Note that, unlike `Line()
<api/redirect.html#lepl.offside.matchers.Line>`_, this does not match an
entire line --- it just skips line breaks.  For an example that uses `Extend()
<api/redirect.html#lepl.offside.matchers.Extend>`_ see the very end of this
section.


Offside Rule and Blocks
-----------------------

In addition to the above, LEPL simplifies offside rule parsing with the
concept of "blocks", which allow text to be described in terms of nested
sections.  Again, this is most simply configured via `LineAwareConfiguration()
<api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ (either the
`block_policy` or the `block_start` option must be given to trigger the
correct behaviour --- see below).

The nested structure is described using `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_ and `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_.  They work together as
shown in the following "picture"::

  BLine()
  BLine()
  Block(BLine()
        BLine()
        Block(BLine()
              BLine())
        BLine()
        Block(BLine()))
  BLine()

In other words: each line is in a separate `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_ and groups of indented lines
are collected inside `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_ elements.  Each `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_ sets the indent required for
the `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ elements it
contains.

In a little more detail: `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_ and `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_ collaborate with a monitor
(an advanced feature of LEPL that allows matchers to share data as they are
added to or leave the call stack) to share the "current indentation level".

Because blocks can be nested we typically have a recursive grammar.  For
example::

  >>> introduce = ~Token(':')
  >>> word = Token(Word(Lower()))

  >>> statement = Delayed()

  >>> simple = BLine(word[:])
  >>> empty = BLine(Empty())
  >>> block = BLine(word[:] & introduce) & Block(statement[:])

  >>> statement += (simple | empty | block) > list

  >>> parser = statement[:].string_parser(LineAwareConfiguration(block_policy=2))
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

The core of the parser above are the three uses of `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_. The first, ``simple``, is a
statement that fits in a single line.  The next, ``empty``, is an empty
statement.  Finally, ``block`` defines a block statement as one that is
introduced by a line that ends in ":" and then contains a series of statements
that are indented relative to the first line.

So you can see that the `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_ matcher's job is to collect
together lines that are indented relative to whatever came just before.  This
works with `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ which
matches a line if it is indented at the correct level.

The `block_policy` parameter in `LineAwareConfiguration()
<api/redirect.html#lepl.offside.config.LineAwareConfiguration>`_ indicates how
many spaces are required for a single level of indentation.  The `block_start`
gives the initial indentation level (zero by default).


Further Matchers
----------------

The other line--aware matchers can also be used with blocks.  For example, a
line for which indentation is not important (a comment, perhaps), can be
matched with `Line() <api/redirect.html#lepl.offside.matchers.Line>`_.

`ContinuedBLineFactory()
<api/redirect.html#lepl.offside.matchers.ContinuedBLineFactory>`_ adds
continuation support for `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_ in exactly the same way as
`ContinuedLineFactory()
<api/redirect.html#lepl.offside.matchers.ContinuedLineFactory>`_ described
earlier.

The following example shows many of these matchers being used in a grammar
that has a Python--like structure::

  >>> word = Token(Word(Lower()))
  >>> continuation = Token(r'\\')
  >>> symbol = Token(Any('()'))
  >>> introduce = ~Token(':')
  >>> comma = ~Token(',')

  >>> CLine = ContinuedBLineFactory(continuation)
                
  >>> statement = Delayed()

  >>> empty = Line(Empty())
  >>> simple = CLine(word[1:])
  >>> ifblock = CLine(word[1:] & introduce) & Block(statement[1:])

  >>> args = Extend(word[:, comma]) > tuple
  >>> fundef = word[1:] & ~symbol('(') & args & ~symbol(')')
  >>> function = CLine(fundef & introduce) & Block(statement[1:])
        
  >>> statement += (empty | simple | ifblock | function) > list
        
  >>> parser = statement[:].string_parser(LineAwareConfiguration(block_policy=2))
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

