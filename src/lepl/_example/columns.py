
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

#@PydevCodeAnalysisIgnore
# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103
# (the code style is for documentation, not "real")

'''
Process a table of data based on values from
http://www.swivel.com/data_sets/spreadsheet/1002196
'''

#from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class ColumnExample(Example):
    
    def test_columns(self):
        #basicConfig(level=DEBUG)
        
        # http://www.swivel.com/data_sets/spreadsheet/1002196
        table = '''
US Foreign Aid, top recipients, constant dollars
Year            Iraq          Israel           Egypt
2005   6,981,200,000   2,684,100,000   1,541,900,000
2004   8,333,400,000   2,782,400,000   2,010,600,000
2003   4,150,000,000   3,878,300,000   1,849,600,000
2002      41,600,000   2,991,200,000   2,362,800,000
'''
        spaces = ~Space()[:]
        integer = (spaces & Digit()[1:, ~Optional(','), ...] & spaces) >> int
        cols = Columns((4,  integer),
                       # if we give widths, they follow on from each other
                       (16, integer),
                       # we can also specify column indices
                       ((23, 36), integer),
                       # and then start with widths again
                       (16, integer))
        # by default, Columns consumes a whole line (see skip argument), so
        # for the whole table we only need to (1) drop the text and (2) put
        # each row in a separate list.
        parser = ~SkipTo(Digit(), include=False) & (cols > list)[:]
        
        self.examples([(lambda: parser.parse(table),
                        '[[2005, 6981200000, 2684100000, 1541900000], ' 
                        '[2004, 8333400000, 2782400000, 2010600000], ' 
                        '[2003, 4150000000, 3878300000, 1849600000], ' 
                        '[2002, 41600000, 2991200000, 2362800000]]')])
        

        
        
        