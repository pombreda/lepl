
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
Show how line aware alphabet can be used.
'''

#@PydevCodeAnalysisIgnore


from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class LineAwareExample(Example):
    
    def test_regexp(self):
        #basicConfig(level=DEBUG)
        start = DfaRegexp('^ *')
        words = Word()[:,~Space()[:]] > list
        end = DfaRegexp('$')
        line = start & words & end
        parser = line.string_parser(LineOrientedConfiguration())
        self.examples([(lambda: parser('  abc def'), 
                        "['  ', ['abc', 'def'], '']")])


    def test_match(self):
        #basicConfig(level=DEBUG)
        start = SOL() & Space()[:, ...]
        words = Word()[:,~Space()[:]] > list
        end = EOL()
        line = start & words & end
        parser = line.string_parser(LineOrientedConfiguration())
        self.examples([(lambda: parser('  abc def'), 
                        "['  ', ['abc', 'def']]")])
