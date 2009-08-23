
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
A regexp implementation for unicode strings.
'''

from sys import maxunicode

from lepl.regexp.str import StrAlphabet


class UnicodeAlphabet(StrAlphabet):
    '''
    An alphabet for unicode strings.
    '''
    
    __cached_instance = None
    
    # pylint: disable-msg=E1002
    # (pylint bug?  this chains back to a new style abc)
    def __init__(self):
        max_ = self.chr(maxunicode)
        super(UnicodeAlphabet, self).__init__(self.chr(0), max_)
        
    @staticmethod
    def chr(code):
        '''
        Convert to a character.
        '''
        try:
            # Python 2.6
            return unichr(code)
        except NameError:
            return chr(code)
    
    def before(self, char):
        '''
        Must return the character before char in the alphabet.  Never called 
        with min (assuming input data are in range).
        ''' 
        return self.chr(ord(char)-1)
    
    def after(self, char): 
        '''
        Must return the character after c in the alphabet.  Never called with
        max (assuming input data are in range).
        ''' 
        return self.chr(ord(char)+1)
    
    @classmethod
    def instance(cls):
        '''
        Get an instance of this alphabet (avoids creating new objects).
        '''
        if cls.__cached_instance is None:
            cls.__cached_instance = UnicodeAlphabet()
        return cls.__cached_instance
