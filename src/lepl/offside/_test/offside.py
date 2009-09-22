
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
from lepl.functions import Letter, Digit
from lepl.matchers import Delayed, Or, Trace
from lepl.offside.config import LineAwareConfiguration
from lepl.offside.matchers import Block, BLine


# pylint: disable-msg=R0201
# unittest convention
class OffsideTest(TestCase):
    '''
    Test lines and blocks.
    '''
    
    def test_bline(self):
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
        line = Or(BLine(number), 
                  BLine(letter) & block) > list
        # and a block is simply a collection of lines, as above
        block += Block(line[1:])
        
        program = Trace(line[1:])
        
        text = '''1
2
a
 3
 b
  4
  5
 6
'''
        parser = program.string_parser(
                                config=LineAwareConfiguration(block_policy=1))
        result = parser(text)
        assert result == [['1'], 
                          ['2'], 
                          ['a', ['3'], 
                                ['b', ['4'], 
                                      ['5']], 
                                ['6']]], result
