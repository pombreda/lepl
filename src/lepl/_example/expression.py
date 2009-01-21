
from logging import basicConfig, DEBUG, INFO
from unittest import TestCase

from lepl.match import *
from lepl.node import Node, make_error, Error, throw


basicConfig(level=INFO)

class BNode(Node):
    def __init__(self, arg):
        print(arg)
        super().__init__(arg)

class Term(BNode): pass
class Factor(BNode): pass
class Expression(BNode): pass
    
expr   = Delayed()
number = Digit()[1:,...]                          > 'number'

with Separator(r'\s*'):
    term    = (number | '(' & expr & ')')         > Term
    muldiv  = Any('*/')                           > 'operator'
    factor  = (term & (muldiv & term)[:])         > Factor
    addsub  = Any('+-')                           > 'operator'
    expr   += (factor & (addsub & factor)[:])     > Expression
    line    = Trace(expr) & Eos()

parser = line.parse_string
print(parser('1 + 2 * (3 + 4 - 5)')[0])
print(parser('12+ 23*45 + 34')[0])
