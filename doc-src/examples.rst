
.. index:: examples
.. _examples:

Examples
========


Parsing a Python Argument List
------------------------------

This problem was discussed on `comp.lang.python
<http://groups.google.com/group/comp.lang.python/msg/3d0aedf525030865>`_,
where a pyparsing solution was posted.  The following is the equivalent LEPL
solution::

  >>> comma  = Drop(',') 
  >>> none   = Literal('None')                        >> (lambda x: None)
  >>> bool   = (Literal('True') | Literal('False'))   >> (lambda x: x == 'True')
  >>> ident  = Word(Letter() | '_', 
  >>>               Letter() | '_' | Digit())
  >>> float_ = Float()                                >> float 
  >>> int_   = Integer()                              >> int
  >>> str_   = String() | String("'")
  >>> item   = str_ | int_ | float_ | none | bool | ident

  >>> with Separator(~Regexp(r'\s*')):
  >>>     value  = Delayed()
  >>>     list_  = Drop('[') & value[:, comma] & Drop(']') > list
  >>>     tuple_ = Drop('(') & value[:, comma] & Drop(')') > tuple
  >>>     value += list_ | tuple_ | item  
  >>>     arg    = value                                   >> 'arg'
  >>>     karg   = (ident & Drop('=') & value              > tuple) >> 'karg'
  >>>     expr   = (karg | arg)[:, comma] & Drop(Eos())    > Node
            
  >>> parser = expr.string_parser()

  >>> ast = parser('True, type=rect, sizes=[3, 4], coords = ([1,2],[3,4])')
  >>> ast[0]
  Node
   +- arg True
   +- karg ('type', 'rect')
   +- karg ('sizes', [3, 4])
   `- karg ('coords', ([1, 2], [3, 4]))
  >>> ast[0].arg
  [True]
  >>> ast[0].karg
  [('type', 'rect'), ('sizes', [3, 4]), ('coords', ([1, 2], [3, 4]))]
  
  >>> ast = parser('None, str="a string"')
  >>> ast[0]
  Node
   +- arg None
   `- karg ('str', 'a string')
  >>> ast[0].arg
  [None]
  >>> ast[0].karg
  [('str', 'a string')]


Configuration and Efficiency
----------------------------

This example shows how different choices of :ref:`configuration` can change
the compilation and parsing times::


Running ``main()`` gives::


Where the first column describes the configuration, the second and third
columns reflect the time needed to compile the parser, and the third and
fourth columns reflect the time needed to run the parser.  The values in
parentheses are relative to the basic configuration.

A number of conclusions are possible:

  * From ``compiled_default`` and ``compiled_managed``, which effectively have
    the same compilation, the "noise" in the measurements is about 0.05s.

  * If efficiency is important, choosing the correct configuration can be
    critical.  Parse times here vary by a factor of almost 100.  The default
    configuration is safe and general, but not particularly efficient.

  * Compilation is not free.  If a parser is to be used several times it may
    be significantly more efficient to create a single instance and re-use it
    (but note that no attempt has been made to make parsers thread--safe).

  * Caching is expensive for simple parsers with a small amount of text (as in
    this example).

  * Using a very simple configuration --- ``Configuration()`` --- is a good
    choice for simple problems.
