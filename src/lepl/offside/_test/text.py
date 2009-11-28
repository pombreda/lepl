
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
An example that avoids using tokens (in a sense) with the line aware
parsing.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl import *


class TextTest(TestCase):
    
    def parser(self):
        '''
        Construct a parser that uses "offside rule" parsing, but which
        avoids using tokens in the grammar.
        '''
        
        # we still need one token, which matches "all the text"
        # for version 3.3.x we must exclude the line start + end
        # TODO - why does this break with * instead of +?
        Text = Token('[^(*SOL)(*EOL)\n]+')
        
        def TLine(contents):
            '''
            A version of BLine() that takes text-based matchers.
            '''
            return BLine(Text(contents))
        
        # from here on we use TLine instead of BLine and don't worry about
        # tokens.
        
        # first define the basic grammar
        with Separator(~Space()[:]):
            name = Word()
            args = name[:, ',']
            fundef = 'def' & name & '(' & args & ')' & ':'
            # in reality we would have more expressions!
            expression = Literal('pass') 
        
        # then define the block structure
        statement = Delayed()
        simple = TLine(expression)
        empty = TLine(Empty())
        block = TLine(fundef) & Block(statement[:])
        statement += (simple | empty | block) > list

        return statement[:].string_parser(
                    LineAwareConfiguration(block_policy=2))
        
    def test_text(self):
        parser = self.parser()
        result = parser('''pass
def foo():
  pass
  def bar():
    pass
''')
        assert result == [['pass'], 
                          ['def', 'foo', '(', ')', ':', 
                           ['pass'], 
                           ['def', 'bar', '(', ')', ':', 
                            ['pass']]]], result


class TextStarTest(TestCase):
    '''
    The above failed when '*' used in regexp.  This is because tokens matching
    an empty string are not a good idea - we now catch this in the underlying
    stream handling (a warning message is generated).
    '''
    
    def parser(self):
        '''
        Construct a parser that uses "offside rule" parsing, but which
        avoids using tokens in the grammar.
        '''
        
        Text = Token('[^(*SOL)(*EOL)\n]*')
        
        def TLine(contents):
            '''
            A version of BLine() that takes text-based matchers.
            '''
            return BLine(Text(contents))
        
        # from here on we use TLine instead of BLine and don't worry about
        # tokens.
        
        # first define the basic grammar
        with Separator(~Space()[:]):
            name = Word()
            args = name[:, ',']
            fundef = 'def' & name & '(' & args & ')' & ':'
            # in reality we would have more expressions!
            expression = Literal('pass') 
        
        # then define the block structure
        statement = Delayed()
        simple = TLine(expression)
        empty = TLine(Empty())
        block = TLine(fundef) & Block(statement[:])
        statement += (simple | empty | block) > list

        return statement[:].string_parser(
                    LineAwareConfiguration(block_policy=2))
        
    def test_text(self):
        #basicConfig(level=DEBUG)
        parser = self.parser()
        result = parser('''pass
def foo():
  pass
  def bar():
    pass
''')
        assert result == [['pass'], 
                          ['def', 'foo', '(', ')', ':', 
                           ['pass'], 
                           ['def', 'bar', '(', ')', ':', 
                            ['pass']]]], result
