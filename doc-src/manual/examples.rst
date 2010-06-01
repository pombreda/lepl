
.. index:: examples
.. _examples:

Examples
========


Parsing a Python Argument List
------------------------------

This problem was discussed on `comp.lang.python
<http://groups.google.com/group/comp.lang.python/msg/3d0aedf525030865>`_,
where a pyparsing solution was posted.  The following is the equivalent Lepl
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
            
  >>> parser = expr.get_parse_string()

  >>> ast = parser('True, type=rect, sizes=[3, 4], coords = ([1,2],[3,4])')
  >>> print(ast[0])
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
  >>> print(ast[0])
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
  from random import random
  from timeit import timeit

  from lepl import *
  from lepl._example.support import Example
  from lepl.support.lib import format

  NUMBER = 10
  REPEAT = 3

  def default():
      '''A simple parser we'll use as an example.'''

      class Term(List): pass
      class Factor(List): pass
      class Expression(List): pass

      expr   = Delayed()
      number = Float()                                >> float

      with DroppedSpace():
          term    = number | '(' & expr & ')'         > Term
          muldiv  = Any('*/')
          factor  = term & (muldiv & term)[:]         > Factor
          addsub  = Any('+-')
          expr   += factor & (addsub & factor)[:]     > Expression
          line    = expr & Eos()

      return line


  # These create a matcher for the parser above with different configurations

  def clear():
      matcher = default()
      matcher.config.clear()
      return matcher

  def no_memo():
      matcher = default()
      matcher.config.no_memoize()
      return matcher

  def full_memo():
      matcher = default()
      matcher.config.auto_memoize(full=True)
      return matcher

  def slow(): 
      matcher = default()
      matcher.config.clear().trace().manage().auto_memoize(full=True)
      return matcher

  def nfa_regexp(): 
      matcher = default()
      matcher.config.clear().compile_to_nfa(force=True)
      return matcher

  def dfa_regexp(): 
      matcher = default()
      matcher.config.clear().compile_to_dfa(force=True)
      return matcher


  # Next, build all the tests, making sure that we pre-compile parsers where
  # necessary and (important!) we avoid reusing a parser with a cache

  data = [format('{0:4.2f} + {1:4.2f} * ({2:4.2f} + {3:4.2f} - {4:4.2f})',
                 random(), random(), random(), random(), random())
          for i in range(NUMBER)]

  matchers = [default, clear, no_memo, full_memo, slow, nfa_regexp, dfa_regexp]

  def build_cached(factory):
      matcher = factory()
      matcher.config.clear_cache()
      parser = matcher.get_parse()
      def test():
          for line in data:
              parser(line)[0]
      return test

  def build_uncached(factory):
      matcher = factory()
      def test():
          for line in data:
              matcher.config.clear_cache()
              matcher.parse(line)[0]
      return test

  tests = {}

  for matcher in matchers:
      tests[matcher] = {True: [], False: []}
      for i in range(REPEAT):
           tests[matcher][True].append(build_cached(matcher))
           tests[matcher][False].append(build_uncached(matcher))


  def run(matcher, cached, repeat):
      '''Time the given test.'''
      stmt = 'tests[{0}][{1}][{2}]()'.format(matcher.__name__, cached, repeat)
      setup = 'from __main__ import tests, {0}'.format(matcher.__name__)
      return timeit(stmt, setup, number=1)

  def analyse(matcher, t_uncached_base=None, t_cached_base=None):
      '''We do our own repeating so we can GC between attempts.'''
      (t_uncached, t_cached) = ([], [])
      for repeat in range(REPEAT):
          collect()
          t_uncached.append(run(matcher, False, repeat))
          collect()
          t_cached.append(run(matcher, True, repeat))
      (t_uncached, t_cached) = (min(t_uncached), min(t_cached))
      t_uncached = 1000.0 * t_uncached / NUMBER
      t_cached = 1000.0 * t_cached / NUMBER 
      print(format('{0:>20s} {1:5.1f} {2:8s}  {3:5.1f} {4:8s}',
                   matcher.__name__, 
                   t_uncached, normalize(t_uncached, t_uncached_base), 
                   t_cached, normalize(t_cached, t_cached_base)))
      return (t_uncached, t_cached)

  def normalize(time, base):
      if base:
          return '(x{0:5.2f})'.format(time / base)
      else:
          return ''

  def main():
      print('{0:d} iterations; time per iteration in ms (best of {1:d})\n'.format(
              NUMBER, REPEAT))
      print(format('{0:>35s}    {1:s}', 're-compiled', 'cached'))
      (t_uncached, t_cached) = analyse(default)
      for matcher in matchers:
          if matcher is not default:
              analyse(matcher, t_uncached, t_cached)

  if __name__ == '__main__':
      main()

