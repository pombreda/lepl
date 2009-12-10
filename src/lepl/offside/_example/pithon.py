
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
from lepl._example.support import Example


class PythonExample(Example):
    
    def test_python(self):
        
        word = Token(Word(Lower()))
        continuation = Token(r'\\')
        symbol = Token(Any('()'))
        introduce = ~Token(':')
        comma = ~Token(',')
        hash = Token('#.*')
        
        CLine = ContinuedBLineFactory(continuation)
        
        statement = word[1:]
        args = Extend(word[:, comma]) > tuple
        function = word[1:] & ~symbol('(') & args & ~symbol(')')

        block = Delayed()
        blank = ~Line(Empty())
        comment = ~Line(hash)
        line = Or((CLine(statement) | block) > list,
                  blank,
                  comment)
        block += CLine((function | statement) & introduce) & Block(line[1:])
        
        program = (line[:] & Eos())
        parser = program.string_parser(
                    LineAwareConfiguration(block_policy=rightmost))
        
        result = parser('''
# this is a grammar with a similar 
# line structure to python

if something:
  then we indent
else:
    something else
    # note a different indent size here
  
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
  # and we can have blank lines inside a block:
  
  like this
    # along with strangely placed comments
  but still keep blocks tied together
''')
        assert result == \
        [
          ['if', 'something', 
            ['then', 'we', 'indent']
          ],
          ['else', 
            ['something', 'else'], 
          ],
          ['def', 'function', ('a', 'b', 'c'), 
            ['we', 'can', 'nest', 'blocks', 
              ['like', 'this']
            ], 
            ['and', 'we', 'can', 'also', 'have', 'explicit', 'continuations', 
             'with', 'any', 'indentation'], 
          ], 
          ['same', 'for', ('argument', 'lists'), 
            ['which', 'do', 'not', 'need', 'the'], 
            ['continuation', 'marker'], 
            ['like', 'this'], 
            ['but', 'still', 'keep', 'blocks', 'tied', 'together']
          ]
        ], result
