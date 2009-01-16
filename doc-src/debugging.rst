
Debugging
=========

When a parser fails to match some text it can be difficult (and slow,
frustrating work) to undertand why.  Fortunately, LEPL includes some features
that can make life easier.

**Note:** This section does not describe "known errors" (for example,
generating an error message for the user when they enter text that is wrong in
an expected way).  That issue is addressed in ....  What is discussed here are
the "unknown errors" you face when a parser fails to work with good input.


Deepest Matches
---------------

It is often useful to know what the last successful match was before the
parser failed.  More exactly, because backtracking will probably find other
matches before the top-most matcher fails completely, it is useful to know the
'longest' match --- the match that consumes as much of the input as possible.

The following code is similat to that used in the `Introduction`_, but fails to
match the given input.  It has been modified to print information about the
longest match::

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
    121  Apply                  15:'\n bob,'...   []
    122  Any(' \t')             16:' bob, '...   [' ']
  Up to 2 failures following longest match:
    123  Lookahead              16:' bob, '...   fail
    124  And                    16:' bob, '...   fail
  Up to 2 successful matches following longest match:
    137  Repeat                  8:'333325'...   ['3', '3', '3', '3', '2', '5']
    138  Apply                   8:'333325'...   ['333325']
  Epoch  Matcher                 Stream          Result
