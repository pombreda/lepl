

from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.match import *
from lepl.node import Node


class NodeTest(TestCase):
    

    def test_node(self):
        basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                   > 'number'
        term        = (number | '(' / expression / ')') > Term
        muldiv      = Any('*/')                         > 'operator'
        factor      = (term / (muldiv / term)[0:])      > Factor
        addsub      = Any('+-')                         > 'operator'
        expression += (factor / (addsub / factor)[0:])  > Expression
        
        (ast, _) = next(expression.match_string('1 + 2 * (3 + 4 - 5)',
                                                min_queue=1))
        print(ast[0])
