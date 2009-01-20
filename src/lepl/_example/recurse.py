
from logging import basicConfig, INFO
#basicConfig(level=INFO)

from lepl.match import *
from lepl.node import make_dict

class Term(Node): pass
class Factor(Node): pass
class Expression(Node): pass

expression  = Delayed()
number      = Digit()[1:,...]                  > 'number'
term        = (number | expression)            > Term
term        = (number <and_deep> expression)         > Term
term        = (number <and_wide> expression)            > Term
term        = (number <or_deep> expression)         > Term
term        = (number <or_wide> expression)            > Term
muldiv      = Any('*/')                        > 'operator'
factor      = (term / (muldiv / term)[:])      > Factor
addsub      = Any('+-')                        > 'operator'
expression += (factor / (addsub / factor)[:])  > Expression
line        = expression / Eos()

print(Trace(line).parse_string('1 + 2 * 3 + 4 - 5')[0])

expression  = Delayed()
number      = Digit()[1:,...]                    > 'number'
term        = (number | expression)              > Term
muldiv      = Any('*/')                          > 'operator'
factor      = (term / (muldiv / term)[::1])      > Factor
addsub      = Any('+-')                          > 'operator'
expression += (factor / (addsub / factor)[::1])  > Expression
line        = expression / Eos()

print(Trace(line).parse_string('1 + 2 * 3 + 4 - 5')[0])

expression  = Delayed()
number      = Digit()[1:,...]                                > 'number'
term        = (number | expression)                          > Term
muldiv      = Any('*/')                                      > 'operator'
factor      = (term / (muldiv / term)[::-1])                 > Factor
addsub      = Any('+-')                                      > 'operator'
expression += (factor / (addsub / factor / Commit())[::-1])  > Expression

print(Trace(expression).parse_string('1 + 2 * 3 + 4 - 5')[0])

stop

expression  = Delayed()
number      = Digit()[1:,...]                     > 'number'
term        = (number | expression)               > Term
muldiv      = Any('*/')                           > 'operator'
factor      = (term / (muldiv / term)[::])      > Factor
addsub      = Any('+-')                           > 'operator'
expression += (factor / (addsub / factor)[::-1])  > Expression

print(Trace(expression).parse_string('1 + 2 * 3 + 4 - 5')[0])

