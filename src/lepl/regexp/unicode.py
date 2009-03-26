
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
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
A regexp implementation for unicode strings.
'''

from sys import maxunicode

from lepl.regexp.core import *
from lepl.regexp.str import *


class UnicodeAlphabet(StrAlphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    def __init__(self):
        try:
            max = chr(maxunicode)
        except: # Python 2.6
            max = unichr(maxunicode)
        super(UnicodeAlphabet, self).__init__(chr(0), max)
    
    def before(self, c): 
        '''
        Must return the character before c in the alphabet.  Never called with
        min (assuming input data are in range).
        ''' 
        return chr(ord(c)-1)
    
    def after(self, c): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return chr(ord(c)+1)


UNICODE = UnicodeAlphabet()


__compiled_unicode_parser = make_str_parser(UNICODE)
'''
Cache the parser to allow efficient re-use.
'''

def unicode_single_parser(label, text):
    '''
    Parse a Unicode regular expression, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)], 
                  UNICODE)


def unicode_parser(*regexps):
    '''
    Parse a set of Unicode regular expressions, returning the associated Regexp.
    '''
    return Regexp([Labelled(label, __compiled_unicode_parser(text), UNICODE)
                   for (label, text) in regexps], UNICODE)


