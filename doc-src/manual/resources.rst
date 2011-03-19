
.. index:: resources
.. _resources:

Resource Management
===================

.. warning::

   This is no longer included in the manual (is linked to only from the
   features page).  It was dropped because it is not used, may be unreliable,
   and is not well supported.  However, tests still exist and continue to be
   maintained, and further support and development may be possible if there is
   a clear need.

.. index:: GeneratorWrapper, backtracking, generators

Generator Management
--------------------

.. note::

  To use the techniques described in this section the ``GeneratorManager()`` monitor must be added to
  the :ref:`configuration` using ``.config.manage()``.

:ref:`backtracking` within Lepl is implemented using generators.  These are
semi--autonomous *loop--like* blocks of code that can be paused and restarted.
Each matcher (in simple terms) has, at its core, a generator that provides
successive matches.  Backtracking means saving these generators for future use
--- if the current match fails then a new start can be made using the next
value from a stored generator.

Because generators may be long--lived they can be a resource sink.  For
example, they maintain references to "old" parts of the input that might
otherwise be reclaimed by garbage collection.

It is possible to configure the system with a ``GeneratorManager()`` that maintains a (weak)
reference to the generators [#]_ used in a parse.  A generator is registered
when it is first used.

Registered generators may be active or inactive.  An active generator is one
which is participating in the current match.  This means that the program's
thread of control is "inside" the generator.  An inactive generator is one
that is not currently in use.  Inactive generators may have been discarded
(for example, if they have returned all possible matches), or they may be
stored in some way for later use (for example, to implement backtracking).

Generators also have a *last--used* date.

Given all this, it is possible to modify the generators and so change the
behaviour of the parser.  In particular, it is possible to close non--active
generators, either implicitly or explicitly.

.. [#] The discussion here omits some details from the implementation.  The
       ``GeneratorManager()``
       actually stores ``GeneratorWrapper()`` instances, which
       are added to generators via the ``tagged`` decorator.


.. index:: resources, queue_len
.. _limiting:

Resource Limiting
-----------------

The ``GeneratorManager()``
can be configured to store only a limited number of generators.  When this
number is exceeded, by the addition of a new generator, the oldest (ie. least
recently used) non--active generator is closed.

.. note::

  A closed generator is not available for backtracking, so prematurely closing
  generators may mean that an otherwise valid grammar fails to match
  successfully.

If all the current generators are active then no generator is discarded and
the upper limit on the number of generators increases to accommodate this.
Currently no attempt is made to later reduce the number back to the original
level.

To configure this limit use the ``queue_len`` parameter::

  >>> matcher = (Literal('*')[:,...][2] & Eos())
  >>> list(matcher.parse_all('*' * 4))
  [(['****'],     ''), 
   (['***', '*'], ''), 
   (['**', '**'], ''), 
   (['*', '***'], ''), 
   (['****'],     '')]
  
  >>> matcher.config.mnager(queue_len=1)
  >>> list(matcher.parse_all('*' * 4))
  [(['****'],     '')]

It may not be clear what the rather compact expressions are doing above.  In
both cases two matchers, each of which can match zero or more "*" characters,
are followed by the end of string test.  They are applied to a string
containing "\****".  With full backtracking all the different solutions
(different ways of splitting the "*" characters between the two matchers) are
available.  When the ``queue_len`` is set to a very low level generators are
discarded whenever possible, making backtracking impossible and providing just
a single match.


.. index:: cut, prolog, queue_len, Commit()
.. _committing:

Committing
----------

An alternative to the above, automatic management of generators, is to
explicitly remove non--active generators as part of the search process.  This
is similar to Prolog's *cut*, I believe.

The ``Commit()`` matcher does
this: it discards all non--active generators.

For ``Commit()`` to work the
``GeneratorManager()`` must
maintain references to generators.  This occurs when the ``queue_len`` value
is 0, which stores references but does not cause :ref:`limiting`.

See also ``First()``.

If this is useful, I'd really appreciate a good, short example to put here.

