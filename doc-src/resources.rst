
.. index:: resources
.. _resources:

Resource Management
===================


.. index:: Stream, Core, memory, file, StreamMixin

Streams
-------

LEPL can process simple strings and lists, but it can also use its own `Stream
<../api/redirect.html#lepl.stream.Stream>`_ class as a wrapper for the input.
There are two advantages to doing this:

#. When reading from a file, the stream will not keep more data in memory than
   is necessary, so files larger than the available memory can be processed.

#. The stream provides access to the central `Core
   <../api/redirect.html#lepl.core.Core>`_ instance, which is necessary for
   :ref:`debugging`, :ref:`limiting`, and :ref:`committing`.

Streams are most simply created by using the ``parse...`` and ``match...``
methods that all matchers implement via `StreamMixin
<../api/redirect.html#lepl.stream.StreamMixin>`_.


.. index:: GeneratorWrapper, backtracking, generators

Generator Management
--------------------

.. warning::

  The functionality to limit the number of generators described in the
  following sections is not well understood.  The implementation is more
  complex than I would like and during development some unit tests changed
  results in a way that I cannot explain.

  By default these features are disabled --- the depth of searches is
  unrestricted.

:ref:`backtracking` within LEPL is implemented using generators.  These are
semi--autonomous *loop--like* blocks of code that can be paused and restarted.
Each matcher (in simple terms) has, at its core, a generator that provides
successive matches.  Backtracking means saving these generators for future use
--- if the current match fails then a new start can be made using the next
value from a stored generator.

Because generators may be long--lived they can be a resource sink.  For
example, they maintain references to "old" parts of the stream that might
otherwise be reclaimed by garbage collection.

The `Core <../api/redirect.html#lepl.core.Core>`_ is an object, created once
per stream, that provides a central location for managing information related
to a parse.  This information can be used for :ref:`debugging`, for example.

It is possible to configure the system so that the `Core
<../api/redirect.html#lepl.core.Core>`_ maintains a (weak) reference to the
generators [#]_ used in a parse.  A generator is registered when it is first
used.

Generators registered with the `Core <../api/redirect.html#lepl.core.Core>`_
may be active or inactive.  An active generator is one which is participating
in the current match.  This means that the program's thread of control is
"inside" the generator.  An inactive generator is one that is not currently in
use.  Inactive generators may have been discarded (for example, if they have
returned all possible matches), or they may be stored in some way for later
use (for example, to implement backtracking).

Generators also have a *last--used* date.  More exactly, they are associated
with the :ref:`epoch` when they were last used.

Given all this, it is possible to modify the generators and so change the
behaviour of the parser.  In particular, it is possible to close non--active
generators, either implicitly or explicitly.

.. [#] The discussion here omits some details from the implementation; the
       `Core <../api/redirect.html#lepl.core.Core>`_ actually stores
       `GeneratorWrapper
       <../api/redirect.html#lepl.resources.GeneratorWrapper>`_ instances,
       which are added to generators via the `managed
       <../api/redirect.html#lepl.resources.managed>`_ decorator.


.. index:: resources, min_queue
.. _limiting:

Resource Limiting
-----------------

The `Core <../api/redirect.html#lepl.core.Core>`_ can be configured to store a
limited number of generators.  When this number is exceeded, by the addition
of a new generator, the oldest (ie. least recently used) non--active generator
is closed.

.. warning::

  A closed generator is not available for backtracking, so prematurely closing
  generators may mean that an otherwise valid grammar fails to match
  successfully.

If all the current generators are active then no generator is discarded and
the upper limit on the number of generators increases to accomodate this.
Currently no attempt is made to later reduce the number back to the original
level.

To configure this limit use the ``min_queue`` parameter.  This can be supplied
on stream creation::

  >>> matcher = (Literal('*')[:,...][2] & Eos()).match_string()('*' * 4)
  >>> list(matcher)
  [(['****'],     Chunk('')[0:]), 
   (['***', '*'], Chunk('')[0:]), 
   (['**', '**'], Chunk('')[0:]), 
   (['*', '***'], Chunk('')[0:]), 
   (['****'],     Chunk('')[0:])]
  
  >>> matcher = (Literal('*')[:,...][2] & Eos()).match_string(min_queue=1)('*' * 4)
  >>> list(matcher)
  [(['****'],     Chunk('')[0:])]

It may not be clear what the rather compact expressions are doing above.  In
both cases two matchers, each of which can match 0 or more "*" characters, are
followed by the end of string test.  They are applied to a string containing
"\****".  With full backtracking all the different solutions (different ways
of splitting the "*" characters between the two matchers) are available.  When
the ``min_queue`` is set to a very low level generators are discarded whenever
possible, making backtracking impossible and providing just a single match.


.. index:: cut, prolog, min_queue
.. _committing:

Committing
----------

An alternative to the above, automatic management of generators, is to
explicitly remove non--active generators as part of the search process.  This
is similar to Prolog's *cut*, I believe.

The `Commit <../api/redirect.html#lepl.match.Commit>`_ matcher does this: it
discards all non--active generators from the `Core
<../api/redirect.html#lepl.core.Core>`_.

To enable `Commit <../api/redirect.html#lepl.match.Commit>`_ the ``min_queue``
parameter must be set.  If no :ref:`limiting` is needed, then a value of 0
(zero) should be used.

If this is useful, I'd really appreciate a good, short example to put here.
