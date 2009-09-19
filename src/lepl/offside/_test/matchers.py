
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
Currently unused.
'''

from unittest import TestCase


class SimpleLanguageTest(TestCase):
    '''
    A parser for a simple language, a little like python, that uses indents.
    '''
    
    PROGRAM = \
'''
# a simple function definition
def myfunc(a, b, c) = a + b + c

# a closure
def counter_from(n) =
  def counter() =
    n = n + 1
  counter
  
# multiline argument list and a different indent size
def first(a, b,
         c) =
   a
'''

#    def parser(self):
#        
#        word = Token('[a-z_][a-z0-9_]*')
#        number = Token(Integer)
#        symbol = Token('[^a-z0-9_]')
#        
#        # any indent, entire line
#        comment = symbol('#') + Star(Any())
#        
#        atom = number | word
#        # ignore line related tokens
#        args = symbol('(') + Freeform(atom[:,symbol(',')]) + symbol(')')
#        simple_expr = ...
#        expr = Line(simple_expr + Opt(comment))
#        
#        line_comment = LineAny(comment)
#        
#        # single line function is distinct
#        func1 = \
#          Line(word('def') + word + args + symbol('=') + expr + Opt(comment))
#        func = Line(word('def') + word + args + symbol('=') + Opt(comment)) + 
#               Block((expr|func|func1)[:])
#        
#        program = (func|func1)[:]
        