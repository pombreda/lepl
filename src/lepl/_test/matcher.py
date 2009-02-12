
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
 Apply(
  And(
   Apply(
    And(
     Apply(
      Or(
       Apply(
        Apply(
         DepthFirst(
          Any(restrict='0123456789'), 1, None, 
          rest=Any(restrict='0123456789')), 
         <function add at 0x7f56d77dbc88>, raw=True, args=False), 
        <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
       And(
        And(
         Literal('('), 
         Apply(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          <function add at 0x7f56d77db050>, raw=True, args=False), 
         Delayed(<loop>)), 
        Apply(
         DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
         <function add at 0x7f56d77dbd98>, raw=True, args=False), 
        Literal(')'))), 
      <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False), 
     Apply(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      <function add at 0x7f56d77dbf30>, raw=True, args=False), 
     DepthFirst(
      And(
       Apply(
        Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, raw=False, 
        args=False), 
       Apply(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        <function add at 0x7f56d77dbd10>, raw=True, args=False), 
       Apply(
        Or(
         Apply(
          Apply(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           <function add at 0x7f56d77dbc88>, raw=True, args=False), 
          <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
         And(
          And(
           Literal('('), 
           Apply(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            <function add at 0x7f56d77db050>, raw=True, args=False), 
           Delayed(<loop>)), 
          Apply(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           <function add at 0x7f56d77dbd98>, raw=True, args=False), 
          Literal(')'))), 
        <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)), 
      0, None, 
      rest=And(
       Apply(
        Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, raw=False, 
        args=False), 
       Apply(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        <function add at 0x7f56d77dbd10>, raw=True, args=False), 
       Apply(
        Or(
         Apply(
          Apply(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           <function add at 0x7f56d77dbc88>, raw=True, args=False), 
          <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
         And(
          And(
           Literal('('), 
           Apply(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            <function add at 0x7f56d77db050>, raw=True, args=False), 
           Delayed(<loop>)), 
          Apply(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           <function add at 0x7f56d77dbd98>, raw=True, args=False), 
          Literal(')'))), 
        <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)))), 
    <function <lambda> at 0x7f56d77dbea8>, raw=False, 
    args=False), 
   Apply(
    DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
    <function add at 0x7f56d77f9270>, raw=True, args=False), 
   DepthFirst(
    And(
     Apply(
      Any(restrict='+-'), <function <lambda> at 0x7f56d77f90d8>, raw=False, 
      args=False), 
     Apply(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      <function add at 0x7f56d77f9050>, raw=True, args=False), 
     Apply(
      And(
       Apply(
        Or(
         Apply(
          Apply(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           <function add at 0x7f56d77dbc88>, raw=True, args=False), 
          <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
         And(
          And(
           Literal('('), 
           Apply(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            <function add at 0x7f56d77db050>, raw=True, args=False), 
           Delayed(<loop>)), 
          Apply(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           <function add at 0x7f56d77dbd98>, raw=True, args=False), 
          Literal(')'))), 
        <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False), 
       Apply(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        <function add at 0x7f56d77dbf30>, raw=True, args=False), 
       DepthFirst(
        And(
         Apply(
          Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, 
          raw=False, args=False), 
         Apply(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          <function add at 0x7f56d77dbd10>, raw=True, args=False), 
         Apply(
          Or(
           Apply(
            Apply(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             <function add at 0x7f56d77dbc88>, raw=True, args=False), 
            <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
           And(
            And(
             Literal('('), 
             Apply(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              <function add at 0x7f56d77db050>, raw=True, args=False), 
             Delayed(<loop>)), 
            Apply(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             <function add at 0x7f56d77dbd98>, raw=True, args=False), 
            Literal(')'))), 
          <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)), 
        0, None, 
        rest=And(
         Apply(
          Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, 
          raw=False, args=False), 
         Apply(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          <function add at 0x7f56d77dbd10>, raw=True, args=False), 
         Apply(
          Or(
           Apply(
            Apply(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             <function add at 0x7f56d77dbc88>, raw=True, args=False), 
            <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
           And(
            And(
             Literal('('), 
             Apply(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              <function add at 0x7f56d77db050>, raw=True, args=False), 
             Delayed(<loop>)), 
            Apply(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             <function add at 0x7f56d77dbd98>, raw=True, args=False), 
            Literal(')'))), 
          <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)))), 
      <function <lambda> at 0x7f56d77dbea8>, raw=False, 
      args=False)), 
    0, None, 
    rest=And(
     Apply(
      Any(restrict='+-'), <function <lambda> at 0x7f56d77f90d8>, raw=False, 
      args=False), 
     Apply(
      DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
      <function add at 0x7f56d77f9050>, raw=True, args=False), 
     Apply(
      And(
       Apply(
        Or(
         Apply(
          Apply(
           DepthFirst(
            Any(restrict='0123456789'), 1, None, 
            rest=Any(restrict='0123456789')), 
           <function add at 0x7f56d77dbc88>, raw=True, args=False), 
          <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
         And(
          And(
           Literal('('), 
           Apply(
            DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
            <function add at 0x7f56d77db050>, raw=True, args=False), 
           Delayed(<loop>)), 
          Apply(
           DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
           <function add at 0x7f56d77dbd98>, raw=True, args=False), 
          Literal(')'))), 
        <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False), 
       Apply(
        DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
        <function add at 0x7f56d77dbf30>, raw=True, args=False), 
       DepthFirst(
        And(
         Apply(
          Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, 
          raw=False, args=False), 
         Apply(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          <function add at 0x7f56d77dbd10>, raw=True, args=False), 
         Apply(
          Or(
           Apply(
            Apply(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             <function add at 0x7f56d77dbc88>, raw=True, args=False), 
            <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
           And(
            And(
             Literal('('), 
             Apply(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              <function add at 0x7f56d77db050>, raw=True, args=False), 
             Delayed(<loop>)), 
            Apply(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             <function add at 0x7f56d77dbd98>, raw=True, args=False), 
            Literal(')'))), 
          <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)), 
        0, None, 
        rest=And(
         Apply(
          Any(restrict='*/'), <function <lambda> at 0x7f56d77dbb78>, 
          raw=False, args=False), 
         Apply(
          DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
          <function add at 0x7f56d77dbd10>, raw=True, args=False), 
         Apply(
          Or(
           Apply(
            Apply(
             DepthFirst(
              Any(restrict='0123456789'), 1, None, 
              rest=Any(restrict='0123456789')), 
             <function add at 0x7f56d77dbc88>, raw=True, args=False), 
            <function <lambda> at 0x7f56d77dbc00>, raw=False, args=False), 
           And(
            And(
             Literal('('), 
             Apply(
              DepthFirst(
               Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
              <function add at 0x7f56d77db050>, raw=True, args=False), 
             Delayed(<loop>)), 
            Apply(
             DepthFirst(
              Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
             <function add at 0x7f56d77dbd98>, raw=True, args=False), 
            Literal(')'))), 
          <function <lambda> at 0x7f56d77dbe20>, raw=False, args=False)))), 
      <function <lambda> at 0x7f56d77dbea8>, raw=False, 
      args=False)))), 
  <function <lambda> at 0x7f56d77f92f8>, raw=False, args=False))''')
        
    def test_simple(self):
        expression  = Delayed()
        number      = Digit()[1:,...]
        expression += (number | '(' / expression / ')')

        description = str(expression)
        self.assert_same(description, r'''Delayed(
 Or(
  Apply(
   DepthFirst(
    Any(restrict='0123456789'), 1, None, rest=Any(restrict='0123456789')), 
   <function add at 0x7f551afda738>, raw=True, args=False), 
  And(
   And(
    Literal('('), 
    Apply(
     DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
     <function add at 0x7f551ab4d380>, raw=True, args=False), 
    Delayed(<loop>)), 
   Apply(
    DepthFirst(Any(restrict=' \t'), 0, None, rest=Any(restrict=' \t')), 
    <function add at 0x7f551ad76d98>, raw=True, args=False), 
   Literal(')'))))''')
 