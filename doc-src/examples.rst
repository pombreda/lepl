
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

  from timeit import timeit
  from lepl import *

  def build(config):

      class Term(Node): pass
      class Factor(Node): pass
      class Expression(Node): pass

      expr   = Delayed()
      number = Float()                                > 'number'
      spaces = Drop(Regexp(r'\s*'))

      with Separator(spaces):
	  term    = number | '(' & expr & ')'         > Term
	  muldiv  = Any('*/')                         > 'operator'
	  factor  = term & (muldiv & term)[:]         > Factor
	  addsub  = Any('+-')                         > 'operator'
	  expr   += factor & (addsub & factor)[:]     > Expression
	  line    = Trace(expr) & Eos()

      parser = line.string_parser(config)
      return parser

  def compile_default(): build(Configuration.default())
  def compile_managed(): build(Configuration.managed())
  def compile_nfa(): build(Configuration.nfa())
  def compile_dfa(): build(Configuration.dfa())
  def compile_nfa_basic(): build(Configuration.nfa_basic())
  def compile_dfa_basic(): build(Configuration.dfa_basic())

  def parse_multiple(config, count=100):
      parser = build(config)
      for i in range(count):
	  parser('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0]

  def parse_default(): parse_multiple(Configuration.default())
  def parse_managed(): parse_multiple(Configuration.managed())
  def parse_nfa(): parse_multiple(Configuration.nfa())
  def parse_dfa(): parse_multiple(Configuration.dfa())
  def parse_nfa_basic(): parse_multiple(Configuration.nfa_basic())
  def parse_dfa_basic(): parse_multiple(Configuration.dfa_basic())

  def time(count, funcs):
      for func in funcs:
	  stmt = '{0}()'.format(func.__name__)
	  setup = 'from __main__ import {0}'.format(func.__name__)
	  print('{0:>16s} {1:4.2f}'.format(func.__name__, 
				     timeit(stmt, setup, number=count)))
  def main():
      print('100 iterations; total time in s\n')
      time(100, [compile_basic, compile_default, compile_managed, 
		 compile_nfa, compile_dfa, compile_nfa_basic, compile_dfa_basic])
      print()
      time(1, [parse_basic, parse_default, parse_managed, 
	       parse_nfa, parse_dfa, parse_nfa_basic, parse_dfa_basic])

Running ``main()`` gives::

  100 iterations; total time in s

	 compile_basic  0.69
       compile_default  5.06
       compile_managed  5.01
	   compile_nfa  7.20
	   compile_dfa  8.25
     compile_nfa_basic  5.65
     compile_dfa_basic  6.79

	   parse_basic  1.45
	 parse_default 19.60
	 parse_managed 35.58
	     parse_nfa 11.76
	     parse_dfa  4.22
       parse_nfa_basic  1.47
       parse_dfa_basic  0.47

From ``compiled_default`` and ``compiled_managed``, which effectively have the
same compilation, the "noise" in the measurements is about 0.05s.  A number of
conclusions are possible:

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
