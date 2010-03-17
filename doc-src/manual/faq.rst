
.. _faq:

Frequently Asked Questions
==========================

 * :ref:`Why do I get "Cannot parse regexp..."? <faq_regexp>`
 * :ref:`Why isn't my parser matching the full expression? (1) <faq_lefttoright1>`
 * :ref:`Why isn't my parser matching the full expression? (2) <faq_lefttoright2>`
 * :ref:`How do I parse an entire file? <faq_file>`
 * :ref:`When I change from > to >> my function isn't called <faq_precedence>`


.. _faq_regexp:

Why do I get "Cannot parse regexp..."?
--------------------------------------

*Why do I get "Cannot parse regexp '(' using ..." for Token('(')?*

String arguments to `Token() <api/redirect.html#lepl.lexer.matchers.Token>`_ are treated as regular expressions.  Because
``(`` has a special meaning in a regular expression you must escape it,
like this: ``Token('\\(')``, or like this: ``Token(r'\(')``


.. _faq_lefttoright1:

Why isn't my parser matching the full expression? (1)
-----------------------------------------------------

*In the code below*::

    word = Token('[a-z]+')
    lpar = Token('\\(')
    rpar = Token('\\)')
    expression = word | (word & lpar & word & rpar)
    
*why does expression.parse('hello(world)') match just 'hello'*?

In general Lepl is greedy (it tries to matches the longest possible string), 
but for `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ it will try alternatives left-to-right.  So in this case you 
should rewrite the parser as::

    expression = (word & lpar & word & rpar) | word
    
Alternatively, you can force the parser to match the entire input by ending
with `Eos() <api/redirect.html#lepl.matchers.derived.Eos>`_::

    expression = word | (word & lpar & word & rpar)
    complete = expression & Eos()   


.. _faq_lefttoright2:

Why isn't my parser matching the full expression? (2)
-----------------------------------------------------

*In the code below*::

	constant = Float() >> float
	matcher = Or (
	   constant >> constant_gen,
	  ... some other stuff ...

	matcher.parse ('2.5x')

	[C(2.5)]

*It seems Float matched the part it liked, and just ignored the rest.*

The simple solution is to add `Eos() <api/redirect.html#lepl.matchers.derived.Eos>`_ to the end of the parser, so that the
entire stream must match.

But it would be better to use tokens here.  You could have one token for
numeric values and another for alphanumeric "words".


.. _faq_file:

How do I parse an entire file?
------------------------------

*I understand how to parse a string, but how do I parse an entire file?*

Instead of ``.parse()`` or ``.parse_string()`` (or ``.match()`` or 
``.match_string()``) use ``.parse_file()`` or ``.parse_path()`` (or 
``.match_file()`` or ``.match_path()``).

Matchers extend `OperatorMatcher() <api/redirect.html#lepl.matchers.OperatorMatcher>`_, which provides these methods.


.. _faq_precedence:

When I change from > to >> my function isn't called
---------------------------------------------------

*Why, when I change my code from*::

    inverted = Drop('[^') & interval[1:] & Drop(']') > invert
    
*to*::
          
    inverted = Drop('[^') & interval[1:] & Drop(']') >> invert      

*is the `invert` function no longer called?*

This is because of operator precedence.  ``>>`` binds more tightly than ``>``,
so ``>>`` is applied only to the result from ``Drop(']')``, which is an empty 
list (because `Drop() <api/redirect.html#lepl.matchers.derived.Drop>`_ discards the results).  Since the list is empty,
the function ``invert`` is not called.

To fix this place the entire expression in parentheses::

    inverted = (Drop('[^') & interval[1:] & Drop(']')) >> invert      
