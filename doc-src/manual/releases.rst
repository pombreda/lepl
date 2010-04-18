
Release History
===============


Summary
-------

==========  =======  ===========
Date        Version  Description
==========  =======  ===========
2009-01-29  1.0b1    Fighting with setuptools etc.
----------  -------  -----------
2009-01-29  1.0b2    Now with source, documentation and inline licence.
----------  -------  -----------
2009-01-30  1.0b3    Fixed version number confusion (was 0.1bx in some places).
----------  -------  -----------
2009-01-31  1.0rc1   With support.
----------  -------  -----------
2009-02-04  1.0      No significant changes from rc1.
----------  -------  -----------
2009-02-23  2.0b1    New trampolining core; matcher graph rewriting; memoisation.
----------  -------  -----------
2009-03-04  2.0b2    Fixed major bug in LMemo for 2.6; general tidying.
----------  -------  -----------
2009-03-05  2.0      Improved documentation.
----------  -------  -----------
2009-03-05  2.0.1    Fixed stupid bug introduced at last minute in 2.0.
----------  -------  -----------
2009-03-06  2.0.2    A few more small bug fixes.
----------  -------  -----------
2009-03-08  2.1b     Improved efficiency.
----------  -------  -----------
2009-03-08  2.1      Minor bugfixes and documentation.
----------  -------  -----------
2009-03-12  2.1.1    Fix flatten() and compose_transforms(); remove GeneratorManager from default configuration.
----------  -------  -----------
2009-03-27  2.2      Added >=, String(), regexp framework.
----------  -------  -----------
2009-04-05  2.3      Compilation to regular expressions.
----------  -------  -----------
2009-04-05  2.3.1    Fix regexp packaging.
----------  -------  -----------
2009-04-05  2.3.2    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.3    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.4    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.5    Make all classes new style in 2.6.
----------  -------  -----------
2009-05-02  2.4      Added lexer.
----------  -------  -----------
2009-06-27  3.0a1    New tutorial; bin package; modified Nodes, `*args` (general clean-up of API).
----------  -------  -----------
2009-07-04  3.0a2    Various small fixes via pylint.
----------  -------  -----------
2009-07-07  3.0b1    Smart separators.
----------  -------  -----------
2009-07-07  3.0b2    Fix packaging issues with b1.
----------  -------  -----------
2009-07-16  3.0b3    More packaging issues (switched to distutils; bundling tests and examples).
----------  -------  -----------
2009-07-16  3.0      New tutorial; bin package; smart separators; modified Nodes, `*args` (general clean-up of API).
----------  -------  -----------
2009-08-19  3.1      Rewritten streams.
----------  -------  -----------
2009-09-05  3.2      Clone bugfix.
----------  -------  -----------
2009-09-09  3.2.1    Clone bugfix bugfix.
----------  -------  -----------
2009-09-13  3.3b1    Whitespace sensitive parsing (no documentation).
----------  -------  -----------
2009-09-23  3.3      Whitespace sensitive parsing.
----------  -------  -----------
2009-11-22  3.3.1    Regexp bugfixes.
----------  -------  -----------
2009-11-22  3.3.2    Regexp bugfixes (correct self-test).
----------  -------  -----------
2009-12-10  3.3.3    Various small tweaks based on user feedback.
----------  -------  -----------
2009-04-03  4.0b1    Broad revision, simplification.
----------  -------  -----------
2009-04-16  4.0      Broad revision, simplification.
----------  -------  -----------
2009-04-18  4.0.1    Small bugfix for left-recursive, whitespace sensitive grammars (hash).
----------  -------  -----------
2009-04-18  4.0.2    Small bugfix for left-recursive, whitespace sensitive grammars (equality).
==========  =======  ===========


.. release_4_0:

4.0
---

See :ref:`Lepl 4 - Simpler, Faster, Easier <lepl4>`.


.. release_3_3:

3.3, 3.3.3
----------

This supports :ref:`line--aware <offside>` parsing.  3.3.3 includes various
small improvements based on user-feedback.


.. release_3_2:

3.2, 3.2.1
----------

A bugfix release to correct a problem with cloning matchers.  3.2 is a minor
release (rather than a 3.1.1 bugfix release) because it also includes
significant internal changes as I work towards supporting
whitespace-significant ("offside rule") parsing.


.. release_3_1:

3.1
---

A fairly small set of changes, focussed on the :ref:`streams <streams>` that
can be used to "wrap" input (instead of parsing a string or list directly).
These have a clearer design (although remain, unfortunately, complex), are
better documented, with clearer interfaces (abstract classes), and will (I
hope) support handling the "offside rule" in a later release.

.. warning::

  Although this is a minor release, some of the "public" has API changed.
  These changes are generally in areas that I believe are not commonly used,
  but you should check that code still runs after upgrading.  Perhaps the most
  likely problem is that `parse_list()` has become `parse_items()
  <api/redirect.html#lepl.matchers.OperatorMatcher.parse_items>`_ to emphasise
  that it is for sequences of "characters" (in contrast, for example, to parse
  a list of "lines", use `parse_lines()
  <api/redirect.html#lepl.matchers.OperatorMatcher.parse_lines>`_; characters
  and lines refer to whether `Any() <api/redirect.html#lepl.matchers.Any>`_
  should match all or part of an entity, respectively).


.. release_3_0:

3.0
---

This release is based on two quite separate themes, both of which have
required modifications to the Lepl core code to the extent that a new major
version is necessary.

First, the handling of whitespace has been revised, extended, and documented.
The preferred approach in most cases, using the :ref:`lexer`, is described in
detail in a new :ref:`tutorial <tutorial>`.  In addition, for those cases
where spaces are significant, :ref:`columns <table_example>` and two new
:ref:`"smart separators" <spaces>` have been added.

The separator work highlighted a source of confusion in the standard matchers:
many used ``&`` and ``[]``, which are modified by separators.  As a
consequence, the library was revised to remove all these uses.  Separators
should now only affect spaces in a clearly predictable way (there is a small
trade-off between usefulness and predictability; the library is now more
predictable, which is probably for the best).

The second theme is the parsing of :ref:`binary data <binary>`.  This is
somewhat obscure, but provides some fairly original functionality (with room
for significant expansion in future releases).

While writing the binary parser I needed to revisit and revise core routines
related to graphs.  Various internal interfaces have been simplified; the most
visible being the `Node() <api/redirect.html#lepl.support.node.Node>`_ class, which is now more "Pythonesque".
