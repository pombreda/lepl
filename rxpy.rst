
.. role:: raw-math(raw)
    :format: latex html

.. raw:: latex

  \renewcommand{\ttdefault}{txtt}
  \lstset{language=Python,
	  morekeywords=[1]{yield}
  }
  \lstloadlanguages{Python}
  \lstset{
    basicstyle=\small\ttfamily,
    keywordstyle=\bfseries,
    commentstyle=\ttfamily\itshape,
    stringstyle=\slshape,
  }
  \lstset{showstringspaces=false}
  \lstset{columns=fixed,
       basewidth={0.5em,0.4em},
       xleftmargin=-1.5em}
  \inputencoding{utf8}

Regular Expressions in Lepl
===========================

Summary
-------

The Lepl parser includes a library for matching regular expressions, called
rxpy.  It is "99% compatible" with the standard Python regular expression
library.  Rxpy's implementation, in native Python, is modular, flexible, and
extensible: it has three matching engines, supports arbitrary alphabets, and
accepts multiple input formats.

:Author: Andrew Cooke (andrew@acooke.org)
:Version: 0.0 / 2011-07-04 / ``Lepl`` v6.0
:Latest: http://www.acooke.org/rxpy.pdf
:Source: http://www.acooke.org/lepl

.. contents::
   :depth: 2

History
-------

Architecture
------------

Alphabet
~~~~~~~~

A regular expression describes a set of *sentences* (ie "a match") consisting
of *characters* from an *alphabet*.  

Regular expressions are defined for a particular alphabet.  An alphabet
includes a set of acceptable characters and various related utilities
(eg. mapping from characters to integers, used to define character ranges).

The alphabet's main role is to describes the data parsed by the regular
expression, but it also provides some support for parsing the expression
itself.  This is limited, but sufficient to handle byte strings instead of
Unicode, for example.

Three alphabets are provided:

string 
  Unicode string data; expression is a Unicode string.  The default when the
  expression is a Unicode string.

bytes   
  Byte array data; expression is an ASCII byte array.  The default when the
  expression is a byte array.

digits
  List of integer data; expression is a Unicode string.  Used for testing.


Note that alphabet characters and sentences are of the same type (as with
Python strings).  So, for the digits alphabet: ``[1]`` is an example
character; ``[1,2,3]`` is a sentence (input or matched group); ``"(1|2*)"`` is
an expression.

Parser and Graph
~~~~~~~~~~~~~~~~

The parser is a hand–written state machine [#]_.  Each state maintains a
reference to its parent, to which it may delegate some actions.  A state takes
a character and returns the next state.  The end of parsing is indicated by
the character ``None``.

The result of parsing the input expression is a graph.  Each graph node is a
Python object that corresponds to an operation in the matching engine.

.. [#] The Lepl library is not used for historical reasons – the ``lepl.rxpy``
       module was originally a standalone library.

Limitations
...........

Currently the system has a single parser and trivial (one character per token)
lexer.  More complex alphabets might require alternative parsers although,
since alphabets map from tokens to characters and the underlying grammar is
fixed, a custom lexer may be sufficient.

Engine and Compilation
~~~~~~~~~~~~~~~~~~~~~~

Each matching algorithm is encapsulated within a separate engine.  All engines
implement the same interface, but may not implement all methods.

To reduce the overhead associated with the visitor pattern and graph
traversal, graphs are "compiled" against a particular engine.  This reduces
the graph to an array of functions, one per node, which call the associated
engine methods.

Engines expose two kinds of methods.  Those that include branching logic
return an index that identifies the next function to be called, which is then
called immediately.  Other methods return either a boolean value: if ``False``
then the next function is called immediately; otherwise control returns to the
caller.  The significance of these behavious depends on the engine, but it is
worth noting that repeated calling of successive functions would exhaust the
stack, so returning to an upper trampoline is necessary at some point.

Streams
~~~~~~~



Compatability
~~~~~~~~~~~~~

The library includes a compatability layer that adapts an engine to the
standard Python ``re`` interface.  This includes support for all the standard
methods and classes.

Almost all the Python tests for the ``re`` package succeed with this library.
The exceptions are: no support for the ``LOCALE`` flag; inability to pickle
matchers; no support for groups with the simple engine.

Matching Algorithms
-------------------

Some crap::

  >>> here
