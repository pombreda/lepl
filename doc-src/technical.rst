Technical Summary
=================

.. index:: recursive descent, generators, stack, parser combinators

In the sections above I have tried to explain LEPL without mentioning any
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
