
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
Support the stack-scoped tracking of indentation level.
'''


from lepl.monitor import ActiveMonitor
from lepl.offside.support import OffsideException


class IndentationMonitor(ActiveMonitor):
    '''
    This tracks the current indentation level (in number of spaces).  It is
    read by `Line` and updated by `Block`.
    '''
    
    def __init__(self):
        super(IndentationMonitor, self).__init__()
        self.__stack = [0]
        
    def push_level(self, level):
        '''
        Add a new indentation level.
        '''
        self.__stack.append(level)
        
    def pop_level(self):
        '''
        Drop one level.
        '''
        self.__stack.pop()
        if not self.__stack:
            raise OffsideException('Closed an unopened indentation.') 
        
    @property
    def indentation(self):
        '''
        The current indentation value (number of spaces).
        '''
        return self.__stack[-1]
    
