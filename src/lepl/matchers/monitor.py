
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
Matchers that interact with monitors.
'''

from lepl.matchers.core import OperatorMatcher
from lepl.core.manager import _GeneratorManager
from lepl.core.trace import _TraceResults
from lepl.core.parser import tagged


class Commit(OperatorMatcher):
    '''
    Commit to the current state - deletes all backtracking information.
    This only works if the `GeneratorManager` monitor is present
    (see `Configuration`) and the min_queue option is greater than zero.
    '''
    
    def __init__(self):
        super(Commit, self).__init__()
        self.monitor_class = _GeneratorManager
    
    # pylint: disable-msg=R0201
    # consistent for subclasses
    @tagged
    def _match(self, _stream):
        '''
        Attempt to match the stream.
        '''
        if False:
            yield
    
    def on_push(self, monitor):
        '''
        Do nothing on entering matcher.
        '''
        pass
    
    def on_pop(self, monitor):
        '''
        On leaving, commit.
        '''
        monitor.commit()
    
    
# pylint: disable-msg=E1101, W0212
class Trace(OperatorMatcher):
    '''
    Enable trace logging for the sub-matcher.
    '''
    
    def __init__(self, matcher, trace=True):
        super(Trace, self).__init__()
        self._arg(matcher=matcher)
        self._karg(trace=trace)
        self.monitor_class = _TraceResults

    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        try:
            generator = self.matcher._match(stream)
            while True:
                yield (yield generator)
        except StopIteration:
            pass
        
    def on_push(self, monitor):
        '''
        On entering, switch monitor on.
        '''
        monitor.switch(1 if self.trace else -1)
        
    def on_pop(self, monitor):
        '''
        On leaving, switch monitor off.
        '''
        monitor.switch(-1 if self.trace else 1)
        
    
