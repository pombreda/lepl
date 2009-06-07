
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers import * 
from lepl.node import Node


class StrTest(TestCase):
    
    def assert_same(self, text1, text2):
        assert self.__clean(text1) == self.__clean(text2), text1
    
    def __clean(self, text):
        depth = 0
        result = ''
        for c in text:
            if c == '<':
                depth += 1
            elif c == '>':
                depth -= 1
            elif depth == 0:
                result += c
        return result

    def test_str(self):
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass

        expression  = Delayed()
        number      = Digit()[1:,...]                      > 'number'
        term        = (number | '(' / expression / ')')    > Term
        muldiv      = Any('*/')                            > 'operator'
        factor      = (term / (muldiv / term)[0::])        > Factor
        addsub      = Any('+-')                            > 'operator'
        expression += (factor / (addsub / factor)[0::])    > Expression

        description = str(expression)
        self.assert_same(description, r'''Delayed(
 matcher=Transform(
  And(
   Transform(
    And(
     Transform(
      Or(
       Transform(
        Transform(
         DepthFirst(
          Any(restrict='0123456789'), 1, None, 
          rest=Any(restrict='0123456789')), 
         [<function add at 0x7f5cd96520d8>]), 
        [<function <lambda> at 0x7f5cd7822c00>]), 
       And(
        And(
         Literal('('), 
         Transform(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          [<function add at 0x7f5cd96520d8>]), 
         Delayed(matcher=<loop>)), 
        Transform(
         DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
         [<function add at 0x7f5cd96520d8>]), 
        Literal(')'))), 
      [<function <lambda> at 0x7f5cd78220d8>]), 
     Transform(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      [<function add at 0x7f5cd96520d8>]), 
     DepthFirst(
      And(
       Transform(Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
       Transform(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        [<function add at 0x7f5cd96520d8>]), 
       Transform(
        Or(
         Transform(
          Transform(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           [<function add at 0x7f5cd96520d8>]), 
          [<function <lambda> at 0x7f5cd7822c00>]), 
         And(
          And(
           Literal('('), 
           Transform(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            [<function add at 0x7f5cd96520d8>]), 
           Delayed(matcher=<loop>)), 
          Transform(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           [<function add at 0x7f5cd96520d8>]), 
          Literal(')'))), 
        [<function <lambda> at 0x7f5cd78220d8>])), 
      0, None, 
      rest=And(
       Transform(Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
       Transform(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        [<function add at 0x7f5cd96520d8>]), 
       Transform(
        Or(
         Transform(
          Transform(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           [<function add at 0x7f5cd96520d8>]), 
          [<function <lambda> at 0x7f5cd7822c00>]), 
         And(
          And(
           Literal('('), 
           Transform(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            [<function add at 0x7f5cd96520d8>]), 
           Delayed(matcher=<loop>)), 
          Transform(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           [<function add at 0x7f5cd96520d8>]), 
          Literal(')'))), 
        [<function <lambda> at 0x7f5cd78220d8>])))), 
    [<function <lambda> at 0x7f5cd78228d0>]), 
   Transform(
    DepthFirst(
     Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
    [<function add at 0x7f5cd96520d8>]), 
   DepthFirst(
    And(
     Transform(Any(restrict='+-'), [<function <lambda> at 0x7f5cd76aa050>]), 
     Transform(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      [<function add at 0x7f5cd96520d8>]), 
     Transform(
      And(
       Transform(
        Or(
         Transform(
          Transform(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           [<function add at 0x7f5cd96520d8>]), 
          [<function <lambda> at 0x7f5cd7822c00>]), 
         And(
          And(
           Literal('('), 
           Transform(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            [<function add at 0x7f5cd96520d8>]), 
           Delayed(matcher=<loop>)), 
          Transform(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           [<function add at 0x7f5cd96520d8>]), 
          Literal(')'))), 
        [<function <lambda> at 0x7f5cd78220d8>]), 
       Transform(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        [<function add at 0x7f5cd96520d8>]), 
       DepthFirst(
        And(
         Transform(
          Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
         Transform(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          [<function add at 0x7f5cd96520d8>]), 
         Transform(
          Or(
           Transform(
            Transform(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             [<function add at 0x7f5cd96520d8>]), 
            [<function <lambda> at 0x7f5cd7822c00>]), 
           And(
            And(
             Literal('('), 
             Transform(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              [<function add at 0x7f5cd96520d8>]), 
             Delayed(matcher=<loop>)), 
            Transform(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             [<function add at 0x7f5cd96520d8>]), 
            Literal(')'))), 
          [<function <lambda> at 0x7f5cd78220d8>])), 
        0, None, 
        rest=And(
         Transform(
          Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
         Transform(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          [<function add at 0x7f5cd96520d8>]), 
         Transform(
          Or(
           Transform(
            Transform(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             [<function add at 0x7f5cd96520d8>]), 
            [<function <lambda> at 0x7f5cd7822c00>]), 
           And(
            And(
             Literal('('), 
             Transform(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              [<function add at 0x7f5cd96520d8>]), 
             Delayed(matcher=<loop>)), 
            Transform(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             [<function add at 0x7f5cd96520d8>]), 
            Literal(')'))), 
          [<function <lambda> at 0x7f5cd78220d8>])))), 
      [<function <lambda> at 0x7f5cd78228d0>])), 
    0, None, 
    rest=And(
     Transform(
      Any(restrict='+-'), [<function <lambda> at 0x7f5cd76aa050>]), 
     Transform(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      [<function add at 0x7f5cd96520d8>]), 
     Transform(
      And(
       Transform(
        Or(
         Transform(
          Transform(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           [<function add at 0x7f5cd96520d8>]), 
          [<function <lambda> at 0x7f5cd7822c00>]), 
         And(
          And(
           Literal('('), 
           Transform(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            [<function add at 0x7f5cd96520d8>]), 
           Delayed(matcher=<loop>)), 
          Transform(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           [<function add at 0x7f5cd96520d8>]), 
          Literal(')'))), 
        [<function <lambda> at 0x7f5cd78220d8>]), 
       Transform(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        [<function add at 0x7f5cd96520d8>]), 
       DepthFirst(
        And(
         Transform(
          Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
         Transform(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          [<function add at 0x7f5cd96520d8>]), 
         Transform(
          Or(
           Transform(
            Transform(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             [<function add at 0x7f5cd96520d8>]), 
            [<function <lambda> at 0x7f5cd7822c00>]), 
           And(
            And(
             Literal('('), 
             Transform(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              [<function add at 0x7f5cd96520d8>]), 
             Delayed(matcher=<loop>)), 
            Transform(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             [<function add at 0x7f5cd96520d8>]), 
            Literal(')'))), 
          [<function <lambda> at 0x7f5cd78220d8>])), 
        0, None, 
        rest=And(
         Transform(
          Any(restrict='*/'), [<function <lambda> at 0x7f5cd7822958>]), 
         Transform(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          [<function add at 0x7f5cd96520d8>]), 
         Transform(
          Or(
           Transform(
            Transform(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             [<function add at 0x7f5cd96520d8>]), 
            [<function <lambda> at 0x7f5cd7822c00>]), 
           And(
            And(
             Literal('('), 
             Transform(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              [<function add at 0x7f5cd96520d8>]), 
             Delayed(matcher=<loop>)), 
            Transform(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             [<function add at 0x7f5cd96520d8>]), 
            Literal(')'))), 
          [<function <lambda> at 0x7f5cd78220d8>])))), 
      [<function <lambda> at 0x7f5cd78228d0>])))), 
  [<function <lambda> at 0x7f5cd76aa160>]))''')
        
    def test_simple(self):
        expression  = Delayed()
        number      = Digit()[1:,...]
        expression += (number | '(' / expression / ')')

        description = str(expression)
        self.assert_same(description, r'''Delayed(
 matcher=Or(
  Transform(
   DepthFirst(
    Any(restrict='0123456789'), 1, None, rest=Any(restrict='0123456789')), 
   [<function add at 0xa4ed10>]), 
  And(
   And(
    Literal('('), 
    Transform(
     DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
     [<function add at 0xa4ed10>]), 
    Delayed(matcher=<loop>)), 
   Transform(
    DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
    [<function add at 0xa4ed10>]), 
   Literal(')'))))''')
 