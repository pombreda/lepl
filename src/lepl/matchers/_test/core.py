
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
Tests for the lepl.matchers.core module.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl._test.base import BaseTest
from lepl.matchers.combine import And, Or
from lepl.matchers.core import Any, Literal, Eof, Regexp, Delayed, Lookahead, \
    Consumer
from lepl.matchers.derived import Word, Newline, Space, AnyBut, Digit, \
    Integer, Columns
from lepl.matchers.monitor import Commit
from lepl.support.node import Node


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, R0201, R0904, R0903
# (dude this is just a test)

    
class AnyTest(TestCase):
    
    def test_any(self):
        result = Any().parse('a')
        assert result, result


class AndTest(BaseTest):

    def test_simple(self):
        #basicConfig(level=DEBUG)
        self.assert_join([1], Any(), ['1'])
        self.assert_join([1,2], And(Any(), Any()), ['12'])
        self.assert_join([1,2,3], And(Any(), Any()), ['12'])
        self.assert_join([1], And(Any(), Any()), [])
        
    def test_and(self):
        #basicConfig(level=DEBUG)
        self.assert_join([1,2], Any() & Any(), ['12'])
        self.assert_join([1,2,3], Any() & Any(), ['12'])
        self.assert_join([1,2,3], Any() & Any() & Any(), ['123'])
        self.assert_join([1], Any() & Any(), [])
        
    def assert_join(self, stream, match, target):
        match.config.no_full_match()
        result = [''.join(map(str, l)) 
                  for (l, _s) in match.match_items(stream)]
        assert target == result, result

    def test_add(self):
        #basicConfig(level=DEBUG)
        self.assert_list(['1','2'], Any() + Any(), [['12']])
        self.assert_list(['1','2','3'], Any() + Any(), [['12']])
        self.assert_list(['1','2','3'], Any() + Any() + Any(), [['123']])
        self.assert_list(['1'], Any() + Any(), [])
    
    
class CoercionTest(BaseTest):
    
    def test_right(self):
        #basicConfig(level=DEBUG)
        self.assert_direct('12', Any() + '2', [['12']])
         
    def test_left(self):
        #basicConfig(level=DEBUG)
        self.assert_direct('12', '1' + Any(), [['12']])
         

class OrTest(BaseTest):

    def test_simple(self):
        self.assert_direct('a', Or(Any('x'), Any('a'), Any()), [['a'],['a']])

    def test_bar(self):
        self.assert_direct('a', Any('x') | Any('a') | Any(), [['a'],['a']])
        
        
class FirstTest(BaseTest):
    
    def test_first(self):
        s = Space()
        aline = '#define' & ~s[1:] & Word() & ~s[1:] & Word() > list
        bline = AnyBut(s[0:] & Newline())[1:]
        line = aline % ~bline
        parser = line[0:,~(s[0:] & Newline())]
        parser.config.no_full_match()
        n = len(list(parser.match('#define A 1\ncrap n stuff\n#define B 22\n')))
        assert n == 16, n
        r = parser.parse('#define A 1\ncrap n stuff\n#define B 22\n')
        assert r == [['#define', 'A', '1'], ['#define', 'B', '22']], r


class LookaheadTest(BaseTest):
    
    def test_simple(self):
        self.assert_direct('ab', Any() + Lookahead('c') + Any(), [])
        self.assert_direct('ab', Any() + Lookahead('b') + Any(), [['ab']])

    def test_bang(self):
        self.assert_direct('ab', Any() + ~Lookahead('c') + Any(), [['ab']])
        self.assert_direct('ab', Any() + ~Lookahead('b') + Any(), [])


class CommitTest(BaseTest):
    
    def test_commit(self):
        self.assert_direct('abcd', 
            (Any()[0::'b'] + (Literal('d') | 
                              Literal('cd') + Commit() | 
                              Literal('bcd')) + Eof()), 
            [['abcd'], ['abcd']])
        

