
.. _lepl4:

Lepl 5 - Better Shape for the Future
====================================

I've simplified how Lepl handles strings (or lists, or iterables, or...).  As
a consequence, some of the API has changed.  So moving from Lepl 4 to 5 may
break your code.  I'm sorry!  But hopefully it should be easy to fix (see
below) and, once running again, should be a little faster.

In the longer term these changes help me maintain Lepl and continue to expand
it.

As part of the stream work I also revisited how Lepl handles left-recursive
grammars.  This resulted in me being less confident of the approach used and
led to additional changes.

The Big Picture
---------------

Understanding what happened "under the hood" may explain the API changes.  But
if you'd rather just have a list of issues please skip to the next section.

Originally, Lepl pretended that all inputs were strings.  Indeed, it was
possible (using ``parse_null()``) to send a string directly to the matchers:
each matcher then passed a new string, containing whatever remained to be
parsed, to the next matcher.

In practice, however, that wasn't so useful.  For example, there was no way to
tell how far you are through the data.  So in most cases (ie. using
``parse()``) Lepl contructed a wrapper that carried the string and the extra
location information together, but which still looked sufficiently string-like
for the matchers to work correctly.

This solved the problem of knowing where you were, but made the code more
complicated.  To avoid duplicating that complex code I used the same wrapper
for many different input types.  And that only made things more complicated.
Worse, the "strings" slowly accumulated extra non-string methods to do other
useful things.

Eventually it became clear that pretending that things were strings when they
were not was a bad idea.  The extra complexity of defining an interface for "a
stream of input data" might complicate matchers a little, but made everything
else too brittle.

Hence Lepl 5, in which I dropped the pretense that the input is "just" a
string.  Instead, matchers work with a "stream" using functions like
``s_next()`` to get the next character, or ``s_line()`` to read a line.

You may be surprised to hear that those are functions, and not objects, so I
will take a moment to explain a little of the implementation.  A stream is now
implemented as a tuple; a pair of values.  The first value is "state" and the
second value is a "helper".  Exactly what the state and helper are depend on
the input, but the helper must implement a standard interface and the
``s_...()`` functions call that interface with the state.

That sounds more complex than it is.  Essentially::

    def s_next(stream):
        (state, helper) = stream
	return helper.next(state)

and the reason for *that* is efficiency.  For a string, for example, state is
the current index into the string.  So every time the stream advances (and
this happens a *lot*) we only have to contruct a new tuple with a different
integer value.  The helper remains the same (in the case of a string it's a
simple wrapper round the the string itself).  This is much more efficient than
constructing a new, heavyweight object at every step.

Changes
-------

OK, so what has changed?  Here is a list of the non-left-recursive changes:

* Some ``parse()`` methods have changed.  ``parse_null()`` no longer exists
  (see above; ``parse_sequence()`` might be the best replacement) and instead
  of ``parse_items()`` you will probably want either ``parse_list()`` (for
  lists) or ``parse_iterable()`` (for iterables).  This is because the new
  helpers (see above) divide the input in slightly different ways to before.

* The idea of a *line* is more clearly defined.  This has two effects:

  * You may need to care more about which ``parse()`` method to use.  A list
    or sequence (the only difference between those is that the formatting for
    displaying lists is a little prettier) treats all the data as one line,
    but a string uses the newline (``'\n'``) character to define lines.  And
    an iterable assumes that each value is a new line (which matches the way
    iterating over files works).  In most cases the generic ``parse()`` will
    do the right thing for you by dispatching on type.

  * Regular expressions don't match across lines.  There is no way to pass a
    general "stream" to regular expressions, so I pass a "line" instead.  If
    you really want to match multiple lines in a string then use
    ``parse_sequence()`` which, as I just explained, treats the entire input
    as a single line.

