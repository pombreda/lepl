
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
Error handling (generating an error while parsing).

This is not that complete or well thought through; it needs to be revised.
'''

from lepl.graph import postorder
from lepl.node import Node
from lepl.support import format


def make_error(msg):
    '''
    Create an error node using a format string.
    
    Invoke as ``** make_error('bad results: {results}')``, for example.
    '''
    def fun(stream_in, stream_out, results):
        '''
        Create the error node when results are available.
        '''
        return Error(results,
            *syntax_error_args(msg, stream_in, stream_out, results))
    return fun


STREAM_IN = 'stream_in'
STREAM_OUT = 'stream_out'
RESULTS = 'results'
FILENAME = 'filename'
LINENO = 'lineno'
OFFSET = 'offset'
LINE = 'line'


def syntax_error_args(msg, stream_in, stream_out, results):
    '''
    Helper function for constructing format dictionary.
    '''
    kargs = syntax_error_kargs(stream_in, stream_out, results)
    filename = kargs[FILENAME]
    lineno = kargs[LINENO]
    offset = kargs[OFFSET]
    line = kargs[LINE]
    # pylint: disable-msg=W0142
    return (format(msg, **kargs), (filename, lineno, offset, line))


def syntax_error_kargs(stream_in, stream_out, results):
    '''
    Helper function for constructing format dictionary.
    '''
    try:
        (lineno, offset, _depth, line, filename) = stream_in.location
        offset += 1 # appears to be 1-based?
    except AttributeError:
        filename = '<unknown> - use stream for better error reporting'
        lineno = -1
        offset = -1
        try:
            line = '...' + stream_in
        except TypeError:
            line = ['...'] + stream_in
    kargs = {STREAM_IN: stream_in, STREAM_OUT: stream_out, 
             RESULTS: results, FILENAME: filename, 
             LINENO: lineno, OFFSET:offset, LINE:line}
    return kargs


def raise_error(msg):
    '''
    As `make_error()`, but also raise the result.
    '''
    def fun(stream_in, stream_out, results):
        '''
        Delay raising the error until called in the parser.
        '''
        raise make_error(msg)(stream_in, stream_out, results)
    return fun


class Error(Node, SyntaxError):
    '''
    Subclass `Node` and Python's SyntaxError to provide an AST
    node that can be raised as an error via `throw`.
    
    Create with `make_error()`.
    '''
    
    def __init__(self, results, msg, location):
        # pylint: disable-msg=W0142
        Node.__init__(self, *results)
        SyntaxError.__init__(self, msg, location)
        
    def __str__(self):
        return SyntaxError.__str__(self)


def throw(node):
    '''
    Raise an error, if one exists in the results (AST trees are traversed).
    Otherwise, the results are returned (invoke with ``>>``).
    '''
    for child in postorder(node, Node):
        if isinstance(child, Exception):
            raise child
    return node
        

