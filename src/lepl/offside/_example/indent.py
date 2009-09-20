
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
Show how the Indent and Eol tokens can be used
'''

# pylint: disable-msg=W0614, W0401, C0111
#@PydevCodeAnalysisIgnore


from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class IndentExample(Example):
    
    def test_indent(self):
        #basicConfig(level=DEBUG)
        words = Token(Word(Lower()))[:] > list
        line = Indent() & words & Eol()
        parser = line.string_parser(LineOrientedConfiguration(tabsize=4))
        self.examples([(lambda: parser('\tabc def'), 
                        "['    ', ['abc', 'def'], '']")])
