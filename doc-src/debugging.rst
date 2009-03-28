
.. index:: debug, errors
.. _debugging:

Debugging
=========

When a parser fails to match some text it can be difficult (slow, frustrating
work) to underhand why.  Fortunately, LEPL includes some features that make
life easier.

.. note::

  This section does not describe *known errors* (for example, generating an
  error message for the user when they enter text that is wrong in an expected
  way).  That issue is addressed in :ref:`errors`.  What is discussed here are
  the *unknown errors* you face when a parser fails to work with good input.


.. index:: longest match, print_longest()
.. _deepest_match:

Deepest Matches
---------------

It is often useful to know what the last successful match was before the
parser failed.  More exactly, because backtracking will probably find other
matches before the top-most matcher fails completely, it is useful to know the
*longest* match --- the match that consumes as much of the input as possible.

The following code is similar to that used in :ref:`getting-started`, but
fails to match the given input.  It has been modified to print information
about the longest match::

  >>> from lepl.match import *
  >>> from logging import basicConfig, INFO
  
  >>> basicConfig(level=INFO)

  >>> name    = Word()              >= 'name'
  >>> phone   = Integer()           >= 'phone'
  >>> line    = name / ',' / phone  >= make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345',
                            Configuration(monitors=[RecordDeepest()]))
  INFO:lepl.trace.RecordDeepest:
  Up to 6 matches before and including longest match:
  00178 '333325...'   1.8   (0008) 005 (['3333253'], Chunk('andrew, 3333253\n')[15:]) -> Apply('phone') -> ([('phone', '3333253')], Chunk('andrew, 3333253\n')[15:])
  00179 'andrew...'   1.0   (0000) 004 ([('phone', '3333253')], Chunk('andrew, 3333253\n')[15:]) -> And -> ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], Chunk('andrew, 3333253\n')[15:])
  00180 'andrew...'   1.0   (0000) 003 ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], Chunk('andrew, 3333253\n')[15:]) -> Apply -> ([{'phone': '3333253', 'name': 'andrew'}], Chunk('andrew, 3333253\n')[15:])
  00185 '\n bob,...'   1.15  (0015) 004                            next(Literal('\n')('\n bob,...')) -> (['\n'], Chunk(' bob, 12345')[0:])
  00186 '\n bob,...'   1.15  (0015) 005                     (['\n'], Chunk(' bob, 12345')[0:]) -> Or -> (['\n'], Chunk(' bob, 12345')[0:])
  00187 '\n bob,...'   1.15  (0015) 004            (['\n'], Chunk(' bob, 12345')[0:]) -> Apply(Drop) -> ([], Chunk(' bob, 12345')[0:])
  Up to 2 failures following longest match:
  00199 ' bob, ...'   2.0   (0016) 012            ([' '], Chunk(' bob, 12345')[1:]) -> Lookahead(~) -> stop
  00200 ' bob, ...'   2.0   (0016) 011                                     stop -> And(' bob, ...') -> stop
  Up to 2 successful matches following longest match:
  00217 'andrew...'   1.0   (0000) 002                              stop -> DepthFirst('andrew...') -> ([{'phone': '3333253', 'name': 'andrew'}], Chunk('andrew, 3333253\n')[15:])
  [{'phone': '3333253', 'name': 'andrew'}]

The left column is a counter that increases with time.  The next column is the
stream, with offset information (line.character and total characters in
parentheses).  After that is the current stack depth.  Finally, there is a
description of the current action.

Lines are generated *after* of matching, so the innermost of a set of nested
matchers is shown first.

The number of entries displayed is controlled by optional parameters supplied
`RecordDeepest <api/redirect.html#lepl.trace.RecordDeepest>`_.

Looking at the output we can see that the first failure after the deepest
match was a `Lookahead() <api/redirect.html#lepl.match.Lookahead>`_ on the
input ``' bob, ...'``, after matching a newline, `Literal('\\n')
<api/redirect.html#lepl.matchers.Literal>`_.  So we are failing to match a
space after the newline that separates lines --- this is why the original (see
:ref:`repetition`) had::

  >>> newline = spaces & Newline() & spaces
  >>> matcher = line[0:,~newline]


