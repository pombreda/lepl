
Part 4 - Evaluation, Efficiency
===============================

Recap
-----

In the previous sections we have developed a parser that could generate a
simple AST for repeated addition and subtraction::

  >>> from lepl import *
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> expr = Delayed()
  >>> add = number & symbol('+') & expr > Node
  >>> sub = number & symbol('-') & expr > Node
  >>> expr += add | sub | number
  >>> expr.parse('1+2-3 +4-5', Configuration.tokens())
  [Node(...)]

(remember that I will not repeat the import statement in the examples below).

In this part of the tutorial we will extend this further, to handle
multiplication and parentheses.  Instead of calculating the value of the
expression as we parse the data we will improve our AST so that it can do the
calculation.

In a simple example like this the two approaches --- processing the results
while generating them, or waiting until afterwards and using the AST --- are
almost equivalent.  But in more complex cases it can be critical that we
separate the two phases.  This is because the processing of the results is
often a much more complicated job that parsing the initial data.

An example of this is an interpreter.  Parsing a program is only one small
step in executing it, and it would make the code for an interpreter needlessly
complicated if all the extra work of executing the program had to be done
during parsing.  So, instead, the parser constructs an AST that represents the
contents of the program in a way that is much easier for other parts of the
interpreter to understand.

.. index:: precedence, binding

Operator Precedence
-------------------

It's a common problem, especially when parsing things like programming
languages, that we need to handle groupings of different priorities.  For
example, in the expression "1 + 2 * 3", "2*3" groups more tightly than the
addition (so we get 7 and not 9 as the correct result).

With LEPL this priority is implicit in the parser.  Priority is determined by
structuring the recursive calls necessary for repeated handling of groups as a
series of layers.  Which is much easier to show than explain in words::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> group2, group3 = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3 & symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group1 & symbol('*') & group2 > Node
  >>> div = group1 & symbol('/') & group2 > Node
  >>> group2 += mul | div | group1

  >>> # third layer, least tightly grouped, is addition
  ... add = group2 & symbol('+') & group3 > Node
  >>> sub = group2 & symbol('-') & group3 > Node
  >>> group3 += add | sub | group2
  >>> ast = group3.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0]
  >>> print(ast)
  Node
   +- 1.0
   +- '+'
   `- Node
       +- Node
       |   +- 2.0
       |   +- '*'
       |   +- '('
       |   +- Node
       |   |   +- 3.0
       |   |   +- '-'
       |   |   `- 4.0
       |   `- ')'
       +- '+'
       `- Node
	   +- Node
	   |   +- 5.0
	   |   +- '/'
	   |   `- 6.0
	   +- '+'
	   `- 7.0

Note how each group can pass to the next, and how parentheses return back to
the first group, giving the overall recursion we need to handle nested groups.

.. index:: ambiguity, recursion, left recursion

Ambiguity and Left Recursion
----------------------------

.. note::

   This and the next section are fairly advanced.  You may want to skip
   them on a first read through.

It's easy, when showing a solution, to pretend that it's obvious and easy.
But try hiding the code above and then writing the parser yourself.  It's not
as simple as it looks.

In this section I will show two possible mistakes you can make (mistakes that
I made while testing the code for this tutorial).

The first mistake is the ordering of the definitions for ``group2`` and
``group3``.  The following code is almost identical, but gives a very
different result::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> group2, group3 = Delayed(), Delayed()
  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3 & symbol(')')
  >>> group1 = parens | number
  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group1 & symbol('*') & group2 > Node
  >>> div = group1 & symbol('/') & group2 > Node

  >>> group2 += group1 | mul | div      # changed!

  >>> # third layer, least tightly grouped, is addition
  ... add = group2 & symbol('+') & group3 > Node
  >>> sub = group2 & symbol('-') & group3 > Node

  >>> group3 += group2 | add | sub      # changed!

  >>> ast = group3.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0]
  >>> print(ast)
  1.0

This isn't as bad as it looks.  LEPL does find the result we are expecting,
it's just not the first result found, which is what ``parse()`` shows.  We can
see how many results are found::

  >>> len(list(group3.match('1+2*(3-4)+5/6+7', Configuration.tokens())))
  6

and it turns out the result we expect is the last one.

You can understand what has happened by tracing out how the text is matched:

* ``group3`` is defined as ``group2 | add | sub``, so ``group2`` is tried
  first (``Or()`` evaluates from left to right)

* ``group2`` is defined as ``group1 | mul | div``, so ``group1`` is tried
  first

* ``group1`` is defined as ``parens | number``, so ``parens`` is tried first

