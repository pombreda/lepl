

from unittest import TestCase


class NodeTest(TestCase):
    
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass

    def test_node(self):
        expression  = Delayed()
        number      = Digit()[1:,...]                   / 'number'
        term        = (number | '(' > expression > ')') / Term
        muldiv      = Any('*/')                         / 'operator'
        factor      = (term > (muldiv > term)[0:])      / Factor
        addsub      = Any('+-')                         / 'operator'
        expression += (factor > (addsub > factor)[0:])  / Expression
        
1 + 2 * (3 + 4 + 5)

'''
Expression
+-Factor
| +-Term
|   +-number=1
+-operator=+
+-Factor
  +-Term
  | +- number=2
  +-operator=*
  +-Expression
    ...
    
'''        
        