Running ``main()`` gives::

  10 iterations; time per iteration in ms (best of 3)

                          re-compiled    cached
               default  78.4             4.2         
                 clear   6.0 (x 0.08)    5.9 (x 1.39)
               no_memo  68.6 (x 0.88)    4.1 (x 0.97)
             full_memo  89.1 (x 1.14)   13.5 (x 3.19)
                  slow 157.1 (x 2.00)  133.3 (x31.55)
            nfa_regexp  35.3 (x 0.45)    4.3 (x 1.01)
            dfa_regexp  38.4 (x 0.49)    5.5 (x 1.30)

The first column describes the configuration --- you can check the code to see
exactly what was used in the function of the same name.

The second two columns are the time (and the ratio of that time relative to
the default) for using a parser that is re--compiled for each parse.  The time
includes the work needed to compile the parser and is appropriate when you're
only using a matcher once.

The final two columns are the time (and the ratio of that time relative to the
default) for re--using a cached parser.  This doesn't include the time needed
to compile the parser and is appropriate for when you're using the same
matcher many times (in which case the compilation time is relatively
unimportant).

Note that you don't need to worry about caching parsers yourself --- a matcher
will automatically cache the parser when it is used.  The test code is much
more complex because it is trying to *disable* caching in various places.

What can we learn from these results?

#. Compilation isn't cheap.  The "re-compiled" times are, except for "clear",
   much larger than the "cached" times.  So if you are dynamically generating
   matchers and using each one just once, you might want to use
   `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

#. But compilation isn't hugely expensive either.  If you're using a matcher
   more than about 20 times, it's worth compiling to get better peformance.

#. It's hard to beat the default configuration.  The compilation time isn't
   too great and, once cached, it generates one of the fastest parsers around.

#. Disabling memoisation makes a cached parser *slightly* faster, but is
   generally not worth the risk (without the minimal minimisation in the
   default parser a left recursive gammar can crash your program).

#. Full memoisation and resource management are slow, but these are very
   specialised configurations that you won't need in normal use.

For anyone interested in absolute speed, the values above are milliseconds
required per iteration on a Dual Core laptop (a Lenovo X60, a couple of years
old), with sufficient memory to avoid paging.


.. index:: tables, columns, tabular data, Columns()
.. _table_example:

Tabular Data
------------

This is a simple example that shows how to parse data in a fixed, tabular
format using the `Columns()
<api/redirect.html#lepl.matchers.derived.matchers>`_ matcher::

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
 

.. index::  Block(), BLine(), offside rule, whitespace sensitive parsing

Simpler Offside Example
-----------------------

Here's a simpler example of how to use offside parsing, as described in
:ref:`offside`.  The idea is that we have a configuration file format with
named sections and subsections; in the subsections are name/value pairs::

    from string import ascii_letters
    from lepl import *

    def config_parser():
        word        = Token(Any(ascii_letters)[1:, ...])
        key_value   = (word & ~Token(':') & word) > tuple
        subsection  = BLine(word) & (Block(BLine(key_value)[1:] > dict)) > list
        section     = BLine(word) & Block(subsection[1:]) > list
        config_file = (section | ~Line(Empty()))[:] > list

        config_file.config.default_line_aware(block_policy=rightmost)
        return config_file.get_parse()

    parser = config_parser()
    parser('''
    one
       a
          foo: bar
          baz: poop
       b
          snozzle: berry

    two
       c
          apple: orange
    ''')[0]

Which prints::

    [['one', ['a', {'foo': 'bar', 'baz': 'poop'}], ['b', {'snozzle': 'berry'}]], ['two', ['c', {'apple': 'orange'}]]]

Note that the name/value pairs are in dictionaries; this is because we passed
a list of tuples to ``dict()``.