* ``parse_items()`` had an option to add an extra list around each value.
  This is not present in ``parse_list()`` because the way that a character is
  accessed has changed.  In Lepl 4 the first character was ``stream[0]``, but
  in Lepl 5 it is ``stream[0:1]``.  This has no impact on strings, but for
  lists it fixes a subtle bug (the problem was a confusion between "first
  character" and "a sub-section of the input stream containing the first
  character" - the latter is what is actually needed).

* Line-aware and offside parsing have changed.  These should make things
  simpler and more consistent:

  * For configuration, use ``config.lines()`` or ``config.blocks()``.

  * Lines are now handled by adding extra tokens (before the lexer added extra
    *characters* which were then matched by special tokens).  That means that
    you can no longer match ``(*SOL*)`` and ``(*EOL*)`` in regular
    expressions (more generally, you must use tokens with line aware and
    offside parsing - before it was technically possible to not do so).

  * In offside parsing (ie. when you are using ``Block()``), you should
    *never* use ``Line()``.  Always use ``BLine()``.  If you want to ignore
    indentation (eg. for empty lines) then use ``Bline(indent=False)``.  So
    replace ``Line(Empty())`` with ``BLine(Empty(), indent=False)``.

* The values available when generating an error message inside the parser have
  changed.  The value names are LINK, and typically are prefixed by ``in_``
  and ``out_`` for the input and output streams.  See also LINK.

* The configuration for "managed generators" has changed from
  ``config.manage()`` to ``config.low_memory()``.  This also adds some
  additional settings that are needed to reduce memory use and restricts the
  size of "secondary" stacks used in search / repetition.  The result is that
  Lepl really can handle inputs larger than available memory - ADD LINK.

* If you define your own matchers you will need to use ``s_next()`` and
  friends instead of accessing the "string".  So replace::
      char = stream[0]
      next_stream = stream[1:]
  with ``(char, next_stream) = s_next(stream)``.  The full set of functions is
  documented at LINK and the source is full of examples.

* `TraceResults() <api/redirect.html#lepl.core.trace.TraceResults>`_,
  configured by ``config.trace()``, is now ``TraceStack()``, configured by
  ``config.trace_stack()``.
  

* Repetition joins values using a "repeat" operator.  By default this joins
  lists, as before, but you can redefine it to define a fold over results.  I
  use this in the large memory example (ADD LINK) which explains the idea in a
  little more detail.

* (Implementation detail) The "wrapper" around tampolining matchers is no
  longer "transformable".  This should have no effect on your code unless you
  are looking at the detailed structure of the matcher tree (it should make
  your code faster as it removes the need to call a generator that does
  nothing but call another generator - something anyone who has watched Lelp
  in a debugger cannot fail to have wondered about...)


Left Recursion
--------------

As I modified the stream code I extended checks related to memoisation and
caching.  This, together with reading a paper ("Memoization in Top Down
Parsing" by Mark Johnson - http://citeseer.ist.psu.edu/580468.html) convinced
me that Lepl's support for left recursion has never been complete (in fact,
Lepl 4 was broken quite seriously).

I will describe Lepl's memoisation algorithm in detail below, but first a
summary of the changes:

* The default configuration now *includes* memoisation for right-recursive
  grammars.  This can be removed with ``config.no_memoize()``.  It is added by
  default because it detects left-recursive grammars (which would otherwise
  loop indefinitely) and raises an error with helpful text.

* To enable handling of (some) left-recursive grammars, the simplest option is
  to use ``config.auto_memoize()`` which will add `LMemo() <api/redirect.html#lepl.matchers.memo.LMemo>`_ caches where
  required and also call ``config.optimize_or()`` to reduce immediate
  left-recursive calls.

* For more detailed control, you can also use:

  * ``config.left_memoize()`` -  add `LMemo() <api/redirect.html#lepl.matchers.memo.LMemo>`_ everywhere

  * ``config.auto_memoize(full=True)`` - add `RMemo() <api/redirect.html#lepl.matchers.memo.RMemo>`_ in addition to
    `LMemo() <api/redirect.html#lepl.matchers.memo.LMemo>`_.

  * ``config.no_optimize_or()`` - don't re-arrange `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ contents.

  * ``config.optimize_or(conservative=True)`` - re-arrange `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ contents
    even on non-critical loops.

The memoisation code does the following:

* Wrappers (LMemo class) are added to critical points in the matcher DAG.  By
  default only the loops that pass through the leftmost matchers are adjusted
  (other paths will presumably consume input in other matchers on each loop),
  but specifying left_memoisation() in the configuration will instrument all
  loops.

* When the parser is invoked, LMemo wrappers create "per-stream caches"
  (PerStreamCache class) for each input stream.  Repeated calls to a
  particular wrapper with the same input will be delegated to the same
  per-stream cache (Note that "per-stream cache" is a misnomer as there is
  another layer of indirection to come).

* The per-stream cache has two states.  In the initial state, on each call, it
  generates a new "per-call cache" that delegates to the underlying matcher
  and caches the results.  At this point results are cached but the cache is
  not used to restrict calls.  The intuition here is that these are recursive
  instances of the call "already being handled".

* In this state it is possible for a left-recursive call to repeatedly
  generate per-call caches as it loops without consuming input.  The
  per-stream cache detects this and restricts the number of possible loops to
  the length of the available input stream.  This is based on the approach
  described in Frost and Hafiz 2006.  Calls after this limit immediately fail
  to match.

* When the *first* per-call cache completes (ie the cache contains all
  available results) the per-stream cache transitions to the second state.  In
  this state new calls receive values from the completed per-call cache.

* In the second state, the limiting on stream length is no longer necessary.

Note that the above is *not* guaranteed to work in all circumstances; even
when it does work it may be inefficient.  The only safe way to parse with Lepl
is to use a right-recursive grammar.



Further Reading
---------------

* `Front Page <index.html>`_
* :ref:`manual`
* :ref:`tutorial`
* :ref:`contents`
