
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

from lepl.matchers import OperatorMatcher, And
from lepl.parser import tagged
from lepl.offside.lexer import Indentation, Eol
from lepl.offside.monitor import IndentationMonitor


# pylint: disable-msg=E1101, R0901, R0904, W0212
# lepl conventions
class Line(OperatorMatcher):
    '''
    Match an entire line, including indentation (if it matches the global 
    indentation level) and the end of line marker.
    '''
    
    indentation = Indentation(compiled=True)
    eol = Eol(compiled=True)
    
    def __init__(self, matcher):
        super(Line, self).__init__()
        self._arg(matcher=matcher)
        self.monitor_class = IndentationMonitor
        self.__current_indentation = None
        
    def on_push(self, monitor):
        '''
        Read the global indentation level.
        '''
        self.__current_indentation = monitor.indentation
        
    def on_pop(self, monitor):
        '''
        Unused
        '''
        
    @tagged
    def _match(self, stream_in):
        '''
        If indentation matches current level match contents and Eol.
        '''
        (indent, stream) = yield self.indentation._match(stream_in)
        try:
            if len(indent[0]) == self.__current_indentation:
                generator = self.matcher._match(stream)
                while True:
                    (result, stream) = yield generator
                    try:
                        (_eol, stream) = yield self.eol._match(stream)
                        yield (result, stream)
                    except StopIteration:
                        # no eol
                        pass
            else:
                self._debug('Incorrect indentation ({0:d} != '
                            'len({1!r}), {2:d})'\
                            .format(self.__current_indentation,
                                    indent[0], len(indent[0])))
        except StopIteration:
            return


def constant_indent(n_spaces):
    '''
    Construct a simple policy for `Block` that increments the indentation
    by some fixed number of spaces.
    '''
    def policy(current, _indentation):
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
By default, expect an indentation equivalent to a tab.
'''


class Block(OperatorMatcher):
    '''
    Set a new indent level for the enclosed matchers (typically `Line` and
    `Block` instances).
    
    In the simplest case, this might increment the global indent by 4, say.
    In a more complex case it might look at the current token, expecting an
    `Indentation`, and set the global indent at that amount if it is larger
    than the current value.
    
    A block will always match an `Indentation`, but will not consumer it
    (it will remain in the stream after the block has finished).
    '''
    
    POLICY = 'policy'
    indentation = Indentation(compiled=True)
    
#    def __init__(self, *lines, policy=None):
    def __init__(self, *lines, **kargs):
        '''
        Lines are invoked in sequence (like `And()`).
        
        The policy is passed the current level and the indentation and must 
        return a new level.  Typically it is set globally by rewriting with
        a default in the configuration.  If it is given as an integer then
        `constant_indent` is used to create a policy from that.
        '''
        super(Block, self).__init__()
        self._args(lines=lines)
        self._kargs(kargs)
        if self.POLICY in kargs:
            policy = kargs[self.POLICY]
        else:
            policy = DEFAULT_POLICY
        if isinstance(policy, int):
            policy = constant_indent(policy)
        self.policy = policy
        self.monitor_class = IndentationMonitor
        self.__monitor = None
        
    def on_push(self, monitor):
        '''
        Store a reference to the monitor which we will update when _match
        is invoked (ie immediately).
        '''
        self.__monitor = monitor
        
    def on_pop(self, monitor):
        '''
        Remove the indentation we added.
        '''
        monitor.pop_level()
        
    @tagged
    def _match(self, stream_in):
        '''
        Pull indentation and call the policy and update the global value, 
        then evaluate the contents.
        '''
        (indent, _stream) = yield self.indentation._match(stream_in)
        current = self.__monitor.indentation
        self.__monitor.push_level(self.policy(current, indent))
        self.__monitor = None
        
        generator = And(*self.lines)._match(stream_in)
        while True:
            yield (yield generator)
        