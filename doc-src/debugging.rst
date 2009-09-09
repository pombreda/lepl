
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


.. index:: log, logging, No handlers could be found for logger

Logging
-------

LEPL uses the standard `Python logging library
<http://docs.python.org/3.1/library/logging.html>`_ and so will display the
message::

  No handlers could be found for logger ...

if no logging has been configured.

The simplest way to configure logging is to add the following to your
program::

  from logging import basicConfig, DEBUG
  basicConfig(level=DEBUG)

To reduce the amount of logging displayed, you can use levels like ``ERROR``
and ``WARN``.

Logging is sent to loggers named after modules and classes.  You can tailor
the logging configuration to only display messages from certain modules or
classes.  See the `Python logging documentation
<http://docs.python.org/3.1/library/logging.html>`_ for more details.

Errors (indicating that the program has failed) use the ``ERROR`` level,
warnings (indicating that you may be mis-using the library) and stack traces
for errors use the ``WARN`` level, and general debug messages use the
``DEBUG`` level.

.. warning::

  Whenever you have a problem with LEPL, the first thing to do is enable
  ``DEBUG`` logging (see above).  And then read the logs.  Common messages and
  errors are described below.


.. index:: stack traces, format_exc, trampolining

Stack Traces
------------

The trampolining used by LEPL to avoid exhausting the stack means that the
traceback from the Python exception raised on failure is not that useful.  A
more useful stack trace, generated from within the trampoline, is logged at
the ``WARN`` level.

If you have enabled logging, but don't see the stack trace, be sure to check
earlier in the output.  Often it is not the last thing displayed in the log.


.. index:: hash, Cannot test for ... in collection, Cannot add ... to collection

Hashable Streams
----------------

LEPL will parse a wide variety of data structures.  Unfortunately, not all
Python's data structures (lists in particular) support hashing.  This means
that some of LEPL's more advanced features, like memoisation, will not work
when a list of data is parsed directly.  Instead you will see warnings
(assusing that logging is enabled - see above) like::

  Cannot add ... to collection
  Cannot test for ... in collection

Fortunately, there is a simple workround for these issues.  Instead of using
the ``.parse()`` and ``.match()`` methods, use ``.parse_items()`` and
``.match_items()``.  These wrap the list in a separate stream that does
support hashing.


.. index:: Lexer rewriter used, but no tokens found

Missing Tokens
--------------

The default `Configuration()
<api/redirect.html#lepl.bin.config.Configuration>`_ includes processing for
lexers.  If no lexers are present, this message is logged::

  Lexer rewriter used, but no tokens found.

