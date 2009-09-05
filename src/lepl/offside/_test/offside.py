
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
Tests for offside.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.lexer.matchers import Token
from lepl.functions import Word, Letter, Digit
from lepl.matchers import Delayed, Or
from lepl.offside.config import OffsideConfiguration
from lepl.offside.lexer import Indentation, Eol
from lepl.offside.matchers import Line, Block


# pylint: disable-msg=R0201
# unittest convention
class TabTest(TestCase):
    '''
    Like the indentation test, but check that spaces replaced with a count.
    '''
    
    def test_indentation(self):
        '''
        Test simple matches against leading spaces.
        '''
        #basicConfig(level=DEBUG)
        text = '''
 onespace
 \tspaceandtab'''
        word = Token(Word(Letter()))
        indent = Indentation()
        line1 = indent('') + Eol()
        line2 = indent(' ') & word('onespace') + Eol()
        line3 = indent('     ') & word('spaceandtab') + Eol()
        parser = (line1 & line2 & line3).string_parser(
                            config=OffsideConfiguration(tabsize=4))
        result = parser(text)
        assert result == ['', ' ', 'onespace', '     ', 'spaceandtab'], result
        
    
class OffsideTest(TestCase):
    '''
    Test lines and blocks.
    '''
    
    def test_offside(self):
        '''
        Test a simple example: letters introduce numbers in an indented block.
        '''
        #basicConfig(level=DEBUG)
        
        number = Token(Digit())
        letter = Token(Letter())
        
        # the simplest whitespace grammar i can think of - lines are either
        # numbers (which are single, simple statements) or letters (which
        # mark the start of a new, indented block).
        block = Delayed()
        line = Or(Line(number), 
                  Line(letter) & block) > list
        # and a block is simply a collection of lines, as above
        block += Block(line[1:])
        
        program = line[1:]
        
        text = '''1
2
a
 3
 b
  4
  5
 6
'''
        parser = program.string_parser(config=OffsideConfiguration(policy=1))
        result = parser(text)
        assert result == [['1'], 
                          ['2'], 
                          ['a', ['3'], 
                                ['b', ['4'], 
                                      ['5']], 
                                ['6']]]
