
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
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#@PydevCodeAnalysisIgnore


from lepl import *
from lepl._example.support import Example


class ResourceExample(Example):
    
    def test_no_limit(self):
        matcher = (Literal('*')[:,...][2] & Eos()).match('*' * 4)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], ''), (['***', '*'], ''), (['**', '**'], ''), (['*', '***'], ''), (['****'], '')]")])

    def test_limit(self):
        config = Configuration(monitors=[GeneratorManager(queue_len=1)])
        matcher = (Literal('*')[:,...][2] & Eos()).match('*' * 4, config)
        self.examples([(lambda: list(matcher), 
                        "[(['****'], ''), (['***', '*'], '')]")])

