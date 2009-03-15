
from unittest import TestCase

from lepl import *


class LeftRecursiveTest(TestCase):
    
    pass
    
#    def test_plain_lookahead(self):
#        '''
#        This stalls because Lookahead consumes nothing.  Can we detect this 
#        case?
#        '''
#        
#        item     = Delayed()
#        item    += item[1:] | ~Lookahead('\\')
#    
#        expr     = item[:] & Drop(Eos())
#        parser = expr.string_parser()
#
#        parser('a(bc)*d')

#    def test_problem_from_regexp(self):
#
#        item     = Delayed()
#        item    += item[1:] 
#        expr     = item & Drop(Eos())
#
#        parser = expr.string_parser()
#        print(parser.matcher)
#        parser('abc')
