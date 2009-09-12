
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
from lepl.offside.lexer import Indent, Eol, BIndent, START, END
from lepl.offside.monitor import BlockMonitor
from lepl.filters import ExcludeSequence


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
        
    def on_pop(self, monitor):
        '''
        Remove the indent we added.
        '''
        if not self.__monitor: # only if we pushed
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
        # this flags we have pushed and need to pop
        self.__monitor = None
        
        generator = And(*self.lines)._match(stream_in)
        while True:
            yield (yield generator)


# pylint: disable-msg=C0103
# consistent interface
def Line(matcher):
    '''
    Match the matcher within a line.
    '''
    return ~Indent(compiled=True) & matcher & ~Eol(compiled=True)


def BLine(matcher):
    '''
    Match the matcher within a line with block indent.
    '''
    return ~BIndent(compiled=True) & matcher & ~Eol(compiled=True)


def only_token(token, item):
    '''
    Check whether the item (from a location stream of tokens) contains only
    the token specified.
    '''
    (tokens, _contents) = item
    return len(tokens) == 1 and tokens[0] == token.id_


def any_token(token, item):
    '''
    Check whether the item (from a location stream of tokens) contains at least
    the token specified.
    '''
    (tokens, _contents) = item
    return token.id_ in tokens


def CLineFactory(continuation):
    '''
    Return a BLine matcher that applies its contents to a stream which 
    continues past line breaks if the given token is present.
    '''
    def Cline(matcher):
        '''
        Like `BLine` (matches the `Block` indentation at the start), but
        continues over multiple lines if the continuation token is found
        at the end of each line.
        '''
        multiple = ExcludeSequence(any_token, 
                    [Eol(compiled=True), continuation, Indent(compiled=True)])
        return BLine(multiple(matcher))
    return Cline
    

Extend = ExcludeSequence(only_token, 
                         [Eol(compiled=True), Indent(compiled=True)])
'''
Provide a stream to the embedded matcher with `Indent` and `Eol` tokens 
filtered out.  On matching, return the "outer" stream at the appropriate
position (ie just after the last matched token in the filtered stream).
'''
