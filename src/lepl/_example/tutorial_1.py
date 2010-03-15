
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


class Tutorial1Example(Example):
    
    def run_parse(self):
        return SignedFloat().parse('123')
    
    def run_match_error(self):
        return SignedFloat().parse('cabbage')
    
    def run_parse_all(self):
        return SignedFloat().parse_all('123')
    
    def run_parse_all_list(self):
        return list(SignedFloat().parse_all('123'))
    
    def run_sum(self):
        add = SignedFloat() & Literal('+') & SignedFloat()
        return add.parse('12+30')
    
    def run_float(self):
      number = SignedFloat() >> float
      return number.parse('12')
  
    def run_float_2(self):
        number = SignedFloat() >> float
        add = number & ~Literal('+') & number
        return add.parse('12+30')

    def run_float_3(self):
        add = (SignedFloat() & Drop(Literal('+')) & SignedFloat()) >> float
        return add.parse('12+30')
    
    def run_sum2(self):
        number = SignedFloat() >> float
        add = number & ~Literal('+') & number > sum
        return add.parse('12+30')

    def test_all(self):
        self.examples([
(self.run_parse,
"""['123']"""),
(self.run_match_error,
"""lepl.stream.maxdepth.FullFirstMatchException: The match failed at 'cabbage',
Line 1, character 0 of str: 'cabbage'.
"""),
(self.run_parse_all,
"""<map object at 0xdf45d0>"""),
(self.run_parse_all_list,
"""[['123'], ['12'], ['1']]"""),
(self.run_sum,
"""['12', '+', '30']"""),
(self.run_float,
"""[12.0]"""),
(self.run_float_2,
"""[12.0, 30.0]"""),
(self.run_float_3,
"""[12.0, 30.0]"""),
(self.run_sum2,
"""[42.0]"""),
])
        
