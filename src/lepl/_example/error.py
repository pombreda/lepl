
from __future__ import with_statement
from logging import basicConfig, DEBUG, INFO
from unittest import TestCase
from lepl import *

basicConfig(level=INFO)

class Term(Node): pass
class Factor(Node): pass
class Expression(Node): pass

expr    = Delayed()
number  = Digit()[1:,...]                          > 'number'
badChar = AnyBut(Space() | Digit() | '(')[1:,...]

with Separator(r'\s*'):
    
    unopen   = number ** make_error('no ( before {stream_out}') & ')'
    unclosed = ('(' & expr & Eos()) ** make_error('no ) for {stream_in}')

    term    = Or(
                 (number | '(' & expr & ')')      > Term,
                 badChar                          ^ 'unexpected text: {results[0]}',
                 unopen                           >> throw,
                 unclosed                         >> throw
                 )
    muldiv  = Any('*/')                           > 'operator'
    factor  = (term & (muldiv & term)[:])         > Factor
    addsub  = Any('+-')                           > 'operator'
    expr   += (factor & (addsub & factor)[:])     > Expression
    line    = Empty() & Trace(expr) & Eos()

parser = line.parse_string
        
#parser('1 + 2 * (3 + 4 - 5')[0]
#  File "<string>", line 1
#    1 + 2 * (3 + 4 - 5
#            ^
#lepl.node.Error: no ) for '(3 + 4...'

#parser('1 + 2 * 3 + 4 - 5)')[0]
#  File "<string>", line 1
#    1 + 2 * 3 + 4 - 5)
#                    ^
#lepl.node.Error: no ( before ')'

#parser('1 + 2 * (3 + four - 5)')[0]
#  File "<string>", line 1
#    1 + 2 * (3 + four - 5)
#                 ^
#lepl.node.Error: unexpected text: four

parser('1 + 2 ** (3 + 4 - 5)')[0]
#  File "<string>", line 1
#    1 + 2 ** (3 + 4 - 5)
#           ^
#lepl.node.Error: unexpected text: *
