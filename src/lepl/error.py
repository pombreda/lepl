

from lepl.graph import postorder
from lepl.node import Node

def make_error(msg):
    '''
    Create an error node using a format string.
    
    Invoke as ``** make_error('bad results: {results}')``, for example.
    '''
    def fun(stream_in, stream_out, results):
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
    try:
        return (msg.format(**kargs), (filename, lineno, offset, line))
    except:
        return (msg, (filename, lineno, offset, line))


def syntax_error_kargs(stream_in, stream_out, results):
    '''
    Helper function for constructing format dictionary.
    '''
    try:
        (lineno, offset, depth, line, filename) = stream_in.location()
        offset += 1 # appears to be 1-based?
    except:
        filename = '<unknown> - use stream for better error reporting'
        lineno = -1
        offset = -1
        try:
            line = '...' + stream_in
        except:
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
        error = make_error(msg)(stream_in, stream_out, results)
        raise error
    return fun


class Error(Node, SyntaxError):
    '''
    Subclass `Node` and Python's SyntaxError to provide an AST
    node that can be raised as an error via `throw`.
    
    Create with `make_error()`.
    '''
    
    def __init__(self, results, msg, location):
        Node.__init__(self, results)
        SyntaxError.__init__(self, msg, location)
        
    def __str__(self):
        return SyntaxError.__str__(self)


def throw(node):
    '''
    Raise an error, if one exists in the results (AST trees are traversed).
    Otherwise, the results are returned (invoke with ``>>``).
    '''
    for child in postorder(node, Node):
        if isinstance(node, Exception):
            raise node
    return node
        

