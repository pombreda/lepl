
.. index:: offside rule, whitespace sensitive parsing
.. _offside:

Line--Aware Parsing and the Offside Rule
========================================

From release 3.3 Lepl includes support to simplify parsing text where lines
and whitespace are significant.  For example, in both Python and Haskell, the
relative indentation of lines changes the meaning of a program.  There are
also many simpler cases where a matcher should be applied to a single line (or
several lines connected with a continuation character).

At the end of this section is an :ref:`example <python_example>` that handles 
indentation in a similar way to Python.

There is nothing special about spaces and newline characters, of course, so in
principle it was always possible to handle such grammars in Lepl, but in
practice doing so was frustratingly complex.  The new extensions make things
much simpler.

Note that I use the phrase "offside rule" in a general way (only) to describe
indentation--aware parsing.  I am not claiming to support the exact parsing
used in any one language, but instead to provide a general toolkit that should
make a variety of different syntaxes possible.

.. warn::

   This has changed significantly in Lepl 5.  It is now implemented by adding
   additional tokens into the token stream.  It also has new configuration
   options and slightly changed matcher names.  For more details of the
   changes see `lepl5`_.

Introduction
------------

Two distinct approaches to "line aware" parsing are available.  The first
allows you to simply match lines.  The second allows lines to be grouped into
blocks whose relative indentation is significant.  Both require the use of
tokens.

.. _lines:
.. index:: lines(), LineStart(), LineEnd(), Line()

Simple Line--Aware Parsing (Lines Only)
---------------------------------------

This is configured with `.config.lines() <api/redirect.html#lepl.core.config.ConfigBuilder.lines>`_.  The ``LineStart()`` and
``LineEnd()`` tokens are added to the token stream so that you can match wen
lines start and end.

For example, to split input into lines you might use::

  >>> contents = Token(Any()[:,...]) > list
  >>> line = LineStart() & contents & LineEnd()
  >>> lines = line[:]
  >>> lines.config.lines()
  >>> lines.parse('line one\nline two\nline three')
  [['line one\n'], ['line two\n'], ['line three']]

Since you will often want to define lines, the ``Line()`` matcher simplifies
this a little::

  >>> contents = Token(Any()[:,...]) > list
  >>> line = Line(contents)
  >>> lines = line[:]
  >>> lines.config.lines()
  >>> lines.parse('line one\nline two\nline three')
  [['line one\n'], ['line two\n'], ['line three']]

.. note::

   The contents of the ``Line()`` matcher should be tokens (they can, of
   course, be specialised, as described in `lexer`_).

.. index:: ContinuedLineFactory(), Extend()

Continued and Extended Lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you may want to have a matcher that "continue" over multiple lines.
You can do this by combining ``Line()`` matchers, but there is also a matcher
for the common case of a "continuation character".  For example, if ``'\'`` is
used to mark a line that continues on then::

  >>> contents = Token('[a-z]+')[:] > list
  >>> CLine = ContinuedLineFactory(r'\\')
  >>> line = CLine(contents)
  >>> lines = line[:]
  >>> lines.config.lines()
  >>> lines.parse('line one \\\nline two\nline three')
  [['line', 'one', 'line', 'two'], ['line', 'three']]

The idea is that you make your own replacement for ``Line()`` that works
similarly, but can be continued if it ends in the right character.

Another common use case is that some matching should ignore lines.  For this
you can use ``Extend()``:

  >>> contents = Token('[a-z]+')[:] > list
  >>> parens = Token('\(') & contents & Token('\)') > list
  >>> line = Line(contents & Optional(Extend(parens)))
  >>> lines = line[:]
  >>> lines.config.lines()
  >>> lines.parse('line one (this\n extends to line two)\nline three')
  [['line', 'one'], ['(', ['this', 'extends', 'to', 'line', 'two'], ')'], ['line', 'three']]

.. _blocks:
.. index:: blocks(), BLine(), Indent()

Offside Parsing (Blocks of Lines)
---------------------------------

This is similar to the line--aware parsing above, but adds the tokens
``Indent()`` (instead of ``LineStart()``) and ``LineEnd()`` to the token
stream.  It is configured with `.config.blocks() <api/redirect.html#lepl.core.config.ConfigBuilder.blocks>`_.

The ``Indent()`` token consumes initial spaces on the line and is used by two
new matchers, ``BLine()`` and ``Block()`` to define how blocks of lines are
nested relative to each other.  They work together as shown in the following
"picture"::

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

Because blocks can be nested we typically have a recursive grammar.  For
example::

  >>> introduce = ~Token(':')
  >>> word = Token(Word(Lower()))

  >>> statement = Delayed()

  >>> simple = BLine(word[:])
  >>> empty = BLine(Empty(), indent=False)
  >>> block = BLine(word[:] & introduce) & Block(statement[:])

  >>> statement += (simple | empty | block) > list
  >>> program = statement[:]

  >>> program.config.blocks(block_policy=2)
  >>> parser = program.get_parse_string()

  >>> parser('''
  ... abc def
  ... ghijk:
  ...   mno pqr:
  ...     stu
  ...   vwx yz
  ... ''')
  [[], 
   ['abc', 'def'], 
   ['ghijk', 
    ['mno', 'pqr', 
     ['stu']], 
    ['vwx', 'yz']]]

