
Style
=====

Remember that operators are just shorthand for matchers (``&`` instead of
``And()`` etc)

Use ``Or(..., ..., ...)`` for alternatives with productions.  The ``|`` syntax
can lead to errors because it binds more tightly than ``>``.

Nodes are typically made with constructors and invoked with ``>``, while the
processing of results is usually done with mapped functions.  So ``>`` is
followed by a Capitalized name, while ``>>`` is followed by a lowercase name.
Noticing and following this convention can help avoid issues with the
behaviour of `lepl.match.Apply` with ``raw=False`` (the default implementation
of ``>``), which adds an extra level of nesting and is usually inappropriate
for use with functions.

Imports
-------

The most commonly used classes are exposed via the ``lepl`` module, so simple
scripts can use::

  from lepl import *

