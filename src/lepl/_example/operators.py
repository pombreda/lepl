
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

from lepl import *
from lepl._example.support import Example


class OperatorExamples(Example):
    
    def test_errors(self):
        self.examples([(lambda: eval("('Mr' | 'Ms') // Word()"),
                        "TypeError: unsupported operand type(s) for |: 'str' and 'str'\n"),
                       (lambda: eval("('Mr' // Word() > 'man' | 'Ms' // Word() > 'woman')"),
                        '''  File "<string>", line None
SyntaxError: The operator > for And was applied to a matcher (<Or>). Check syntax and parentheses.\n''')])

    def test_override(self):
        
        abcd = None
        with Override(or_=And, and_=Or):
            abcd = (Literal('a') & Literal('b')) | ( Literal('c') & Literal('d'))
        
        self.examples([(lambda: abcd.parse_string('ac'), "['a', 'c']"),
                       (lambda: abcd.parse_string('ab'), "None")])
            
        sentence = None
        word = Letter()[:,...]
        with Separator(r'\s+'):
            sentence = word[1:]
            
        self.examples([(lambda: sentence.parse_string('hello world'), 
                        "['hello', ' ', 'world']")])
        
