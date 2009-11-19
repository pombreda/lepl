
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
from lepl.offside.support import OffsideError
from lepl.state import State
from lepl.support import LogMixin, format


class BlockMonitor(ActiveMonitor, LogMixin):
    '''
    This tracks the current indent level (in number of spaces).  It is
    read by `Line` and updated by `Block`.
    '''
    
    def __init__(self, start=0):
        '''
        start is the initial indent (in spaces).
        '''
        super(BlockMonitor, self).__init__()
        self.__stack = [start]
        self.__state = State.singleton()
        
    def push_level(self, level):
        '''
        Add a new indent level.
        '''
        self.__stack.append(level)
        self.__state[BlockMonitor] = level
        self._debug(format('Indent -> {0:d}', level))
        
    def pop_level(self):
        '''
        Drop one level.
        '''
        self.__stack.pop()
        if not self.__stack:
            raise OffsideError('Closed an unopened indent.') 
        self.__state[BlockMonitor] = self.indent
        self._debug(format('Indent <- {0:d}', self.indent))
       
    @property
    def indent(self):
        '''
        The current indent value (number of spaces).
        '''
        return self.__stack[-1]
    

def block_monitor(start=0):
    '''
    Add an extra lambda for the standard monitor interface.
    '''
    return lambda: BlockMonitor(start)
