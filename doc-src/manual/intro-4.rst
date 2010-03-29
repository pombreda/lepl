
Part 4 - Evaluation, Efficiency
===============================

Recap
-----

In the previous sections we have developed a parser that could generate a
simple AST for repeated addition and subtraction::

  >>> from lepl import *
  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> number = Optional(symbol('-')) + value >> float
  >>> expr = Delayed()
  >>> add = number & symbol('+') & expr > List
  >>> sub = number & symbol('-') & expr > List
  >>> expr += add | sub | number
  >>> expr.parse('1+2-3 +4-5')
  [List(...)]

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

With Lepl this priority is implicit in the parser.  Priority is determined by
structuring the recursive calls necessary for repeated handling of groups as a
series of layers.  Which is much easier to show than explain in words::

  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> number = Optional(symbol('-')) + value >> float
  >>> group2, group3 = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3 & symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group1 & symbol('*') & group2 > List
  >>> div = group1 & symbol('/') & group2 > List
  >>> group2 += mul | div | group1

  >>> # third layer, least tightly grouped, is addition
  ... add = group2 & symbol('+') & group3 > List
  >>> sub = group2 & symbol('-') & group3 > List
  >>> group3 += add | sub | group2
  >>> ast = group3.parse('1+2*(3-4)+5/6+7')[0]
  >>> print(ast)
  List
   +- 1.0
   +- '+'
   `- List
       +- List
       |   +- 2.0
       |   +- '*'
       |   +- '('
       |   +- List
       |   |   +- 3.0
       |   |   +- '-'
       |   |   `- 4.0
       |   `- ')'
       +- '+'
       `- List
           +- List
           |   +- 5.0
           |   +- '/'
           |   `- 6.0
           +- '+'
           `- 7.0

Note how each group can pass to the next, and how parentheses return back to
the first group, giving the overall recursion we need to handle nested groups.

.. index:: ambiguity, recursion, left-recursion

Ambiguity and Left Recursion
----------------------------

.. note::

   This and the next section are fairly advanced.  You may want to skip
   them on a first read through.

It's easy, when showing a solution, to pretend that it's obvious.  But try
hiding the code above and then writing the parser yourself.  It's not as
simple as it looks.

In this section I will show two possible mistakes you can make (mistakes that
I made while testing the code for this tutorial).

The first mistake is the ordering of the definitions for ``group2`` and
``group3``.  The following code is almost identical, but gives a very
different result::

  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> number = Optional(symbol('-')) + value >> float
  >>> group2, group3b = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3b & symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group1 & symbol('*') & group2 > List
  >>> div = group1 & symbol('/') & group2 > List
  >>> group2 += group1 | mul | div      # changed!

  >>> # third layer, least tightly grouped, is addition
  ... add = group2 & symbol('+') & group3b > List
  >>> sub = group2 & symbol('-') & group3b > List
  >>> group3b += group2 | add | sub     # changed!
  >>> ast = group3b.parse('1+2*(3-4)+5/6+7')[0]
  >>> print(ast)
  [...]
  lepl.stream.maxdepth.FullFirstMatchException: The match failed at '+',
  Line 1, character 1 of str: '1+2*(3-4)+5/6+7'.

This isn't as bad as it looks.  Lepl does find the result we are expecting,
it's just not the first result found, which is what ``parse()`` returns.  We
can see how many results are found::

  >>> group3b.config.no_full_first_match()
  >>> len(list(group3b.parse_all('1+2*(3-4)+5/6+7')))
  6

and it turns out the result we expect is the last one.

You can understand what has happened by tracing out how the text is matched:

* ``group3b`` is defined as ``group2 | add | sub``, so ``group2`` is tried
  first (`Or() <api/redirect.html#lepl.matchers.combine.Or>`_ evaluates from
  left to right)

* ``group2`` is defined as ``group1 | mul | div``, so ``group1`` is tried
  first

* ``group1`` is defined as ``parens | number``, so ``parens`` is tried first

* ``parens`` fails to match, because the input does not start with "("

