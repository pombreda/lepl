
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


class FullFirstMatchTest(Example):
    
    def run_null(self):
        matcher = Any()[5]
        try:
            matcher.parse_null('1234567')
        except FullFirstMatchException as e:
            print(str(e))
            return str(e)
        
    def run_string(self):
        matcher = Any()[5]
        try:
            matcher.parse_string('1234567')
        except FullFirstMatchException as e:
            print(str(e))
            return str(e)

    def test_all(self):
        self.examples([(self.run_null, "The match failed at '67'."),
                       (self.run_string,
"""The match failed at '67',
Line 1, character 5 of str: '1234567'.""")])
    
