
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
Matchers that are indent aware.
'''

from lepl.matchers import OperatorMatcher, And
from lepl.parser import tagged
from lepl.offside.lexer import Indent, Eol, BIndent
from lepl.offside.monitor import BlockMonitor
from lepl.filters import Filter


def constant_indent(n_spaces):
    '''
    Construct a simple policy for `Block` that increments the indent
    by some fixed number of spaces.
    '''
    def policy(current, _indent):
        '''
        Increment current by n_spaces
        '''
        return current + n_spaces
    return policy


# pylint: disable-msg=W0105
# epydoc convention
DEFAULT_TABSIZE = 8
'''
The default number of spaces for a tab.
'''

DEFAULT_POLICY = constant_indent(DEFAULT_TABSIZE)
'''
By default, expect an indent equivalent to a tab.
'''


# pylint: disable-msg=E1101, W0212, R0901, R0904
# pylint conventions
class Block(OperatorMatcher):
    '''
    Set a new indent level for the enclosed matchers (typically `Line` and
    `Block` instances).
    
    In the simplest case, this might increment the global indent by 4, say.
    In a more complex case it might look at the current token, expecting an
    `Indent`, and set the global indent at that amount if it is larger
    than the current value.
    
    A block will always match an `Indent`, but will not consumer it
    (it will remain in the stream after the block has finished).
    '''
    
    POLICY = 'policy'
    INDENT = 'indent'
    # class-wide default
    __indent = Indent()
    
# Python 2.6 does not support this syntax
#    def __init__(self, *lines, policy=None, indent=None):
    def __init__(self, *lines, **kargs):
        '''
        Lines are invoked in sequence (like `And()`).
        
        The policy is passed the current level and the indent and must 
        return a new level.  Typically it is set globally by rewriting with
        a default in the configuration.  If it is given as an integer then
        `constant_indent` is used to create a policy from that.
        '''
        super(Block, self).__init__()
        self._args(lines=lines)
        policy = kargs.get(self.POLICY, DEFAULT_POLICY)
        if isinstance(policy, int):
            policy = constant_indent(policy)
        self._karg(policy=policy)
        indent = kargs.get(self.INDENT, self.__indent)
        self._karg(indent=indent)
        self.monitor_class = BlockMonitor
        self.__monitor = None
        
    def on_push(self, monitor):
        '''
        Store a reference to the monitor which we will update when _match
        is invoked (ie immediately).
        '''
        self.__monitor = monitor
        
    @staticmethod
    def on_pop(monitor):
        '''
        Remove the indent we added.
        '''
        monitor.pop_level()
        
    @tagged
    def _match(self, stream_in):
        '''
        Pull indent and call the policy and update the global value, 
        then evaluate the contents.
        '''
        (indent, _stream) = yield self.indent._match(stream_in)
        current = self.__monitor.indent
        self.__monitor.push_level(self.policy(current, indent))
        self.__monitor = None
        
        generator = And(*self.lines)._match(stream_in)
        while True:
            yield (yield generator)


# pylint: disable-msg=C0103
# consistent interface
def BLine(matcher):
    '''
    Match the matcher within a block indent.
    '''
    return ~BIndent() & matcher & ~Eol()


class Nodent(OperatorMatcher):
    '''
    Provide a stream to the embedded matcher with `Indent` and `Eol` tokens 
    filtered out.  On matching, return the "outer" stream at the appropriate
    position (ie just after the last matched token in the filtered stream).
    '''
    
    def __init__(self, matcher):
        super(Nodent, self).__init__()
        self._arg(matcher=matcher)
    
    @staticmethod
    def filter(token):
        '''
        Remove `Indent` and `Eol` tokens.
        '''
        return not isinstance(token, Indent) and not isinstance(token, Eol)
    
    @tagged
    def _match(self, stream_in):
        '''
        Provide a filtered stream to the embedded matcher.
        '''
        filter_ = Filter(self.filter, stream_in)
        generator = self.matcher._match(filter_.stream)
        try:
            while True:
                (result, stream) = yield generator
                yield (result, filter_.locate(stream))
        except StopIteration:
            return
