
.. index:: debug, errors
.. _debugging:

Debugging
=========

When a parser fails to match some text it can be difficult (slow, frustrating
work) to understand why.  Fortunately, Lepl includes some features that make
life easier.

.. note::

  This section does not describe *known errors* (for example, generating an
  error message for the user when they enter text that is wrong in an expected
  way).  That issue is addressed in :ref:`errors`.  What is discussed here are
  the *unknown errors* you face when a parser fails to work with good input.


.. index:: log, logging, No handlers could be found for logger

Logging
-------

Lepl uses the standard `Python logging library
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

  Whenever you have a problem with Lepl, the first thing to do is enable
  ``DEBUG`` logging (see above).  And then read the logs.  Common messages and
  errors are described below.


.. index:: stack traces, format_exc, trampolining

Stack Traces
------------

Lepl 4 has improved trampolining which should give exceptions whose traceback
information identifies the source of any problem (earlier versions printed a
separate stack trace to the log --- that is no longer necessary).


.. index:: variable traces, TraceVariable

Variable Traces
---------------

The traces described later in this section give a very detailed picture of the
processing that occurs  within Lepl, but they are  difficult to understand and
show an overwhelming amount of information.

Often, to understand a problem, it is sufficient to see how the matchers
associated with variables are being matched.  This is displayed when the
variables are defined inside a ``with TraceVariables()`` scope::

  >>> with TraceVariables():
  ...     word = ~Lookahead('OR') & Word()
  ...     phrase = String()
  ...     with DroppedSpace():
  ...         text = (phrase | word)[1:] > list
  ...         query = text[:, Drop('OR')]
  ...
  >>> query.parse('spicy meatballs OR "el bulli restaurant"')
        phrase failed                             stream = 'spicy meatballs OR...
          word = ['spicy']                        stream = ' meatballs OR "el ...
        phrase failed                             stream = 'meatballs OR "el b...
          word = ['meatballs']                    stream = ' OR "el bulli rest...
        phrase failed                             stream = 'OR "el bulli resta...
          word failed                             stream = 'OR "el bulli resta...
        phrase failed                             stream = ' OR "el bulli rest...
          word failed                             stream = ' OR "el bulli rest...
          text = [['spicy', 'meatballs']]         stream = ' OR "el bulli rest...
        phrase = ['el bulli restaurant']          stream = ''
        phrase failed                             stream = ''
          word failed                             stream = ''
          text = [['el bulli restaurant']]        stream = ''
  [['spicy', 'meatballs'], ['el bulli restaurant']]

The display above shows, on the left, the current match.  On the right is the
head of the stream (what is left after being matched).


.. index:: longest match, print_longest()
.. _deepest_match:

Deepest Matches
---------------

The `.config.full_first_match() <api/redirect.html#lepl.core.config.ConfigBuilder.full_first_match>`_ option, enabled by default, gives a simple
error indicating the deepest match within the stream.  A more detailed report
is also possible via `.config.record_deepest() <api/redirect.html#lepl.core.config.ConfigBuilder.record_deepest>`_.

The following code is similar to that used in :ref:`getting-started`, but
fails to match the given input.  It has been modified to print information
about the longest match::

  >>> from lepl.match import *
  >>> from logging import basicConfig, INFO
  
  >>> basicConfig(level=INFO)

  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> line    = name / ',' / phone  > make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.config.clear().record_deepest()
  >>> matcher.parse('andrew, 3333253\n bob, 12345')
  INFO:lepl.core.trace._RecordDeepest:
  Up to 6 matches before and including longest match:
  00204 'andrew...'   1.0   (0000) 005 ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], 'andrew, 3333253\n'[15:])  ->  And(And, Transform, Transform)('andrew, 3333253\n'[0:])  ->  ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], 'andrew, 3333253\n'[15:])
  00205 'andrew...'   1.0   (0000) 004 ([('name', 'andrew'), ',', ' ', ('phone', '3333253')], 'andrew, 3333253\n'[15:])  ->  Transform(And, TransformationWrapper(<apply>))('andrew, 3333253\n'[0:])  ->  ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])
  00212 '\n'          1.15  (0015) 007 next(Literal('\n')('andrew, 3333253\n'[15:]))  ->  (['\n'], ' bob, 12345'[0:])
  00213 '\n'          1.15  (0015) 008 (['\n'], ' bob, 12345'[0:])  ->  Or(Literal, Literal)('andrew, 3333253\n'[15:])  ->  (['\n'], ' bob, 12345'[0:])
  00214 '\n'          1.15  (0015) 007 (['\n'], ' bob, 12345'[0:])  ->  Or(Literal, Literal)('andrew, 3333253\n'[15:])  ->  (['\n'], ' bob, 12345'[0:])
  00215 '\n'          1.15  (0015) 006 (['\n'], ' bob, 12345'[0:])  ->  Transform(Or, TransformationWrapper(<apply>))('andrew, 3333253\n'[15:])  ->  ([], ' bob, 12345'[0:])
  Up to 2 failures following longest match:
  00230 ' bob, ...'   2.0   (0016) 017 ([' '], ' bob, 12345'[1:])  ->  Lookahead(Any, True)(' bob, 12345'[0:])  ->  stop
  00231 ' bob, ...'   2.0   (0016) 016 stop  ->  And(Lookahead, Any)(' bob, 12345'[0:])  ->  stop
  Up to 2 successful matches following longest match:
  00254 'andrew...'   1.0   (0000) 003 stop  ->  DepthFirst(0, None, rest=And, first=Transform)('andrew, 3333253\n'[0:])  ->  ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])
  00255 'andrew...'   1.0   (0000) 002 ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])  ->  DepthFirst(0, None, rest=And, first=Transform)('andrew, 3333253\n'[0:])  ->  ([{'phone': '3333253', 'name': 'andrew'}], 'andrew, 3333253\n'[15:])

