
.. _faq:

Frequently Asked Questions
==========================


When I change from > to >> my function isn't called
---------------------------------------------------

Why, when I change my code from::

    inverted = Drop('[^') & interval[1:] & Drop(']')       > invert
    
to
          
    inverted = Drop('[^') & interval[1:] & Drop(']')       >> invert      

is the `invert` function no longer called?

This is because of operator precedence.  `>>` binds more tightly than `>`,
so `>>` is applied only to the result from `Drop(']')`, which is an empty 
list (because `Drop()` discards the results).  Since the list is empty,
the function `invert` is not called.

To fix this place the entire expression in parentheses::

    inverted = (Drop('[^') & interval[1:] & Drop(']'))     >> invert      
