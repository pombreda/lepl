
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#from logging import basicConfig, getLogger, DEBUG, INFO

from lepl import *
from lepl._example.support import Example


class LexerExample(Example):
    
    def test_add(self):
        
        #basicConfig(level=DEBUG)
        #basicConfig(level=INFO)
        #getLogger('lepl.lexer.stream.lexed_simple_stream').setLevel(DEBUG)
        
        value = Token(UnsignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = value >> float
        add = number & ~symbol('+') & number > sum
        self.examples([
            (lambda: add.parse('12+30'), '[42.0]')])

    def test_bad(self):
        
        #basicConfig(level=DEBUG)
        #basicConfig(level=INFO)
        #getLogger('lepl.lexer.stream.lexed_simple_stream').setLevel(DEBUG)
        
        value = Token(SignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = value >> float
        add = number & ~symbol('+') & number > sum
        self.examples([
            (lambda: add.parse('12+30'), 'None')])