The left column is a counter that increases with time.  The next column is the
stream, with offset information (line.character and total characters in
parentheses).  After that is the current stack depth.  Finally, there is a
description of the current action.

Lines are generated *after* of matching, so the innermost of a set of nested
matchers is shown first.

The number of entries displayed is controlled by optional parameters supplied
to `.config.record_deepest() <api/redirect.html#lepl.core.config.ConfigBuilder.record_deepest>`_.

Looking at the output we can see that the first failure after the deepest
match was a `Lookahead() <api/redirect.html#lepl.match.Lookahead>`_ on the
input ``' bob, ...'``, after matching a newline, `Literal('\\n')
<api/redirect.html#lepl.matchers.core.Literal>`_.  So we are failing to match a
space after the newline that separates lines --- this is why the original (see
:ref:`repetition`) had::

  >>> newline = spaces & Newline() & spaces
  >>> matcher = line[0:,~newline]


.. index:: execution trace, Trace(), logging

Trace Output
------------

The same data can also be displayed to the logs with the `Trace()
<api/redirect.html#lepl.matchers.monitor.Trace>`_ matcher.  This takes a
matcher as an argument --- tracing is enabled when the selected matcher is
called::

  >>> from lepl.match import *
  >>> from logging import basicConfig, INFO
  
  >>> basicConfig(level=INFO)

  >>> name    = Word()                   > 'name'
  >>> phone   = Trace(Integer(), 'here') > 'phone'
  >>> line    = name / ',' / phone       > make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.config.clear().trace()
  >>> matcher.parse('andrew, 3333253\n bob, 12345')
  INFO:lepl.core.trace._TraceResults:00176 '3333253\n'   1.8   (0008) 013 stop  ->  DepthFirst(0, 1, rest=Any, first=Any)('andrew, 3333253\n'[8:])  ->  ([], 'andrew, 3333253\n'[8:])
  INFO:lepl.core.trace._TraceResults:00177 '3333253\n'   1.8   (0008) 012 ([], 'andrew, 3333253\n'[8:])  ->  DepthFirst(0, 1, rest=Any, first=Any)('andrew, 3333253\n'[8:])  ->  ([], 'andrew, 3333253\n'[8:])
  INFO:lepl.core.trace._TraceResults:00182 '3333253\n'   1.8   (0008) 013 next(Any('0123456789')('andrew, 3333253\n'[8:]))  ->  (['3'], 'andrew, 3333253\n'[9:])
  INFO:lepl.core.trace._TraceResults:00184 '333253\n'    1.9   (0009) 013 next(Any('0123456789')('andrew, 3333253\n'[9:]))  ->  (['3'], 'andrew, 3333253\n'[10:])
  INFO:lepl.core.trace._TraceResults:00186 '33253\n'     1.10  (0010) 013 next(Any('0123456789')('andrew, 3333253\n'[10:]))  ->  (['3'], 'andrew, 3333253\n'[11:])
  INFO:lepl.core.trace._TraceResults:00188 '3253\n'      1.11  (0011) 013 next(Any('0123456789')('andrew, 3333253\n'[11:]))  ->  (['3'], 'andrew, 3333253\n'[12:])
  INFO:lepl.core.trace._TraceResults:00190 '253\n'       1.12  (0012) 013 next(Any('0123456789')('andrew, 3333253\n'[12:]))  ->  (['2'], 'andrew, 3333253\n'[13:])
  INFO:lepl.core.trace._TraceResults:00192 '53\n'        1.13  (0013) 013 next(Any('0123456789')('andrew, 3333253\n'[13:]))  ->  (['5'], 'andrew, 3333253\n'[14:])
  INFO:lepl.core.trace._TraceResults:00194 '3\n'         1.14  (0014) 013 next(Any('0123456789')('andrew, 3333253\n'[14:]))  ->  (['3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00197 '3333253\n'   1.8   (0008) 014 stop  ->  DepthFirst(1, None, rest=Any, first=Any)('andrew, 3333253\n'[8:])  ->  (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00198 '3333253\n'   1.8   (0008) 013 (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])  ->  DepthFirst(1, None, rest=Any, first=Any)('andrew, 3333253\n'[8:])  ->  (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00199 '3333253\n'   1.8   (0008) 012 (['3', '3', '3', '3', '2', '5', '3'], 'andrew, 3333253\n'[15:])  ->  Transform(DepthFirst, TransformationWrapper(<add>))('andrew, 3333253\n'[8:])  ->  (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00200 '3333253\n'   1.8   (0008) 011 (['3333253'], 'andrew, 3333253\n'[15:])  ->  And(DepthFirst, Transform)('andrew, 3333253\n'[8:])  ->  (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00201 '3333253\n'   1.8   (0008) 010 (['3333253'], 'andrew, 3333253\n'[15:])  ->  And(DepthFirst, Transform)('andrew, 3333253\n'[8:])  ->  (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00202 '3333253\n'   1.8   (0008) 009 (['3333253'], 'andrew, 3333253\n'[15:])  ->  Transform(And, TransformationWrapper(<add>))('andrew, 3333253\n'[8:])  ->  (['3333253'], 'andrew, 3333253\n'[15:])
  INFO:lepl.core.trace._TraceResults:00203 '3333253\n'   1.8   (0008) 008 (['3333253'], 'andrew, 3333253\n'[15:])  ->  Trace(Transform, True)('andrew, 3333253\n'[8:])  ->  (['3333253'], 'andrew, 3333253\n'[15:])

.. note::

  `Trace() <api/redirect.html#lepl.matchers.monitor.Trace>`_ expects the
  parser to be configured with the `TraceResults
  <api/redirect.html#lepl.trace.TraceResults>`_ monitor.  This is done with
  `.config.trace() <api/redirect.html#lepl.core.config.ConfigBuilder.trace>`_.


.. index:: common errors

Common Errors
-------------

.. index:: hash, Cannot test for ... in collection, Cannot add ... to collection

Hashable Streams
~~~~~~~~~~~~~~~~

Lepl will parse a wide variety of data structures.  Unfortunately, not all
Python's data structures (lists in particular) support hashing.  This means
that some of Lepl's more advanced features, like memoisation, will not work
when a list of data is parsed directly.  Instead you will see warnings
(assusing that logging is enabled - see above) like::

  Cannot add ... to collection
  Cannot test for ... in collection

Fortunately, there is a workround for these issues.  Instead of using the
`matcher.parse() <api/redirect.html#lepl.core.config.ParserMixin.parse>`_ and `matcher.match() <api/redirect.html#lepl.core.config.ParserMixin.match>`_ methods, use
`matcher.parse_items() <api/redirect.html#lepl.core.config.ParserMixin.parse_items>`_ and `matcher.match_items() <api/redirect.html#lepl.core.config.ParserMixin.match_items>`_.  These wrap the list
in a separate stream that does support hashing.


.. index:: Lexer rewriter used but no tokens found

Missing Tokens
~~~~~~~~~~~~~~

The default `Configuration()
<api/redirect.html#lepl.config.Configuration>`_ includes processing for
lexers.  If no lexers are present, this message is logged::

  Lexer rewriter used, but no tokens found.

This is not a problem (assuming you didn't intend to use lexing, of course).


.. index:: A Token was specified with a matcher but

Rewriter Order
~~~~~~~~~~~~~~

Before Lepl 4 it was possible to specify the order of rewriters; the new
configuration interface automatically places them in the correct order.  So
hopefully this error will no longer occur.

