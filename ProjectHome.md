# Lepl - A Parser Library for Python 2.6+ (including 3!) #

## Welcome! ##

This is the Development Site for [Lepl](http://www.acooke.org/lepl), a Parser Library for Python.  Thank-you for your interest in this project.

Experienced users will want to start with the [manual](http://www.acooke.org/lepl) which has a [guided introduction](http://www.acooke.org/lepl/intro.html) and [examples](http://www.acooke.org/lepl/examples.html).  It also includes [download and installation](http://www.acooke.org/lepl/download.html#download) details.

A longer introduction to Lepl is available in the [tutorial](http://www.acooke.org/lepl/intro.html).

## Features ##

The latest version (5+) includes:
  * **Parsers are Python code**, defined in Python itself.  No separate grammar is necessary.
  * **Friendly syntax** using Python's operators.
  * Integrated, optional **lexer** simplifies handling whitespace.
  * Built-in **AST support** (a generic Node class).  Improved support for the visitor pattern and tree re--writing.
  * Generic, pure-Python approach supports parsing a wide variety of data including **bytes** (Python 3+ only).
  * **Well documented** and easy to extend.
  * **Unlimited recursion depth**.  The underlying algorithm is recursive descent, which can exhaust the stack for complex grammars and large data sets.  LEPL avoids this problem by using Python generators as coroutines (aka "trampolining").
  * Support for ambiguous grammars (**complete backtracking**).  A parser can return more than one result (aka **parse forests**).
  * **Packrat parsing**.  Parsers can be made much more efficient with automatic memoisation.
  * **Parser rewriting**.  The parser can itself be manipulated by Python code.  This gives limited opportunities for future expansion and optimisation.
  * **Left recursive grammars**.  Memoisation can detect and control left--recursive grammars.  Together with LEPL's support for ambiguity this means that "any" grammar can be supported.
  * Pluggable trace and resource management, including **deepest match diagnostics** and the ability to limit backtracking.
  * Various ways to improve parsing speed, including compilation to regular expressions.
  * Support for the **offside rule** (significant indentation levels).
  * Parsing of **binary data** (Python 3 only).

## Support ##

At the moment you can:

  * Discuss Lepl, ask for help, report problems, etc, on the [discussion list](http://groups.google.com/group/lepl).
  * Report a bug using the [Issue Tracker](http://code.google.com/p/lepl/issues/list).

Paid support is also a possibility.

## Quick Start ##

Users that have [distribute](http://pypi.python.org/pypi/distribute) installed can install Lepl from [PyPI](http://pypi.python.org/pypi/LEPL) with
```
easy_install lepl
```

([setuptools](http://pypi.python.org/pypi/setuptools) will also work for Python 2.6).

Otherwise, please follow the [download and installation](http://www.acooke.org/lepl/download.html#download) instructions.

## Contact ##

Lepl is written and maintained by [Andrew Cooke](http://www.acooke.org).  You can contact me at [andrew@acooke.org](mailto:andrew@acooke.org).