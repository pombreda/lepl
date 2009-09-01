

from unittest import TestCase


class SimpleLanguageTest(TestCase):
    '''
    A parser for a simple language, a little like python, that uses indentation.
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
  
# multiline argument list and a different indentation size
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
#        func1 = Line(word('def') + word + args + symbol('=') + expr + Opt(comment))
#        func = Line(word('def') + word + args + symbol('=') + Opt(comment)) + 
#               Block((expr|func|func1)[:])
#        
#        program = (func|func1)[:]
        