
.. index:: debug, errors
.. _debugging:

Debugging
=========

When a parser fails to match some text it can be difficult (slow, frustrating
work) to undertand why.  Fortunately, LEPL includes some features that make
life easier.

.. note::

  This section does not describe *known errors* (for example, generating an
  error message for the user when they enter text that is wrong in an expected
  way).  That issue is addressed in :ref:`errors`.  What is discussed here are
  the *unknown errors* you face when a parser fails to work with good input.


.. index:: longest match, print_longest()

Deepest Matches
---------------

It is often useful to know what the last successful match was before the
parser failed.  More exactly, because backtracking will probably find other
matches before the top-most matcher fails completely, it is useful to know the
*longest* match --- the match that consumes as much of the input as possible.

The following code is similar to that used in the :ref:`introduction`, but
fails to match the given input.  It has been modified to print information
about the longest match::

  >>> from lepl.match import *
  >>> from lepl.node import make_dict
  >>> from lepl.stream import Stream

  >>> name    = Word()              >= 'name'
  >>> phone   = Integer()           >= 'phone'
  >>> line    = name / ',' / phone  >= make_dict
  >>> matcher = line[0:,~Newline()]
  >>> stream = Stream.from_string('andrew, 3333253\n bob, 12345', memory=(4,2,2))
  >>> next(matcher(stream))
  ([{'phone': '3333253', 'name': 'andrew'}], Chunk('andrew, 3333253\n')[15:])
  
  >>> stream.core.bb.print_longest()
  Up to 4 matches before and including longest match:
     91  Literal('\n')                    1.15  (00015) '\n bob,...'   ['\n']
     92  Or                               1.15  (00015) '\n bob,...'   ['\n']
     93  Apply(Drop)                      1.15  (00015) '\n bob,...'   []
     94  Any(' \t\n\r\x0b\x0c')           2.0   (00016) ' bob, ...'   [' ']
  Up to 2 failures following longest match:
     95  Lookahead(~)                     2.0   (00016) ' bob, ...'   fail
     96  And                              2.0   (00016) ' bob, ...'   fail
  Up to 2 successful matches following longest match:
    109  _Repeat(...)                     1.0   (00000) 'andrew...'   [{'phone': '3333253', 'name': 'andrew'}]
  Epoch  Matcher                       Line.Chr (Chars) Stream        Result

The left column (Epoch) is a counter that increases with time.  The next
column is the matcher, which may include extra information within ``()``.
After that comes the stream (line and character, then character offset, then a
sample of the next text to match).  Finally, on the right, is the result or,
on failure, "fail".

Lines are generated *after* of matching, so the innermost of a set of nested
matchers is shown first.

The number of entries displayed is controlled by the ``memory`` parameter
supplied to the `Stream <api/redirect.html#lepl.stream.Stream>`_.

Looking at the output we can see that the longest match was a whitespace,
presumably associated with the `Lookahead()
<api/redirect.html#lepl.match.Lookahead>`_ that fails immediately
afterwards.  So "anything but a whitespace" failed, which is the likely
definition of `Word() <api/redirect.html#lepl.match.Word>`_.  Comparing
that with our grammar, we can see (with a little practice) that ``name`` is
failing because of the space before "bob".


.. index:: execution trace, Trace(), logging

Trace Output
------------

The same data can also be displayed to the logs with the `Trace()
<api/redirect.html#lepl.match.Trace>`_ matcher.  This takes a matcher as an
argument, along with some optional text.  Tracing is then enabled when the
selected matcher is called::

  >>> from logging import basicConfig, INFO
  
  >>> basicConfig(level=INFO)
  >>> name    = Word()                   >= 'name'
  >>> phone   = Trace(Integer(), 'here') >= 'phone'
  >>> line    = name / ',' / phone       >= make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  INFO:lepl.trace.BlackBox:   74  Empty(+phone)                    1.8   (00008) '333325...'   []
  INFO:lepl.trace.BlackBox:   75  Any('+-')                        1.8   (00008) '333325...'   fail
  INFO:lepl.trace.BlackBox:   76  _Repeat(...)                     1.8   (00008) '333325...'   []
  INFO:lepl.trace.BlackBox:   77  Any('0123456789')                1.8   (00008) '333325...'   ['3']
  INFO:lepl.trace.BlackBox:   78  Any('0123456789')                1.9   (00009) '333253...'   ['3']
  INFO:lepl.trace.BlackBox:   79  Any('0123456789')                1.10  (00010) '33253\n...'   ['3']
  INFO:lepl.trace.BlackBox:   80  Any('0123456789')                1.11  (00011) '3253\n ...'   ['3']
  INFO:lepl.trace.BlackBox:   81  Any('0123456789')                1.12  (00012) '253\n b...'   ['2']
  INFO:lepl.trace.BlackBox:   82  Any('0123456789')                1.13  (00013) '53\n bo...'   ['5']
  INFO:lepl.trace.BlackBox:   83  Any('0123456789')                1.14  (00014) '3\n bob...'   ['3']
  INFO:lepl.trace.BlackBox:   84  Any('0123456789')                1.15  (00015) '\n bob,...'   fail
  INFO:lepl.trace.BlackBox:   85  _Repeat(1:1:d)                   1.8   (00008) '333325...'   ['3', '3', '3', '3', '2', '5', '3']
  INFO:lepl.trace.BlackBox:   86  Apply(...)                       1.8   (00008) '333325...'   ['3333253']
  INFO:lepl.trace.BlackBox:   87  And                              1.8   (00008) '333325...'   ['3333253']
  INFO:lepl.trace.BlackBox:   88  Apply(Add)                       1.8   (00008) '333325...'   ['3333253']
  INFO:lepl.trace.BlackBox:   89  Empty(-phone)                    1.8   (00008) '333325...'   []
  [{'phone': '3333253', 'name': 'andrew'}]


.. _epoch:

Epoch
-----

.. index:: epoch

A word of warning --- despite the examples here, epoch doesn't always increase
by exactly 1 per match.  It is guaranteed to increase between matches, but is
used internally for labelling various events and may "jump" by unpredictable
(but positive) values.
