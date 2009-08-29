
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
Tests for indentation.
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.lexer.matchers import Token
from lepl.functions import Word, Letter
from lepl.offside.config import IndentationConfiguration
from lepl.offside.lexer import Indentation


# pylint: disable-msg=R0201
# unittest convention
class IndentationTest(TestCase):
    '''
    Test the `Indentation` token.
    '''
    
    def test_indentation(self):
        '''
        Test simple matches against leading spaces.
        '''
        #basicConfig(level=DEBUG)
        text = '''
left
    four'''
        word = Token(Word(Letter()))
        indent = Indentation()
        line1 = indent('')
        line2 = indent('') & word('left')
        line3 = indent('    ') & word('four')
        parser = (line1 & line2 & line3).string_parser(
                                        config=IndentationConfiguration())
        result = parser(text)
        assert result == ['', '', 'left', '    ', 'four'], result
        
        