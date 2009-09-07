
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
Illustrate some of the finer points of lexing.
'''

#from logging import basicConfig, DEBUG

from lepl import Token, Integer, Eos, Literal
from lepl._example.support import Example


class Limitations(Example):
    '''
    These are used in the lexer part of the manual.
    '''

    def test_ambiguity(self):
        '''
        A (signed) integer will consume a - sign. 
        '''
        tokens = (Token(Integer()) | Token(r'\-'))[:] & Eos()
        self.examples([(lambda: list(tokens.match('1-2')), 
                        "[(['1', '-2'], None[0:])]")])
        matchers = (Integer() | Literal('-'))[:] & Eos()
        self.examples([(lambda: list(matchers.match('1-2')), 
                        "[(['1', '-2'], ''), (['1', '-', '2'], '')]")])
    
    def test_complete(self):
        '''
        The complete flag indicates whether the entire token must be consumed.
        '''
        #basicConfig(level=DEBUG)
        abc = Token('abc')
        incomplete = abc(Literal('ab'))
        self.examples([(lambda: incomplete.parse('abc'), "None")])
        abc = Token('abc')
        incomplete = abc(Literal('ab'), complete=False)
        self.examples([(lambda: incomplete.parse('abc'), "['ab']")])
