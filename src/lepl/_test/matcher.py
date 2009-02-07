
from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers import * 
from lepl.node import Node


class StrTest(TestCase):
    
    def assert_same(self, text1, text2):
        assert self.__clean(text1) == self.__clean(text2), self.__clean(text1)
    
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

        description = repr(expression)
        self.assert_same(description, r'''Delayed(
 matcher=Apply(
  function=<function <lambda> at 0x7f63608010d8>, 
  matcher=And(
   Apply(
    function=<function <lambda> at 0x7f63608012f8>, 
    matcher=And(
     Apply(
      function=<function <lambda> at 0x7f63607f6d10>, 
      matcher=Or(
       Apply(
        function=<function <lambda> at 0x7f63607f67c0>, 
        matcher=Apply(
         function=<function add at 0x7f63607f6af0>, 
         matcher=DepthFirst(
          start=1, stop=None, rest=Any(restrict='0123456789'), 
          first=Any(restrict='0123456789')), 
         args=False, raw=True), 
        args=False, raw=False), 
       And(
        And(
         Literal(text='('), 
         Apply(
          function=<function add at 0x7f63607f6c00>, 
          matcher=DepthFirst(
           start=0, stop=None, rest=Any(restrict=' \t'), 
           first=Any(restrict=' \t')), 
          args=False, raw=True), 
         Delayed(matcher=<loop>)), 
        Apply(
         function=<function add at 0x7f63607f66b0>, 
         matcher=DepthFirst(
          start=0, stop=None, rest=Any(restrict=' \t'), 
          first=Any(restrict=' \t')), 
         args=False, raw=True), 
        Literal(text=')'))), 
      args=False, raw=False), 
     Apply(
      function=<function add at 0x7f6360801490>, 
      matcher=DepthFirst(
       start=0, stop=None, rest=Any(restrict=' \t'), 
       first=Any(restrict=' \t')), 
      args=False, raw=True), 
     DepthFirst(
      start=0, stop=None, 
      rest=And(
       Apply(
        function=<function <lambda> at 0x7f63608016b0>, 
        matcher=Any(restrict='*/'), args=False, raw=False), 
       Apply(
        function=<function add at 0x7f6360801518>, 
        matcher=DepthFirst(
         start=0, stop=None, rest=Any(restrict=' \t'), 
         first=Any(restrict=' \t')), 
        args=False, raw=True), 
       Apply(
        function=<function <lambda> at 0x7f63607f6d10>, 
        matcher=Or(
         Apply(
          function=<function <lambda> at 0x7f63607f67c0>, 
          matcher=Apply(
           function=<function add at 0x7f63607f6af0>, 
           matcher=DepthFirst(
            start=1, stop=None, rest=Any(restrict='0123456789'), 
            first=Any(restrict='0123456789')), 
           args=False, raw=True), 
          args=False, raw=False), 
         And(
          And(
           Literal(text='('), 
           Apply(
            function=<function add at 0x7f63607f6c00>, 
            matcher=DepthFirst(
             start=0, stop=None, rest=Any(restrict=' \t'), 
             first=Any(restrict=' \t')), 
            args=False, raw=True), 
           Delayed(matcher=<loop>)), 
          Apply(
           function=<function add at 0x7f63607f66b0>, 
           matcher=DepthFirst(
            start=0, stop=None, rest=Any(restrict=' \t'), 
            first=Any(restrict=' \t')), 
           args=False, raw=True), 
          Literal(text=')'))), 
        args=False, raw=False)), 
      first=And(
       Apply(
        function=<function <lambda> at 0x7f63608016b0>, 
        matcher=Any(restrict='*/'), args=False, raw=False), 
       Apply(
        function=<function add at 0x7f6360801518>, 
        matcher=DepthFirst(
         start=0, stop=None, rest=Any(restrict=' \t'), 
         first=Any(restrict=' \t')), 
        args=False, raw=True), 
       Apply(
        function=<function <lambda> at 0x7f63607f6d10>, 
        matcher=Or(
         Apply(
          function=<function <lambda> at 0x7f63607f67c0>, 
          matcher=Apply(
           function=<function add at 0x7f63607f6af0>, 
           matcher=DepthFirst(
            start=1, stop=None, rest=Any(restrict='0123456789'), 
            first=Any(restrict='0123456789')), 
           args=False, raw=True), 
          args=False, raw=False), 
         And(
          And(
           Literal(text='('), 
           Apply(
            function=<function add at 0x7f63607f6c00>, 
            matcher=DepthFirst(
             start=0, stop=None, rest=Any(restrict=' \t'), 
             first=Any(restrict=' \t')), 
            args=False, raw=True), 
           Delayed(matcher=<loop>)), 
          Apply(
           function=<function add at 0x7f63607f66b0>, 
           matcher=DepthFirst(
            start=0, stop=None, rest=Any(restrict=' \t'), 
            first=Any(restrict=' \t')), 
           args=False, raw=True), 
          Literal(text=')'))), 
        args=False, raw=False)))), 
    args=False, 
    raw=False), 
   Apply(
    function=<function add at 0x7f6360801270>, 
    matcher=DepthFirst(
     start=0, stop=None, rest=Any(restrict=' \t'), first=Any(restrict=' \t')), 
    args=False, raw=True), 
   DepthFirst(
    start=0, stop=None, 
    rest=And(
     Apply(
      function=<function <lambda> at 0x7f63608015a0>, 
      matcher=Any(restrict='+-'), args=False, raw=False), 
     Apply(
      function=<function add at 0x7f6360801408>, 
      matcher=DepthFirst(
       start=0, stop=None, rest=Any(restrict=' \t'), 
       first=Any(restrict=' \t')), 
      args=False, raw=True), 
     Apply(
      function=<function <lambda> at 0x7f63608012f8>, 
      matcher=And(
       Apply(
        function=<function <lambda> at 0x7f63607f6d10>, 
        matcher=Or(
         Apply(
          function=<function <lambda> at 0x7f63607f67c0>, 
          matcher=Apply(
           function=<function add at 0x7f63607f6af0>, 
           matcher=DepthFirst(
            start=1, stop=None, rest=Any(restrict='0123456789'), 
            first=Any(restrict='0123456789')), 
           args=False, raw=True), 
          args=False, raw=False), 
         And(
          And(
           Literal(text='('), 
           Apply(
            function=<function add at 0x7f63607f6c00>, 
            matcher=DepthFirst(
             start=0, stop=None, rest=Any(restrict=' \t'), 
             first=Any(restrict=' \t')), 
            args=False, raw=True), 
           Delayed(matcher=<loop>)), 
          Apply(
           function=<function add at 0x7f63607f66b0>, 
           matcher=DepthFirst(
            start=0, stop=None, rest=Any(restrict=' \t'), 
            first=Any(restrict=' \t')), 
           args=False, raw=True), 
          Literal(text=')'))), 
        args=False, raw=False), 
       Apply(
        function=<function add at 0x7f6360801490>, 
        matcher=DepthFirst(
         start=0, stop=None, rest=Any(restrict=' \t'), 
         first=Any(restrict=' \t')), 
        args=False, raw=True), 
       DepthFirst(
        start=0, stop=None, 
        rest=And(
         Apply(
          function=<function <lambda> at 0x7f63608016b0>, 
          matcher=Any(restrict='*/'), args=False, raw=False), 
         Apply(
          function=<function add at 0x7f6360801518>, 
          matcher=DepthFirst(
           start=0, stop=None, rest=Any(restrict=' \t'), 
           first=Any(restrict=' \t')), 
          args=False, raw=True), 
         Apply(
          function=<function <lambda> at 0x7f63607f6d10>, 
          matcher=Or(
           Apply(
            function=<function <lambda> at 0x7f63607f67c0>, 
            matcher=Apply(
             function=<function add at 0x7f63607f6af0>, 
             matcher=DepthFirst(
              start=1, stop=None, rest=Any(restrict='0123456789'), 
              first=Any(restrict='0123456789')), 
             args=False, raw=True), 
            args=False, raw=False), 
           And(
            And(
             Literal(text='('), 
             Apply(
              function=<function add at 0x7f63607f6c00>, 
              matcher=DepthFirst(
               start=0, stop=None, rest=Any(restrict=' \t'), 
               first=Any(restrict=' \t')), 
              args=False, raw=True), 
             Delayed(matcher=<loop>)), 
            Apply(
             function=<function add at 0x7f63607f66b0>, 
             matcher=DepthFirst(
              start=0, stop=None, rest=Any(restrict=' \t'), 
              first=Any(restrict=' \t')), 
             args=False, raw=True), 
            Literal(text=')'))), 
          args=False, raw=False)), 
        first=And(
         Apply(
          function=<function <lambda> at 0x7f63608016b0>, 
          matcher=Any(restrict='*/'), args=False, raw=False), 
         Apply(
          function=<function add at 0x7f6360801518>, 
          matcher=DepthFirst(
           start=0, stop=None, rest=Any(restrict=' \t'), 
           first=Any(restrict=' \t')), 
          args=False, raw=True), 
         Apply(
          function=<function <lambda> at 0x7f63607f6d10>, 
          matcher=Or(
           Apply(
            function=<function <lambda> at 0x7f63607f67c0>, 
            matcher=Apply(
             function=<function add at 0x7f63607f6af0>, 
             matcher=DepthFirst(
              start=1, stop=None, rest=Any(restrict='0123456789'), 
              first=Any(restrict='0123456789')), 
             args=False, raw=True), 
            args=False, raw=False), 
           And(
            And(
             Literal(text='('), 
             Apply(
              function=<function add at 0x7f63607f6c00>, 
              matcher=DepthFirst(
               start=0, stop=None, rest=Any(restrict=' \t'), 
               first=Any(restrict=' \t')), 
              args=False, raw=True), 
             Delayed(matcher=<loop>)), 
            Apply(
             function=<function add at 0x7f63607f66b0>, 
             matcher=DepthFirst(
              start=0, stop=None, rest=Any(restrict=' \t'), 
              first=Any(restrict=' \t')), 
             args=False, raw=True), 
            Literal(text=')'))), 
          args=False, raw=False)))), 
      args=False, 
      raw=False)), 
    first=And(
     Apply(
      function=<function <lambda> at 0x7f63608015a0>, 
      matcher=Any(restrict='+-'), args=False, raw=False), 
     Apply(
      function=<function add at 0x7f6360801408>, 
      matcher=DepthFirst(
       start=0, stop=None, rest=Any(restrict=' \t'), 
       first=Any(restrict=' \t')), 
      args=False, raw=True), 
     Apply(
      function=<function <lambda> at 0x7f63608012f8>, 
      matcher=And(
       Apply(
        function=<function <lambda> at 0x7f63607f6d10>, 
        matcher=Or(
         Apply(
          function=<function <lambda> at 0x7f63607f67c0>, 
          matcher=Apply(
           function=<function add at 0x7f63607f6af0>, 
           matcher=DepthFirst(
            start=1, stop=None, rest=Any(restrict='0123456789'), 
            first=Any(restrict='0123456789')), 
           args=False, raw=True), 
          args=False, raw=False), 
         And(
          And(
           Literal(text='('), 
           Apply(
            function=<function add at 0x7f63607f6c00>, 
            matcher=DepthFirst(
             start=0, stop=None, rest=Any(restrict=' \t'), 
             first=Any(restrict=' \t')), 
            args=False, raw=True), 
           Delayed(matcher=<loop>)), 
          Apply(
           function=<function add at 0x7f63607f66b0>, 
           matcher=DepthFirst(
            start=0, stop=None, rest=Any(restrict=' \t'), 
            first=Any(restrict=' \t')), 
           args=False, raw=True), 
          Literal(text=')'))), 
        args=False, raw=False), 
       Apply(
        function=<function add at 0x7f6360801490>, 
        matcher=DepthFirst(
         start=0, stop=None, rest=Any(restrict=' \t'), 
         first=Any(restrict=' \t')), 
        args=False, raw=True), 
       DepthFirst(
        start=0, stop=None, 
        rest=And(
         Apply(
          function=<function <lambda> at 0x7f63608016b0>, 
          matcher=Any(restrict='*/'), args=False, raw=False), 
         Apply(
          function=<function add at 0x7f6360801518>, 
          matcher=DepthFirst(
           start=0, stop=None, rest=Any(restrict=' \t'), 
           first=Any(restrict=' \t')), 
          args=False, raw=True), 
         Apply(
          function=<function <lambda> at 0x7f63607f6d10>, 
          matcher=Or(
           Apply(
            function=<function <lambda> at 0x7f63607f67c0>, 
            matcher=Apply(
             function=<function add at 0x7f63607f6af0>, 
             matcher=DepthFirst(
              start=1, stop=None, rest=Any(restrict='0123456789'), 
              first=Any(restrict='0123456789')), 
             args=False, raw=True), 
            args=False, raw=False), 
           And(
            And(
             Literal(text='('), 
             Apply(
              function=<function add at 0x7f63607f6c00>, 
              matcher=DepthFirst(
               start=0, stop=None, rest=Any(restrict=' \t'), 
               first=Any(restrict=' \t')), 
              args=False, raw=True), 
             Delayed(matcher=<loop>)), 
            Apply(
             function=<function add at 0x7f63607f66b0>, 
             matcher=DepthFirst(
              start=0, stop=None, rest=Any(restrict=' \t'), 
              first=Any(restrict=' \t')), 
             args=False, raw=True), 
            Literal(text=')'))), 
          args=False, raw=False)), 
        first=And(
         Apply(
          function=<function <lambda> at 0x7f63608016b0>, 
          matcher=Any(restrict='*/'), args=False, raw=False), 
         Apply(
          function=<function add at 0x7f6360801518>, 
          matcher=DepthFirst(
           start=0, stop=None, rest=Any(restrict=' \t'), 
           first=Any(restrict=' \t')), 
          args=False, raw=True), 
         Apply(
          function=<function <lambda> at 0x7f63607f6d10>, 
          matcher=Or(
           Apply(
            function=<function <lambda> at 0x7f63607f67c0>, 
            matcher=Apply(
             function=<function add at 0x7f63607f6af0>, 
             matcher=DepthFirst(
              start=1, stop=None, rest=Any(restrict='0123456789'), 
              first=Any(restrict='0123456789')), 
             args=False, raw=True), 
            args=False, raw=False), 
           And(
            And(
             Literal(text='('), 
             Apply(
              function=<function add at 0x7f63607f6c00>, 
              matcher=DepthFirst(
               start=0, stop=None, rest=Any(restrict=' \t'), 
               first=Any(restrict=' \t')), 
              args=False, raw=True), 
             Delayed(matcher=<loop>)), 
            Apply(
             function=<function add at 0x7f63607f66b0>, 
             matcher=DepthFirst(
              start=0, stop=None, rest=Any(restrict=' \t'), 
              first=Any(restrict=' \t')), 
             args=False, raw=True), 
            Literal(text=')'))), 
          args=False, raw=False)))), 
      args=False, 
      raw=False)))), 
  args=False, raw=False))''')
        
    def test_simple(self):
        expression  = Delayed()
        number      = Digit()[1:,...]
        expression += (number | '(' / expression / ')')

        description = repr(expression)
        self.assert_same(description, r'''Delayed(
 matcher=Or(
  Apply(
   function=<function add at 0x7f63607f4c00>, 
   matcher=DepthFirst(
    start=1, stop=None, rest=Any(restrict='0123456789'), 
    first=Any(restrict='0123456789')), 
   args=False, raw=True), 
  And(
   And(
    Literal(text='('), 
    Apply(
     function=<function add at 0x7f63607f68d0>, 
     matcher=DepthFirst(
      start=0, stop=None, rest=Any(restrict=' \t'), 
      first=Any(restrict=' \t')), 
     args=False, raw=True), 
    Delayed(matcher=<loop>)), 
   Apply(
    function=<function add at 0x7f63607f69e0>, 
    matcher=DepthFirst(
     start=0, stop=None, rest=Any(restrict=' \t'), first=Any(restrict=' \t')), 
    args=False, raw=True), 
   Literal(text=')'))))''')
 