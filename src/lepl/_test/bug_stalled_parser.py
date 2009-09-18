
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Tests for a bug.
'''

# pylint: disable-msg=W0614, W0401, C0111, R0201
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class LeftRecursiveTest(TestCase):
    
#    def test_limited_lookahead(self):
#        '''
#        This stalls because Lookahead consumes nothing.  Can we detect this 
#        case?
#        '''
        #basicConfig(level=DEBUG)
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
        #basicConfig(level=DEBUG)
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
#        print(parser.matcher)
        parser('abc')
