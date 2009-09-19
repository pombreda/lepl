
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0201,R0903
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class ErrorTest(Example):
    
    def make_parser(self):

        #basicConfig(level=DEBUG)
        
        class Term(Node): pass
        class Factor(Node): pass
        class Expression(Node): pass
        
        expr    = Delayed()
        number  = Digit()[1:,...]                          > 'number'
        badChar = AnyBut(Space() | Digit() | '(')[1:,...]
        
        with Separator(r'\s*'):
            
            unopen   = number ** make_error("no ( before '{stream_out}'") & ')'
            unclosed = ('(' & expr & Eos()) ** make_error("no ) for '{stream_in}'")
        
            term    = Or(
                         (number | '(' & expr & ')')      > Term,
                         badChar                          ^ 'unexpected text: {results[0]}',
                         unopen                           >> throw,
                         unclosed                         >> throw
                         )
            muldiv  = Any('*/')                           > 'operator'
            factor  = (term & (muldiv & term)[:])         > Factor
            addsub  = Any('+-')                           > 'operator'
            expr   += (factor & (addsub & factor)[:])     > Expression
            line    = Empty() & Trace(expr) & Eos()
        
        return line.parse_string
    
    def test_errors(self):
        parser = self.make_parser()
        self.examples([(lambda: parser('1 + 2 * (3 + 4 - 5')[0],
                       """  File "str: '1 + 2 * (3 + 4 - 5'", line 1
    1 + 2 * (3 + 4 - 5
            ^
lepl.error.Error: no ) for '(3 + 4 - 5'
"""),
                       (lambda: parser('1 + 2 * 3 + 4 - 5)')[0],
                        """  File "str: '1 + 2 * 3 + 4 - 5)'", line 1
    1 + 2 * 3 + 4 - 5)
                    ^
lepl.error.Error: no ( before ')'
"""),
                       (lambda: parser('1 + 2 * (3 + four - 5)')[0],
                        """  File "str: '1 + 2 * (3 + four - 5)'", line 1
    1 + 2 * (3 + four - 5)
                 ^
lepl.error.Error: unexpected text: four
"""),
                       (lambda: parser('1 + 2 ** (3 + 4 - 5)')[0],
                        """  File "str: '1 + 2 ** (3 + 4 - 5)'", line 1
    1 + 2 ** (3 + 4 - 5)
           ^
lepl.error.Error: unexpected text: *
""")])
        