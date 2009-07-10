
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
==========  =======  ===========


.. release_3_0:

3.0
---

This release is based on two quite separate themes, both of which have
required modifications to the LEPL core code to the extent that a new major
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
visible being the `Node() <api/redirect.html#lepl.node.Node>`_ class, which is now more "Pythonesque".
