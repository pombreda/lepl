
Part 3 - Recursion, Abstract Syntax Trees
=========================================

Recap
-----

In the previous section we defined a parser that could add two numbers, even
if the expression contained spaces.  Our final version used tokens::

  >>> from lepl import *
  >>> value = Token(UnsignedFloat())
  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> add = number & ~symbol('+') & number > sum
  >>> add.parse('12 + -30')
  [-18.0]

(remember that I will not repeat the import statement in the examples below).

In this part of the tutorial we will extend this slightly, to handle a series
of additions, and then look at how to construct an internal representation of
the data --- an abstract syntax tree (AST).

Back to Basics
--------------

Since our aim is to construct an AST, I am going to stop calling ``sum`` to
process the results.  And to make clear exactly what rules we're matching,
I'll keep the addition symbol.

So here's what we're starting with::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> add = number & symbol('+') & number
  >>> add.parse('12 + -30')
  [12.0, '+', -30.0]

Adding Subtraction
------------------

This doesn't involve anything new; we just need to add the alternative to our
parser.  We could do this in various ways.  One way would be to change
``symbol('+')`` to ``symbol(Any('+-'))``.  But that will make constructing the
AST harder (it's better to have one line per AST node), so instead I'm going
to go with::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> add = number & symbol('+') & number
  >>> sub = number & symbol('-') & number
  >>> expr = add | sub
  >>> expr.parse('12 + -30')
  [12.0, '+', -30.0]
  >>> expr.parse('12 -30')
  [12.0, '-', 30.0]

That should be clear enough, I hope.  Remember that ``|`` is another way of
writing `Or() <api/redirect.html#lepl.matchers.combine.Or>`_.

.. index:: recursion

Recursion
---------

One limitation of our parser is that it doesn't handle repeated addition and
subtraction.  There's a neat trick that can fix that: in the definition of
``add`` and ``sub`` we can replace the second ``number`` with ``expr``, which
will allow us to match more and more additions / subtractions.  The only
problem with that is that we have no way to stop --- each time we try to match
``add``, say, we need to match another ``expr``, which means matching another
``add`` or ``sub``...  To allow the cycle to end we must allow ``expr`` to be
a simple ``number`` (which we needed anyway, if we want our expression parser
to be general enough to match a single value).

What I've just described above is easy to implement, but unfortunately won't
work::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> add = number & symbol('+') & expr
  >>> sub = number & symbol('-') & expr
  >>> expr = add | sub | number

.. warning::

  The parser above is broken.  Do not use it!  Depending on what you have
  already typed in to Python, it may not even compile.

What is wrong with the code above?

The problem is that ``expr`` is used before it is defined.  So either it won't
compile or (worse!) it will use a definition of ``expr`` from an earlier
example that you had typed into Python.  There's no simple fix, because if you
put ``expr`` before the ``add``, for example, then the ``add`` in the
definition of ``expr`` won't have been defined!

More generally, the problem is that we have a circular set of references,
because we have a recursive grammar.

But it's unfair to call this a "problem".  Recursive grammars are very useful.
The real problem is that I haven't shown how to handle recursive definitions
in Lepl.

.. index:: Delayed(), recursion

Delayed Matchers
----------------

The solution to our problem is to use the `Delayed() <api/redirect.html#lepl.matchers.Delayed>`_ matcher.  This lets us
introduce something, so that we can use it, and then add a definition later.
That might sound odd, but it's really simple to use::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> expr = Delayed()
  >>> add = number & symbol('+') & expr
  >>> sub = number & symbol('-') & expr
  >>> expr += add | sub | number

Note the use of ``+=`` when we give the final definition.  This works
perfectly::

  >>> expr.parse('1+2-3 +4-5')
  [1.0, '+', 2.0, '-', 3.0, '+', 4.0, '-', 5.0]

.. index:: AST, abstract syntax tree, Node()

Building an AST with Node
-------------------------

OK, finally we are at the point where it makes sense to build an AST.  The
motivation for the sections above (apart from the sheer joy of learning, of
course) is that we needed something complicated enough for this to be
worthwhile.

The simplest way of building an AST is almost trivial.  We just send the
results for the addition and subtraction to `Node() <api/redirect.html#lepl.node.Node>`_::

  >>> symbol = Token('[^0-9a-zA-Z \t\r\n]')
  >>> value = Token(UnsignedFloat())
  >>> negfloat = lambda x: -float(x)
  >>> number = Or(value >> float,
  ...             ~symbol('-') & value >> negfloat)
  >>> expr = Delayed()
  >>> add = number & symbol('+') & expr > Node
  >>> sub = number & symbol('-') & expr > Node
  >>> expr += add | sub | number
  >>> expr.parse('1+2-3 +4-5')
  [Node(...)]

OK, not so exciting, but let's look at that first result::

  >>> ast = expr.parse('1+2-3 +4-5')[0]
  >>> print(ast)
  Node
   +- 1.0
   +- '+'
   `- Node
       +- 2.0
       +- '-'
       `- Node
	   +- 3.0
	   +- '+'
	   `- Node
	       +- 4.0
	       +- '-'
	       `- 5.0

That's our first AST.  It's a bit of a lop--sided tree, I admit --- we will
make some more attractive trees later --- but if you have worked through this
tutorial from zero, this is a major achievement.  Congratulations!

(I hope it's clear that the result above is a "picture" of the tree of nodes.
At the top is the parent node, which has three children: the value ``1.0``;
the symbol ``'+'``; a ``Node`` with a first child of ``2.0`` etc.)


.. index:: nodes, Node()

Nodes
-----

Nodes are so useful that it's worth spending time getting to know them better.
They combine features from lists and dicts, as you can see from the following
examples.

First, simple list--like behaviour::

  >>> abc = Node('a', 'b', 'c')
  >>> abc[1]
  'b'
  >>> abc[1:]
  ['b', 'c']
  >>> abc[:-1]
  ['a', 'b']

Next, dict--like behaviour through attributes::

  >>> fb = Node(('foo', 23), ('bar', 'baz'))
  >>> fb.foo
  [23]
  >>> fb.bar
  ['baz']

Both mixed together::

  >>> fb = Node(('foo', 23), ('bar', 'baz'), 43, 'zap', ('foo', 'again'))
  >>> fb[:]
  [23, 'baz', 43, 'zap', 'again']
  >>> fb.foo
  [23, 'again']

Note how ``('name', value)`` pairs have a special meaning in the `Node() <api/redirect.html#lepl.node.Node>`_
constructor.  Lepl has a feature that helps exploit this, which I will explain
in the next section.


.. index:: node attributes

Node Attributes
---------------

Node attributes won't play a big part in our arithmetic parser, so here's a
small illustration of how they can be used::

  >>> letter = Letter() > 'letter'
  >>> digit = Digit() > 'digit'
  >>> example = (letter | digit)[:] > Node

This uses `Letter() <api/redirect.html#lepl.functions.Letter>`_ and `Digit() <api/redirect.html#lepl.functions.Digit>`_ (both standard Lepl matchers) to match
(single) letters and digits.  Each character is sent to a label (eg. ``>
'letter'``).  This is a special case programmed into the ``>`` operator: when
the target is a string (like ``'letter'`` or ``'digit```) then a ``('name',
value)`` pair (see above) is created.

Later, when the results are passed to the ``Node``, these ``('name', value)``
pairs become attributes::

  >>> n = example.parse('abc123d45e')[0]
  >>> n.letter
  ['a', 'b', 'c', 'd', 'e']
  >>> n.digit
  ['1', '2', '3', '4', '5']

.. index:: *args, ApplyArgs

\*args
------

You may have been wondering how a `Node() <api/redirect.html#lepl.node.Node>`_
constructor works.  Earlier I said that ``>`` sends a list of results as a
single argument, but, as we've seen in some of the examples above, `Node()
<api/redirect.html#lepl.node.Node>`_ actually takes a series of values.  So in
this case it seems as though ``>`` is calling `Node()
<api/redirect.html#lepl.node.Node>`_ with "\*args" (ie. ``Node(*results)``
rather than ``Node(results)``, if ``results`` is the list of results).

(If this makes no sense, you may need to read the `Python documentation
<http://docs.python.org/3.0/reference/compound_stmts.html#index-664>`_.)

This is correct --- Lepl is calling `Node()
<api/redirect.html#lepl.node.Node>`_ with "\*args".  `Node()
<api/redirect.html#lepl.node.Node>`_ is being treated in a special way because
it is registered with the ``ApplyArgs`` ABC, and any ``ApplyArgs`` subclass is
called in this way.

An alternative way to get ``>`` to make a "\*args" style call is to use the
`args() <api/redirect.html#lepl.functions.args>`_ wrapper::

  >>> matcher > args(target)

In the code snippet above, ``target`` will be called as ``target(*results)``.

.. index:: visitors, graphs, iterators

Other Node--Related Functions
-----------------------------

Matchers are implemented in Lepl using nodes.  As a consequence Lepl contains
quite a few library functions that you may find useful.  In particular, it has
methods for iterating over nodes in a tree (or graph) and support for the
visitor pattern.  One visitor implementation will (if the node subclass
follows certain conventions) clone a graph; another generates the "ASCII tree
diagrams" we saw above.

These are all a bit advanced for an introductory tutorial, so I will simply
point you to the `API Documentation <api>`_; in particular the `graph module
<api/redirect.html#lepl.graph>`_.

Summary
-------

What more have we learnt?

* Recursive grammars are supported with `Delayed() <api/redirect.html#lepl.matchers.Delayed>`_.

* `Node() <api/redirect.html#lepl.node.Node>`_ can be used to construct ASTs.

* Nodes combine list and dict behaviour.

* Lepl has comprehensive support for nodes (and their subclasses).
