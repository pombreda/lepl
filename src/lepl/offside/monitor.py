
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
Support the stack-scoped tracking of indent level blocks.
'''


from lepl.monitor import ActiveMonitor
from lepl.offside.support import OffsideException
from lepl.support import LogMixin


class BlockMonitor(ActiveMonitor, LogMixin):
    '''
    This tracks the current indent level (in number of spaces).  It is
    read by `Line` and updated by `Block`.
    '''
    
    def __init__(self):
        super(BlockMonitor, self).__init__()
        self.__stack = [0]
        
    def push_level(self, level):
        '''
        Add a new indent level.
        '''
        self.__stack.append(level)
        self._debug('Indent -> {0:d}'.format(level))
        
    def pop_level(self):
        '''
        Drop one level.
        '''
        self.__stack.pop()
        if not self.__stack:
            raise OffsideException('Closed an unopened indent.') 
        self._debug('Indent <- {0:d}'.format(self.indent))
       
    @property
    def indent(self):
        '''
        The current indent value (number of spaces).
        '''
        return self.__stack[-1]
    
