
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class LeftRecursiveTest(TestCase):
    
#    def test_limited_lookahead(self):
#        '''
#        This stalls because Lookahead consumes nothing.  Can we detect this 
#        case?
#        '''
#        basicConfig(level=DEBUG)
#        
#        item     = Delayed()
#        item    += item[1:3] | ~Lookahead('\\')
#    
#        expr     = item[:2] & Drop(Eos())
##        parser = expr.string_parser(Configuration(rewriters=[memoize(LMemo)]))
#        parser = expr.string_parser()
#        print(parser.matcher)
#
#        parser('abc')

#    def test_plain_lookahead(self):
#        '''
#        This stalls because Lookahead consumes nothing.  Can we detect this 
#        case?
#        '''
#        basicConfig(level=DEBUG)
#        
#        item     = Delayed()
#        item    += item[1:] | ~Lookahead('\\')
#    
#        expr     = item & Drop(Eos())
#        parser = expr.string_parser()
#        print(parser.matcher)
#
#        parser('abc')

    def test_problem_from_regexp(self):

        item     = Delayed()
        item    += item[1:] 
        expr     = item & Drop(Eos())

        parser = expr.string_parser()
        print(parser.matcher)
        parser('abc')