.. index:: execution trace, Trace(), logging

Trace Output
------------

The same data can also be displayed to the logs with the `Trace()
<api/redirect.html#lepl.match.Trace>`_ matcher.  This takes a matcher as an
argument --- tracing is enabled when the selected matcher is called::

  >>> from lepl.match import *
  >>> from logging import basicConfig, INFO
  
  >>> basicConfig(level=INFO)

  >>> name    = Word()                   >= 'name'
  >>> phone   = Trace(Integer(), 'here') >= 'phone'
  >>> line    = name / ',' / phone       >= make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  INFO:lepl.trace.TraceResults:00154 '333325...'   1.8   (0008) 009                              stop -> DepthFirst('333325...') -> ([], Chunk('andrew, 3333253\n')[8:])
  INFO:lepl.trace.TraceResults:00158 '333325...'   1.8   (0008) 009                         next(Any('0123456789')('333325...')) -> (['3'], Chunk('andrew, 3333253\n')[9:])
  INFO:lepl.trace.TraceResults:00160 '333253...'   1.9   (0009) 009                         next(Any('0123456789')('333253...')) -> (['3'], Chunk('andrew, 3333253\n')[10:])
  INFO:lepl.trace.TraceResults:00162 '33253\n...'   1.10  (0010) 009                        next(Any('0123456789')('33253\n...')) -> (['3'], Chunk('andrew, 3333253\n')[11:])
  INFO:lepl.trace.TraceResults:00164 '3253\n ...'   1.11  (0011) 009                        next(Any('0123456789')('3253\n ...')) -> (['3'], Chunk('andrew, 3333253\n')[12:])
  INFO:lepl.trace.TraceResults:00166 '253\n b...'   1.12  (0012) 009                        next(Any('0123456789')('253\n b...')) -> (['2'], Chunk('andrew, 3333253\n')[13:])
  INFO:lepl.trace.TraceResults:00168 '53\n bo...'   1.13  (0013) 009                        next(Any('0123456789')('53\n bo...')) -> (['5'], Chunk('andrew, 3333253\n')[14:])
  INFO:lepl.trace.TraceResults:00170 '3\n bob...'   1.14  (0014) 009                        next(Any('0123456789')('3\n bob...')) -> (['3'], Chunk('andrew, 3333253\n')[15:])
  INFO:lepl.trace.TraceResults:00173 '333325...'   1.8   (0008) 010                              stop -> DepthFirst('333325...') -> (['3', '3', '3', '3', '2', '5', '3'], Chunk('andrew, 3333253\n')[15:])
  INFO:lepl.trace.TraceResults:00174 '333325...'   1.8   (0008) 009 (['3', '3', '3', '3', '2', '5', '3'], Chunk('andrew, 3333253\n')[15:]) -> Apply(Add) -> (['3333253'], Chunk('andrew, 3333253\n')[15:])
  INFO:lepl.trace.TraceResults:00175 '333325...'   1.8   (0008) 008        (['3333253'], Chunk('andrew, 3333253\n')[15:]) -> And -> (['3333253'], Chunk('andrew, 3333253\n')[15:])
  INFO:lepl.trace.TraceResults:00176 '333325...'   1.8   (0008) 007 (['3333253'], Chunk('andrew, 3333253\n')[15:]) -> Apply(Add) -> (['3333253'], Chunk('andrew, 3333253\n')[15:])
  INFO:lepl.trace.TraceResults:00177 '333325...'   1.8   (0008) 006      (['3333253'], Chunk('andrew, 3333253\n')[15:]) -> Trace -> (['3333253'], Chunk('andrew, 3333253\n')[15:])
  [{'phone': '3333253', 'name': 'andrew'}]

.. note::

  `Trace() <api/redirect.html#lepl.match.Trace>`_ expects the parser to be
  configured with the `TraceResults
  <api/redirect.html#lepl.trace.TraceResults>`_ monitor.  This is done by the
  `default configuration
  <api/redirect.html#lepl.matchers.BaseMatcher.default_config>`_, and can also
  be specified manually using a `Configuration()
  <api/redirect.html#lepl.parser.Configuration>`_.
