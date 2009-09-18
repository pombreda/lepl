
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,W0621,W0703
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

from logging import getLogger
from unittest import TestCase
from traceback import format_exception_only, format_exc


class Example(TestCase):
    
    def examples(self, examples):
        '''
        Run each example and check expected against actual output. 
        '''
        for (example, target) in examples:
            try:
                result = str(example())
            except Exception as e:
                getLogger('lepl._example.support.Example').debug(format_exc())
                result = ''.join(format_exception_only(type(e), e))
            # Python 2.6 unicode strings - hack removal
            result = result.replace("u'", "'")
            assert target == result, '"' + result + '" != "' + target + '"'
