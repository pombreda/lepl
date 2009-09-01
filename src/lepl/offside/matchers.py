
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
Matchers that are indentation aware.
'''

from lepl.matchers import OperatorMatcher
from lepl.offside.lexer import Indentation, Eol
from lepl.offside.monitor import IndentationMonitor


class Line(OperatorMatcher):
    '''
    Match an entire line, including indentation (if it matches the global 
    indentation level) and the end of line marker.
    '''
    
    indentation = Indentation()
    eol = Eol()
    
    def __init__(self, matcher):
        super(Line, self).__init__()
        self._arg(matcher=matcher)
        self.monitor_class = IndentationMonitor
        
    def on_push(self, monitor):
        '''
        Read the global indentation level.
        '''
        self.__current_indentation = monitor.indentation
        
    def _match(self, stream_in):
        (indent, stream) = yield (self.indentation._match(stream_in))
        