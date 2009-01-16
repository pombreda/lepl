
LEPL - A Parser Library for Python
==================================

Using LEPL you can describe how some text is structured and then generate
Python data (lists, dicts, and even trees of objects) with the text in that
form.  It is intended to be simple and easy to use, but also has some features
that may interest advanced users, including full backtracking.

LEPL's *weakest* point is probably performance.  It is intended more for
exploratory and one--off jobs than, for example, a compiler front--end; it
values your time, as a programmer, over CPU time (or, less favourably, the
time of the end--user).

The `API documentation <../api/index.html>`_ is also available.

Contents:

.. toctree::
   :maxdepth: 2

   intro
   matchers
   operators
   nodes
   resources
   debugging
   credits

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

