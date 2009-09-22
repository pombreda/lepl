
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


# pylint: disable-msg=W0614, W0401, W0621, C0103, C0111, R0201, R0904
#@PydevCodeAnalysisIgnore

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class PithonTest(TestCase):
    
    @property
    def parser(self):
        
        word = Token(Word(Lower()))
        continuation = Token(r'\\')
        symbol = Token(Any('()'))
        introduce = ~Token(':')
        comma = ~Token(',')
        
        CLine = ContinuedBLineFactory(continuation)
        
        statement = word[1:]
        args = Extend(word[:, comma]) > tuple
        function = word[1:] & ~symbol('(') & args & ~symbol(')')

        block = Delayed()
        line = (CLine(statement) | block | Line(Empty())) > list
        block += CLine((function | statement) & introduce) & Block(line[1:])
        
        program = (line[:] & Eos())
        return program.string_parser(
                    LineAwareConfiguration(block_policy=2,
                                         monitors=[TraceResults(True)]))
    
    def test_blocks(self):
        #basicConfig(level=DEBUG)
        program1 = '''
kopo fjire ifejfr
ogptkr jgitr gtr
ffjireofr(kfkorp, freopk):
  jifr fireo
  frefre jifoji
  jio frefre:
    jiforejifre fiorej
    jfore fire
    jioj
  jioj
jiojio
'''
        result = self.parser(program1)
        assert result == [[], 
                          ['kopo', 'fjire', 'ifejfr'], 
                          ['ogptkr', 'jgitr', 'gtr'], 
                          ['ffjireofr', ('kfkorp', 'freopk'), 
                           ['jifr', 'fireo'], 
                           ['frefre', 'jifoji'], 
                           ['jio', 'frefre',
                            ['jiforejifre', 'fiorej'], 
                            ['jfore', 'fire'], 
                            ['jioj']], 
                           ['jioj']], 
                          ['jiojio']], result
        
    def test_no_lexer(self):
        #basicConfig(level=DEBUG)
        try:
            self.parser('123')
            assert False, 'expected exception'
        except LexerError as error:
            assert str(error) == 'No lexer for \'123\' at ' \
                'line 1 character 0 of str: \'123\'.', str(error)
                
    def test_extend(self):
        #basicConfig(level=DEBUG)
        result = self.parser('''
def foo(abc, def,
        ghi):
  jgiog
''')
        assert result == [[], 
                          ['def', 'foo', ('abc', 'def', 'ghi'), 
                           ['jgiog']]], result
        
    def test_cline(self):
        #basicConfig(level=DEBUG)
        result = self.parser('''
this is a single \
  line spread over \
    many actual \
lines
and this is another
''')
        assert result == [[], 
                          ['this', 'is', 'a', 'single', 'line', 'spread', 
                           'over', 'many', 'actual', 'lines'], 
                           ['and', 'this', 'is', 'another']], result
                           
    def test_all(self):
        #basicConfig(level=DEBUG)
        result = self.parser('''
this is a grammar with a similar 
line structure to python

if something:
  then we indent
else:
  something else
  
def function(a, b, c):
  we can nest blocks:
    like this
  and we can also \
    have explicit continuations \
    with \
any \
       indentation
       
same for (argument,
          lists):
  which do not need the
  continuation marker
''')
        assert result == \
        [ [], 
          ['this', 'is', 'a', 'grammar', 'with', 'a', 'similar'], 
          ['line', 'structure', 'to', 'python'], 
          [], 
          ['if', 'something', 
            ['then', 'we', 'indent']], 
          ['else', 
            ['something', 'else'], 
          []], 
          ['def', 'function', ('a', 'b', 'c'), 
            ['we', 'can', 'nest', 'blocks', 
              ['like', 'this']], 
            ['and', 'we', 'can', 'also', 'have', 'explicit', 
             'continuations', 'with', 'any', 'indentation'], 
            []], 
          ['same', 'for', ('argument', 'lists'), 
            ['which', 'do', 'not', 'need', 'the'], 
            ['continuation', 'marker']]], result
