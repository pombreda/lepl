
Search
======

In the examples that parse an arithmetic expression you may have noticed that
the recursive reference to a ``expression`` is within parentheses.  This helps
clarify the semantics, but is not really necessary --- we know that
multiplication and division bind more tightly than addition and subtraction,
and that is reflected in the grammar.

However, if you remove the parentheses the parser will exhaust stack space and
then fail.

This is because the default depth--first search never finds a 