class RegexpTest(BaseTest):
    
    def test_group(self):
        self.assert_direct('  123x', Regexp(r'\s*\d+') & Any(), [['  123', 'x']])
        
    def test_groups(self):
        self.assert_direct('  123x', Regexp(r'\s*(\d)(\d+)') & Any(), [['1','23','x']])


class WordTest(BaseTest):
    
    def test_phone(self):
        self.assert_direct('andrew, 3333253', Word() / ',' / Integer() / Eof(), 
                           [['andrew', ',', ' ', '3333253']])
        
        
class EofTest(BaseTest):
    
    def test_eof(self):
        self.assert_direct('foo ', 'foo' / Eof(), [['foo', ' ']])
        

class LiteralTest(BaseTest):
    
    def test_literal(self):
        self.assert_direct('foo ', Literal('foo'), [['foo']])
        
        
class TransformTest(BaseTest):
    
    @staticmethod
    def mkappend(x):
        return lambda a: a + x
    
    def test_apply(self):
        # note extra list 
        self.assert_direct('foo ', Literal('foo') > self.mkappend(['b']), [[['foo', 'b']]])
        
    def test_kapply(self):
        # note extra list 
        self.assert_direct('foo ', Literal('foo') >> self.mkappend('b'), [['foob']])
        
    def test_nested(self):
        # note extra list 
        self.assert_direct('foo ', 
                           (Literal('foo') >> self.mkappend('b')) > self.mkappend(['c']), 
                           [[['foob', 'c']]])
        
        
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

        description = repr(expression)
        self.assert_same(description, r'''Delayed(matcher=Transform:[<function <lambda> at 0xfc96b0>](
 TransformableTrampolineWrapper<And:[]>(
  Transform:[<function <lambda> at 0xfc9490>](
   TransformableTrampolineWrapper<And:[]>(
    Transform:[<function <lambda> at 0xfc9270>](
     TransformableTrampolineWrapper<Or:[]>(
      Transform:[<function <lambda> at 0xfc9160>](
       Transform:[<function add at 0xbce628>](
        TrampolineWrapper<DepthFirst>(
         start=1,
         stop=None,
         rest=FunctionWrapper<Any:[]>('0123456789'),
         first=FunctionWrapper<Any:[]>('0123456789')),
        Transformation([<function add at 0xbce628>])),
       Transformation([<function <lambda> at 0xfc9160>])),
      TransformableTrampolineWrapper<And:[]>(
       TransformableTrampolineWrapper<And:[]>(
        '(',
        Transform:[<function add at 0xbce628>](
         TrampolineWrapper<DepthFirst>(
          start=0,
          stop=None,
          rest=FunctionWrapper<Any:[]>(' \t'),
          first=FunctionWrapper<Any:[]>(' \t')),
         Transformation([<function add at 0xbce628>])),
        [Delayed]),
       Transform:[<function add at 0xbce628>](
        TrampolineWrapper<DepthFirst>(
         start=0,
         stop=None,
         rest=FunctionWrapper<Any:[]>(' \t'),
         first=FunctionWrapper<Any:[]>(' \t')),
        Transformation([<function add at 0xbce628>])),
       ')')),
     Transformation([<function <lambda> at 0xfc9270>])),
    Transform:[<function add at 0xbce628>](
     TrampolineWrapper<DepthFirst>(
      start=0,
      stop=None,
      rest=FunctionWrapper<Any:[]>(' \t'),
      first=FunctionWrapper<Any:[]>(' \t')),
     Transformation([<function add at 0xbce628>])),
    TrampolineWrapper<DepthFirst>(
     start=0,
     stop=None,
     rest=TransformableTrampolineWrapper<And:[]>(
      Transform:[<function <lambda> at 0xfc9380>](
       FunctionWrapper<Any:[]>('*/'),
       Transformation([<function <lambda> at 0xfc9380>])),
      Transform:[<function add at 0xbce628>](
       TrampolineWrapper<DepthFirst>(
        start=0,
        stop=None,
        rest=FunctionWrapper<Any:[]>(' \t'),
        first=FunctionWrapper<Any:[]>(' \t')),
       Transformation([<function add at 0xbce628>])),
      Transform:[<function <lambda> at 0xfc9270>](
       TransformableTrampolineWrapper<Or:[]>(
        Transform:[<function <lambda> at 0xfc9160>](
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=1,
           stop=None,
           rest=FunctionWrapper<Any:[]>('0123456789'),
           first=FunctionWrapper<Any:[]>('0123456789')),
          Transformation([<function add at 0xbce628>])),
         Transformation([<function <lambda> at 0xfc9160>])),
        TransformableTrampolineWrapper<And:[]>(
         TransformableTrampolineWrapper<And:[]>(
          '(',
          Transform:[<function add at 0xbce628>](
           TrampolineWrapper<DepthFirst>(
            start=0,
            stop=None,
            rest=FunctionWrapper<Any:[]>(' \t'),
            first=FunctionWrapper<Any:[]>(' \t')),
           Transformation([<function add at 0xbce628>])),
          [Delayed]),
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=0,
           stop=None,
           rest=FunctionWrapper<Any:[]>(' \t'),
           first=FunctionWrapper<Any:[]>(' \t')),
          Transformation([<function add at 0xbce628>])),
         ')')),
       Transformation([<function <lambda> at 0xfc9270>]))),
     first=TransformableTrampolineWrapper<And:[]>(
      Transform:[<function <lambda> at 0xfc9380>](
       FunctionWrapper<Any:[]>('*/'),
       Transformation([<function <lambda> at 0xfc9380>])),
      Transform:[<function add at 0xbce628>](
       TrampolineWrapper<DepthFirst>(
        start=0,
        stop=None,
        rest=FunctionWrapper<Any:[]>(' \t'),
        first=FunctionWrapper<Any:[]>(' \t')),
       Transformation([<function add at 0xbce628>])),
      Transform:[<function <lambda> at 0xfc9270>](
       TransformableTrampolineWrapper<Or:[]>(
        Transform:[<function <lambda> at 0xfc9160>](
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=1,
           stop=None,
           rest=FunctionWrapper<Any:[]>('0123456789'),
           first=FunctionWrapper<Any:[]>('0123456789')),
          Transformation([<function add at 0xbce628>])),
         Transformation([<function <lambda> at 0xfc9160>])),
        TransformableTrampolineWrapper<And:[]>(
         TransformableTrampolineWrapper<And:[]>(
          '(',
          Transform:[<function add at 0xbce628>](
           TrampolineWrapper<DepthFirst>(
            start=0,
            stop=None,
            rest=FunctionWrapper<Any:[]>(' \t'),
            first=FunctionWrapper<Any:[]>(' \t')),
           Transformation([<function add at 0xbce628>])),
          [Delayed]),
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=0,
           stop=None,
           rest=FunctionWrapper<Any:[]>(' \t'),
           first=FunctionWrapper<Any:[]>(' \t')),
          Transformation([<function add at 0xbce628>])),
         ')')),
       Transformation([<function <lambda> at 0xfc9270>]))))),
   Transformation([<function <lambda> at 0xfc9490>])),
  Transform:[<function add at 0xbce628>](
   TrampolineWrapper<DepthFirst>(
    start=0,
    stop=None,
    rest=FunctionWrapper<Any:[]>(' \t'),
    first=FunctionWrapper<Any:[]>(' \t')),
   Transformation([<function add at 0xbce628>])),
  TrampolineWrapper<DepthFirst>(
   start=0,
   stop=None,
   rest=TransformableTrampolineWrapper<And:[]>(
    Transform:[<function <lambda> at 0xfc95a0>](
     FunctionWrapper<Any:[]>('+-'),
     Transformation([<function <lambda> at 0xfc95a0>])),
    Transform:[<function add at 0xbce628>](
     TrampolineWrapper<DepthFirst>(
      start=0,
      stop=None,
      rest=FunctionWrapper<Any:[]>(' \t'),
      first=FunctionWrapper<Any:[]>(' \t')),
     Transformation([<function add at 0xbce628>])),
    Transform:[<function <lambda> at 0xfc9490>](
     TransformableTrampolineWrapper<And:[]>(
      Transform:[<function <lambda> at 0xfc9270>](
       TransformableTrampolineWrapper<Or:[]>(
        Transform:[<function <lambda> at 0xfc9160>](
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=1,
           stop=None,
           rest=FunctionWrapper<Any:[]>('0123456789'),
           first=FunctionWrapper<Any:[]>('0123456789')),
          Transformation([<function add at 0xbce628>])),
         Transformation([<function <lambda> at 0xfc9160>])),
        TransformableTrampolineWrapper<And:[]>(
         TransformableTrampolineWrapper<And:[]>(
          '(',
          Transform:[<function add at 0xbce628>](
           TrampolineWrapper<DepthFirst>(
            start=0,
            stop=None,
            rest=FunctionWrapper<Any:[]>(' \t'),
            first=FunctionWrapper<Any:[]>(' \t')),
           Transformation([<function add at 0xbce628>])),
          [Delayed]),
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=0,
           stop=None,
           rest=FunctionWrapper<Any:[]>(' \t'),
           first=FunctionWrapper<Any:[]>(' \t')),
          Transformation([<function add at 0xbce628>])),
         ')')),
       Transformation([<function <lambda> at 0xfc9270>])),
      Transform:[<function add at 0xbce628>](
       TrampolineWrapper<DepthFirst>(
        start=0,
        stop=None,
        rest=FunctionWrapper<Any:[]>(' \t'),
        first=FunctionWrapper<Any:[]>(' \t')),
       Transformation([<function add at 0xbce628>])),
      TrampolineWrapper<DepthFirst>(
       start=0,
       stop=None,
       rest=TransformableTrampolineWrapper<And:[]>(
        Transform:[<function <lambda> at 0xfc9380>](
         FunctionWrapper<Any:[]>('*/'),
         Transformation([<function <lambda> at 0xfc9380>])),
        Transform:[<function add at 0xbce628>](
         TrampolineWrapper<DepthFirst>(
          start=0,
          stop=None,
          rest=FunctionWrapper<Any:[]>(' \t'),
          first=FunctionWrapper<Any:[]>(' \t')),
         Transformation([<function add at 0xbce628>])),
        Transform:[<function <lambda> at 0xfc9270>](
         TransformableTrampolineWrapper<Or:[]>(
          Transform:[<function <lambda> at 0xfc9160>](
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=1,
             stop=None,
             rest=FunctionWrapper<Any:[]>('0123456789'),
             first=FunctionWrapper<Any:[]>('0123456789')),
            Transformation([<function add at 0xbce628>])),
           Transformation([<function <lambda> at 0xfc9160>])),
          TransformableTrampolineWrapper<And:[]>(
           TransformableTrampolineWrapper<And:[]>(
            '(',
            Transform:[<function add at 0xbce628>](
             TrampolineWrapper<DepthFirst>(
              start=0,
              stop=None,
              rest=FunctionWrapper<Any:[]>(' \t'),
              first=FunctionWrapper<Any:[]>(' \t')),
             Transformation([<function add at 0xbce628>])),
            [Delayed]),
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=0,
             stop=None,
             rest=FunctionWrapper<Any:[]>(' \t'),
             first=FunctionWrapper<Any:[]>(' \t')),
            Transformation([<function add at 0xbce628>])),
           ')')),
         Transformation([<function <lambda> at 0xfc9270>]))),
       first=TransformableTrampolineWrapper<And:[]>(
        Transform:[<function <lambda> at 0xfc9380>](
         FunctionWrapper<Any:[]>('*/'),
         Transformation([<function <lambda> at 0xfc9380>])),
        Transform:[<function add at 0xbce628>](
         TrampolineWrapper<DepthFirst>(
          start=0,
          stop=None,
          rest=FunctionWrapper<Any:[]>(' \t'),
          first=FunctionWrapper<Any:[]>(' \t')),
         Transformation([<function add at 0xbce628>])),
        Transform:[<function <lambda> at 0xfc9270>](
         TransformableTrampolineWrapper<Or:[]>(
          Transform:[<function <lambda> at 0xfc9160>](
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=1,
             stop=None,
             rest=FunctionWrapper<Any:[]>('0123456789'),
             first=FunctionWrapper<Any:[]>('0123456789')),
            Transformation([<function add at 0xbce628>])),
           Transformation([<function <lambda> at 0xfc9160>])),
          TransformableTrampolineWrapper<And:[]>(
           TransformableTrampolineWrapper<And:[]>(
            '(',
            Transform:[<function add at 0xbce628>](
             TrampolineWrapper<DepthFirst>(
              start=0,
              stop=None,
              rest=FunctionWrapper<Any:[]>(' \t'),
              first=FunctionWrapper<Any:[]>(' \t')),
             Transformation([<function add at 0xbce628>])),
            [Delayed]),
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=0,
             stop=None,
             rest=FunctionWrapper<Any:[]>(' \t'),
             first=FunctionWrapper<Any:[]>(' \t')),
            Transformation([<function add at 0xbce628>])),
           ')')),
         Transformation([<function <lambda> at 0xfc9270>]))))),
     Transformation([<function <lambda> at 0xfc9490>]))),
   first=TransformableTrampolineWrapper<And:[]>(
    Transform:[<function <lambda> at 0xfc95a0>](
     FunctionWrapper<Any:[]>('+-'),
     Transformation([<function <lambda> at 0xfc95a0>])),
    Transform:[<function add at 0xbce628>](
     TrampolineWrapper<DepthFirst>(
      start=0,
      stop=None,
      rest=FunctionWrapper<Any:[]>(' \t'),
      first=FunctionWrapper<Any:[]>(' \t')),
     Transformation([<function add at 0xbce628>])),
    Transform:[<function <lambda> at 0xfc9490>](
     TransformableTrampolineWrapper<And:[]>(
      Transform:[<function <lambda> at 0xfc9270>](
       TransformableTrampolineWrapper<Or:[]>(
        Transform:[<function <lambda> at 0xfc9160>](
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=1,
           stop=None,
           rest=FunctionWrapper<Any:[]>('0123456789'),
           first=FunctionWrapper<Any:[]>('0123456789')),
          Transformation([<function add at 0xbce628>])),
         Transformation([<function <lambda> at 0xfc9160>])),
        TransformableTrampolineWrapper<And:[]>(
         TransformableTrampolineWrapper<And:[]>(
          '(',
          Transform:[<function add at 0xbce628>](
           TrampolineWrapper<DepthFirst>(
            start=0,
            stop=None,
            rest=FunctionWrapper<Any:[]>(' \t'),
            first=FunctionWrapper<Any:[]>(' \t')),
           Transformation([<function add at 0xbce628>])),
          [Delayed]),
         Transform:[<function add at 0xbce628>](
          TrampolineWrapper<DepthFirst>(
           start=0,
           stop=None,
           rest=FunctionWrapper<Any:[]>(' \t'),
           first=FunctionWrapper<Any:[]>(' \t')),
          Transformation([<function add at 0xbce628>])),
         ')')),
       Transformation([<function <lambda> at 0xfc9270>])),
      Transform:[<function add at 0xbce628>](
       TrampolineWrapper<DepthFirst>(
        start=0,
        stop=None,
        rest=FunctionWrapper<Any:[]>(' \t'),
        first=FunctionWrapper<Any:[]>(' \t')),
       Transformation([<function add at 0xbce628>])),
      TrampolineWrapper<DepthFirst>(
       start=0,
       stop=None,
       rest=TransformableTrampolineWrapper<And:[]>(
        Transform:[<function <lambda> at 0xfc9380>](
         FunctionWrapper<Any:[]>('*/'),
         Transformation([<function <lambda> at 0xfc9380>])),
        Transform:[<function add at 0xbce628>](
         TrampolineWrapper<DepthFirst>(
          start=0,
          stop=None,
          rest=FunctionWrapper<Any:[]>(' \t'),
          first=FunctionWrapper<Any:[]>(' \t')),
         Transformation([<function add at 0xbce628>])),
        Transform:[<function <lambda> at 0xfc9270>](
         TransformableTrampolineWrapper<Or:[]>(
          Transform:[<function <lambda> at 0xfc9160>](
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=1,
             stop=None,
             rest=FunctionWrapper<Any:[]>('0123456789'),
             first=FunctionWrapper<Any:[]>('0123456789')),
            Transformation([<function add at 0xbce628>])),
           Transformation([<function <lambda> at 0xfc9160>])),
          TransformableTrampolineWrapper<And:[]>(
           TransformableTrampolineWrapper<And:[]>(
            '(',
            Transform:[<function add at 0xbce628>](
             TrampolineWrapper<DepthFirst>(
              start=0,
              stop=None,
              rest=FunctionWrapper<Any:[]>(' \t'),
              first=FunctionWrapper<Any:[]>(' \t')),
             Transformation([<function add at 0xbce628>])),
            [Delayed]),
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=0,
             stop=None,
             rest=FunctionWrapper<Any:[]>(' \t'),
             first=FunctionWrapper<Any:[]>(' \t')),
            Transformation([<function add at 0xbce628>])),
           ')')),
         Transformation([<function <lambda> at 0xfc9270>]))),
       first=TransformableTrampolineWrapper<And:[]>(
        Transform:[<function <lambda> at 0xfc9380>](
         FunctionWrapper<Any:[]>('*/'),
         Transformation([<function <lambda> at 0xfc9380>])),
        Transform:[<function add at 0xbce628>](
         TrampolineWrapper<DepthFirst>(
          start=0,
          stop=None,
          rest=FunctionWrapper<Any:[]>(' \t'),
          first=FunctionWrapper<Any:[]>(' \t')),
         Transformation([<function add at 0xbce628>])),
        Transform:[<function <lambda> at 0xfc9270>](
         TransformableTrampolineWrapper<Or:[]>(
          Transform:[<function <lambda> at 0xfc9160>](
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=1,
             stop=None,
             rest=FunctionWrapper<Any:[]>('0123456789'),
             first=FunctionWrapper<Any:[]>('0123456789')),
            Transformation([<function add at 0xbce628>])),
           Transformation([<function <lambda> at 0xfc9160>])),
          TransformableTrampolineWrapper<And:[]>(
           TransformableTrampolineWrapper<And:[]>(
            '(',
            Transform:[<function add at 0xbce628>](
             TrampolineWrapper<DepthFirst>(
              start=0,
              stop=None,
              rest=FunctionWrapper<Any:[]>(' \t'),
              first=FunctionWrapper<Any:[]>(' \t')),
             Transformation([<function add at 0xbce628>])),
            [Delayed]),
           Transform:[<function add at 0xbce628>](
            TrampolineWrapper<DepthFirst>(
             start=0,
             stop=None,
             rest=FunctionWrapper<Any:[]>(' \t'),
             first=FunctionWrapper<Any:[]>(' \t')),
            Transformation([<function add at 0xbce628>])),
           ')')),
         Transformation([<function <lambda> at 0xfc9270>]))))),
     Transformation([<function <lambda> at 0xfc9490>]))))),
 Transformation([<function <lambda> at 0xfc96b0>])))''')
        
    def test_simple(self):
        expression  = Delayed()
        number      = Digit()[1:,...]
        expression += (number | '(' / expression / ')')

        description = repr(expression)
        self.assert_same(description, r'''Delayed(matcher=TransformableTrampolineWrapper<Or:[]>(
 Transform:[<function add at 0xbce628>](
  TrampolineWrapper<DepthFirst>(
   start=1,
   stop=None,
   rest=FunctionWrapper<Any:[]>('0123456789'),
   first=FunctionWrapper<Any:[]>('0123456789')),
  Transformation([<function add at 0xbce628>])),
 TransformableTrampolineWrapper<And:[]>(
  TransformableTrampolineWrapper<And:[]>(
   '(',
   Transform:[<function add at 0xbce628>](
    TrampolineWrapper<DepthFirst>(
     start=0,
     stop=None,
     rest=FunctionWrapper<Any:[]>(' \t'),
     first=FunctionWrapper<Any:[]>(' \t')),
    Transformation([<function add at 0xbce628>])),
   [Delayed]),
  Transform:[<function add at 0xbce628>](
   TrampolineWrapper<DepthFirst>(
    start=0,
    stop=None,
    rest=FunctionWrapper<Any:[]>(' \t'),
    first=FunctionWrapper<Any:[]>(' \t')),
   Transformation([<function add at 0xbce628>])),
  ')')))''')
        description = expression.tree()
        self.assert_same(description, r"""Delayed
 `- matcher TransformableTrampolineWrapper
     +- Transform
     |   +- TrampolineWrapper
     |   |   +- start 1
     |   |   +- stop None
     |   |   +- rest FunctionWrapper
     |   |   |   `- '0123456789'
     |   |   `- first FunctionWrapper
     |   |       `- '0123456789'
     |   `- Transformation([<function add at 0xbce5a0>])
     `- TransformableTrampolineWrapper
         +- TransformableTrampolineWrapper
         |   +- '('
         |   +- Transform
         |   |   +- TrampolineWrapper
         |   |   |   +- start 0
         |   |   |   +- stop None
         |   |   |   +- rest FunctionWrapper
         |   |   |   |   `- ' \t'
         |   |   |   `- first FunctionWrapper
         |   |   |       `- ' \t'
         |   |   `- Transformation([<function add at 0xbce5a0>])
         |   `- Delayed
         |       `- matcher <loop>
         +- Transform
         |   +- TrampolineWrapper
         |   |   +- start 0
         |   |   +- stop None
         |   |   +- rest FunctionWrapper
         |   |   |   `- ' \t'
         |   |   `- first FunctionWrapper
         |   |       `- ' \t'
         |   `- Transformation([<function add at 0xbce5a0>])
         `- ')'""")