This is not a problem (assuming you didn't intend to use lexing, of course).


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
  00156 '3333253\n'   1.8   (0008) 005  (['3333253'], 'andrew, 3333253\n'[15:]) -> Transform(Apply) -> ([('phone', '3333253')], 'andrew, 3333253\n'[15:])
  00157 'andrew...'   1.0   (0000) 004    ([('phone', '3333253')], 'andrew, 3333253\n'[15:]) -> And -> ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], 'andrew, 3333253\n'[15:])
  00158 'andrew...'   1.0   (0000) 003 ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], 'andrew, 3333253\n'[15:]) -> Transform(Apply) -> ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])
  00163 '\n'          1.15  (0015) 004                next(Literal('\n')('andrew, 3333253\n'[15:])) -> (['\n'], ' bob, 12345'[0:])
  00164 '\n'          1.15  (0015) 005                            (['\n'], ' bob, 12345'[0:]) -> Or -> (['\n'], ' bob, 12345'[0:])
  00165 '\n'          1.15  (0015) 004               (['\n'], ' bob, 12345'[0:]) -> Transform(Drop) -> ([], ' bob, 12345'[0:])
  Up to 2 failures following longest match:
  00176 ' bob, ...'   2.0   (0016) 011                   ([' '], ' bob, 12345'[1:]) -> Lookahead(~) -> stop
  00177 ' bob, ...'   2.0   (0016) 010                       stop -> And(AnyBut)(' bob, 12345'[0:]) -> stop
  Up to 2 successful matches following longest match:
  00193 'andrew...'   1.0   (0000) 002                  stop -> DepthFirst('andrew, 3333253\n'[0:]) -> ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])

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
  INFO:lepl.lexer.rewriters.lexer_rewriter:Lexer rewriter used, but no tokens found.
  INFO:lepl.trace._TraceResults:00360 '3333253\n'   1.8   (0008) 019                  stop -> DepthFirst('andrew, 3333253\n'[8:]) -> ([], 'andrew, 3333253\n'[8:])
  INFO:lepl.trace._TraceResults:00361 '3333253\n'   1.8   (0008) 018          ([], 'andrew, 3333253\n'[8:]) -> RTable(DepthFirst) -> ([], 'andrew, 3333253\n'[8:])
  INFO:lepl.trace._TraceResults:00362 '3333253\n'   1.8   (0008) 017           ([], 'andrew, 3333253\n'[8:]) -> RMemo(DepthFirst) -> ([], 'andrew, 3333253\n'[8:])
  INFO:lepl.trace._TraceResults:00372 '3333253\n'   1.8   (0008) 023             next(Any('0123456789')('andrew, 3333253\n'[8:])) -> (['3'], 'andrew, 3333253\n'[9:])
  INFO:lepl.trace._TraceResults:00373 '3333253\n'   1.8   (0008) 024 (['3'], 'andrew, 3333253\n'[9:]) -> RTable(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[9:])
  INFO:lepl.trace._TraceResults:00374 '3333253\n'   1.8   (0008) 023 (['3'], 'andrew, 3333253\n'[9:]) -> RMemo(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[9:])
  INFO:lepl.trace._TraceResults:00378 '333253\n'    1.9   (0009) 023             next(Any('0123456789')('andrew, 3333253\n'[9:])) -> (['3'], 'andrew, 3333253\n'[10:])
  INFO:lepl.trace._TraceResults:00379 '333253\n'    1.9   (0009) 024 (['3'], 'andrew, 3333253\n'[10:]) -> RTable(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[10:])
  INFO:lepl.trace._TraceResults:00380 '333253\n'    1.9   (0009) 023 (['3'], 'andrew, 3333253\n'[10:]) -> RMemo(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[10:])
  INFO:lepl.trace._TraceResults:00384 '33253\n'     1.10  (0010) 023            next(Any('0123456789')('andrew, 3333253\n'[10:])) -> (['3'], 'andrew, 3333253\n'[11:])
  INFO:lepl.trace._TraceResults:00385 '33253\n'     1.10  (0010) 024 (['3'], 'andrew, 3333253\n'[11:]) -> RTable(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[11:])
  INFO:lepl.trace._TraceResults:00386 '33253\n'     1.10  (0010) 023 (['3'], 'andrew, 3333253\n'[11:]) -> RMemo(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[11:])
  INFO:lepl.trace._TraceResults:00390 '3253\n'      1.11  (0011) 023            next(Any('0123456789')('andrew, 3333253\n'[11:])) -> (['3'], 'andrew, 3333253\n'[12:])
  INFO:lepl.trace._TraceResults:00391 '3253\n'      1.11  (0011) 024 (['3'], 'andrew, 3333253\n'[12:]) -> RTable(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[12:])
  INFO:lepl.trace._TraceResults:00392 '3253\n'      1.11  (0011) 023 (['3'], 'andrew, 3333253\n'[12:]) -> RMemo(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[12:])
  INFO:lepl.trace._TraceResults:00396 '253\n'       1.12  (0012) 023            next(Any('0123456789')('andrew, 3333253\n'[12:])) -> (['2'], 'andrew, 3333253\n'[13:])
  INFO:lepl.trace._TraceResults:00397 '253\n'       1.12  (0012) 024 (['2'], 'andrew, 3333253\n'[13:]) -> RTable(Any('0123456789')) -> (['2'], 'andrew, 3333253\n'[13:])
  INFO:lepl.trace._TraceResults:00398 '253\n'       1.12  (0012) 023 (['2'], 'andrew, 3333253\n'[13:]) -> RMemo(Any('0123456789')) -> (['2'], 'andrew, 3333253\n'[13:])
  INFO:lepl.trace._TraceResults:00402 '53\n'        1.13  (0013) 023            next(Any('0123456789')('andrew, 3333253\n'[13:])) -> (['5'], 'andrew, 3333253\n'[14:])
  INFO:lepl.trace._TraceResults:00403 '53\n'        1.13  (0013) 024 (['5'], 'andrew, 3333253\n'[14:]) -> RTable(Any('0123456789')) -> (['5'], 'andrew, 3333253\n'[14:])
  INFO:lepl.trace._TraceResults:00404 '53\n'        1.13  (0013) 023 (['5'], 'andrew, 3333253\n'[14:]) -> RMemo(Any('0123456789')) -> (['5'], 'andrew, 3333253\n'[14:])
  INFO:lepl.trace._TraceResults:00408 '3\n'         1.14  (0014) 023            next(Any('0123456789')('andrew, 3333253\n'[14:])) -> (['3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00409 '3\n'         1.14  (0014) 024 (['3'], 'andrew, 3333253\n'[15:]) -> RTable(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00410 '3\n'         1.14  (0014) 023 (['3'], 'andrew, 3333253\n'[15:]) -> RMemo(Any('0123456789')) -> (['3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00417 '3333253\n'   1.8   (0008) 022                  stop -> DepthFirst('andrew, 3333253\n'[8:]) -> (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00418 '3333253\n'   1.8   (0008) 021 (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:]) -> RTable(DepthFirst) -> (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00419 '3333253\n'   1.8   (0008) 020 (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:]) -> RMemo(DepthFirst) -> (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00420 '3333253\n'   1.8   (0008) 019 (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:]) -> Transform(Add) -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00421 '3333253\n'   1.8   (0008) 018 (['3333253'], 'andrew, 3333253\n'[15:]) -> RTable(Transform(Add)) -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00422 '3333253\n'   1.8   (0008) 017 (['3333253'], 'andrew, 3333253\n'[15:]) -> RMemo(Transform(Add)) -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00423 '3333253\n'   1.8   (0008) 016               (['3333253'], 'andrew, 3333253\n'[15:]) -> And -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00424 '3333253\n'   1.8   (0008) 015       (['3333253'], 'andrew, 3333253\n'[15:]) -> RTable(And) -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00425 '3333253\n'   1.8   (0008) 014        (['3333253'], 'andrew, 3333253\n'[15:]) -> RMemo(And) -> (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.trace._TraceResults:00426 '3333253\n'   1.8   (0008) 013             (['3333253'], 'andrew, 3333253\n'[15:]) -> Trace -> (['3333253'], 'andrew, 3333253\n'[15:])
  [{'phone': '3333253', 'name': 'andrew'}]

.. note::

  `Trace() <api/redirect.html#lepl.match.Trace>`_ expects the parser to be
  configured with the `TraceResults
  <api/redirect.html#lepl.trace.TraceResults>`_ monitor.  This is done by the
  `default configuration
  <api/redirect.html#lepl.functions.BaseMatcher.default_config>`_, and can also
  be specified manually using a `Configuration()
  <api/redirect.html#lepl.config.Configuration>`_.
