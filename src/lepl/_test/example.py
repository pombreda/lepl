
from lepl.match import *
from lepl.node import Node


class Term(Node): pass
class Factor(Node): pass
class Expression(Node): pass


def parse_expression(text):
    
    expression  = Delayed()
    number      = Digit()[1:,...]                   > 'number'
    term        = (number | '(' / expression / ')') > Term
    muldiv      = Any('*/')                         > 'operator'
    factor      = (term / (muldiv / term)[0:])      > Factor
    addsub      = Any('+-')                         > 'operator'
    expression += (factor / (addsub / factor)[0:])  > Expression
    
    # parse_string returns a list of tokens, but expression 
    # returns a single value, so take the first entry
    return expression.parse_string(text)[0]

if __name__ == '__main__':
    print(parse_expression('1 + 2 * (3 + 4 - 5)'))
