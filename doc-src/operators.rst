
Operators
=========


Caveats and Limitations
-----------------------

It is unfortunate, but realistic, that the chapter on operators should start
with some warnings to the user.

Operators --- things like ``&`` and ``|``, used to join matchers --- can help
produce grammars that are easy to read, easier to understand, and so less
likely to contain errors.  But their implementation pushes Python's
boundaries, giving problems with precedence and applicability.  This is
exacerbated by the automatic coercion of strings to ``Literal`` matchers
wherever possible.

Many of the guidelines in the Style chapter are intended to help manage these
problems.

Examples here...


Catalogue
---------



Type Checking
-------------



Replacement
-----------

