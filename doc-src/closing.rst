
Closing Remarks
===============


Supported Versions
------------------

The code was written using Python 3.0.  It was then backported to Python 2.6
and appears to work fine there (except that the ``//`` operator doesn't
exist).  It might even work with Python 2.5 if you add appropriate ``from
__future__ import ...`` in various places (you could make the ``Matcher`` ABC
a simple class without really harming anything).

However, it's not regularly tested on anything other than 3.0...


Licence
-------

Licensed under the Lesser Gnu Public Licence.  Copyright 2009 Andrew Cooke
(andrew@acooke.org).


Technical Summary
-----------------

.. index:: recursive descent, generators, stack, parser combinators

In the chapters above I have tried to explain LEPL without mentioning any
"theoretical" details.  Now I am going to jump ahead and give a short,
technical description that requires a lot more background knowledge.  The aim
here is to show experts how the system is implemented; you do not need to
understand this section to use LEPL.

LEPL is, at heart, a recursive descent parser.  It owes much to standard
parser combinator libraries in functional languages.  For example, each
matcher takes a stream as an argument and, on success, returns a tuple
containing a list of matches and a new stream.  

However, LEPL also exploits Python in two ways.  First, it overloads operators
to provide a large helping of syntactic sugar (operators simply apply more
combinators, so ``a | b`` is equivalent to ``Or(a, b)``).  Second, generators
are used to manage backtracking.

Consistent use of generators means that the entire parser can backtrack
(typically recursive descent parsing restricts backtracking to ``Or(...)``).
It also reduces the use of the C stack (naturally replacing recursion with
iteration) and allows the environmental cost of backtracking to be managed
(generators can be tracked and closed, effectively reclaiming resources on the
"stack"; the same mechanism can implement "cut").


Search
------

Since LEPL supports full backtracking via generators it is possible to request
all the alternative parses for a given input::





Credits
-------

.. index:: Tim Peters, Sam Wilmott, Pattern Matching in Python, Guy Cousineau,
           Michel Mauny, PyParsing, Paul McGuire

Blame Tim Peters' `test_generators.py
<http://www.koders.com/python/fid9B99238B5452E1EDA851459C2F4B5FD19ECBAD17.aspx?s=mdef%3Amd5>`_
for starting me thinking about this, but that would have got nowhere without Sam
Wilmott's `Pattern Matching in Python
<http://www.wilmott.ca/python/patternmatching.html>`_ from which I have
stolen almost everything (including the repetition syntax).

`PyParsing <http://pyparsing.wikispaces.com/>`_ was also a major motivation
(if you don't like the way LEPL handles spaces, you may prefer Paul McGuire's
package which is, I think, pretty much the standard for simple, recursive
descent Python parsers).

Finally, thanks to `Guy Cousineau and Michel Mauny
<http://books.google.cl/books?hl=en&id=-vQPDXciXUMC&dq=cousineau+mauny>`_ for
the original education.



Endnote
-------

LEPL was written as Israel largely destroyed Gaza.