* so the next alternative in the `Or()
  <api/redirect.html#lepl.matchers.combine.Or>`_ for ``group1`` is tried,
  which is ``number``

* ``number`` succeeds and has nothing following it

* returning back up the stack of pending matchers (``group1``, ``group2``,
  ``group3b``), all have no following matcher, so the match is complete

* so the "successful" parse is ``1.0``, but that hasn't consumed all the
  input, so we get the error.

.. warning::

   The exercise above, while useful, is not always completely accurate,
   because Lepl may modify the matchers before using them.  You are most
   likely to see this when using a grammar with left--recursion (see below)
   --- Lepl may re-arrange the order of matchers inside `Or()
   <api/redirect.html#lepl.matchers.combine.Or>`_ so that the left--recursive
   case comes last.

   With the default configuration Lepl should always maintain the basic logic
   of the grammar --- the result will be consistent with the parser given ---
   but the order of the matches may not be what is expected from the arguments
   above.

   If the order is critical you can control Lepl's optimisations by giving an
   explicit :ref:`configuration <configuration>`.

There's an easy fix for this (but see comments on efficiency below), which is
to explicitly say that the parser must match the entire output (`Eos()
<api/redirect.html#lepl.matchers.derived.Eos>`_ matches "end of string" or
"end of stream").  This works because the sequence described above fails (as
some input remains), so the next alternative is tried (which in this case
would be the ``mul`` in ``group2``, since ``group1`` has run out of
alternatives).  Eventually an arrangement of matchers is found that matches
the complete input::

  >>> expr = group3b & Eos()
  >>> print(expr.parse('1+2*(3-4)+5/6+7')[0])
  List
   +- 1.0
   +- '+'
   `- List
       +- List
       |   +- 2.0
       |   +- '*'
       |   +- '('
       |   +- List
       |   |   +- 3.0
       |   |   +- '-'
       |   |   `- 4.0
       |   `- ')'
       +- '+'
       `- List
	   +- List
	   |   +- 5.0
	   |   +- '/'
	   |   `- 6.0
	   +- '+'
	   `- 7.0
  >>> len(list(expr.parse_all('1+2*(3-4)+5/6+7')))
  1

The second mistake is to duplicate the recursive call on both sides of the
operator.  So below, for example, we have ``add = group3c...`` instead of
``add = group2...``::

  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> number = Optional(symbol('-')) + value >> float
  >>> group2, group3c = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = symbol('(') & group3c & symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... mul = group2 & symbol('*') & group2 > List     # changed
  >>> div = group2 & symbol('/') & group2 > List     # changed
  >>> group2 += mul | div | group1

  >>> # third layer, least tightly grouped, is addition
  ... add = group3c & symbol('+') & group3c > List   # changed
  >>> sub = group3c & symbol('-') & group3c > List   # changed
  >>> group3c += add | sub | group2
  >>> ast = group3c.parse('1+2*(3-4)+5/6+7')[0]
  >>> print(ast)
  [...]
  lepl.stream.maxdepth.FullFirstMatchException: The match failed at '+',
  Line 1, character 1 of str: '1+2*(3-4)+5/6+7'.
  >>> group3c.config.no_full_first_match()
  >>> len(list(group3c.parse_all('1+2*(3-4)+5/6+7')))
  12
  >>> expr = group3c & Eos()
  >>> len(list(expr.parse_all('1+2*(3-4)+5/6+7')))
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

The issues above do not result in incorrect results (once we add `Eos()
<api/redirect.html#lepl.matchers.derived.Eos>`_), but they do make the parser less
efficient.  To see this we first need to separate the parsing process into two
separate stages.

When a parser is used, via the ``parse()``, ``parse_all()`` and ``match()``
methods, Lepl must first do some preparatory work (compiling regular
expressions, for example) before actually parsing the input data.  