* ``parens`` fails to match, because the input does not start with "("

* so the next alternative in the ``Or()`` for ``group1`` is tried, which is
  ``number``

* ``number`` succeeds and has nothing following it

* returning back up the stack of pending matchers (``group1``, ``group2``,
  ``group3``), all have no following matcher, so the match is complete

.. warning::

   The exercise above, while useful, is not always completely accurate,
   because LEPL may modify the matchers before using them.  You are most
   likely to see this when using a grammar with left--recursion (see below)
   --- LEPL may re-arrange the order of matchers inside ``Or()`` so that the
   left--recursive case comes last.

   With the default configuration LEPL should always maintain the basic logic
   of the grammar --- the result will be consistent with the parser given ---
   but the order of the matches may not be what is expected from the arguments
   above.

   If the order is critical you can control LEPL's optimisations by giving an
   explicit configuration.

There's an easy fix for this, which is to explicitly say that the parser must
match the entire output (``Eos()`` matches "end of string" or "end of
stream").  This works because the sequence described above fails (as some
input remains), so the next alternative is tried (which in this case would be
the ``mul`` in ``group2``, since ``group1`` has run out of alternatives).
Eventually an arrangement of matchers is found that matches the complete
input::

  >>> expr = group3 & Eos()
  >>> print(expr.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0])
  Node
   +- 1.0
   +- '+'
   `- Node
       +- Node
       |   +- 2.0
       |   +- '*'
       |   +- '('
       |   +- Node
       |   |   +- 3.0
       |   |   +- '-'
       |   |   `- 4.0
       |   `- ')'
       +- '+'
       `- Node
	   +- Node
	   |   +- 5.0
	   |   +- '/'
	   |   `- 6.0
	   +- '+'
	   `- 7.0
  >>> len(list(expr.match('1+2*(3-4)+5/6+7', Configuration.tokens())))
  1

The second mistake is to duplicate the recursive call on both sides of the
operator.  So below, for example, we have ``add = group3...`` instead of ``add
= group2...``::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> group2, group3 = Delayed(), Delayed()
  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3 & symbol(')')
  >>> group1 = parens | number
  >>> # second layer, next most tightly grouped, is multiplication

  ... mul = group2 & symbol('*') & group2 > Node      # changed!
  >>> div = group2 & symbol('/') & group2 > Node      # changed!

  >>> group2 += mul | div | group1
  >>> # third layer, least tightly grouped, is addition

  ... add = group3 & symbol('+') & group3 > Node      # changed!
  >>> sub = group3 & symbol('-') & group3 > Node      # changed!

  >>> group3 += add | sub | group2
  >>> ast = group3.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0]
  >>> print(ast)
  1.0
  >>> len(list(group3.match('1+2*(3-4)+5/6+7', Configuration.tokens())))
  12
  >>> expr = group3 & Eos()
  >>> len(list(expr.match('1+2*(3-4)+5/6+7', Configuration.tokens())))
  5

Here, not only do we get a short match first, but we also get 5 different
matches when we force the entire input to be matched.  If you look at those
matches in detail you'll see that they are all logically equivalent,
corresponding to the different ways you can divide up an expression like
"1+2+3" --- as "(1+2)+3" or "1+(2+3)".

A rough rule of thumb to help avoid this case is to avoid expressions where
two matchers do the same job and only one is needed --- the symmetry in the
problematic definitions above is a good hint that something is wrong.

.. index:: efficiency, timing

Efficiency
----------

The issues above do not result in incorrect results (once we add ``Eos()``),
but they do make the parser less efficient.  To see this we first need to
separate the parsing process into two separate stages.

When a parser is used, via the ``parse()`` or ``match()`` methods, LEPL must
first do some preparatory work (compiling regular expressions, for example)
before actually parsing the input data.  This preparation usually needs to be
done just once, so LEPL provides methods that allow the prepared code (the
parser) to be saved and reused.

Any talk of efficiency usually addresses only the second stage --- parsing the
data.  So if we want to measure this we should make sure to generate the
parser first, as described above.  We will do this by calling
``string_parser()``::

  >>> parser = group3.string_parser(Configuration.tokens())
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  3.6650979518890381

  >>> parser = expr.string_parser(Configuration.tokens())
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  4.6738321781158447

  >>> parser = expr.string_parser(Configuration.tokens())
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  4.9616038799285889

