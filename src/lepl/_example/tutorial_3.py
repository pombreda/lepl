
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


class Tutorial3Example(Example):
    
    def run_add_sub_node(self):
        value = Token(UnsignedFloat())
        symbol = Token('[^0-9a-zA-Z \t\r\n]')
        number = Optional(symbol('-')) + value >> float
        expr = Delayed()
        add = number & symbol('+') & expr > List
        sub = number & symbol('-') & expr > List
        expr += add | sub | number
        return expr.parse('1+2-3 +4-5')[0]

    def test_all(self):
        
        abc = Node('a', 'b', 'c')
        fb = Node(('foo', 23), ('bar', 'baz'))
        fbz = Node(('foo', 23), ('bar', 'baz'), 43, 'zap', ('foo', 'again'))
        
        self.examples([
(self.run_add_sub_node,
"""List
 +- 1.0
 +- '+'
 `- List
     +- 2.0
     +- '-'
     `- List
         +- 3.0
         +- '+'
         `- List
             +- 4.0
             +- '-'
             `- 5.0"""),
(lambda: abc[1], """b"""),
(lambda: abc[1:], """['b', 'c']"""),
(lambda: abc[:-1], """['a', 'b']"""),
(lambda: fb.foo, """[23]"""),
(lambda: fb.bar, """['baz']"""),
(lambda: fbz[:], """[23, 'baz', 43, 'zap', 'again']"""),
(lambda: fbz.foo, """[23, 'again']"""),
])
        
