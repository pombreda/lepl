
Debugging
=========

.. index:: debug, errors

When a parser fails to match some text it can be difficult (slow, frustrating
work) to undertand why.  Fortunately, LEPL includes some features that can
make life easier.

**Note:** This section does not describe "known errors" (for example,
generating an error message for the user when they enter text that is wrong in
an expected way).  That issue is addressed in ....  What is discussed here are
the "unknown errors" you face when a parser fails to work with good input.


Deepest Matches
---------------

.. index:: longest match, print_longest()

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

  >>> name    = Word()              > 'name'
  >>> phone   = Integer()           > 'phone'
  >>> line    = name / ',' / phone  > make_dict
  >>> matcher = line[0:,~Newline()]
  >>> stream = Stream.from_string('andrew, 3333253\n bob, 12345', memory=(4,2,2))
  >>> next(matcher(stream))
  ([{'phone': '3333253', 'name': 'andrew'}], Chunk('andrew, 3333253\n'...)[15:])

  >>> stream.core.bb.print_longest()
  Up to 4 matches before and including longest match:
    119  Literal('\n')          15:'\n bob,'...   ['\n']
    120  Or                     15:'\n bob,'...   ['\n']
    121  Apply(Drop)            15:'\n bob,'...   [[[]]]
    122  Any(' \t')             16:' bob, '...   [' ']
  Up to 2 failures following longest match:
    123  Lookahead              16:' bob, '...   fail
    124  And                    16:' bob, '...   fail
  Up to 2 successful matches following longest match:
    137  Repeat(1::,...)         8:'333325'...   ['3', '3', '3', '3', '2', '5']
    138  Apply(Add)              8:'333325'...   [['333325']]
  Epoch  Matcher                 Stream          Result

The left column (Epoch) is a counter that increases with time.  The next
column is that matcher, which may also display some extra useful information.
After that comes the stream (character offset and a sample of the next text to
match).  Finally, on the right, is the result or, on failure, "fail".

Lines are generated "at the end" of matching, so the innermost of a set of
nested matchers is shown first.

Looking at the output we can see that the longest match was a whitespace,
presumably associated with the ``Lookahead`` failure.  So "anything but a
whitespace" failed, which is the likely definition of ``Word``.  Comparing
that with our grammar, we can see that ``name`` is failing because of the
space before "bob".


Trace Output
------------

.. index:: trace, Trace(), logging

The same matching data can also be displayed to the logs with the ``Trace``
matcher.  This takes a matcher as an argument, along with some optional text.
Tracing is then enabled when the selected matcher is called::

  >>> from logging import basicConfig, INFO

  >>> basicConfig(level=INFO)
  >>> name    = Word()                   > 'name'
  >>> phone   = Trace(Integer(), 'here') > 'phone'
  >>> line    = name / ',' / phone       > make_dict
  >>> matcher = line[0:,~Newline()]
  >>> matcher.parse_string('andrew, 3333253\n bob, 12345')
  INFO:lepl.trace.BlackBox:   95  Empty(+here)            8:'333325'...   []
  INFO:lepl.trace.BlackBox:   96  Any('+-')               8:'333325'...   fail
  INFO:lepl.trace.BlackBox:   97  Repeat(0:1:)            8:'333325'...   []
  INFO:lepl.trace.BlackBox:   98  Any('0123456789')       8:'333325'...   ['3']
  INFO:lepl.trace.BlackBox:   99  Any('0123456789')       9:'333253'...   ['3']
  INFO:lepl.trace.BlackBox:  100  Any('0123456789')      10:'33253\n'...   ['3']
  INFO:lepl.trace.BlackBox:  101  Any('0123456789')      11:'3253\n '...   ['3']
  INFO:lepl.trace.BlackBox:  102  Any('0123456789')      12:'253\n b'...   ['2']
  INFO:lepl.trace.BlackBox:  103  Any('0123456789')      13:'53\n bo'...   ['5']
  INFO:lepl.trace.BlackBox:  104  Any('0123456789')      14:'3\n bob'...   ['3']
  INFO:lepl.trace.BlackBox:  105  Any('0123456789')      15:'\n bob,'...   fail
  INFO:lepl.trace.BlackBox:  106  Any('0123456789')      14:'3\n bob'...   fail
  INFO:lepl.trace.BlackBox:  107  Any('0123456789')      13:'53\n bo'...   fail
  INFO:lepl.trace.BlackBox:  108  Any('0123456789')      12:'253\n b'...   fail
  INFO:lepl.trace.BlackBox:  109  Any('0123456789')      11:'3253\n '...   fail
  INFO:lepl.trace.BlackBox:  110  Any('0123456789')      10:'33253\n'...   fail
  INFO:lepl.trace.BlackBox:  111  Any('0123456789')       9:'333253'...   fail
  INFO:lepl.trace.BlackBox:  112  Any('0123456789')       8:'333325'...   fail
  INFO:lepl.trace.BlackBox:  113  Repeat(1::,...)         8:'333325'...   ['3', '3', '3', '3', '2', '5', '3']
  INFO:lepl.trace.BlackBox:  114  Apply(Add)              8:'333325'...   [['3333253']]
  INFO:lepl.trace.BlackBox:  115  And                     8:'333325'...   [['3333253']]
  INFO:lepl.trace.BlackBox:  116  Apply(Add)              8:'333325'...   [[['3333253']]]
  INFO:lepl.trace.BlackBox:  117  Empty(-here)            8:'333325'...   []
  ...



Epoch
-----

.. index:: epoch

A word of warning --- despite the examples here, epoch doesn't always increase
by exactly 1 per match.  It is guaranteed to increase between matches, but is
used internally for resource management and may "jump" by unpredictable (but
positive) values.