For any particular configuration this work is done once, and then the result
is cached for re-use.  This gives an efficient system, but for timing tests we
often want to focus only on the parsing time (since this will dominate if the
same parser is re-used many times).  So Lepl provides methods that allow the
prepared code (the parser) to be saved --- these are ``get_parse()``, etc.::

  >>> parser = group3.get_parse()
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  3.31537699699

  >>> parser = (group3b & Eos()).get_parse()
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  4.10263490677

  >>> parser = (group3c & Eos()).get_parse()
  >>> timeit('parser("1+2*(3-4)+5/6+7")',
  ...     'from __main__ import parser', number=100)
  3.10528898239

The results above are for the three parsers in the same order as the text
(correct; doesn't produce longest first; ambiguous).  The differences appear
to be significant: the second parser is slower because it has to work through
more variations; the third is actually faster, probably because, although it
also has to work through some variations, the ambiguity allows a full match to
be found earlier.

Understanding speed variations in detail requires an in--depth understanding
of Lepl's implementation but two good rules of thumb are:

* Try to get the best (longest) parse as the first result, without needing to
  add `Eos() <api/redirect.html#lepl.matchers.derived.Eos>`_ (but then add
  `Eos() <api/redirect.html#lepl.matchers.derived.Eos>`_ anyway, in case
  there's some corner case you didn't expect).

* Avoid ambiguity.  This helps with debugging and usually improves performance
  (the third example above is a "lucky break" --- until Lepl 4's improved
  memoisation and handling of left-recursive grammars, that solution was
  slower).

One final tip: avoid left--recursion.  In the parser above, we have recursion
where, for example, ``add = group2 & symbol('+') & group3``, because that can
lead back to ``group3`` (which is where we found ``add``...).  That is
right--recursion, because ``group3`` is on the right.  Left recursion would be
``add = group3 & symbol('+') & group2``, with ``group3`` on the left.  This is
particularly nasty because the parser can "go round in circles" without doing
any matching (if this isn't clear, trace out how Lepl will try to match
``group3``).  Lepl includes checks and corrections for this, but they use
memory and slow the parser down (the third case above, which *is* left
recursive, should get significantly slower as the amount of text to parse
increases).

.. index:: List()

Subclassing List
----------------

Back to our arithmetic expression parser.  We can make the AST more useful by
using subclasses of List to indicate different operations (I've dropped the
operations because, with this extra information, they are no longer needed;
the parentheses can go too)::

  >>> class Add(List): pass
  ... 
  >>> class Sub(List): pass
  ... 
  >>> class Mul(List): pass
  ... 
  >>> class Div(List): pass
  ... 

  >>> # tokens
  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')

  >>> number = Optional(symbol('-')) + value >> float
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

  >>> ast = group3.parse('1+2*(3-4)+5/6+7')[0]
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
tree node.  If we do this via ``__float__`` then ``float()`` provides a
uniform interface to access the value of both float values and nodes.

I'll also make use of the `operator package
<http://docs.python.org/3.0/library/operator.html>`_ to provide the
operations::

  >>> from operator import add, sub, mul, truediv

  >>> # ast nodes
  ... class Op(List):
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
  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')

  >>> number = Optional(symbol('-')) + value >> float
  >>> group2, group3 = Delayed(), Delayed()

  >>> # first layer, most tightly grouped, is parens and numbers
  ... parens = ~symbol('(') & group3 & ~symbol(')')
  >>> group1 = parens | number

  >>> # second layer, next most tightly grouped, is multiplication
  ... mul_ = group1 & ~symbol('*') & group2 > Mul
  >>> div_ = group1 & ~symbol('/') & group2 > Div
  >>> group2 += mul_ | div_ | group1

  >>> # third layer, least tightly grouped, is addition
  ... add_ = group2 & ~symbol('+') & group3 > Add
  >>> sub_ = group2 & ~symbol('-') & group3 > Sub
  >>> group3 += add_ | sub_ | group2

  ... ast = group3.parse('1+2*(3-4)+5/6+7')[0]
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

* We can subclass `List() <api/redirect.html#lepl.support.list.List>`_ to add
  functionality to AST nodes.

Thanks for reading!
