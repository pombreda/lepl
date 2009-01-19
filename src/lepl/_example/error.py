
from logging import basicConfig, INFO
basicConfig(level=INFO)

from lepl.match import *
from lepl.node import make_dict

class Term(Node): pass
class Factor(Node): pass
class Expression(Node): pass

expression  = Delayed()
bad_text    = AnyBut(Whitespace() | Digit())[1:,...]                 ^ 'unexpected text: {results[0]}'
number      = Digit()[1:,...]                                        > 'number'
term        = (number 
               | '(' / expression / ')' 
               | bad_text 
               | '(' / expression / Error('no "(" for {stream_in}')
               ) > Term
muldiv      = Any('*/')                                              > 'operator'
factor      = (term / (muldiv / term)[0::])                          > Factor
addsub      = Any('+-')                                              > 'operator'
expression += (factor / (addsub / factor)[0::])               > Expression
line        = expression / Eos()

print(line.parse_string('1 + 2 * (3 + 4 - 5)')[0])
line.parse_string('1 + 2 * 3 + 4 - 5)')
expression.parse_string('1 + 2 * foo')