The core of the parser above is the three uses of `BLine()
<api/redirect.html#lepl.offside.matchers.BLine>`_.  The first, ``simple``, is
a statement that fits in a single line.  The next, ``empty``, is an empty
statement (this has ``indent=False`` because we don't care about the indent of
empty lines).  Finally, ``block`` defines a block statement as one that is
introduced by a line that ends in ":" and then contains a series of statements
that are indented relative to the first line.

So you can see that the `Block()
<api/redirect.html#lepl.offside.matchers.Block>`_ matcher's job is to collect
together lines that are indented relative to whatever came just before.  This
works with `BLine() <api/redirect.html#lepl.offside.matchers.BLine>`_ which
matches a line if it is indented at the correct level.

.. index:: ContinuedBLineFactory()
.. _python_example:  

Continued and Extended Lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with simple line--aware parsing, we would sometimes like a line to continue
over several lines if it ends with a certain matcher.  We can make a similar
matcher to `BLine() <api/redirect.html#lepl.offside.matchers.Line>`_ that
continues over multiple lines using `ContinuedBLineFactory()
<api/redirect.html#lepl.offside.matchers.ContinuedLineFactory>`_.

It is also possible to use ``BExtend()`` to allow some matchers to ignore line
breaks.

Using these two matchers we can write a simple, Python--like language:

  * Blocks are defined by relative indentation
  * The `\` marker indicates that a line extends past a line break
  * Some constructions (like parentheses) automatically allow a line
    to extend past a line break
  * Comments can have any indentation
  
(To keep the example simple there's only minimal parsing apart from the
basic structure - a useful Python parser would obviously need much more work).

::

    word = Token(Word(Lower()))
    continuation = Token(r'\\')
    symbol = Token(Any('()'))
    introduce = ~Token(':')
    comma = ~Token(',')
    hash = Token('#.*')

    CLine = ContinuedBLineFactory(continuation)

    statement = word[1:]
    args = BExtend(word[:, comma]) > tuple
    function = word[1:] & ~symbol('(') & args & ~symbol(')')

    block = Delayed()
    blank = ~BLine(Empty(), indent=False)
    comment = ~BLine(hash, indent=False)
    line = Or((CLine(statement) | block) > list,
	      blank,
	      comment)
    block += CLine((function | statement) & introduce) & Block(line[1:])

    program = (line[:] & Eos())
    program.config.blocks(block_policy=explicit)
    parser = program.get_parse_string()
  
When applied to input like::

    # this is a grammar with a similar
    # line structure to python

    if something:
      then we indent
    else:
        something else
        # note a different indent size here

    def function(a, b, c):
      we can nest blocks:
        like this
      and we can also \
        have explicit continuations \
        with \
    any \
           indentation

    same for (argument,
                        lists):
      which do not need the
      continuation marker
      # and we can have blank lines inside a block:

      like this
        # along with strangely placed comments
      but still keep blocks tied together

The following structure is generated::

    [
      ['if', 'something', 
        ['then', 'we', 'indent']
      ],
      ['else', 
        ['something', 'else'], 
      ],
      ['def', 'function', ('a', 'b', 'c'), 
        ['we', 'can', 'nest', 'blocks', 
          ['like', 'this']
        ], 
        ['and', 'we', 'can', 'also', 'have', 'explicit', 'continuations', 
         'with', 'any', 'indentation'], 
      ], 
      ['same', 'for', ('argument', 'lists'), 
        ['which', 'do', 'not', 'need', 'the'], 
        ['continuation', 'marker'], 
        ['like', 'this'], 
        ['but', 'still', 'keep', 'blocks', 'tied', 'together']
      ]
    ]

The important thing to notice here is that the nesting of lists in the final
result matches the indentation of the original source.

Configuration
~~~~~~~~~~~~~

Various parameters can be passed to the `.config.blocks() <api/redirect.html#lepl.core.config.ConfigBuilder.blocks>`_ configuration:

 * `block_policy` defines how indentations are detected:

   * A simple integer gives the number of spaces by which a new block should
     be indented.  This uses the ``constant_indent()`` policy.

   * Alternatively, an explicit "policy" function can be given:

     * ``to_right()`` allows any size indent, as long as it moves to the
       right.

     * ``explicit()`` allows any size indent (blocks must be introduced by
       some explicit means in the grammar --- for example, by using Python's
       ":" marker).

 * `block_start` is the initial indentation level (0 by default).

 * `discard` defines the regular expression used to match whitespace.

 * `tabsize` defines the number of spaces used to replace a tab (`None` to
   disable).
