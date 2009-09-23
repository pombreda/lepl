
.. index:: recursive descent, generators, stack, parser combinators, implementation
.. _implementation:

Implementation
==============

LEPL is, in many ways, a very traditional recursive descent parser.  This
chapter does not describe the basic ideas behind recursive descent parsing
[*]_.  Instead I will focus on the details that are unique to this particular
implementation.

.. [*] There is a broad--bush description of how matchers work in
       :ref:`implementation_details`.
   

.. index:: trampolining
.. _trampolining:

Trampolining
------------

A typical recursive descent parser uses at least one stack frame for each
recursive call to a matcher.  Unfortunately, the default Python stack is
rather small and there is no optimisation of tail--recursive calls.  So the
degree of recursion is limited.  This problem is exacerbated by a "clean",
orthogonal design that constructs matchers in a hierarchical manner
(eg. `Word() <api/redirect.html#lepl.Word>`_ calls, `Any()
<api/redirect.html#lepl.Any>`_ to handle character matching; memoisation uses
nested matchers to manage caches).

Trampolining removes this limitation by moving evaluation to a separate
function, which manages the evaluation sequence separately from the program
stack.

A trampolining implementation would typically use a continuation passing
style, but Python supports co--routines (via extended generators) which
automate the encapsulation of a local environment.  Trampolining then becomes
a simple loop that repeatedly evaluates co-routines stored in a stack
allocated on the heap.

The conversion from nested functions to trampolining with generators involves
little more than replacing evaluation with ``yield`` (which presents the
target to the trampoline function for evaluation).

Trampolining is most visible in the source in two areas:

#. The `trampoline() <api/redirect.html#lepl.parser.trampoline>`_ function is
   the main evaluation loop.

#. Each matcher in the `matchers <api/redirect.html#lepl.matchers>`_ package
   is modified to ``yield`` sub-matchers rather than evaluating them directly.

The second case above, individual matchers, nearly always follows the same
pattern.  Code that originally looked like::

  def _match(self, stream1):
    (result, stream2) = self.matcher._match(stream1)
    # do something here (eg process results)
    yield (result, stream2)

where the submatcher (``self.matcher``) is invoked and the result modified,
becomes::

  def _match(self, stream1):
    (result, stream2) = yield self.matcher._match(stream1)
    # do something here (eg process results)
    yield (result, stream2)
    
The first ``yield`` returns the generator (constructed by ``._match(stream)``)
to the trampoline.  This is then evaluated (which may mean evaluating other
generators, yielded by the generator we returned), and the final result
returned to the matcher from the trampoline via ``generator.send(result,
stream2)``.

It is clear, then, that during the transition from versions 1 to 2 (when
trampolining was introduced), the impact on existing code was fairly small.


.. index:: memoisation, Norvig, Frost, Hafiz, left-recursion
.. _memoisation_impl:

Memoisation
-----------

The simple memoizer, `RMemo() <api/redirect.html#lepl.memo.RMemo>`_, is
equivalent to the approach described by `Norvig 1991
<http://acl.ldc.upenn.edu/J/J91/J91-1004.pdf>`_ (I may be mistaken, because it
seems odd that something so simple is so famous, but perhaps life was simpler
back then).

During the application of left--recursive grammars a matcher may be called with
the same stream, but within different contexts (eg. consider ``a = Optional(a)
& b``, where each repeated call to ``a`` is from an additional "step down").

.. warning::

   Without memoisation left recursion will cause an infinite loop and crash the
   program.

`Frost and Hafiz 2006 <http://www.cs.uwindsor.ca/~hafiz/p46-frost.pdf>`_
observed that there is a natural limit to the number of times left recursion
can be meaningful, which is the length of the remaining input (since you have
to consumer `something` each time round).  They therefore recommended
extending the simple cache with a counter that blocks recursion past that
depth.

This approach is implemented in `LMemo() <api/redirect.html#lepl.memo.LMemo>`_
which makes LEPL robust to left--recursive grammars.


.. index:: rewriting, graph, flattening

Parser Rewriting
----------------

A parser is constructed from a set matchers that form a directed (possibly
cyclic) graph.  By storing the constructor arguments for the matcher objects
(and knowing their types, which are constructors in Python) we can reconstruct
(and, more generally, rewrite) the graph.

The base classes for the graph are in the `graph
<api/redirect.html#lepl.graph>`_ package (the `node
<api/redirect.html#lepl.node>`_ package, used for ASTs, builds on these
classes so many of the tools used internally within LEPL may also be useful to
process ASTs).  Matcher graph rewriting occurs during parser construction
(see the `parser <api/redirect.html#lepl.parser>`_ package).

Parser rewriting allows memoisation to be transparently added to all nodes,
for example.

Tree traversal (without rewriting) is also useful; it is used to generate
various textual representations of the matchers (and the pretty ASCII trees
for ASTs).


.. index:: streams, SimpleStream(), LocationStream(), StreamFactory()
.. _streams:

Streams
-------

LEPL can process simple strings and lists, but it can also use its own stream
abstraction, which implements the `LocationStream()
<api/redirect.html#lepl.stream.LocationStream>`_ interface.  This tracks the
position of each character within the source (useful for errors and, in the
future, parsing with the "offside rule").

Streams are created automatically by methods like `parse_string()
<api/redirect.html#lepl.matchers.OperatorMatcher.parse_string>`_,
`string_parser()
<api/redirect.html#lepl.matchers.OperatorMatcher.string_parser>`_,
`match_string()
<api/redirect.html#lepl.matchers.OperatorMatcher.match_string>`_,
`string_matcher()
<api/redirect.html#lepl.matchers.OperatorMatcher.string_matcher>`_ etc.  But
the methods `parse()
<api/redirect.html#lepl.matchers.OperatorMatcher.parse>`_, `null_parser()
<api/redirect.html#lepl.matchers.OperatorMatcher.null_parser>`_, `match()
<api/redirect.html#lepl.matchers.OperatorMatcher.match>`_, `null_matcher()
<api/redirect.html#lepl.matchers.OperatorMatcher.null_matcher>`_ do not do so.

The streams are created by a `StreamFactory()
<api/redirect.html#lepl.stream.StreamFactory>`_ which is supplied by the
`Configuration() <api/redirect.html#lepl.config.Configuration>`_, so it is
possible for a user (or a package that provides a custom configuration) to
replace the stream implementation that is used.
