
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
Show how the BLine and Block tokens can be used
'''

# pylint: disable-msg=W0401, W0614, W0621, C0103, C0111, R0201, C0301, R0904
#@PydevCodeAnalysisIgnore


#from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class OffsideExample(Example):
    
    def test_offside(self):
        #basicConfig(level=DEBUG)
        introduce = ~Token(':')
        word = Token(Word(Lower()))
        scope = Delayed()
        line = (BLine(word[:] | Empty()) > list) | scope
        scope += BLine(word[:] & introduce) & Block(line[:]) > list
        parser = line[:].string_parser(LineAwareConfiguration(block_policy=2))
        self.examples([(lambda: parser('''
abc def
ghijk:
  mno pqr:
    stuv
  wx yz
'''), "[[], ['abc', 'def'], ['ghijk', ['mno', 'pqr', ['stuv']], ['wx', 'yz']]]")])

    def test_offside2(self):
        #basicConfig(level=DEBUG)
        introduce = ~Token(':')
        word = Token(Word(Lower()))
        statement = Delayed()
        simple = BLine(word[:])
        empty = BLine(Empty())
        block = BLine(word[:] & introduce) & Block(statement[:])
        statement += (simple | empty | block) > list
        parser = statement[:].string_parser(LineAwareConfiguration(block_policy=2))
        self.examples([(lambda: parser('''
abc def
ghijk:
  mno pqr:
    stuv
  wx yz
'''),
"[[], ['abc', 'def'], ['ghijk', ['mno', 'pqr', ['stuv']], ['wx', 'yz']]]")])
        
   
    def test_pithon(self):
        #basicConfig(level=DEBUG)
        
        word = Token(Word(Lower()))
        continuation = Token(r'\\')
        symbol = Token(Any('()'))
        introduce = ~Token(':')
        comma = ~Token(',')

        CLine = ContinuedBLineFactory(continuation)
                
        statement = Delayed()

        empty = Line(Empty())
        simple = CLine(word[1:])
        ifblock = CLine(word[1:] & introduce) & Block(statement[1:])

        args = Extend(word[:, comma]) > tuple
        fundef = word[1:] & ~symbol('(') & args & ~symbol(')')
        function = CLine(fundef & introduce) & Block(statement[1:])
        
        statement += (empty | simple | ifblock | function) > list
        
        parser = statement[:].string_parser(
                                LineAwareConfiguration(block_policy=2))

        self.examples([(lambda: parser('''
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
'''), 
"[[], ['this', 'is', 'a', 'grammar', 'with', 'a', 'similar'], "
"['line', 'structure', 'to', 'python'], [], "
"['if', 'something', ['then', 'we', 'indent']], "
"['else', ['something', 'else'], []], "
"['def', 'function', ('a', 'b', 'c'), "
"['we', 'can', 'nest', 'blocks', ['like', 'this']], "
"['and', 'we', 'can', 'also', 'have', 'explicit', 'continuations', "
"'with', 'any', 'indentation'], []], "
"['same', 'for', ('argument', 'lists'), "
"['which', 'do', 'not', 'need', 'the'], "
"['continuation', 'marker']]]")])
        
        
    def test_initial_offset(self):
        #basicConfig(level=DEBUG)
        word = Token(Word(Lower()))
        line = Delayed()
        block = Block(line[1:])
        # this also tests left recursion and blocks
        line += BLine(word | Empty()) | block
        parser = line[:].string_parser(
                        LineAwareConfiguration(block_policy=4, block_start=3))
        result = parser('''
   foo
       bar
''')
        assert result == [], result
         