The results above are for the three parsers in the same order as the text
(correct; doesn't produce longest first; ambiguous).  The differences are
clear (although thankfully not huge in this case).

Understanding speed variations in detail requires an in--depth understanding
of LEPL's implementation but, as the examples above show, two good rules of
thumb are:

* Try to get the best (longest) parse as the first result, without needing to
  add ``Eos()`` (but then add ``Eos()`` anyway, in case there's some corner
  case you didn't expect).

* Avoid ambiguity.

One final tip: avoid left--recursion.  In the parser above, we have recursion
where, for example, ``add = group2 & symbol('+') & group3``, because that can
lead back to ``group3``.  That is right--recursion, because ``group3`` is on
the right.  Left recursion would be ``add = group3 & symbol('+') & group2``,
with ``group3`` on the left.  This is particularly nasty because the parser
can "go round in circles" without doing any matching (if this isn't clear,
trace out how LEPL will try to match ``group3``).  LEPL includes checks and
corrections for this, but they're not perfect (as we can see above --- the
last and slowest example is left recursive).

.. index:: Node()

Subclassing Node
----------------

Back to our arithmetic expression parser.  We can make the AST more useful by
using subclasses of Node to indicate different operations (I've dropped the
operations because, with this extra information, they are no longer needed;
the parentheses can go too)::

  >>> class Add(Node): pass
  ... 
  >>> class Sub(Node): pass
  ... 
  >>> class Mul(Node): pass
  ... 
  >>> class Div(Node): pass
  ... 
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> group2, group3 = Delayed(), Delayed()
  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = ~symbol('(') & group3 & ~symbol(')')
  >>> group1 = parens | number
  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group1 & ~symbol('*') & group2 > Mul
  >>> div = group1 & ~symbol('/') & group2 > Div
  >>> group2 += mul | div | group1
  >>> # third layer, least tightly grouped, is addition
  ... add = group2 & ~symbol('+') & group3 > Add
  >>> sub = group2 & ~symbol('-') & group3 > Sub
  >>> group3 += add | sub | group2
  >>> ast = group3.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0]
  >>> print(ast)
  Add
   +- 1.0
   `- Add
       +- Mul
       |   +- 2.0
       |   `- Sub
       |       +- 3.0
       |       `- 4.0
       `- Add
	   +- Div
	   |   +- 5.0
	   |   `- 6.0
	   `- 7.0

Evaluation
----------

We can make the AST "evaluate itself" by adding an appropriate action to each
node.  If we do this via ``__float__`` then ``float()`` provides a uniform
interface to access the value of both float values and nodes.

I'll also make use of the `operators package
<http://docs.python.org/3.0/library/operator.html>`_ to provide the operation
for each node type::

  >>> from operator import add, sub, mul, truediv

  >>> # ast nodes
  ... class Op(Node):
  ...     def __float__(self):
  ...         return self._op(float(self[0]), float(self[1]))
  ...
  >>> class Add(Op): _op = add
  ...
  >>> class Sub(Op): _op = sub
  ...
  >>> class Mul(Op): _op = mul
  ...
  >>> class Div(Op): _op = truediv
  ...

  >>> # tokens
  ... symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())

  >>> # support functions etc
  ... negfloat = lambda x: -float(x)
  >>> group2, group3 = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> parens = ~symbol('(') & group3 & ~symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... ml = group1 & ~symbol('*') & group2 > Mul
  >>> dv = group1 & ~symbol('/') & group2 > Div
  >>> group2 += ml | dv | group1

  >>> # third layer, least tightly grouped, is addition
  ... ad = group2 & ~symbol('+') & group3 > Add
  >>> sb = group2 & ~symbol('-') & group3 > Sub
  >>> group3 += ad | sb | group2

  >>> # and test
  ... ast = group3.parse('1+2*(3-4)+5/6+7', Configuration.tokens())[0]
  >>> print(ast)
  Add
   +- 1.0
   `- Add
       +- Mul
       |   +- 2.0
       |   `- Sub
       |       +- 3.0
       |       `- 4.0
       `- Add
	   +- Div
	   |   +- 5.0
	   |   `- 6.0
	   `- 7.0
  >>> float(ast)
  6.833333333333333
  >>> 1+2*(3-4)+5/6+7
  6.833333333333333

Yowzah!

Hopefully you can see how powerful this --- it wouldn't be too much extra work
to extend it to include variable bindings (you would need to start passing
round an "environment" that maps names to values, and which can push and pop
variables).  Soon you could have an interpreter for your own small language...

Summary
-------

What have we learnt in this section?

* Operator precedence can be handled by careful design of the grammar.

* For efficient parsing, we should be aware of ambiguity and left--recursion.

* We can subclass ``Node`` to add functionality to AST nodes.

Thanks for reading!
