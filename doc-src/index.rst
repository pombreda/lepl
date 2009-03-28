
LEPL - A Parser Library for Python 3 (and 2.6)
==============================================

LEPL is a recursive descent parser, written in Python, which has a a friendly,
easy--to--use syntax (:ref:`example`).  The underlying implementation includes
several features that make it more powerful than might be expected.

For example, it is not limited by the Python stack, because it uses
trampolining and co--routines.  Multiple parses can be found for ambiguous
grammars and it can also handle left--recursive grammars.

The aim is a powerful, extensible parser that will also give solid, reliable
results to first--time users.

This release (2.2) adds :ref:`>= <ge>` and `String()
<api/redirect.html#lepl.matchers.String>`_, fixes a few bugs, and introduces a
new pure--Python regular expression framework (which will be put to use in the
next release).


Contents
--------

.. toctree::
   :maxdepth: 2

   overview
   started
   matchers
   operators
   nodes
   errors
   resources
   debugging
   advanced
   style
   download
   implementation
   examples
   closing


Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

