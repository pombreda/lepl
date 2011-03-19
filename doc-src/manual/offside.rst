
.. index:: offside rule, whitespace sensitive parsing
.. _offside:

Line--Aware Parsing and the Offside Rule
========================================

From release 3.3 Lepl includes support to simplify parsing text where newlines
and leftmost whitespace are significant.  For example, in both Python and
Haskell, the relative indentation of lines changes the meaning of a program.
At the end of this section is an :ref:`example <python_example>` that handles
indentation in a similar way to Python.

Lepl also supports many simpler cases where a matcher should be applied to a
single line (or several lines connected with a continuation character).

There is nothing special about spaces and newlines, of course, so in principle
it was always possible to handle these in Lepl, but in practice doing so was
sometimes frustratingly complex.  The extensions described here make things
much simpler.

Note that I use the phrase "offside rule" in a general way (only) to describe
indentation--aware parsing.  I am not claiming to support the exact parsing
used in any one language, but instead to provide a general toolkit that should
make a variety of different syntaxes possible.

.. warning::

   This has changed significantly in Lepl 5.  It is now implemented by adding
   additional tokens into the token stream.  It also has new configuration
   options and slightly changed matchers.  For more details of the changes see
   :ref:`Lepl 5 <lepl5>`.

.. index:: lines(), LineStart(), LineEnd(), Line()

Simple Line--Aware Parsing (Lines Only)
---------------------------------------

If line-aware parsing is enabled using ``.config.lines()`` (with no
parameters) then two tokens will be added to each line: ``LineStart()`` at the
beginning and ``LineEnd()`` at the end.  Neither token will return any result,
but they must both be matched for the line as a whole to parse correctly.

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
   course, be specialised, as described in :ref:`lexer`).

.. index:: ContinuedLineFactory(), Extend()

Continued and Extended Lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you may want to have a matcher that continues over multiple lines.
You can do this by combining ``Line()`` matchers, but there is also a matcher
for the common case of a "continuation character".  For example, if ``\`` is
used to mark a line that continues then::

  >>> contents = Token('[a-z]+')[:] > list
  >>> CLine = ContinuedLineFactory(r'\\')
  >>> line = CLine(contents)
  >>> lines = line[:]
  >>> lines.config.lines()
  >>> lines.parse('line one \\\nline two\nline three')
  [['line', 'one', 'line', 'two'], ['line', 'three']]

The idea is that you make your own replacement for ``Line()`` that works
similarly, but can be continued if it ends in the right character (the
continuation character is actually a regular expression which is why it's
written as ``r'\\'`` --- the backslash must be escaped).

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
.. index:: Block(),

Offside Parsing (Blocks of Lines)
---------------------------------

This extends the line--aware parsing above.  In broad terms:

 * Any space at the start of the line is included in the ``LineStart()``
   token.

 * The ``Block()`` matcher will check the start of the first line and set a
   "global" variable to that indentation level.

 * Each ``LineStart()`` will check the variable set by ``Block()`` and only
   match if the indentation level agrees with the space at the start of that
   line.

Together these modifications mean that all the ``LineStart()`` tokens in a
single block must have the same indentation.  In other words, all lines in
a ``Block()`` are indented the same.

Since ``Line()`` continues to work as before, using the modified
``LineStart()`` described above, we can think of the text as being structured
like this::

  Block(Line()
	Line()
	Block(Line()
	      Line()
	      Block(Line()
		    Line())
	      Line()
	      Block(Line()))
	Line())

Each line is a separate ``Line()`` and groups of indented lines are collected
inside ``Block()``.

Configuration
~~~~~~~~~~~~~

To enable the block--based parsing specify the ``block_policy`` or
``block_indent`` parameters in ``.config.lines()``.

The ``block_policy`` decides what indentations are acceptable.  The default,
``constant_indent()`` expects each block to be indented an additional, fixed
number of spaces relative to previous lines.  Other options include
``explicit()``, which will accept any indent (and so is typically used
following a line with a special syntax, like ending in ``":"``) and
``to_right()`` which will accept any indent as long as it is larger than what
went before.

The ``block_indent`` is used with the default ``constant_indent()`` policy and
sets the indentation amount.

A ``tabsize`` parameter can also be specified --- any tab at the start of the
line is replaced with this many spaces.

Example
~~~~~~~

Because blocks can be nested we typically have a recursive grammar.  For
example::

  >>> introduce = ~Token(':')
  >>> word = Token(Word(Lower()))

  >>> statement = Delayed()

  >>> simple = Line(word[:])
  >>> empty = Line(Empty(), indent=False)
  >>> block = Line(word[:] & introduce) & Block(statement[:])

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

The core of the parser above is the three uses of ``Line()``.  The first,
``simple``, is a statement that fits in a single line.  The next, ``empty``,
is an empty statement (this has ``indent=False`` because we don't care about
the indentation of empty lines).  Finally, ``block`` defines a block statement
as one that is introduced by a line that ends in ":" and then contains a
series of statements that are indented relative to the first line.

So you can see that the ``Block()`` matcher's job is to collect
together lines that are indented relative to whatever came just before.  This
works with ``Line()`` which matches a line if it is indented at the correct
level.

.. _python_example:  

Continued and Extended Lines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with simple line--aware parsing, we would sometimes like a line to continue
over several lines if it ends with a certain matcher.  We can make a similar
matcher to ``Line()`` that
continues over multiple lines using ``ContinuedLineFactory()``.

It is also possible to use ``Extend()`` to allow some matchers to ignore line
breaks.

Using these two matchers we can write a simple, Python--like language:

  * Blocks are defined by relative indentation
  * The ``\`` marker indicates that a line extends past a line break
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

    CLine = ContinuedLineFactory(continuation)

    statement = word[1:]
    args = Extend(word[:, comma]) > tuple
    function = word[1:] & ~symbol('(') & args & ~symbol(')')

    block = Delayed()
    blank = ~Line(Empty(), indent=False)
    comment = ~Line(hash, indent=False)
    line = Or((CLine(statement) | block) > list,
	      blank,
	      comment)
    block += Line((function | statement) & introduce) & Block(line[1:])

    program = (line[:] & Eos())
    program.config.lines(block_policy=explicit)
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

