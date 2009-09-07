
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
A proof-of-concept regexp implementation for binary data strings.

The hope is that one day we can parse binary data in the same way as text...
'''

from lepl.regexp.core import Expression, Labelled
from lepl.regexp.str import StrAlphabet, make_str_parser


class BinaryAlphabet(StrAlphabet):
    '''
    An alphabet for binary strings.
    '''
    
    # pylint: disable-msg=E1002
    # (pylint bug?  this chains back to a new style abc)
    def __init__(self):
        super(BinaryAlphabet, self).__init__(0, 1)
    
    def before(self, char): 
        '''
        Must return the character before c in the alphabet.  Never called with
        min (assuming input data are in range).
        ''' 
        return char-1
    
    def after(self, char): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return char+1
    
    def from_char(self, char):
        '''
        Convert to 0 or 1.
        '''
        char = int(char)
        assert char in (0, 1)
        return char


BINARY = BinaryAlphabet()


# pylint: disable-msg=W0105, C0103
__compiled_binary_parser = make_str_parser(BINARY)
'''
Cache the parser to allow efficient re-use.
'''

def binary_single_parser(label, text):
    '''
    Parse a binary regular expression, returning the associated Regexp.
    '''
    return Expression([Labelled(label, __compiled_binary_parser(text), BINARY)], 
                      BINARY)


def binary_parser(*regexps):
    '''
    Parse a set of binary regular expressions, returning the associated Regexp.
    '''
    return Expression([Labelled(label, __compiled_binary_parser(text), BINARY)
                       for (label, text) in regexps], BINARY)


