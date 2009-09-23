
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


.. index:: optimisation, efficiency, configuration
.. _config_example:

Configuration and Efficiency
----------------------------

This example shows how different choices of :ref:`configuration` can change
the compilation and parsing times::

  from gc import collect
  from timeit import timeit

  from lepl import *

  NUMBER = 50
  REPEAT = 5

  def build(config):
      '''
      Construct a parser for simple arithmetic expressions using floating
      point values (Float() is defined in terms of simpler matchers and
      is quite complex; it is a good candidate for speed improvements by
      compilation to a regular expression).

      This is called for each kind of configuration we want to time.
      '''

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

  # The timeit package requires simple no-argument functions, so below we
  # define these for both building the parser with different configurations
  # and then parsing the example text.

  # These use the standard configuration options
  def default(): return build(Configuration.default())
  def managed(): return build(Configuration.managed())
  def nfa(): return build(Configuration.nfa())
  def dfa(): return build(Configuration.dfa())
  def basic(): return build(Configuration())

  # These use hand-tweaked configurations that isolate individual features.
  def trace_only(): 
      return build(
	  Configuration(monitors=[lambda: TraceResults(False)]))
  def manage_only(): 
      return build(
	  Configuration(monitors=[lambda: GeneratorManager(queue_len=0)]))
  def memo_only(): 
      return build(
	  Configuration(rewriters=[auto_memoize()]))
  def nfa_only(): 
      return build(
	  Configuration(rewriters=[
	      regexp_rewriter(UnicodeAlphabet.instance(), False)]))
  def dfa_only(): 
      return build(
	  Configuration(rewriters=[
	      regexp_rewriter(UnicodeAlphabet.instance(), False, DfaRegexp)]))

  # And the functions that timeit will call to do parsing.
  def parse_default(): parse_multiple(default())
  def parse_managed(): parse_multiple(managed())
  def parse_nfa(): parse_multiple(nfa())
  def parse_dfa(): parse_multiple(dfa())
  def parse_basic(): parse_multiple(basic())
  def parse_trace_only(): parse_multiple(trace_only())
  def parse_manage_only(): parse_multiple(manage_only())
  def parse_memo_only(): parse_multiple(memo_only())
  def parse_nfa_only(): parse_multiple(nfa_only())
  def parse_dfa_only(): parse_multiple(dfa_only())

  def parse_multiple(parser):
      '''
      Parse the expression NUMBER times with the given parser.
      '''
      for i in range(NUMBER):
	  parser('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0]

  def time(number, name):
      '''
      Call timeit to time a named function.  The timeit interface is rather
      odd - it takes a string, which we construct here.
      '''
      stmt = '{0}()'.format(name)
      setup = 'from __main__ import {0}'.format(name)
      return timeit(stmt, setup, number=number)

  def analyse(func, time1_base=None, time2_base=None):
      '''
      Generate and print timing information for a particular function
      (the function passed generates the configuration; because the parser
      functions have related names we can time those too).

      We do our own repeating so we can GC between attempts.
      '''
      name = func.__name__
      (time1, time2) = ([], [])
      for i in range(REPEAT):
	  collect()
	  time1.append(time(NUMBER, name))
	  collect()
	  time2.append(time(1, 'parse_' + name))
      # minimum time since there are annoying background processes
      (time1, time2) = (min(time1), min(time2))
      print('{0:>20s} {1:5.2f} {2:7s}  {3:5.2f} {4:7s}'.format(name, 
	      time1, normalize(time1, time1_base), 
	      time2, normalize(time2, time2_base)))
      return (time1, time2)

  def normalize(time, base):
      '''
      Helper function for calculating and formatting relative times.
      '''
      if base:
	  return '({0:5.2f})'.format(time / base)
      else:
	  return ''

  def main():
      '''
      Print timing information for compiling and using a parser with the
      various configurations.
      '''
      print('{0:d} iterations; total time in s (best of {1:d})\n'.format(
	      NUMBER, REPEAT))
      (time1, time2) = analyse(basic)
      for config in [default, managed, nfa, dfa]:
	  analyse(config, time1, time2)
      print()
      for config in [trace_only, manage_only, memo_only, nfa_only, dfa_only]:
	  analyse(config, time1, time2)

Running ``main()`` gives::

  50 iterations; total time in s (best of 5)

		 basic  0.21           0.43
	       default  1.59 ( 7.69)   7.26 (17.01)
	       managed  1.63 ( 7.87)  10.90 (25.56)
		   nfa  2.59 (12.48)   3.24 ( 7.58)
		   dfa  2.69 (12.96)   1.14 ( 2.66)

	    trace_only  0.21 ( 1.02)   2.97 ( 6.97)
	   manage_only  0.21 ( 1.01)   2.09 ( 4.89)
	     memo_only  1.21 ( 5.81)   1.24 ( 2.90)
	      nfa_only  1.16 ( 5.61)   0.39 ( 0.90)
	      dfa_only  1.48 ( 7.15)   0.15 ( 0.35)

Where the first column describes the configuration, the second and third
columns reflect the time needed to compile the parser, and the third and
fourth columns reflect the time needed to run the parser.  The values in
parentheses are relative to the basic configuration.

The parenthetic values are easiest to read.  Looking at the parser times
(rightmost column) we can see that ``default`` is the second--slowest of all
configurations, while only ``nfa_only`` and ``dfa_only`` are faster than
giving an empty configuration (``basic``).  Of course, when interpreting these
numbers it is important to remember the trade--offs involved --- the default
configuration, although slower, can handle a much wider variety of grammars.

I learnt the following from writing and running this test and others like it:

  * Using the simplest possible configuration --- `Configuration() <api/redirect.html#lepl.config.Configuration>`_ or
    ``basic`` in the table above --- is a good choice for simple problems.

  * The default configuration --- ``Configuration.default()`` --- was chosen
    to work with a wide variety of problems.  Flexibility took priority over
    performance (and it shows).

  * If efficiency is important, choosing the correct configuration can be
    critical.  Parse times here vary by a factor of almost 100.

  * Creating a parser is not "free".  If a parser is to be used several times
    it may be significantly more efficient to create a single instance and
    re-use it (but note that no attempt has been made to make parsers
    thread--safe).

  * Much of the advantage of the DFA regular expression appears to come from
    avoiding alternate parses.

  * :ref:`memoisation` is expensive for simple parsers with a small amount of
    text (as in this example).

  * From ``compiled_default`` and ``compiled_managed``, which effectively have
    the same compilation, the "noise" in the measurements above is about
    0.05s.

For anyone interested in absolute speed, the values above are seconds required
for 50 iterations on a Dual Core desktop, with sufficient memory to avoid
paging, over--clocked to 2.8GHz.  So for that machine a single parse of the
expression given in the code takes between 0.003 and 0.2 seconds.



.. index:: tables, columns, tabular data, Columns()
.. _table_example:

Tabular Data
------------

This is a simple example that shows how to parse data in a fixed, tabular
format using the `Columns() <api/redirect.html#lepl.matchers.Columns>`_ matcher::

    def columns_example():
	# http://www.swivel.com/data_sets/spreadsheet/1002196
	table = '''
    US Foreign Aid, top recipients, constant dollars
    Year            Iraq          Israel           Egypt
    2005   6,981,200,000   2,684,100,000   1,541,900,000
    2004   8,333,400,000   2,782,400,000   2,010,600,000
    2003   4,150,000,000   3,878,300,000   1,849,600,000
    2002      41,600,000   2,991,200,000   2,362,800,000
    '''
	spaces = ~Space()[:]
	integer = (spaces & Digit()[1:, ~Optional(','), ...] & spaces) >> int
	cols = Columns((4,  integer),
		       # if we give widths, they follow on from each other
		       (16, integer),
		       # we can also specify column indices
		       ((23, 36), integer),
		       # and then start with widths again
		       (16, integer))
	# by default, Columns consumes a whole line (see skip argument), so
	# for the whole table we only need to (1) drop the text and (2) put
	# each row in a separate list.
	parser = ~SkipTo(Digit(), include=False) & (cols > list)[:]
	parser.parse(table)

    columns_example()

Which prints::

    [[2005, 6981200000, 2684100000, 1541900000],
     [2004, 8333400000, 2782400000, 2010600000],
     [2003, 4150000000, 3878300000, 1849600000],
     [2002, 41600000, 2991200000, 2362800000]]