class ColumnsTest(BaseTest):
    
    def test_columns(self):
        self.assert_direct('0123456789', 
                           Columns(((0,3), Any()[3,...]),
                                   ((0,4), Any()[4:,...]),
                                   ((5,8), Any()[3:,...])),
                           [['012', '0123', '567']])

    def test_table(self):
        #basicConfig(level=DEBUG)
        self.assert_direct(
'''0123456789
abcdefghij
''', 
                           Columns(((0,3), Any()[3:,...]),
                                   ((0,4), Any()[4:,...]),
                                   ((5,8), Any()[3:,...]))[2],
                           [['012', '0123', '567',
                             'abc', 'abcd', 'fgh']])


class ConsumerTest(BaseTest):
    
    def test_simple(self):
        parser = Consumer(Any()).null_parser()
        result = parser('a')
        assert ['a'] == result, result
        
    def test_fail(self):
        matcher = Consumer(Any('b'))
        matcher.config.no_full_match()
        parser = matcher.null_parser()
        result = parser('a')
        assert None == result, result
        
    def test_complex(self):
        '''
        This test requires evaluation of sub-matchers via trampolining; if
        it fails then there may be an issue with generator_matcher.
        '''
        parser = Consumer(Any() & Any('b')).null_parser()
        result = parser('ab')
        assert ['a', 'b'] == result, result
        