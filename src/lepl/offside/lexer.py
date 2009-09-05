
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
Tokens for indentation.
'''


from lepl.lexer.matchers import BaseToken
from lepl.offside.regexp import START, END


# pylint: disable-msg=R0901, R0904, R0913, E1101
# lepl conventions
class Indentation(BaseToken):
    '''
    Match an indentation (start of line marker plus spaces and tabs).
    
    This token is identified by its class.
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        if id_ is None:
            id_ = START
        super(Indentation, self).__init__(content=content, id_=id_, 
                                          alphabet=alphabet, complete=complete, 
                                          compiled=compiled)
        self.regexp = '^[ \t]*'
                
        
class Eol(BaseToken):
    '''
    Match the end of line marker.
    
    This token is identified by its class.
    '''
    
    def __init__(self, content=None, id_=None, alphabet=None, complete=True, 
                 compiled=False):
        if id_ is None:
            id_ = END
        super(Eol, self).__init__(content=content, id_=id_, 
                                  alphabet=alphabet, complete=complete, 
                                  compiled=compiled)
        self.regexp = '$'


