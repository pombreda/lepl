
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
Support for matcher tests.
'''

#from logging import basicConfig, DEBUG
from re import sub
from unittest import TestCase

from lepl.support.lib import basestring, str


class BaseTest(TestCase):
    
    def assert_direct(self, stream, match, target):
        match.config.no_full_first_match()
        result = [x for (x, _s) in match.match_string(stream)]
        assert target == result, result
    
    def assert_list(self, stream, match, target, **kargs):
        match.config.no_full_first_match()
        matcher = match.get_parse_items_all()
        #print(matcher.matcher)
        result = list(matcher(stream, **kargs))
        assert target == result, result
        
def assert_str(a, b):
    '''
    Assert two strings are approximately equal, allowing tests to run in
    Python 3 and 2.
    '''
    def clean(x):
        x = str(x)
        x = x.replace("u'", "'")
        x = x.replace("lepl.matchers.error.Error", "Error")
        x = x.replace("lepl.stream.maxdepth.FullFirstMatchException", "FullFirstMatchException")
        x = sub('<(.+) 0x[0-9a-fA-F]*>', '<\\1 0x...>', x)
        x = sub('(\\d+)L', '\\1', x)
        return x
    a = clean(a)
    b = clean(b)
    assert a == b, '"' + a + '" != "' + b + '"'
